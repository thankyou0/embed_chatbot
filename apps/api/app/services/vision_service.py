"""
Enhanced Vision Service for Image Analysis
Supports multiple providers: Google Gemini (free tier), Groq
"""
import base64
import httpx
import json
import re
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field, asdict
from app.core.config import settings, get_groq_api_key
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ImageAttributes:
    """Represents extracted product/visual attributes from an image."""
    
    # Core product attributes
    product_type: str = ""          # e.g., "shoes", "dress", "watch"
    category: str = ""              # e.g., "footwear", "clothing", "accessories"
    subcategory: str = ""           # e.g., "sneakers", "formal shoes", "sandals"
    
    # Visual attributes (maintain backward compatibility with 'color' field)
    primary_color: str = ""         # Main color
    secondary_colors: List[str] = field(default_factory=list)  # Additional colors
    pattern: str = ""               # e.g., "solid", "striped", "floral", "checkered"
    material: str = ""              # e.g., "leather", "cotton", "silk", "metal"
    
    # Style attributes
    style: str = ""                 # e.g., "casual", "formal", "sporty", "bohemian"
    occasion: str = ""              # e.g., "everyday", "party", "wedding", "office"
    gender_target: str = ""         # e.g., "men", "women", "unisex", "kids"
    
    # Additional details
    brand_visible: str = ""         # Only if clearly visible (no guessing)
    notable_features: List[str] = field(default_factory=list)  # Special features
    other_attributes: str = ""      # Legacy field for backward compatibility
    
    # Meta
    confidence: float = 0.0         # Overall confidence score
    raw_description: str = ""       # Full description from model
    needs_clarification: bool = False  # If image is unclear/ambiguous
    clarification_question: str = ""   # What to ask user if unclear
    
    def __post_init__(self):
        # Ensure lists are initialized
        if self.secondary_colors is None:
            self.secondary_colors = []
        if self.notable_features is None:
            self.notable_features = []
    
    @property
    def color(self) -> str:
        """Backward compatibility: return primary_color as 'color'."""
        return self.primary_color
    
    @color.setter
    def color(self, value: str):
        """Backward compatibility: set primary_color via 'color'."""
        self.primary_color = value
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['color'] = self.primary_color  # Add backward compatible field
        return result
    
    def get_color_string(self) -> str:
        """Get combined color string."""
        colors = [self.primary_color] if self.primary_color else []
        if self.secondary_colors:
            colors.extend(self.secondary_colors[:2])  # Limit to 2 secondary
        return " and ".join(colors) if colors else ""
    
    def to_search_query(self) -> str:
        """Build an optimized search query string from attributes."""
        parts = []
        
        # Priority order for search relevance
        if self.primary_color:
            parts.append(self.primary_color)
        
        if self.material and self.material.lower() not in ["unknown", "mixed"]:
            parts.append(self.material)
        
        if self.product_type:
            parts.append(self.product_type)
        elif self.subcategory:
            parts.append(self.subcategory)
        elif self.category:
            parts.append(self.category)
        
        if self.style and self.style.lower() not in ["casual", "regular", "standard"]:
            parts.append(self.style)
        
        if self.gender_target and self.gender_target.lower() not in ["unisex"]:
            parts.append(f"for {self.gender_target}")
        
        # Include other_attributes for backward compatibility
        if self.other_attributes:
            parts.append(self.other_attributes)
        
        return " ".join(parts) if parts else ""
    
    def to_detailed_query(self) -> str:
        """Build a more detailed query for better RAG retrieval."""
        parts = []
        
        # Build comprehensive description
        if self.gender_target:
            parts.append(self.gender_target)
        
        if self.primary_color:
            parts.append(self.primary_color)
        
        if self.pattern and self.pattern.lower() != "solid":
            parts.append(self.pattern)
        
        if self.material:
            parts.append(self.material)
        
        if self.style:
            parts.append(self.style)
        
        if self.product_type:
            parts.append(self.product_type)
        elif self.subcategory:
            parts.append(self.subcategory)
        elif self.category:
            parts.append(self.category)
        
        if self.occasion and self.occasion.lower() not in ["everyday", "general"]:
            parts.append(f"for {self.occasion}")
        
        # Add notable features
        if self.notable_features:
            parts.extend(self.notable_features[:2])
        
        return " ".join(parts) if parts else ""


class VisionService:
    """
    Enhanced Vision Service for Image Analysis.
    Supports multiple providers: Google Gemini (free tier), Groq.
    
    Default provider is Gemini (free tier with 1500 requests/day).
    Groq is used as fallback or can be configured as primary.
    """
    
    # Model configurations
    PROVIDERS = {
        "gemini": {
            "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent",
            "model": "gemini-2.0-flash-lite",
            "free_tier": True,
            "rate_limit": "1500/day"
        },
        "groq": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",  # Llama 4 Scout - latest vision model
            "free_tier": True,
            "rate_limit": "30/min"
        }
    }
    
    # Enhanced extraction prompt with structured output
    EXTRACTION_PROMPT = """Analyze this product image carefully and extract detailed attributes for e-commerce search.

CRITICAL RULES:
1. ONLY describe what you can CLEARLY see in the image
2. DO NOT guess brands unless logo/text is clearly visible and readable
3. DO NOT identify people or faces - focus ONLY on products/items
4. If the image is unclear, blurry, or doesn't show a recognizable product, set low confidence
5. Be SPECIFIC with colors (e.g., "navy blue" not just "blue", "burgundy" not just "red")
6. For jewelry: identify type (ring, necklace, etc.), metal (gold, silver), and any gemstones

Return ONLY valid JSON in this exact format (no markdown, no extra text):
{
    "product_type": "specific product name (e.g., sneakers, cocktail dress, wristwatch, solitaire ring)",
    "category": "broad category (footwear, clothing, accessories, jewelry, electronics, home decor)",
    "subcategory": "more specific (running shoes, evening wear, analog watch, engagement ring)",
    "primary_color": "main/dominant color (be specific: navy blue, rose gold, burgundy)",
    "secondary_colors": ["other", "visible", "colors"],
    "pattern": "solid, striped, floral, checkered, geometric, printed, embroidered, plain",
    "material": "visible material (leather, cotton, silk, gold, silver, platinum, stainless steel, fabric)",
    "style": "casual, formal, sporty, elegant, vintage, modern, minimalist, bohemian, traditional",
    "occasion": "everyday, party, wedding, office, sports, festival, casual outing",
    "gender_target": "men, women, unisex, kids",
    "brand_visible": "only if brand name/logo is CLEARLY readable, else empty string",
    "notable_features": ["distinctive features", "like gemstones", "embroidery", "heel height"],
    "confidence": 0.85,
    "needs_clarification": false,
    "clarification_question": ""
}

CONFIDENCE GUIDELINES:
- 0.8-1.0: Clear product image, all attributes visible
- 0.6-0.8: Good image, some attributes unclear
- 0.4-0.6: Partial view or multiple items, need clarification
- 0.0-0.4: Blurry, unclear, or no recognizable product

If image needs clarification, set:
- needs_clarification: true
- clarification_question: "A specific, helpful question to ask the user"

Return ONLY the JSON object."""

    # Quick analysis prompt for faster responses
    QUICK_ANALYSIS_PROMPT = """Identify the main product in this image quickly.
Return JSON only: {"product": "specific name", "color": "main color", "type": "category", "confidence": 0.8}
Be specific. No extra text."""

    @staticmethod
    def encode_image_to_base64(image_bytes: bytes) -> str:
        """Encode image bytes to base64 string."""
        return base64.b64encode(image_bytes).decode("utf-8")
    
    @staticmethod
    def get_image_mime_type(image_bytes: bytes) -> str:
        """Detect image MIME type from magic bytes."""
        if len(image_bytes) < 12:
            return "image/jpeg"
        
        # Check magic bytes for common formats
        if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            return "image/png"
        elif image_bytes[:2] == b'\xff\xd8':
            return "image/jpeg"
        elif image_bytes[:6] in (b'GIF87a', b'GIF89a'):
            return "image/gif"
        elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
            return "image/webp"
        elif image_bytes[:4] == b'\x00\x00\x00\x0c' or image_bytes[4:8] == b'ftyp':
            return "image/heic"
        
        return "image/jpeg"  # Default fallback
    
    @classmethod
    def _get_provider_config(cls) -> Tuple[str, Dict[str, Any]]:
        """Get the configured vision provider and its config."""
        provider = getattr(settings, 'VISION_MODEL_PROVIDER', 'gemini').lower()
        
        if provider not in cls.PROVIDERS:
            logger.warning(f"Unknown vision provider '{provider}', falling back to gemini")
            provider = "gemini"
        
        return provider, cls.PROVIDERS[provider]
    
    @classmethod
    def _has_api_key(cls, provider: str) -> bool:
        """Check if API key is configured for a provider."""
        if provider == "gemini":
            return bool(getattr(settings, 'GEMINI_API_KEY', None))
        elif provider == "groq":
            return bool(getattr(settings, 'GROQ_API_KEY', None))
        return False
    
    @classmethod
    async def analyze_image(
        cls, 
        image_bytes: bytes, 
        user_context: str = "",
        quick_mode: bool = False
    ) -> ImageAttributes:
        """
        Analyze an image and extract product attributes.
        
        Args:
            image_bytes: Raw image bytes
            user_context: Optional user message for context-aware analysis
            quick_mode: If True, use simplified prompt for faster response
            
        Returns:
            ImageAttributes object with extracted attributes
        """
        provider, config = cls._get_provider_config()
        
        # Determine which provider to use based on API key availability
        # Always try Gemini first (better free tier), then Groq
        preferred_order = ["gemini", "groq"] if provider == "gemini" else ["groq", "gemini"]
        
        working_provider = None
        for prov in preferred_order:
            if cls._has_api_key(prov):
                working_provider = prov
                break
        
        if not working_provider:
            logger.error("No vision API keys configured (neither GEMINI_API_KEY nor GROQ_API_KEY)")
            return ImageAttributes(
                confidence=0.0, 
                needs_clarification=True,
                clarification_question="Image analysis is not available. Please describe what you're looking for."
            )
        
        provider = working_provider
        logger.info(f"Using vision provider: {provider}")
        
        try:
            if provider == "gemini":
                return await cls._analyze_with_gemini(image_bytes, user_context, quick_mode)
            elif provider == "groq":
                return await cls._analyze_with_groq(image_bytes, user_context, quick_mode)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Vision analysis failed with {provider}: {e}", exc_info=True)
            
            # Try fallback provider
            fallback = "groq" if provider == "gemini" else "gemini"
            if cls._has_api_key(fallback):
                try:
                    logger.warning(f"Primary provider {provider} failed, attempting fallback to {fallback}")
                    if fallback == "gemini":
                        return await cls._analyze_with_gemini(image_bytes, user_context, quick_mode)
                    else:
                        return await cls._analyze_with_groq(image_bytes, user_context, quick_mode)
                except Exception as fallback_error:
                    logger.error(f"Fallback to {fallback} also failed: {fallback_error}", exc_info=True)
            
            return ImageAttributes(
                confidence=0.0, 
                needs_clarification=True,
                clarification_question="I couldn't analyze the image. Could you describe what you're looking for?"
            )
    
    @classmethod
    async def _analyze_with_gemini(
        cls, 
        image_bytes: bytes, 
        user_context: str = "",
        quick_mode: bool = False
    ) -> ImageAttributes:
        """Analyze image using Google Gemini (free tier: 1500 requests/day)."""
        
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        base64_image = cls.encode_image_to_base64(image_bytes)
        mime_type = cls.get_image_mime_type(image_bytes)
        
        # Build prompt with optional context
        prompt = cls.QUICK_ANALYSIS_PROMPT if quick_mode else cls.EXTRACTION_PROMPT
        if user_context:
            prompt = f"Context: User is looking for '{user_context}'\n\n{prompt}"
        
        url = f"{cls.PROVIDERS['gemini']['url']}?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64_image
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1024,
                "topP": 0.8,
                "topK": 40
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Gemini API error: {response.status_code} - {error_text}")
                
                # Parse error for helpful message
                try:
                    error_json = response.json()
                    error_msg = error_json.get('error', {}).get('message', error_text)
                    raise Exception(f"Gemini API error ({response.status_code}): {error_msg}")
                except:
                    raise Exception(f"Gemini API error: {response.status_code} - {error_text[:200]}")
            
            res_data = response.json()
            
            # Extract content from Gemini response
            try:
                content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                logger.info(f"Gemini analysis successful (confidence check in parsing)")
                logger.debug(f"Gemini raw response: {content[:500]}")
            except (KeyError, IndexError) as e:
                logger.error(f"Failed to extract Gemini response: {e}, data: {res_data}")
                raise Exception(f"Invalid Gemini response format: {e}")
            
            return cls._parse_attributes(content, quick_mode)
    
    @classmethod
    async def _analyze_with_groq(
        cls, 
        image_bytes: bytes, 
        user_context: str = "",
        quick_mode: bool = False
    ) -> ImageAttributes:
        """Analyze image using Groq with Llama Vision (free tier: 30 req/min)."""
        
        api_key = get_groq_api_key()
        if not api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        base64_image = cls.encode_image_to_base64(image_bytes)
        mime_type = cls.get_image_mime_type(image_bytes)
        
        # Build prompt with optional context
        prompt = cls.QUICK_ANALYSIS_PROMPT if quick_mode else cls.EXTRACTION_PROMPT
        if user_context:
            prompt = f"Context: User is looking for '{user_context}'\n\n{prompt}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                cls.PROVIDERS["groq"]["url"],
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": cls.PROVIDERS["groq"]["model"],
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1024
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Groq API error: {response.status_code} - {error_text}")
                
                # Parse error for helpful message
                try:
                    error_json = response.json()
                    error_details = error_json.get('error', {})
                    error_msg = error_details.get('message', error_text)
                    error_code = error_details.get('code', 'unknown')
                    
                    # Special handling for model decommissioned error
                    if 'decommission' in error_msg.lower() or 'deprecated' in error_msg.lower():
                        logger.error(f"Groq model {cls.PROVIDERS['groq']['model']} is decommissioned. Please update the model in vision_service.py")
                        raise Exception(f"Groq vision model unavailable. Model needs updating: {error_msg}")
                    
                    raise Exception(f"Groq API error ({response.status_code}, {error_code}): {error_msg}")
                except Exception as parse_err:
                    if 'Groq vision model' in str(parse_err):
                        raise  # Re-raise our custom error
                    raise Exception(f"Groq API error: {response.status_code} - {error_text[:200]}")
            
            res_data = response.json()
            content = res_data["choices"][0]["message"]["content"]
            logger.info(f"Groq analysis successful with model: {cls.PROVIDERS['groq']['model']}")
            logger.debug(f"Groq raw response: {content[:500]}")
            
            return cls._parse_attributes(content, quick_mode)
    
    @classmethod
    def _parse_attributes(cls, content: str, quick_mode: bool = False) -> ImageAttributes:
        """Parse the LLM response into ImageAttributes."""
        try:
            content = content.strip()
            
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                parts = content.split("```")
                if len(parts) >= 2:
                    content = parts[1].strip()
                    # Remove language identifier if present
                    if content.lower().startswith("json"):
                        content = content[4:].strip()
            
            # Try to find JSON object in content
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                content = json_match.group(0)
            
            data = json.loads(content)
            
            # Handle quick mode response (simpler format)
            if quick_mode:
                return ImageAttributes(
                    product_type=data.get("product", ""),
                    primary_color=data.get("color", ""),
                    category=data.get("type", ""),
                    confidence=float(data.get("confidence", 0.5)),
                    raw_description=content
                )
            
            # Parse full response
            return ImageAttributes(
                product_type=data.get("product_type", ""),
                category=data.get("category", ""),
                subcategory=data.get("subcategory", ""),
                primary_color=data.get("primary_color", data.get("color", "")),  # Fallback to 'color'
                secondary_colors=data.get("secondary_colors", []) or [],
                pattern=data.get("pattern", ""),
                material=data.get("material", ""),
                style=data.get("style", ""),
                occasion=data.get("occasion", ""),
                gender_target=data.get("gender_target", ""),
                brand_visible=data.get("brand_visible", ""),
                notable_features=data.get("notable_features", []) or [],
                other_attributes=data.get("other_attributes", ""),
                confidence=float(data.get("confidence", 0.5)),
                needs_clarification=data.get("needs_clarification", False),
                clarification_question=data.get("clarification_question", ""),
                raw_description=content
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse vision response: {e}. Content: {content[:500]}")
            
            # Try to extract basic info from raw text
            attrs = cls._extract_from_raw_text(content)
            attrs.raw_description = content
            return attrs
    
    @classmethod
    def _extract_from_raw_text(cls, text: str) -> ImageAttributes:
        """Fallback: Extract basic attributes from unstructured text."""
        text_lower = text.lower()
        attrs = ImageAttributes(confidence=0.3)
        
        # Common product types by category
        product_keywords = {
            "footwear": ["shoe", "sneaker", "boot", "sandal", "heel", "loafer", "slipper", "flip flop"],
            "clothing": ["shirt", "dress", "pants", "jeans", "jacket", "coat", "blouse", "skirt", "top", "saree", "kurta"],
            "accessories": ["bag", "purse", "wallet", "belt", "scarf", "hat", "cap", "sunglasses"],
            "jewelry": ["ring", "necklace", "bracelet", "earring", "pendant", "chain", "watch", "bangle", "anklet"],
            "electronics": ["phone", "laptop", "tablet", "camera", "headphone", "speaker", "earbuds"]
        }
        
        for category, keywords in product_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    attrs.product_type = keyword
                    attrs.category = category
                    attrs.confidence = 0.4
                    break
            if attrs.product_type:
                break
        
        # Extract colors
        colors = [
            "red", "blue", "green", "yellow", "orange", "purple", "pink", "black", 
            "white", "gray", "grey", "brown", "beige", "navy", "gold", "silver",
            "burgundy", "maroon", "teal", "coral", "cream", "ivory", "rose gold",
            "champagne", "bronze", "copper", "platinum"
        ]
        
        for color in colors:
            if color in text_lower:
                if not attrs.primary_color:
                    attrs.primary_color = color
                elif color not in attrs.secondary_colors:
                    attrs.secondary_colors.append(color)
        
        # Extract materials
        materials = ["leather", "cotton", "silk", "wool", "denim", "gold", "silver", "platinum", "metal", "fabric"]
        for material in materials:
            if material in text_lower:
                attrs.material = material
                break
        
        return attrs
    
    # ============================================================================
    # LLM-POWERED QUERY BUILDER (Generalized Approach)
    # ============================================================================
    # Instead of regex patterns, we use the LLM to understand user intent
    # and intelligently merge image attributes with user requests.
    # This handles ALL cases including:
    # - "show me this color shirts" (color from image, product from text)
    # - "same but for mens" (product from image, gender from text)
    # - "do you have this one" (exact match from image)
    # - "show me red shirt with half sleeve" (user overrides everything)
    # ============================================================================
    
    QUERY_BUILDER_PROMPT = """You are a smart e-commerce search query builder. Your job is to understand what the user wants based on:
1. An IMAGE they uploaded (I'll give you the extracted attributes)
2. Their TEXT message

CRITICAL RULES:
- Generate a SEARCH QUERY that will find exactly what the user wants
- The query should be concise (3-8 words max) and searchable
- Understand REFERENCES: "this color", "same style", "like this" refer to the IMAGE
- Understand OVERRIDES: If user specifies something explicitly, use THEIR value, not image's
- For "do you have this" type questions, include key identifying attributes (color, product type)
- For exact matches, include the COLOR if it helps identify the specific product

EXAMPLES:
1. Image: [blue running shoes] | User: "show me this in red" 
   → Query: "red running shoes" (color from user, product from image)

2. Image: [kids blue silk shirt] | User: "same color but for mens"
   → Query: "blue silk shirt for men" (color+product from image, gender from user)

3. Image: [orange full sleeve shirt] | User: "show me red half sleeve shirts"
   → Query: "red half sleeve shirt" (user overrides everything)

4. Image: [red small toy car] | User: "do you have this"
   → Query: "red small toy car" (exact match - include color to identify product)

5. Image: [light blue sneakers] | User: "show me this color shirts"
   → Query: "light blue shirts" (color from image, product from user)

6. Image: [red leather handbag] | User: "similar but cheaper"
   → Query: "budget red leather handbag" (image attrs + modifier)

7. Image: [Royal Blue kids silk shirt] | User: "can you have same color shirt but for mens"
   → Query: "Royal Blue silk shirt for men" (color+material from image, gender from user)

Now analyze:
IMAGE ATTRIBUTES:
{image_json}

USER MESSAGE: "{user_message}"

Return ONLY a JSON object (no markdown, no explanation):
{{
    "intent": "exact_match|color_transfer|style_transfer|attribute_override|similar_search|general_query",
    "search_query": "the optimized search query",
    "from_image": ["list", "of", "attributes", "taken", "from", "image"],
    "from_user": ["list", "of", "attributes", "taken", "from", "user", "text"],
    "confidence": 0.9
}}"""

    @classmethod
    async def build_query_with_llm(
        cls,
        user_message: str,
        image_attrs: Optional[ImageAttributes]
    ) -> Tuple[str, str, str]:
        """
        Use LLM to intelligently build search query from image + user text.
        
        This is the GENERALIZED approach that handles ALL cases:
        - Color/style transfers ("this color but shirts")
        - Attribute overrides ("same but for mens")  
        - Exact matches ("do you have this")
        - Full overrides ("show me red shirts")
        
        Returns:
            Tuple of (search_query, intent, detailed_info)
        """
        if not image_attrs or image_attrs.confidence < 0.3:
            return (user_message or "", "no_image", "")
        
        # Prepare image attributes as JSON for LLM
        image_json = json.dumps({
            "product_type": image_attrs.product_type,
            "category": image_attrs.category,
            "subcategory": image_attrs.subcategory,
            "primary_color": image_attrs.primary_color,
            "secondary_colors": image_attrs.secondary_colors,
            "pattern": image_attrs.pattern,
            "material": image_attrs.material,
            "style": image_attrs.style,
            "occasion": image_attrs.occasion,
            "gender_target": image_attrs.gender_target,
            "notable_features": image_attrs.notable_features
        }, indent=2)
        
        prompt = cls.QUERY_BUILDER_PROMPT.format(
            image_json=image_json,
            user_message=user_message or "find this product"
        )
        
        try:
            # Use Gemini for query building (fast and free)
            result = await cls._call_llm_for_query(prompt)
            
            if result:
                search_query = result.get("search_query", "")
                intent = result.get("intent", "general_query")
                from_image = result.get("from_image", [])
                from_user = result.get("from_user", [])
                
                logger.info(
                    f"LLM Query Builder: intent='{intent}' | "
                    f"query='{search_query}' | "
                    f"from_image={from_image} | from_user={from_user}"
                )
                
                detailed = f"{search_query} (from image: {', '.join(from_image) if from_image else 'none'})"
                return (search_query, intent, detailed)
                
        except Exception as e:
            logger.warning(f"LLM query building failed: {e}, using fallback")
        
        # Fallback to simple image-based query
        fallback_query = image_attrs.to_search_query()
        return (fallback_query, "fallback", fallback_query)
    
    @classmethod
    async def _call_llm_for_query(cls, prompt: str) -> Optional[Dict[str, Any]]:
        """Call LLM (Gemini preferred) to build the query."""
        
        # Try Gemini first (faster, better free tier)
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if api_key:
            try:
                url = f"{cls.PROVIDERS['gemini']['url']}?key={api_key}"
                
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 256,
                        "topP": 0.8
                    }
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=payload, timeout=10.0)
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        content = res_data["candidates"][0]["content"]["parts"][0]["text"]
                        
                        # Parse JSON from response
                        content = content.strip()
                        if "```json" in content:
                            content = content.split("```json")[1].split("```")[0].strip()
                        elif "```" in content:
                            content = content.split("```")[1].split("```")[0].strip()
                        
                        json_match = re.search(r'\{[\s\S]*\}', content)
                        if json_match:
                            return json.loads(json_match.group(0))
                            
            except Exception as e:
                logger.warning(f"Gemini query builder failed: {e}")
        
        # Fallback to Groq
        api_key = get_groq_api_key()
        if api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        cls.PROVIDERS["groq"]["url"],
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-8b-instant",  # Fast text model
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.1,
                            "max_tokens": 256
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        content = res_data["choices"][0]["message"]["content"]
                        
                        json_match = re.search(r'\{[\s\S]*\}', content)
                        if json_match:
                            return json.loads(json_match.group(0))
                            
            except Exception as e:
                logger.warning(f"Groq query builder failed: {e}")
        
        return None
    
    @classmethod
    def build_combined_query(
        cls,
        user_message: str,
        image_attrs: Optional[ImageAttributes],
        conversation_context: str = ""
    ) -> Tuple[str, str]:
        """
        Synchronous wrapper for backward compatibility.
        For new code, use build_query_with_llm() directly.
        
        This uses a simple heuristic fallback when async LLM call isn't available.
        """
        if not image_attrs or image_attrs.confidence < 0.3:
            return (user_message or "", user_message or "")
        
        user_lower = user_message.lower().strip() if user_message else ""
        
        # Simple heuristic for sync fallback
        # The async build_query_with_llm() should be used in production
        
        # Check for reference words that indicate user wants something FROM the image
        references_image = any(word in user_lower for word in [
            "this", "same", "similar", "like this", "these", "that",
            "this color", "this style", "this type", "same color"
        ])
        
        # Check if user mentions a DIFFERENT product type than the image
        user_product = cls._extract_product_from_text(user_lower)
        image_product = image_attrs.product_type or image_attrs.subcategory or image_attrs.category
        
        # Check for explicit attribute mentions
        user_color = cls._extract_color_from_text(user_lower)
        user_style = cls._extract_style_from_text(user_lower)
        user_gender = cls._extract_gender_from_text(user_lower)
        
        parts = []
        
        if references_image:
            # User is referencing the image for some attributes
            
            # Color: user specified or from image
            if user_color:
                parts.append(user_color)
            elif "this color" in user_lower or "same color" in user_lower:
                if image_attrs.primary_color:
                    parts.append(image_attrs.primary_color)
            elif not user_product:  # No different product, use image color
                if image_attrs.primary_color:
                    parts.append(image_attrs.primary_color)
            
            # Material from image (if relevant)
            if image_attrs.material and image_attrs.material.lower() not in ["unknown", "mixed", "fabric"]:
                if not user_product or "this" in user_lower:
                    parts.append(image_attrs.material)
            
            # Product: user specified or from image
            if user_product:
                parts.append(user_product)
            elif image_product:
                parts.append(image_product)
            
            # Style
            if user_style:
                parts.append(user_style)
            elif image_attrs.style and image_attrs.style.lower() not in ["casual", "regular"]:
                parts.append(image_attrs.style)
            
            # Gender: user specified or from image
            if user_gender:
                parts.append(f"for {user_gender}")
            elif "for mens" in user_lower or "for men" in user_lower:
                parts.append("for men")
            elif "for women" in user_lower or "for ladies" in user_lower:
                parts.append("for women")
            elif "for kids" in user_lower or "for children" in user_lower:
                parts.append("for kids")
            elif image_attrs.gender_target and image_attrs.gender_target.lower() not in ["unisex"]:
                # Only include image gender if user didn't mention different product
                if not user_product:
                    parts.append(f"for {image_attrs.gender_target}")
        else:
            # User is NOT referencing image much, prioritize their text
            if user_color:
                parts.append(user_color)
            if user_product:
                parts.append(user_product)
            elif image_product:
                parts.append(image_product)
            if user_style:
                parts.append(user_style)
            if user_gender:
                parts.append(f"for {user_gender}")
        
        # Handle special cases
        if not parts:
            # Nothing extracted, use image attributes
            return (image_attrs.to_search_query(), image_attrs.to_detailed_query())
        
        # Check for modifiers
        if any(w in user_lower for w in ["cheaper", "budget", "affordable"]):
            parts.insert(0, "budget")
        elif any(w in user_lower for w in ["premium", "luxury", "expensive"]):
            parts.insert(0, "premium")
        
        primary_query = " ".join(parts)
        detailed_query = f"{primary_query} (based on uploaded image)"
        
        logger.info(f"QUERY BUILD: user='{user_message}' | image='{image_product}' | result='{primary_query}'")
        
        return (primary_query, detailed_query)
    
    @staticmethod
    def _extract_product_from_text(text: str) -> str:
        """Extract product type mentioned in user text."""
        products = {
            # Clothing
            "shirt": ["shirt", "shirts"],
            "t-shirt": ["tshirt", "t-shirt", "tee"],
            "dress": ["dress", "dresses", "gown"],
            "pants": ["pants", "pant", "trousers", "jeans"],
            "jacket": ["jacket", "jackets", "coat", "blazer"],
            "sweater": ["sweater", "sweaters", "pullover", "hoodie"],
            "skirt": ["skirt", "skirts"],
            "shorts": ["shorts", "short"],
            "kurta": ["kurta", "kurtas", "kurti"],
            "saree": ["saree", "sarees", "sari"],
            # Footwear
            "shoes": ["shoe", "shoes", "footwear"],
            "sneakers": ["sneaker", "sneakers"],
            "sandals": ["sandal", "sandals"],
            "heels": ["heel", "heels", "stiletto"],
            "boots": ["boot", "boots"],
            "slippers": ["slipper", "slippers", "flip flop"],
            # Accessories
            "bag": ["bag", "bags", "handbag", "purse"],
            "watch": ["watch", "watches"],
            "belt": ["belt", "belts"],
            "wallet": ["wallet", "wallets"],
            "sunglasses": ["sunglasses", "glasses", "shades"],
            "hat": ["hat", "hats", "cap", "caps"],
            "scarf": ["scarf", "scarves"],
            # Jewelry
            "ring": ["ring", "rings"],
            "necklace": ["necklace", "necklaces", "chain", "pendant"],
            "bracelet": ["bracelet", "bracelets", "bangle"],
            "earrings": ["earring", "earrings"],
        }
        
        text_lower = text.lower()
        for product, keywords in products.items():
            for keyword in keywords:
                if re.search(rf'\b{re.escape(keyword)}\b', text_lower):
                    return product
        return ""
    
    @staticmethod
    def _extract_gender_from_text(text: str) -> str:
        """Extract target gender/audience from text."""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["mens", "men's", "for men", "male", "gents", "boys"]):
            return "men"
        elif any(w in text_lower for w in ["womens", "women's", "for women", "female", "ladies", "girls"]):
            return "women"
        elif any(w in text_lower for w in ["kids", "children", "child", "baby", "toddler"]):
            return "kids"
        elif any(w in text_lower for w in ["unisex", "anyone", "all"]):
            return "unisex"
        
        return ""
    
    @staticmethod
    def _is_vague_message(text: str) -> bool:
        """Check if user message is too vague to be useful alone."""
        vague_patterns = [
            r'^(show|find|get|give)\s*(me)?\s*(this|these|it|them|some|similar)?\s*$',
            r'^(i\s+)?(want|need|like)\s*(this|these|it|something)?\s*(like\s+this)?\s*$',
            r'^(what|where)\s*(is|are)?\s*(this|these|it)?\s*$',
            r'^similar\s*(ones?|products?)?\s*$',
            r'^(more|other)\s*(options?|choices?)?\s*$',
            r'^(yes|no|ok|okay|sure|please|thanks?)\s*$',
            r'^show\s+me\s+(red|blue|green|black|white)\s+ones?\s*$',
        ]
        
        for pattern in vague_patterns:
            if re.match(pattern, text):
                return True
        return len(text) < 8
    
    @staticmethod
    def _extract_color_from_text(text: str) -> str:
        """Extract color mentioned in user text."""
        colors = [
            "red", "blue", "green", "yellow", "orange", "purple", "pink", "black",
            "white", "gray", "grey", "brown", "beige", "navy", "maroon", "teal",
            "gold", "silver", "rose gold", "burgundy", "coral", "cream", "ivory",
            "turquoise", "olive", "mint", "lavender", "peach", "rust", "mustard",
            "champagne", "bronze", "copper", "platinum"
        ]
        
        text_lower = text.lower()
        for color in colors:
            if re.search(rf'\b{re.escape(color)}\b', text_lower):
                return color
        return ""
    
    @staticmethod
    def _extract_style_from_text(text: str) -> str:
        """Extract style preference from user text."""
        styles = {
            "casual": ["casual", "everyday", "relaxed", "comfortable", "comfy"],
            "formal": ["formal", "professional", "office", "business", "work"],
            "sporty": ["sporty", "athletic", "sport", "gym", "workout", "running"],
            "elegant": ["elegant", "classy", "sophisticated", "chic", "fancy"],
            "vintage": ["vintage", "retro", "classic", "old school", "antique"],
            "modern": ["modern", "contemporary", "trendy", "minimalist", "sleek"],
            "bohemian": ["boho", "bohemian", "hippie", "free spirit", "ethnic"],
            "luxurious": ["luxury", "luxurious", "premium", "high-end", "designer", "expensive"],
            "traditional": ["traditional", "ethnic", "cultural", "heritage"]
        }
        
        text_lower = text.lower()
        for style, keywords in styles.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return style
        return ""
    
    @staticmethod
    def _extract_action_intent(text: str) -> str:
        """Extract user's intent/action from their message."""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["similar", "like this", "same", "matching", "look alike"]):
            return "similar"
        elif any(w in text_lower for w in ["cheaper", "budget", "affordable", "less expensive", "under", "inexpensive"]):
            return "cheaper"
        elif any(w in text_lower for w in ["luxury", "premium", "high-end", "expensive", "best", "top"]):
            return "luxury"
        elif any(w in text_lower for w in ["different", "other", "alternative", "options"]):
            return "alternative"
        
        return ""
    
    @classmethod
    def format_image_context_for_llm(cls, image_attrs: ImageAttributes) -> str:
        """Format image attributes as context string for the main chat LLM."""
        if not image_attrs or image_attrs.confidence < 0.3:
            return ""
        
        parts = []
        
        # Product identification
        if image_attrs.product_type:
            product_desc = image_attrs.product_type
            if image_attrs.subcategory and image_attrs.subcategory != image_attrs.product_type:
                product_desc = f"{image_attrs.subcategory} ({image_attrs.product_type})"
            parts.append(f"Product: {product_desc}")
        
        # Visual details
        visual_parts = []
        if image_attrs.primary_color:
            color_str = image_attrs.get_color_string()
            visual_parts.append(color_str)
        if image_attrs.pattern and image_attrs.pattern.lower() not in ["solid", "plain"]:
            visual_parts.append(f"{image_attrs.pattern} pattern")
        if image_attrs.material:
            visual_parts.append(image_attrs.material)
        
        if visual_parts:
            parts.append(f"Appearance: {', '.join(visual_parts)}")
        
        # Style info
        style_parts = []
        if image_attrs.style:
            style_parts.append(image_attrs.style)
        if image_attrs.occasion and image_attrs.occasion.lower() not in ["everyday", "general", "any"]:
            style_parts.append(f"suitable for {image_attrs.occasion}")
        if image_attrs.gender_target:
            style_parts.append(f"for {image_attrs.gender_target}")
        
        if style_parts:
            parts.append(f"Style: {', '.join(style_parts)}")
        
        # Notable features
        if image_attrs.notable_features:
            parts.append(f"Features: {', '.join(image_attrs.notable_features[:3])}")
        
        if not parts:
            return ""
        
        # Confidence indicator
        confidence_level = "high" if image_attrs.confidence >= 0.7 else "moderate" if image_attrs.confidence >= 0.5 else "low"
        
        return f"[Image Analysis ({confidence_level} confidence)]\n" + "\n".join(parts)

