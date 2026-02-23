-- Tentree: only Hindi & Gujarati
UPDATE chatbot_appearances SET languages = '["hi", "gu"]'::jsonb
WHERE chatbot_id = '799637f9-391b-4b9d-84cb-5fdd17cdf109';

-- Zevaramaze: only English & Hindi
UPDATE chatbot_appearances SET languages = '["en", "hi"]'::jsonb
WHERE chatbot_id = 'e79b3754-006d-45d5-b21d-2391710e08ca';

-- Ramraj: only English & Gujarati
UPDATE chatbot_appearances SET languages = '["en", "gu"]'::jsonb
WHERE chatbot_id = '182f88cd-02d8-4c94-824d-b41432847400';

-- Verify
SELECT c.name, ca.languages
FROM chatbot_appearances ca
JOIN chatbots c ON c.id = ca.chatbot_id
WHERE c.id IN ('799637f9-391b-4b9d-84cb-5fdd17cdf109', 'e79b3754-006d-45d5-b21d-2391710e08ca', '182f88cd-02d8-4c94-824d-b41432847400');
