import asyncio
import httpx
import re
import json
import base64
import time
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import Embedding, KnowledgeSourceType
from app.models.chatbot import Chatbot
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.services.embedding_service import get_single_embedding
from app.services.vision_service import VisionService, ImageAttributes
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.chat import ChatMessageResponse, ChatSource, ImageAnalysisResult

logger = get_logger(__name__)

# Confidence threshold for vision analysis
VISION_CONFIDENCE_THRESHOLD = 0.4

class ChatService:
    @staticmethod
    async def get_or_create_session(db: AsyncSession, chatbot_id: UUID, session_id: Optional[str] = None, is_preview: bool = False) -> ChatSession:
        if session_id:
            try:
                session_uuid = UUID(session_id)
                stmt = select(ChatSession).where(ChatSession.id == session_uuid, ChatSession.chatbot_id == chatbot_id)
                result = await db.execute(stmt)
                session = result.scalar_one_or_none()
                if session:
                    return session
            except (ValueError, AttributeError):
                pass
        
        # Create new session if not found or invalid
        session = ChatSession(chatbot_id=chatbot_id, is_preview=is_preview)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_history(db: AsyncSession, session_id: UUID, limit: int = 6) -> List[ChatMessage]:
        stmt = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(desc(ChatMessage.created_at)).limit(limit)
        result = await db.execute(stmt)
        return list(reversed(result.scalars().all()))

    @staticmethod
    async def summarize_conversation(
        session: ChatSession, 
        last_messages: List[ChatMessage]
    ) -> str:
        if not last_messages:
            return session.conversation_summary or ""

        messages_str = "\n".join([f"{m.role.value}: {m.content}" for m in last_messages])
        
        async with httpx.AsyncClient() as client:
            prompt = (
                "Summarize this conversation in 1-2 sentences, focusing on what the user is looking for:\n"
                f"{messages_str}\n\n"
                f"Previous summary: {session.conversation_summary or 'None'}\n\n"
                "Updated summary:"
            )
            
            try:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-8b-instant", # Use a smaller model for summarization
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant that summarizes conversations accurately and concisely."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    res_data = response.json()
                    return res_data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                logger.error(f"Error generating summary: {e}")
        
        return session.conversation_summary or ""

    @staticmethod
    async def get_response(
        db: AsyncSession,
        chatbot_id: UUID,
        message: Optional[str] = None,
        session_id: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        is_preview: bool = False
    ) -> ChatMessageResponse:
        # Track response time
        start_time = time.time()
        
        # --- 1. Get/Create Session ---
        session = await ChatService.get_or_create_session(db, chatbot_id, session_id, is_preview=is_preview)
        
        # --- 2. Get chatbot and history ---
        chatbot_stmt = select(Chatbot).where(Chatbot.id == chatbot_id)
        chatbot_res = await db.execute(chatbot_stmt)
        chatbot = chatbot_res.scalar_one()
        
        history = await ChatService.get_history(db, session.id, limit=6)
        summary = session.conversation_summary or ""

        # --- 3. Process image if provided ---
        image_attrs: Optional[ImageAttributes] = None
        image_analysis_result: Optional[ImageAnalysisResult] = None
        
        if image_bytes:
            logger.info("Processing uploaded image...")
            image_attrs = await VisionService.analyze_image(image_bytes)
            
            # Build image analysis result for response
            needs_clarification = image_attrs.confidence < VISION_CONFIDENCE_THRESHOLD
            image_analysis_result = ImageAnalysisResult(
                product_type=image_attrs.product_type,
                category=image_attrs.category,
                color=image_attrs.color,
                style=image_attrs.style,
                other_attributes=image_attrs.other_attributes,
                confidence=image_attrs.confidence,
                needs_clarification=needs_clarification
            )
            
            logger.info(f"Image analysis: {image_attrs.to_dict()}")

        # --- 4. Build effective search query ---
        # Combine user message with image attributes (user text overrides image)
        text_content = message or ""
        effective_message = VisionService.build_combined_query(text_content, image_attrs) if image_attrs else text_content
        
        # --- 5. Hybrid Search with context ---
        # Search query includes message + summary for better context
        search_query = f"{effective_message} | Context: {summary}" if summary else effective_message
        
        # Get query embedding from HuggingFace API
        query_vector = await get_single_embedding(search_query)
        
        vector_stmt = select(
            Embedding,
            (1 - Embedding.embedding.cosine_distance(query_vector)).label("similarity")
        ).where(
            Embedding.chatbot_id == chatbot_id
        ).order_by(
            Embedding.embedding.cosine_distance(query_vector)
        ).limit(10)
        
        vector_results = await db.execute(vector_stmt)
        vector_hits = vector_results.all()

        keyword_stmt = select(Embedding).where(
            Embedding.chatbot_id == chatbot_id,
            Embedding.content.ilike(f"%{message}%")
        ).limit(5)
        
        keyword_results = await db.execute(keyword_stmt)
        keyword_hits = keyword_results.scalars().all()

        seen_ids = set()
        combined_results = []

        for emb, sim in vector_hits:
            if emb.id not in seen_ids:
                score = sim * emb.priority_weight
                if emb.source_type == KnowledgeSourceType.QA_PAIR:
                    score += 0.15
                combined_results.append({"embedding": emb, "score": score})
                seen_ids.add(emb.id)

        for emb in keyword_hits:
            if emb.id not in seen_ids:
                score = 0.8 * emb.priority_weight 
                if emb.source_type == KnowledgeSourceType.QA_PAIR:
                    score += 0.15
                combined_results.append({"embedding": emb, "score": score})
                seen_ids.add(emb.id)

        combined_results.sort(key=lambda x: x["score"], reverse=True)
        top_chunks = combined_results[:5]
        
        # Track retrieval confidence (highest similarity score)
        retrieval_confidence = top_chunks[0]["score"] if top_chunks else 0.0
        sources_count = len(top_chunks)

        # --- 6. Prepare LLM Prompt ---

        context_text = "\n\n".join([c["embedding"].content for c in top_chunks])
        
        # Build image context for LLM if image was analyzed
        image_context = ""
        if image_attrs and image_attrs.confidence >= VISION_CONFIDENCE_THRESHOLD:
            image_context = (
                f"\n\nImage Analysis: The user uploaded an image showing a {image_attrs.color} {image_attrs.product_type}"
                f" ({image_attrs.style} style, {image_attrs.category} category)."
                f" Additional details: {image_attrs.other_attributes}"
            )
        elif image_attrs and image_attrs.confidence < VISION_CONFIDENCE_THRESHOLD:
            image_context = "\n\nNote: User uploaded an image but it was unclear. Ask for clarification if needed."
        
        # improved System Prompt
        system_prompt = (
            f"You are a helpful AI assistant for {chatbot.name}.\n"
            "Your goal is to assist users based on the provided Knowledge Base context.\n"
            "\n"
            "--- GUIDELINES ---\n"
            "1. **Context-Only Principle**: Answer questions **exclusively** using the information in the 'Background Context' below. "
            "Do not use outside knowledge or make assumptions. If the answer is not in the context, strictly state that you don't have that information.\n"
            "2. **Greetings & Pleasantries**: If the user sends a greeting (e.g., 'Hi', 'Hello') or polite expression ('Thanks', 'Good job'), "
            "reply naturally and politely. You do NOT need context for this.\n"
            "3. **Irrelevant Queries**: If the user asks about topics completely unrelated to the business/context (e.g., political figures, celebrities, general trivia), "
            "reply nicely that you can only answer questions related to {chatbot.name}, and append the tag `[[IRRELEVANT]]` to the very end of your response.\n"
            "4. **Missing Information**: If the question IS relevant to the business but the specific answer is not in the context, "
            "apologize and state you don't have that information, and append the tag `[[MISSING_INFO]]` to the very end of your response.\n"
            "5. **Response Format**: Keep answers concise, professional and formatted in Markdown.\n"
            "\n"
            f"Background Context: {summary}{image_context}\n"
            f"{context_text}\n"
            "\n"
            "--- STRICT RESPONSE FORMAT ---\n"
            "1. Your Answer\n"
            "2. (Optional) `[[IRRELEVANT]]` or `[[MISSING_INFO]]` tag if applicable. Do NOT output both.\n"
            "3. `---SUGGESTIONS---`\n"
            "4. JSON list of exactly 2 follow-up questions from the USER'S perspective (e.g. \"How do I...?\").\n"
            "5. `---END---`"
        )
        
        llm_messages = [
            {
                "role": "system", 
                "content": system_prompt
            }
        ]
        
        # Add recent history (last 3-4 messages for immediate context)
        for h in history[-4:]:
            llm_messages.append({"role": h.role.value, "content": h.content})
        
        # Build user message content
        user_content = f"User question: {text_content}"
        if image_attrs:
            user_content += f"\n\n(User uploaded an image and is looking for: {effective_message})"
        
        llm_messages.append({"role": "user", "content": user_content})

        # --- 7. Generate response ---
        sources = []
        for c in top_chunks:
            meta = c["embedding"].metadata_json
            if meta.get("url"):
                source = ChatSource(title=meta.get("title") or meta.get("url"), url=meta.get("url"))
                if source not in sources:
                    sources.append(source)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": llm_messages,
                        "temperature": 0.1 # Lower temperature for adherence
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Groq error: {response.text}")
                    return ChatMessageResponse(session_id=str(session.id), message="Service error.", sources=[], suggestions=[])
                
                res_data = response.json()
                full_content = res_data["choices"][0]["message"]["content"]
                
                # Check for control tags
                is_irrelevant = "[[IRRELEVANT]]" in full_content
                is_missing_info = "[[MISSING_INFO]]" in full_content
                
                # Clean content
                full_content = full_content.replace("[[IRRELEVANT]]", "").replace("[[MISSING_INFO]]", "")
                
                parts = full_content.split("---SUGGESTIONS---")
                final_message = parts[0].strip()
                suggestion_block = parts[1] if len(parts) > 1 else ""

                suggestions = []
                if suggestion_block:
                    suggestion_block = suggestion_block.replace("---END---", "").strip()
                    json_match = re.search(r'(\[.*?\])', suggestion_block, re.DOTALL)
                    if json_match:
                        try:
                            suggestions = json.loads(json_match.group(1))
                        except:
                            suggestions = [q.strip(' "[]') for q in suggestion_block.split('\n') if len(q.strip()) > 5][:2]
                
                final_message = re.sub(r'---SUGGESTIONS---.*', '', final_message, flags=re.DOTALL).strip()

                # --- 8. Save messages to DB ---
                response_time_ms = int((time.time() - start_time) * 1000)
                
                # Determine "Was Answered" Status
                # Logic:
                # 1. If [[MISSING_INFO]] -> False (Valid query, but we failed to answer)
                # 2. If [[IRRELEVANT]] -> True (Handled correctly by ignoring/refusing)
                # 3. If Retrieval Confidence High -> True
                # 4. If Retrieval Confidence Low BUT no negative tags -> True (Assume LLM answered via general chit-chat capability or found weak signal)
                
                if is_missing_info:
                    was_answered = False
                elif is_irrelevant:
                    was_answered = True # Don't log as "Unanswered" (Action Item)
                else:
                    was_answered = True # Default to answered (including greetings)

                user_metadata = {}
                if image_attrs:
                    user_metadata["image_analysis"] = image_attrs.to_dict()
                    user_metadata["effective_query"] = effective_message
                
                user_msg = ChatMessage(
                    session_id=session.id, 
                    role=MessageRole.USER, 
                    content=text_content or "(Image uploaded)",
                    metadata_json=user_metadata
                )
                
                assistant_metadata = {
                    "suggestions": suggestions,
                    "retrieval_confidence": round(retrieval_confidence, 3),
                    "sources_count": sources_count,
                    "response_time_ms": response_time_ms,
                    "was_answered": was_answered,
                    "is_irrelevant": is_irrelevant,
                    "is_missing_info": is_missing_info
                }
                
                assistant_msg = ChatMessage(
                    session_id=session.id, 
                    role=MessageRole.ASSISTANT, 
                    content=final_message, 
                    metadata_json=assistant_metadata
                )
                db.add(user_msg)
                db.add(assistant_msg)
                
                # --- 9. Update Summary if needed ---
                from sqlalchemy import func
                count_stmt = select(func.count(ChatMessage.id)).where(ChatMessage.session_id == session.id)
                count_res = await db.execute(count_stmt)
                existing_count = count_res.scalar() or 0
                total_messages = existing_count + 2

                if total_messages % 8 == 0:
                    new_summary = await ChatService.summarize_conversation(session, history + [user_msg, assistant_msg])
                    session.conversation_summary = new_summary
                
                session.last_message_at = func.now()
                await db.commit()

                return ChatMessageResponse(
                    session_id=str(session.id),
                    message=final_message,
                    sources=sources,
                    suggestions=suggestions[:2] if isinstance(suggestions, list) else [],
                    image_analysis=image_analysis_result
                )
                
            except Exception as e:
                logger.error(f"Error in chat service: {e}")
                import traceback
                traceback.print_exc()
                return ChatMessageResponse(session_id=str(session.id), message="An error occurred.", sources=[], suggestions=[])
