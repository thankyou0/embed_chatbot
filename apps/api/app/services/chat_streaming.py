import asyncio
import httpx
import re
import json
import time
from typing import AsyncGenerator, Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import Embedding
from app.models.chatbot import Chatbot, ChatbotStatus
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.services.embedding_service import get_single_embedding
from app.services.vision_service import VisionService
from app.services.chat_service import (
    ChatService,
    is_product_query,
    extract_price_filter,
    extract_color_filter,
    extract_products_from_chunks,
    is_likely_non_product_url
)
from app.core.config import settings, get_groq_api_key
from app.core.logging import get_logger
from app.schemas.chat import ChatSource, ImageAnalysisResult, ProductInfo

logger = get_logger(__name__)


class ChatStreamingService:
    """Service for handling streaming chat responses."""
    
    @staticmethod
    async def get_response_stream(
        db: AsyncSession,
        chatbot_id: UUID,
        message: Optional[str] = None,
        session_id: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        is_preview: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream chat response as Server-Sent Events.
        
        Yields chunks in the format:
        - {"type": "session", "session_id": "..."}
        - {"type": "content", "content": "text chunk"}
        - {"type": "done", "sources": [...], "suggestions": [...], "products": [...], "image_analysis": {...}}
        - {"type": "error", "error": "error message"}
        """
        start_time = time.time()
        
        try:
            # --- 1. Get/Create Session ---
            session = await ChatService.get_or_create_session(db, chatbot_id, session_id, is_preview=is_preview)
            
            # Send session ID first
            yield {
                "type": "session",
                "session_id": str(session.id)
            }
            
            # --- 2. Get chatbot and history ---
            chatbot_stmt = select(Chatbot).where(Chatbot.id == chatbot_id)
            chatbot_res = await db.execute(chatbot_stmt)
            chatbot = chatbot_res.scalar_one()
            
            # Check if chatbot is paused (and not in preview mode)
            if not is_preview and chatbot.status == ChatbotStatus.PAUSED:
                paused_message = (
                    f"🚧 {chatbot.name} is currently offline for maintenance. "
                    "Please check back later. We appreciate your patience!"
                )
                
                # Stream paused message
                for char in paused_message:
                    yield {"type": "content", "content": char}
                    await asyncio.sleep(0.02)  # Simulate typing
                
                # Save messages
                if message:
                    user_msg = ChatMessage(
                        session_id=session.id, 
                        role=MessageRole.USER, 
                        content=message,
                        metadata_json={"paused_chatbot": True}
                    )
                    db.add(user_msg)
                
                assistant_msg = ChatMessage(
                    session_id=session.id, 
                    role=MessageRole.ASSISTANT, 
                    content=paused_message,
                    metadata_json={
                        "is_paused_response": True,
                        "response_time_ms": int((time.time() - start_time) * 1000)
                    }
                )
                db.add(assistant_msg)
                await db.commit()
                
                yield {
                    "type": "done",
                    "sources": [],
                    "suggestions": [],
                    "products": [],
                    "image_analysis": None
                }
                return
            
            # --- 3. Process image if provided (vision analysis) ---
            image_attrs = None
            image_analysis_result = None
            effective_message = message
            
            if image_bytes:
                try:
                    image_attrs = await VisionService.analyze_image(image_bytes)
                    image_analysis_result = ImageAnalysisResult(
                        product_type=image_attrs.product_type,
                        category=image_attrs.category,
                        color=image_attrs.color,
                        style=image_attrs.style,
                        other_attributes=image_attrs.other_attributes,
                        confidence=image_attrs.confidence,
                        needs_clarification=image_attrs.needs_clarification
                    )
                    
                    if image_attrs.confidence >= 0.4:
                        effective_message = f"Looking for: {image_attrs.product_type} {image_attrs.category} {image_attrs.color} {image_attrs.style} {image_attrs.other_attributes}".strip()
                        if message:
                            effective_message = f"{message}. {effective_message}"
                except Exception as e:
                    logger.error(f"Vision analysis failed: {e}")
            
            text_content = effective_message or message or "What is this?"
            
            # --- 4. Get chat history and summary ---
            history = await ChatService.get_history(db, session.id, limit=6)
            summary = session.conversation_summary or ""
            
            # --- 5. Retrieve relevant context using RAG ---
            query_embedding = await get_single_embedding(text_content)
            
            # Text-based retrieval
            stmt = select(Embedding).where(Embedding.chatbot_id == chatbot_id).order_by(
                Embedding.embedding.cosine_distance(query_embedding)
            ).limit(20)
            result = await db.execute(stmt)
            embeddings = result.scalars().all()
            
            text_results = []
            for emb in embeddings:
                distance = 1 - (emb.embedding.cosine_distance(query_embedding))
                text_results.append({
                    "embedding": emb,
                    "score": distance,
                    "source": "text"
                })
            
            # Vision-based retrieval if image provided
            vision_results = []
            if image_attrs and image_attrs.confidence >= 0.4:
                vision_embedding = await get_single_embedding(effective_message)
                vision_stmt = select(Embedding).where(Embedding.chatbot_id == chatbot_id).order_by(
                    Embedding.embedding.cosine_distance(vision_embedding)
                ).limit(30)
                vision_result = await db.execute(vision_stmt)
                vision_embeddings = vision_result.scalars().all()
                
                for emb in vision_embeddings:
                    meta = emb.metadata_json or {}
                    if is_likely_non_product_url(meta.get("url", "")):
                        continue
                    
                    distance = 1 - (emb.embedding.cosine_distance(vision_embedding))
                    vision_results.append({
                        "embedding": emb,
                        "score": distance,
                        "source": "vision"
                    })
            
            # Combine results
            combined_results = text_results + vision_results
            combined_results.sort(key=lambda x: x["score"], reverse=True)
            
            # Deduplicate
            seen_chunks = set()
            top_chunks = []
            for r in combined_results:
                chunk_id = r["embedding"].id
                if chunk_id not in seen_chunks:
                    seen_chunks.add(chunk_id)
                    top_chunks.append(r)
                if len(top_chunks) >= 12:
                    break
            
            # Calculate retrieval confidence
            retrieval_confidence = max([c["score"] for c in top_chunks]) if top_chunks else 0.0
            sources_count = len(top_chunks)
            
            # --- 6. Build system prompt with context ---
            context_text = ""
            if top_chunks:
                context_text = "Relevant information from knowledge base:\n\n"
                for i, c in enumerate(top_chunks[:8], 1):
                    meta = c["embedding"].metadata_json or {}
                    title = meta.get("title", "Untitled")
                    url = meta.get("url", "")
                    content = c["embedding"].content[:500]
                    context_text += f"[Source {i}] Title: {title}\nURL: {url}\n{content}\n\n"
            
            # Extract filters
            price_filter = extract_price_filter(text_content)
            attribute_filter = extract_color_filter(text_content)
            
            # Build context strings
            image_context = ""
            if image_attrs and image_attrs.confidence >= 0.4:
                image_context = (
                    f"\n\nUser uploaded an image. Analysis: "
                    f"Type: {image_attrs.product_type}, "
                    f"Category: {image_attrs.category}, "
                    f"Color: {image_attrs.color}, "
                    f"Style: {image_attrs.style}, "
                    f"Attributes: {image_attrs.other_attributes}, "
                    f"Confidence: {image_attrs.confidence:.2f}"
                )
            
            price_context = ""
            if price_filter:
                if 'max_price' in price_filter and 'min_price' in price_filter:
                    price_context = f"\n\nPrice Filter: Between {price_filter['min_price']} and {price_filter['max_price']}"
                elif 'max_price' in price_filter:
                    price_context = f"\n\nPrice Filter: Under {price_filter['max_price']}"
                elif 'min_price' in price_filter:
                    price_context = f"\n\nPrice Filter: Above {price_filter['min_price']}"
            
            attribute_context = ""
            if attribute_filter:
                if 'color' in attribute_filter:
                    attribute_context += f"\n\nColor Filter: {attribute_filter['color']}"
            
            system_prompt = (
                f"You are a helpful AI assistant for {chatbot.name}. "
                "Your role is to answer questions based on the provided context.\n\n"
                "**Instructions:**\n"
                "1. **Accuracy First**: Answer ONLY from the provided context. If information is not in the context, say so politely.\n"
                "2. **Conversational**: Be friendly and natural. Handle greetings warmly. Use emojis sparingly (only for greetings or excitement).\n"
                "3. **Out-of-Scope Queries**: If asked about something completely unrelated to the business (e.g., general knowledge, other companies), "
                f"reply nicely that you can only answer questions related to {chatbot.name}, and append the tag `[[IRRELEVANT]]` to the very end of your response.\n"
                "4. **Missing Information**: Use [[MISSING_INFO]] ONLY if ALL these conditions are met: "
                "(a) The query is about a business-specific topic (products, services, policies, pricing, features, etc.), "
                "(b) You cannot find the answer in the provided context, "
                "(c) You must respond with a message saying you don't have that information. "
                "DO NOT use [[MISSING_INFO]] for: greetings, contact information, general business info, or when you CAN answer from context.\n"
                "5. **Response Format**: \n"
                "   - Use HTML formatting: <strong>bold</strong>, <em>italic</em>, <br> for line breaks\n"
                "   - For lists: use <ul><li>item</li></ul> or <ol><li>item</li></ol>\n"
                "   - For headings: use <strong> tags to emphasize important text\n"
                "   - Use <strong> for emphasis and important information\n"
                "   - Use <em> for subtle emphasis or technical terms\n"
                "   - Keep answers concise and professional\n"
                "   - DO NOT use markdown symbols like ##, *, **, ***, - for formatting\n"
                "   - DO NOT use <u> or underline tags\n"
                "6. **Product Listings**: When products will be displayed (product carousel will show automatically), keep your text response MINIMAL:\n"
                "   - Use a short intro like 'Here are our products:' or 'Available products:'\n"
                "   - DO NOT list product details (name, price, etc.) as they appear in the product carousel\n"
                "   - Keep response to 1-2 sentences maximum\n"
                "7. **Price Filters**: If a price filter is applied, STRICTLY only mention products that fall within the specified price range. Do not recommend products outside the user's budget.\n"
                "8. **Color/Attribute Filters**: If a color or attribute filter is applied, STRICTLY only mention products that match the specified color/attribute.\n"
                "\n"
                f"Background Context: {summary}{image_context}{price_context}{attribute_context}\n"
                f"{context_text}\n"
                "\n"
                "--- STRICT RESPONSE FORMAT ---\n"
                "1. Your Answer (use HTML formatting as specified)\n"
                "2. (Optional) `[[IRRELEVANT]]` or `[[MISSING_INFO]]` tag if applicable. Do NOT output both.\n"
                "3. `---SUGGESTIONS---`\n"
                "4. JSON list of exactly 2 follow-up questions from the USER'S perspective (e.g. \"How do I...?\").\n"
                "5. `---END---`"
            )
            
            llm_messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent history
            for h in history[-4:]:
                llm_messages.append({"role": h.role.value, "content": h.content})
            
            # Build user message content
            user_content = f"User question: {text_content}"
            if image_attrs:
                user_content += f"\n\n(User uploaded an image and is looking for: {effective_message})"
            
            llm_messages.append({"role": "user", "content": user_content})
            
            # --- 7. Generate streaming response from Groq ---
            sources = []
            for c in top_chunks:
                meta = c["embedding"].metadata_json
                if meta.get("url"):
                    source = ChatSource(title=meta.get("title") or meta.get("url"), url=meta.get("url"))
                    if source not in sources:
                        sources.append(source)
            
            # Extract products if this is a product-related query
            products = []
            if is_product_query(text_content) or (image_attrs is not None):
                products = extract_products_from_chunks(
                    combined_results[:30],
                    limit=10,
                    price_filter=price_filter,
                    attribute_filter=attribute_filter
                )
            
            # Stream response from Groq
            full_content = ""
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {get_groq_api_key()}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": llm_messages,
                        "temperature": 0.1,
                        "stream": True
                    },
                    timeout=60.0
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"Groq error: {error_text}")
                        raise Exception("Service error")
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            
                            try:
                                chunk = json.loads(data)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    full_content += content
                                    yield {"type": "content", "content": content}
                            except json.JSONDecodeError:
                                continue
            
            # --- 8. Post-process response ---
            is_irrelevant = "[[IRRELEVANT]]" in full_content
            is_missing_info = "[[MISSING_INFO]]" in full_content
            
            # Post-processing validation
            if is_missing_info:
                user_lower = text_content.lower().strip()
                response_lower = full_content.lower()
                
                greeting_patterns = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
                is_greeting = any(user_lower.startswith(g) for g in greeting_patterns)
                
                contact_patterns = ['contact', 'reach', 'phone', 'email', 'address', 'location']
                has_contact_query = any(pattern in user_lower for pattern in contact_patterns)
                has_contact_info = any(pattern in response_lower for pattern in ['email', 'phone', 'contact', 'address', '@', 'call'])
                
                if is_greeting or (has_contact_query and has_contact_info):
                    is_missing_info = False
            
            # Clean content
            full_content = full_content.replace("[[IRRELEVANT]]", "").replace("[[MISSING_INFO]]", "")
            
            # Extract suggestions
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
            
            # --- 9. Save messages to DB ---
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if is_missing_info:
                was_answered = False
            elif is_irrelevant:
                was_answered = True
            else:
                was_answered = True
            
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
            
            # Update summary if needed
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
            
            # --- 10. Send final metadata ---
            yield {
                "type": "done",
                "sources": [{"title": s.title, "url": s.url} for s in sources],
                "suggestions": suggestions[:2] if isinstance(suggestions, list) else [],
                "products": [p.dict() for p in products],
                "image_analysis": image_analysis_result.dict() if image_analysis_result else None
            }
            
        except Exception as e:
            logger.error(f"Error in streaming chat service: {e}")
            import traceback
            traceback.print_exc()
            yield {"type": "error", "error": str(e)}


# Add streaming method to ChatService
ChatService.get_response_stream = ChatStreamingService.get_response_stream
