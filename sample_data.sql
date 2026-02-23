-- Language settings
SELECT c.name, ca.languages
FROM chatbot_appearances ca
JOIN chatbots c ON c.id = ca.chatbot_id
WHERE c.id IN ('799637f9-391b-4b9d-84cb-5fdd17cdf109', 'e79b3754-006d-45d5-b21d-2391710e08ca', '1cb18dc0-4909-409d-ab03-0436524fcec4');

-- Tentree sample products (20)
SELECT cp.title, LEFT(cp.url, 100), cp.is_product, LEFT(cp.product_metadata::text, 200)
FROM crawled_pages cp
JOIN knowledge_sources ks ON cp.knowledge_source_id = ks.id
WHERE ks.chatbot_id = '799637f9-391b-4b9d-84cb-5fdd17cdf109' AND NOT cp.is_removed AND cp.is_product
ORDER BY random() LIMIT 20;

-- Tentree non-product pages
SELECT cp.title, LEFT(cp.url, 100), cp.is_product
FROM crawled_pages cp
JOIN knowledge_sources ks ON cp.knowledge_source_id = ks.id
WHERE ks.chatbot_id = '799637f9-391b-4b9d-84cb-5fdd17cdf109' AND NOT cp.is_removed AND NOT cp.is_product
ORDER BY random() LIMIT 15;

-- Zevaramaze sample products (20)
SELECT cp.title, LEFT(cp.url, 100), cp.is_product, LEFT(cp.product_metadata::text, 200)
FROM crawled_pages cp
JOIN knowledge_sources ks ON cp.knowledge_source_id = ks.id
WHERE ks.chatbot_id = 'e79b3754-006d-45d5-b21d-2391710e08ca' AND NOT cp.is_removed AND cp.is_product
ORDER BY random() LIMIT 20;

-- Zevaramaze non-product pages
SELECT cp.title, LEFT(cp.url, 100), cp.is_product
FROM crawled_pages cp
JOIN knowledge_sources ks ON cp.knowledge_source_id = ks.id
WHERE ks.chatbot_id = 'e79b3754-006d-45d5-b21d-2391710e08ca' AND NOT cp.is_removed AND NOT cp.is_product
ORDER BY random() LIMIT 10;

-- Kriyanta sample products (20)
SELECT cp.title, LEFT(cp.url, 100), cp.is_product, LEFT(cp.product_metadata::text, 200)
FROM crawled_pages cp
JOIN knowledge_sources ks ON cp.knowledge_source_id = ks.id
WHERE ks.chatbot_id = '1cb18dc0-4909-409d-ab03-0436524fcec4' AND NOT cp.is_removed AND cp.is_product
ORDER BY random() LIMIT 20;

-- Kriyanta non-product pages
SELECT cp.title, LEFT(cp.url, 100), cp.is_product
FROM crawled_pages cp
JOIN knowledge_sources ks ON cp.knowledge_source_id = ks.id
WHERE ks.chatbot_id = '1cb18dc0-4909-409d-ab03-0436524fcec4' AND NOT cp.is_removed AND NOT cp.is_product
ORDER BY random() LIMIT 15;
