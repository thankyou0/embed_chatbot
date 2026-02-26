SELECT cm.metadata_json
FROM chat_messages cm
JOIN chat_sessions cs ON cm.session_id = cs.id
WHERE cs.id = '923b59bd-74db-48d9-ab98-005eb6d5e392'
  AND cm.role = 'assistant'
ORDER BY cm.created_at DESC
LIMIT 1;
