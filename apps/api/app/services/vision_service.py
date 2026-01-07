import base64
import httpx
import json
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ImageAttributes:
    """Represents extracted product attributes from an image."""
    def __init__(
        self,
        product_type: str = "",
        category: str = "",
        color: str = "",
        style: str = "",
        other_attributes: str = "",
        confidence: float = 0.0,
        raw_description: str = ""
    ):
        self.product_type = product_type
        self.category = category
        self.color = color
        self.style = style
        self.other_attributes = other_attributes
        self.confidence = confidence
        self.raw_description = raw_description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_type": self.product_type,
            "category": self.category,
            "color": self.color,
            "style": self.style,
            "other_attributes": self.other_attributes,
            "confidence": self.confidence,
            "raw_description": self.raw_description
        }
    
    def to_search_query(self) -> str:
        """Build a search query string from the attributes."""
        parts = []
        if self.color:
            parts.append(self.color)
        if self.product_type:
            parts.append(self.product_type)
        if self.style:
            parts.append(self.style)
        if self.category and self.category not in parts:
            parts.append(self.category)
        if self.other_attributes:
            parts.append(self.other_attributes)
        return " ".join(parts) if parts else ""


class VisionService:
    """Service for analyzing images using Groq's vision model."""
    
    VISION_MODEL = "llama-3.2-90b-vision-preview"
    GROQ_VISION_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    EXTRACTION_PROMPT = """Extract product attributes from this image. Return ONLY valid JSON in this exact format:
{
  "product_type": "the type of product (e.g., shoes, shirt, bag)",
  "category": "broader category (e.g., footwear, clothing, accessories)",
  "color": "primary color(s)",
  "style": "style description (e.g., casual, formal, sporty)",
  "other_attributes": "any other notable features (material, pattern, etc.)",
  "confidence": 0.8
}

Rules:
- Only extract what you can clearly see
- Leave fields as empty strings if uncertain
- Set confidence between 0.0 and 1.0 based on image clarity
- Do NOT identify specific brands or SKUs
- Do NOT identify people or faces
- Focus only on product attributes

Return ONLY the JSON object, no other text."""

    @staticmethod
    def encode_image_to_base64(image_bytes: bytes) -> str:
        """Encode image bytes to base64 string."""
        return base64.b64encode(image_bytes).decode("utf-8")
    
    @staticmethod
    def get_image_mime_type(image_bytes: bytes) -> str:
        """Detect image MIME type from bytes."""
        # Check magic bytes
        if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            return "image/png"
        elif image_bytes[:2] == b'\xff\xd8':
            return "image/jpeg"
        elif image_bytes[:6] in (b'GIF87a', b'GIF89a'):
            return "image/gif"
        elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
            return "image/webp"
        # Default to jpeg
        return "image/jpeg"
    
    @classmethod
    async def analyze_image(cls, image_bytes: bytes) -> ImageAttributes:
        """
        Analyze an image and extract product attributes.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            ImageAttributes object with extracted attributes
        """
        try:
            base64_image = cls.encode_image_to_base64(image_bytes)
            mime_type = cls.get_image_mime_type(image_bytes)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    cls.GROQ_VISION_URL,
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": cls.VISION_MODEL,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": cls.EXTRACTION_PROMPT
                                    },
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
                        "max_tokens": 500
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Vision API error: {response.status_code} - {response.text}")
                    return ImageAttributes(confidence=0.0)
                
                res_data = response.json()
                content = res_data["choices"][0]["message"]["content"]
                
                # Parse JSON response
                return cls._parse_attributes(content)
                
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return ImageAttributes(confidence=0.0)
    
    @classmethod
    def _parse_attributes(cls, content: str) -> ImageAttributes:
        """Parse the LLM response into ImageAttributes."""
        try:
            # Try to extract JSON from the response
            content = content.strip()
            
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            data = json.loads(content)
            
            return ImageAttributes(
                product_type=data.get("product_type", ""),
                category=data.get("category", ""),
                color=data.get("color", ""),
                style=data.get("style", ""),
                other_attributes=data.get("other_attributes", ""),
                confidence=float(data.get("confidence", 0.5)),
                raw_description=content
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse vision response: {e}. Content: {content}")
            # Return with raw description for fallback
            return ImageAttributes(
                confidence=0.3,
                raw_description=content
            )
    
    @staticmethod
    def build_combined_query(
        user_message: str,
        image_attrs: Optional[ImageAttributes]
    ) -> str:
        """
        Build a combined search query from user text and image attributes.
        User text overrides image attributes.
        
        Example:
            User: "show me red ones" + image of blue shoes
            Image attrs: { product_type: "shoes", color: "blue" }
            Override: color → "red"  
            Result: "red shoes"
        """
        if not image_attrs or image_attrs.confidence < 0.3:
            return user_message
        
        # Start with image-derived query
        base_query = image_attrs.to_search_query()
        
        if not user_message.strip():
            return base_query
        
        user_lower = user_message.lower()
        
        # Check for color overrides in user message
        colors = ["red", "blue", "green", "yellow", "black", "white", "pink", 
                  "purple", "orange", "brown", "gray", "grey", "beige", "navy"]
        user_color = None
        for color in colors:
            if color in user_lower:
                user_color = color
                break
        
        # Build final query
        parts = []
        
        # Add color (user override or image)
        if user_color:
            parts.append(user_color)
        elif image_attrs.color:
            parts.append(image_attrs.color)
        
        # Add product type from image
        if image_attrs.product_type:
            parts.append(image_attrs.product_type)
        
        # Add style if present
        if image_attrs.style:
            parts.append(image_attrs.style)
        
        # Append any additional context from user message
        # Filter out color words we already used
        additional_words = []
        for word in user_message.split():
            word_lower = word.lower().strip(",.!?")
            if word_lower not in colors and word_lower not in ["show", "me", "ones", "like", "this", "similar", "to"]:
                if len(word_lower) > 2:
                    additional_words.append(word)
        
        if additional_words:
            parts.extend(additional_words[:3])  # Limit additional context
        
        combined = " ".join(parts) if parts else user_message
        logger.info(f"Combined query: '{combined}' (from user: '{user_message}', image: '{base_query}')")
        
        return combined

