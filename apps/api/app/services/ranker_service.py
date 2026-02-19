"""
Cross-Encoder Re-Ranking Service for improved retrieval relevance.

This service implements a two-stage retrieval approach:
1. Fast bi-encoder retrieval (existing vector search)
2. Accurate cross-encoder re-ranking of top candidates

Cross-encoders are more accurate than bi-encoders because they process
query and document together, allowing for deeper semantic understanding.
"""

import asyncio
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Cross-encoder reranker model for HuggingFace Inference API.
# NOTE:
# - The previous model (`cross-encoder/ms-marco-MiniLM-L-6-v2`) often fails with
#   `StopIteration` on hosted inference routes in this environment.
# - BGE reranker supports `text-classification` task and works reliably here.
CROSS_ENCODER_MODEL = "BAAI/bge-reranker-v2-m3"

# Re-ranking configuration
RERANK_ENABLED = True  # Can be disabled via config if needed
RERANK_TOP_K = 20  # Number of candidates to re-rank
RERANK_OUTPUT_K = 8  # Number of results to return after re-ranking


async def rerank_chunks(
    query: str,
    chunks: List[Dict[str, Any]],
    top_k: int = RERANK_OUTPUT_K,
    enabled: bool = RERANK_ENABLED,
) -> List[Dict[str, Any]]:
    """
    Re-rank chunks using cross-encoder for better relevance.

    Args:
        query: The user's query
        chunks: List of chunk dicts with 'embedding' and 'score' keys
        top_k: Number of results to return after re-ranking
        enabled: Whether to apply re-ranking (falls back to original order if False)

    Returns:
        Re-ranked list of chunks (top_k best matches)
    """
    if not chunks:
        return []

    if not enabled or len(chunks) <= top_k:
        # No need to re-rank if disabled or few results
        return chunks[:top_k]

    try:
        # Import here to avoid startup overhead if not used
        from huggingface_hub import InferenceClient

        client = InferenceClient(token=settings.HF_API_KEY)

        # Prepare query-document pairs for cross-encoder
        # Extract content from embeddings
        pairs = []
        for chunk in chunks[:RERANK_TOP_K]:
            content = chunk.get("embedding")
            if content and hasattr(content, "content"):
                doc_text = content.content[:1000]  # Limit to first 1000 chars
            else:
                continue
            pairs.append({"text": query, "text_pair": doc_text})

        if not pairs:
            return chunks[:top_k]

        # Call cross-encoder via HuggingFace API
        # Run in thread pool since HF client is synchronous
        loop = asyncio.get_event_loop()

        def get_scores():
            try:
                # Use text-classification endpoint for reranker models.
                # Format prompt as query-document pair.
                results = []
                fallback_count = 0
                first_fallback_error = None
                for pair in pairs:
                    try:
                        score_input = (
                            f"query: {pair['text']}\n"
                            f"document: {pair['text_pair']}"
                        )
                        score_result = client.text_classification(
                            score_input,
                            model=CROSS_ENCODER_MODEL,
                        )
                        if isinstance(score_result, list) and len(score_result) > 0:
                            first_item = score_result[0]
                            if isinstance(first_item, dict):
                                raw_score = first_item.get("score", 0.5)
                            else:
                                raw_score = getattr(first_item, "score", 0.5)
                            normalized_score = max(0.0, min(1.0, float(raw_score)))
                            results.append(normalized_score)
                        else:
                            results.append(0.5)
                    except Exception as e:
                        # Avoid spamming logs for every pair; collect and log once.
                        fallback_count += 1
                        if first_fallback_error is None:
                            first_fallback_error = str(e)[:200]
                        results.append(0.5)  # Neutral score on error

                        # If first call already failed, remaining calls usually fail too.
                        # Short-circuit with neutral scores to reduce latency/log noise.
                        remaining = len(pairs) - len(results)
                        if remaining > 0:
                            results.extend([0.5] * remaining)
                        break

                if fallback_count > 0:
                    logger.debug(
                        "Cross-encoder scoring fallback "
                        f"({fallback_count}/{len(pairs)} pairs, model={CROSS_ENCODER_MODEL}): "
                        f"{first_fallback_error}"
                    )
                return results
            except Exception as e:
                logger.debug(f"Cross-encoder batch fallback: {str(e)[:200]}")
                return [0.5] * len(pairs)

        scores = await loop.run_in_executor(None, get_scores)

        # Combine cross-encoder scores with original scores
        # Weight: 70% cross-encoder, 30% original bi-encoder
        reranked = []
        for i, chunk in enumerate(chunks[: len(scores)]):
            ce_score = scores[i] if i < len(scores) else 0.5
            original_score = chunk.get("score", 0.5)

            # Combined score
            combined_score = 0.7 * ce_score + 0.3 * original_score

            reranked.append(
                {
                    **chunk,
                    "score": combined_score,
                    "ce_score": ce_score,
                    "original_score": original_score,
                }
            )

        # Add remaining chunks (not re-ranked) with slight penalty
        for chunk in chunks[len(scores) :]:
            reranked.append(
                {
                    **chunk,
                    "score": chunk.get("score", 0.5)
                    * 0.8,  # 20% penalty for not being re-ranked
                    "ce_score": None,
                    "original_score": chunk.get("score", 0.5),
                }
            )

        # Sort by combined score descending
        reranked.sort(key=lambda x: x["score"], reverse=True)

        logger.debug(f"Re-ranked {len(chunks)} chunks, returning top {top_k}")
        return reranked[:top_k]

    except Exception as e:
        logger.warning(f"Cross-encoder re-ranking failed, using original order: {e}")
        # Fallback to original scoring
        return chunks[:top_k]


def calculate_query_complexity(
    query: str,
    is_product_query: bool = False,
    is_greeting: bool = False,
) -> str:
    """
    Determine query complexity for dynamic context window sizing.

    Returns:
        'simple': Short greetings, basic queries (2-3 chunks needed)
        'medium': Standard queries (6-8 chunks needed)
        'complex': Comparisons, detailed questions (10-12 chunks needed)
    """
    if is_greeting:
        return "simple"

    words = query.lower().split()
    word_count = len(words)

    # Complex indicators (English + Hindi + Gujarati)
    complex_keywords = [
        "compare",
        "comparison",
        "vs",
        "versus",
        "difference",
        "between",
        "which is better",
        "pros and cons",
        "advantages",
        "disadvantages",
        "similar to",
        "alternative",
        "options",
        "all",
        "every",
        "list",
        "detailed",
        "explain",
        "how does",
        "why",
        "comprehensive",
        # Hindi
        "तुलना",
        "अंतर",
        "फर्क",
        "बेहतर",
        "कौनसा",
        "कौन सा",
        "फायदे",
        "नुकसान",
        "विकल्प",
        "सभी",
        "सारे",
        "हर",
        "विस्तार",
        "समझाओ",
        "क्यों",
        "कैसे",
        # Gujarati
        "સરખામણી",
        "તફાવત",
        "ફરક",
        "સારું",
        "કયું",
        "કયુ",
        "ફાયદા",
        "ગેરફાયદા",
        "વિકલ્પ",
        "બધા",
        "બધું",
        "દરેક",
        "વિગતવાર",
        "સમજાવો",
        "કેમ",
        "કેવી રીતે",
    ]

    has_complex_indicator = any(kw in query.lower() for kw in complex_keywords)

    # Simple indicators (English + Hindi + Gujarati)
    simple_keywords = [
        "hi",
        "hello",
        "hey",
        "thanks",
        "thank you",
        "bye",
        "goodbye",
        "ok",
        "okay",
        "yes",
        "no",
        "sure",
        "help",
        # Hindi
        "नमस्ते",
        "नमस्कार",
        "हेलो",
        "हाय",
        "धन्यवाद",
        "शुक्रिया",
        "अलविदा",
        "हां",
        "हाँ",
        "नहीं",
        "ठीक",
        "मदद",
        # Gujarati
        "નમસ્તે",
        "નમસ્કાર",
        "હેલો",
        "હાય",
        "આભાર",
        "ધન્યવાદ",
        "આવજો",
        "હા",
        "ના",
        "બરાબર",
        "ઠીક",
        "મદદ",
    ]

    is_simple = (
        word_count <= 3
        and not is_product_query
        and any(kw in query.lower() for kw in simple_keywords)
    )

    if is_simple:
        return "simple"
    elif has_complex_indicator or word_count > 15:
        return "complex"
    elif is_product_query or word_count > 8:
        return "medium"
    else:
        return "medium"  # Default to medium


def get_context_chunk_limit(complexity: str) -> int:
    """
    Get the number of context chunks based on query complexity.

    This implements dynamic context window sizing to:
    - Save tokens on simple queries
    - Provide more context for complex queries
    """
    limits = {
        "simple": 3,
        "medium": 8,
        "complex": 12,
    }
    return limits.get(complexity, 8)


def get_retrieval_limit(complexity: str) -> int:
    """
    Get the number of candidates to retrieve for re-ranking based on complexity.
    """
    limits = {
        "simple": 10,
        "medium": 20,
        "complex": 30,
    }
    return limits.get(complexity, 20)
