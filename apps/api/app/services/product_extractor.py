"""
Product Data Extractor

Multi-layer approach to extract product information from any e-commerce page.
Works with:
- Sites with JSON-LD structured data (Shopify, WooCommerce, etc.)
- Sites with OpenGraph meta tags
- Custom sites using heuristic detection

This extractor is additive - it doesn't affect non-product pages.
"""

import re
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProductDataExtractor:
    """
    Extracts product data from HTML using multiple detection layers.
    Returns None for non-product pages - safe for all page types.
    """
    
    # URL patterns that indicate a product page
    PRODUCT_URL_PATTERNS = [
        r'/products?/',          # /product/, /products/
        r'/p/[^/]+',             # /p/item-123
        r'/item/',               # /item/
        r'/shop/[^/]+/[^/]+',    # /shop/category/item
        r'/buy/',                # /buy/
        r'[?&]product[_-]?id=',  # ?product_id=123
        r'/dp/',                 # Amazon style /dp/
        r'/gp/product/',         # Amazon /gp/product/
    ]
    
    # Keywords that indicate "Add to Cart" functionality
    ADD_TO_CART_KEYWORDS = [
        'add to cart', 'add to bag', 'add to basket',
        'buy now', 'purchase', 'order now',
        'कार्ट में जोड़ें', 'खरीदें',  # Hindi
    ]
    
    # Price patterns for different currencies
    PRICE_PATTERNS = [
        # Indian Rupee
        (r'₹\s?([\d,]+(?:\.\d{2})?)', 'INR'),
        (r'Rs\.?\s?([\d,]+(?:\.\d{2})?)', 'INR'),
        (r'INR\s?([\d,]+(?:\.\d{2})?)', 'INR'),
        # US Dollar
        (r'\$\s?([\d,]+(?:\.\d{2})?)', 'USD'),
        (r'USD\s?([\d,]+(?:\.\d{2})?)', 'USD'),
        # Euro
        (r'€\s?([\d,]+(?:\.\d{2})?)', 'EUR'),
        (r'EUR\s?([\d,]+(?:\.\d{2})?)', 'EUR'),
        # British Pound
        (r'£\s?([\d,]+(?:\.\d{2})?)', 'GBP'),
        # Generic price labels
        (r'(?:Price|MRP|Sale Price|Offer Price)[:\s]*[\$₹€£]?\s?([\d,]+(?:\.\d{2})?)', None),
    ]
    
    def __init__(self, html: str, url: str):
        self.html = html
        self.url = url
        self.soup = BeautifulSoup(html, 'html.parser')
        self.confidence_score = 0
        self.extraction_sources = []  # Track where data came from
    
    # URL patterns that indicate INFORMATIONAL/NON-PRODUCT pages
    # These should NEVER be detected as products
    NON_PRODUCT_URL_PATTERNS = [
        r'/returns?[-_]?policy',       # Returns policy
        r'/refund[-_]?policy',         # Refund policy
        r'/privacy[-_]?policy',        # Privacy policy
        r'/terms[-_]?(and[-_])?conditions?', # Terms and conditions
        r'/terms[-_]?of[-_]?(service|use)', # Terms of service/use
        r'/shipping[-_]?(policy|info)', # Shipping info
        r'/contact[-_]?us',            # Contact us
        r'/contact$',                  # Contact page
        r'/about[-_]?us',              # About us
        r'/about$',                    # About page
        r'/faq',                       # FAQ
        r'/help',                      # Help page
        r'/support',                   # Support page
        r'/blog/',                     # Blog posts
        r'/news/',                     # News
        r'/careers?',                  # Careers page
        r'/jobs?',                     # Jobs page
        r'/login',                     # Login page
        r'/register',                  # Register page
        r'/signup',                    # Signup page
        r'/account',                   # Account page
        r'/cart',                      # Cart page
        r'/checkout',                  # Checkout page
        r'/wishlist',                  # Wishlist page
        r'/track[-_]?order',           # Order tracking
        r'/order[-_]?status',          # Order status
        r'/my[-_]?orders?',            # My orders
        r'/sitemap',                   # Sitemap
        r'/404',                       # Error page
        r'/error',                     # Error page
        r'/not[-_]?found',             # Not found page
    ]
    
    # URL patterns that indicate a COLLECTION/LISTING page (NOT a single product)
    # Note: These are checked ONLY if URL doesn't contain /products/ or /product/
    COLLECTION_URL_PATTERNS = [
        r'/collections?/[^/]+/?$',  # Shopify collections WITHOUT /products/ after (e.g., /collections/shirts)
        r'/collections?/[^/]+\?',   # Collection with query params (e.g., /collections/shirts?page=2)
        r'/category/[^/]+/?$',      # Category pages without product
        r'/categories/',            # Categories
        r'/c/[^/]+$',              # /c/category-name (no product after)
        r'/shop/?$',               # Shop landing page
        r'/store/?$',              # Store landing page
        r'/all-products',          # All products page
        r'/search',                # Search results
        r'[?&]page=\d+',           # Pagination - likely a listing
        r'[?&]sort=',              # Sort parameter - listing
        r'[?&]filter',             # Filter parameter - listing
        r'[?&]category=',          # Category filter
        r'/tag/',                  # Tag pages
        r'/brand/',                # Brand listing pages
    ]
    
    def _is_non_product_page(self) -> bool:
        """Check if URL matches non-product page patterns (policy, contact, about, etc.)"""
        for pattern in self.NON_PRODUCT_URL_PATTERNS:
            if re.search(pattern, self.url, re.IGNORECASE):
                return True
        return False
    
    def _is_collection_page(self) -> bool:
        """Check if URL matches collection/listing page patterns"""
        url_lower = self.url.lower()
        
        # IMPORTANT: If URL contains /products/ or /product/, it's a product page, NOT a collection
        if '/products/' in url_lower or '/product/' in url_lower:
            return False
        
        # Check collection patterns
        for pattern in self.COLLECTION_URL_PATTERNS:
            if re.search(pattern, self.url, re.IGNORECASE):
                return True
        return False
    
    def extract(self) -> Optional[Dict[str, Any]]:
        """
        Main extraction method. Returns product data or None if not a product page.
        """
        # FIRST: Check if this is a non-product page (policy, contact, about, etc.)
        if self._is_non_product_page():
            logger.debug(f"Page {self.url} is a non-product page (policy/contact/etc), skipping")
            return None
        
        # SECOND: Check if this is a collection/listing page
        # We'll still try to extract product data, but apply stricter validation
        is_collection = self._is_collection_page()
        if is_collection:
            logger.debug(f"Page {self.url} appears to be a collection/listing page - applying strict validation")
        
        product_data = {
            'name': None,
            'price': None,
            'currency': None,
            'original_price': None,  # For sale items
            'images': [],
            'description': None,
            'brand': None,
            'sku': None,
            'availability': None,
            'rating': None,
            'review_count': None,
            'variants': [],
            'categories': [],
            'url': self.url,
        }
        
        # Layer 1: JSON-LD (highest priority)
        jsonld_data = self._extract_jsonld()
        if jsonld_data:
            product_data = self._merge_data(product_data, jsonld_data)
            self.confidence_score += 50
            self.extraction_sources.append('json-ld')
        
        # Layer 2: OpenGraph meta tags
        og_data = self._extract_opengraph()
        if og_data:
            product_data = self._merge_data(product_data, og_data)
            self.confidence_score += 20
            self.extraction_sources.append('opengraph')
        
        # Layer 3: Microdata
        microdata = self._extract_microdata()
        if microdata:
            product_data = self._merge_data(product_data, microdata)
            self.confidence_score += 15
            self.extraction_sources.append('microdata')
        
        # Layer 4: URL pattern check
        if self._matches_product_url():
            self.confidence_score += 15
            self.extraction_sources.append('url-pattern')
        
        # Layer 5: Heuristic extraction (fills gaps)
        heuristic_data = self._extract_heuristics()
        if heuristic_data:
            product_data = self._merge_data(product_data, heuristic_data)
            if heuristic_data.get('has_add_to_cart'):
                self.confidence_score += 15
                self.extraction_sources.append('add-to-cart-detected')
            if heuristic_data.get('price'):
                self.confidence_score += 10
                self.extraction_sources.append('price-heuristic')
        
        # Threshold: 30+ points = likely a product page
        # For collection/listing pages, require higher confidence (50+) to avoid false positives
        min_confidence = 50 if is_collection else 30
        
        if self.confidence_score < min_confidence:
            logger.debug(f"Page {self.url} is not a product (score: {self.confidence_score}, required: {min_confidence}, is_collection: {is_collection})")
            return None
        
        # Additional validation for collection pages: must have concrete product details
        if is_collection:
            # Collection pages must have at least name AND (price OR images) to be valid
            has_name = bool(product_data.get('name', '').strip())
            has_price = bool(product_data.get('price'))
            has_images = bool(product_data.get('images'))
            
            if not (has_name and (has_price or has_images)):
                logger.debug(f"Collection page {self.url} lacks concrete product details (name: {has_name}, price: {has_price}, images: {has_images})")
                return None
        
        # Clean up the data
        product_data = self._clean_product_data(product_data)
        
        # Add metadata
        product_data['_extraction_info'] = {
            'confidence_score': self.confidence_score,
            'sources': self.extraction_sources,
        }
        
        logger.info(f"Extracted product data from {self.url} (confidence: {self.confidence_score}, sources: {self.extraction_sources})")
        
        return product_data
    
    def _extract_jsonld(self) -> Optional[Dict[str, Any]]:
        """Extract product data from JSON-LD schema"""
        scripts = self.soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string or '')
                
                # Handle @graph structure
                if isinstance(data, dict) and '@graph' in data:
                    data = data['@graph']
                
                # Handle array of schemas
                if isinstance(data, list):
                    for item in data:
                        product = self._parse_jsonld_product(item)
                        if product:
                            return product
                else:
                    product = self._parse_jsonld_product(data)
                    if product:
                        return product
                        
            except (json.JSONDecodeError, TypeError) as e:
                logger.debug(f"Failed to parse JSON-LD: {e}")
                continue
        
        return None
    
    def _parse_jsonld_product(self, data: Dict) -> Optional[Dict[str, Any]]:
        """Parse a JSON-LD object for product data"""
        if not isinstance(data, dict):
            return None
        
        schema_type = data.get('@type', '')
        
        # Check for product types
        product_types = ['Product', 'IndividualProduct', 'ProductModel', 'Vehicle']
        if isinstance(schema_type, list):
            is_product = any(t in product_types for t in schema_type)
        else:
            is_product = schema_type in product_types
        
        if not is_product:
            return None
        
        result = {
            'name': data.get('name'),
            'description': data.get('description'),
            'brand': self._extract_brand(data.get('brand')),
            'sku': data.get('sku') or data.get('productID') or data.get('gtin13'),
            'images': self._extract_images(data.get('image')),
            'categories': self._extract_categories(data.get('category')),
        }
        
        # Extract offers/pricing
        offers = data.get('offers') or data.get('Offers')
        if offers:
            offer_data = self._parse_offers(offers)
            result.update(offer_data)
        
        # Extract ratings
        rating = data.get('aggregateRating')
        if rating:
            result['rating'] = self._safe_float(rating.get('ratingValue'))
            result['review_count'] = self._safe_int(rating.get('reviewCount') or rating.get('ratingCount'))
        
        return result
    
    def _parse_offers(self, offers: Any) -> Dict[str, Any]:
        """Parse offers/pricing from JSON-LD"""
        result = {}
        
        # Handle single offer or array of offers
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        if isinstance(offers, dict):
            result['price'] = self._safe_float(offers.get('price'))
            result['currency'] = offers.get('priceCurrency')
            
            # Check for sale/original price
            if offers.get('priceSpecification'):
                spec = offers['priceSpecification']
                if isinstance(spec, list):
                    spec = spec[0]
                if isinstance(spec, dict):
                    result['price'] = self._safe_float(spec.get('price')) or result['price']
                    result['currency'] = spec.get('priceCurrency') or result['currency']
            
            # Availability
            availability = offers.get('availability', '')
            if 'InStock' in str(availability):
                result['availability'] = 'in_stock'
            elif 'OutOfStock' in str(availability):
                result['availability'] = 'out_of_stock'
            elif 'PreOrder' in str(availability):
                result['availability'] = 'pre_order'
        
        return result
    
    def _extract_opengraph(self) -> Optional[Dict[str, Any]]:
        """Extract product data from OpenGraph meta tags"""
        result = {}
        
        # Check if it's a product type
        og_type = self._get_meta('og:type')
        product_meta = self._get_meta('product:price:amount')
        
        # If not explicitly a product and no price meta, skip
        if og_type != 'product' and not product_meta:
            # Still extract image for potential use
            og_image = self._get_meta('og:image')
            if og_image:
                result['images'] = [self._make_absolute_url(og_image)]
            return result if result else None
        
        result['name'] = self._get_meta('og:title')
        result['description'] = self._get_meta('og:description')
        
        og_image = self._get_meta('og:image')
        if og_image:
            result['images'] = [self._make_absolute_url(og_image)]
        
        # Product-specific OG tags
        result['price'] = self._safe_float(self._get_meta('product:price:amount'))
        result['currency'] = self._get_meta('product:price:currency')
        result['availability'] = self._normalize_availability(self._get_meta('product:availability'))
        result['brand'] = self._get_meta('product:brand')
        
        return result
    
    def _extract_microdata(self) -> Optional[Dict[str, Any]]:
        """Extract product data from Microdata (itemprop attributes)"""
        result = {}
        
        # Check if there's a Product itemtype
        product_elem = self.soup.find(itemtype=re.compile(r'schema\.org/Product', re.I))
        if not product_elem:
            # Try finding individual itemprop elements
            pass
        
        # Extract common itemprops
        name_elem = self.soup.find(itemprop='name')
        if name_elem:
            result['name'] = name_elem.get_text(strip=True)
        
        price_elem = self.soup.find(itemprop='price')
        if price_elem:
            price_val = price_elem.get('content') or price_elem.get_text(strip=True)
            result['price'] = self._safe_float(price_val)
        
        currency_elem = self.soup.find(itemprop='priceCurrency')
        if currency_elem:
            result['currency'] = currency_elem.get('content') or currency_elem.get_text(strip=True)
        
        image_elem = self.soup.find(itemprop='image')
        if image_elem:
            img_url = image_elem.get('src') or image_elem.get('content') or image_elem.get('href')
            if img_url:
                result['images'] = [self._make_absolute_url(img_url)]
        
        return result if result else None
    
    def _extract_heuristics(self) -> Optional[Dict[str, Any]]:
        """Extract product data using heuristic patterns"""
        result = {}
        
        # Check for Add to Cart button
        page_text = self.soup.get_text().lower()
        result['has_add_to_cart'] = any(kw in page_text for kw in self.ADD_TO_CART_KEYWORDS)
        
        # Extract price using patterns
        if not result.get('price'):
            price_data = self._extract_price_heuristic()
            if price_data:
                result['price'] = price_data.get('price')
                result['currency'] = price_data.get('currency')
        
        # Extract main product image
        if not result.get('images'):
            images = self._extract_images_heuristic()
            if images:
                result['images'] = images
        
        # Extract product name from h1
        if not result.get('name'):
            h1 = self.soup.find('h1')
            if h1:
                result['name'] = h1.get_text(strip=True)
        
        return result
    
    def _extract_price_heuristic(self) -> Optional[Dict[str, Any]]:
        """Extract price using regex patterns"""
        html_text = self.html
        
        for pattern, currency in self.PRICE_PATTERNS:
            match = re.search(pattern, html_text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    price = float(price_str)
                    if 0 < price < 10000000:  # Sanity check
                        return {'price': price, 'currency': currency}
                except ValueError:
                    continue
        
        return None
    
    def _is_valid_product_image(self, img_url: str) -> bool:
        """Check if image URL is likely a valid product image, not a generic/logo image"""
        if not img_url:
            return False
        
        img_lower = img_url.lower()
        
        # Skip generic/placeholder images
        skip_patterns = [
            'placeholder', 'default', 'no-image', 'noimage', 'no_image',
            'logo', 'icon', 'favicon', 'sprite', 'spacer', 'blank',
            'loading', 'loader', 'spinner', 'transparent', 'pixel',
            'badge', 'banner', 'ad_', 'ads_', 'advertisement',
            'social', 'facebook', 'twitter', 'instagram', 'pinterest',
            'share', 'email', 'cart', 'wishlist', 'search',
            '/assets/', '/static/images/', '/img/ui/', '/images/site/',
        ]
        
        if any(skip in img_lower for skip in skip_patterns):
            return False
        
        # Check for small image dimensions in URL (often icons)
        small_patterns = [
            r'[_-](\d{1,2})x(\d{1,2})[_.]',  # 16x16, 32x32, etc.
            r'[_-]thumb[_.]', r'[_-]tiny[_.]', r'[_-]micro[_.]',
        ]
        for pattern in small_patterns:
            if re.search(pattern, img_lower):
                return False
        
        return True
    
    def _extract_images_heuristic(self) -> List[str]:
        """Extract product images using heuristics"""
        images = []
        
        # Look for images with product-related classes/IDs FIRST (more reliable than og:image)
        product_img_patterns = [
            'product', 'gallery', 'main-image', 'featured',
            'product-image', 'product-photo', 'ProductImage',
            'item-image', 'detail-image', 'zoom', 'magnify'
        ]
        
        # Priority 1: Images inside product containers
        product_containers = self.soup.find_all(
            ['div', 'section', 'article'],
            class_=re.compile(r'product|item|gallery|detail', re.I)
        )
        
        for container in product_containers:
            for img in container.find_all('img', src=True):
                img_src = img.get('src', '')
                img_url = self._make_absolute_url(img_src)
                if img_url and self._is_valid_product_image(img_url) and img_url not in images:
                    images.append(img_url)
                    if len(images) >= 3:  # Found good images in product container
                        break
            if len(images) >= 3:
                break
        
        # Priority 2: Images with product-related classes/attributes
        if len(images) < 3:
            for img in self.soup.find_all('img', src=True):
                img_class = ' '.join(img.get('class', []))
                img_id = img.get('id', '')
                img_alt = img.get('alt', '')
                img_src = img.get('src', '')
                
                # Check if image seems product-related
                combined = f"{img_class} {img_id} {img_alt} {img_src}".lower()
                if any(pattern in combined for pattern in product_img_patterns):
                    img_url = self._make_absolute_url(img_src)
                    if img_url and self._is_valid_product_image(img_url) and img_url not in images:
                        images.append(img_url)
                        if len(images) >= 5:
                            break
        
        # Priority 3: og:image as fallback (can be generic for some sites)
        if len(images) == 0:
            og_image = self._get_meta('og:image')
            if og_image:
                img_url = self._make_absolute_url(og_image)
                if img_url and self._is_valid_product_image(img_url):
                    images.append(img_url)
        
        # Priority 4: Check srcset for high-res images
        if len(images) < 3:
            for img in self.soup.find_all('img', srcset=True):
                srcset = img.get('srcset', '')
                if srcset:
                    parts = srcset.split(',')
                    # Get the highest resolution image (usually last in srcset)
                    for part in reversed(parts):
                        url_part = part.strip().split()[0]
                        if url_part:
                            img_url = self._make_absolute_url(url_part)
                            if img_url and self._is_valid_product_image(img_url) and img_url not in images:
                                images.append(img_url)
                                break
        
        return images[:5]  # Limit to 5 images
    
    def _matches_product_url(self) -> bool:
        """Check if URL matches product page patterns"""
        for pattern in self.PRODUCT_URL_PATTERNS:
            if re.search(pattern, self.url, re.IGNORECASE):
                return True
        return False
    
    def _get_meta(self, property_name: str) -> Optional[str]:
        """Get meta tag content by property or name"""
        meta = self.soup.find('meta', property=property_name)
        if not meta:
            meta = self.soup.find('meta', attrs={'name': property_name})
        return meta.get('content') if meta else None
    
    def _make_absolute_url(self, url: str) -> Optional[str]:
        """Convert relative URL to absolute"""
        if not url:
            return None
        if url.startswith('//'):
            return 'https:' + url
        if url.startswith('/'):
            parsed = urlparse(self.url)
            return f"{parsed.scheme}://{parsed.netloc}{url}"
        if not url.startswith('http'):
            return urljoin(self.url, url)
        return url
    
    def _extract_brand(self, brand: Any) -> Optional[str]:
        """Extract brand name from various formats"""
        if not brand:
            return None
        if isinstance(brand, str):
            return brand
        if isinstance(brand, dict):
            return brand.get('name')
        if isinstance(brand, list) and brand:
            return self._extract_brand(brand[0])
        return None
    
    def _extract_images(self, image: Any) -> List[str]:
        """Extract image URLs from various formats"""
        if not image:
            return []
        if isinstance(image, str):
            return [self._make_absolute_url(image)]
        if isinstance(image, list):
            images = []
            for img in image[:5]:  # Limit to 5 images
                if isinstance(img, str):
                    images.append(self._make_absolute_url(img))
                elif isinstance(img, dict):
                    url = img.get('url') or img.get('contentUrl')
                    if url:
                        images.append(self._make_absolute_url(url))
            return images
        if isinstance(image, dict):
            url = image.get('url') or image.get('contentUrl')
            return [self._make_absolute_url(url)] if url else []
        return []
    
    def _extract_categories(self, category: Any) -> List[str]:
        """Extract categories from various formats"""
        if not category:
            return []
        if isinstance(category, str):
            return [category]
        if isinstance(category, list):
            return [c if isinstance(c, str) else c.get('name', '') for c in category[:5]]
        return []
    
    def _normalize_availability(self, availability: Optional[str]) -> Optional[str]:
        """Normalize availability value"""
        if not availability:
            return None
        availability = availability.lower()
        if 'instock' in availability or 'in stock' in availability:
            return 'in_stock'
        if 'outofstock' in availability or 'out of stock' in availability:
            return 'out_of_stock'
        if 'preorder' in availability:
            return 'pre_order'
        return availability
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float"""
        if value is None:
            return None
        try:
            if isinstance(value, str):
                value = value.replace(',', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to int"""
        if value is None:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _merge_data(self, base: Dict, new: Dict) -> Dict:
        """Merge new data into base, only filling empty fields"""
        for key, value in new.items():
            if value is not None:
                if key == 'images':
                    # Merge image lists
                    existing = base.get('images', [])
                    for img in value:
                        if img and img not in existing:
                            existing.append(img)
                    base['images'] = existing[:5]  # Limit to 5
                elif base.get(key) is None:
                    base[key] = value
        return base
    
    def _clean_product_data(self, data: Dict) -> Dict:
        """Clean up the final product data"""
        # Remove empty values
        cleaned = {}
        for key, value in data.items():
            if value is not None and value != '' and value != []:
                cleaned[key] = value
        
        # Ensure images is always a list
        if 'images' not in cleaned:
            cleaned['images'] = []
        
        return cleaned


def extract_product_data(html: str, url: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to extract product data from HTML.
    Returns None if the page is not a product page.
    
    Usage:
        product_data = extract_product_data(html_content, page_url)
        if product_data:
            # It's a product page
            print(f"Price: {product_data['price']} {product_data['currency']}")
        else:
            # Regular content page
            pass
    """
    extractor = ProductDataExtractor(html, url)
    return extractor.extract()
