SELECT cs.session_id, cs.id, cm.role, 
       LEFT(cm.content, 80) as content_preview,
       cm.metadata_json->>'is_missing_info' as is_missing
FROM chat_sessions cs 
JOIN chat_messages cm ON cm.session_id = cs.id
WHERE cm.role = 'assistant'
  AND cm.created_at > NOW() - INTERVAL '30 minutes'
ORDER BY cm.created_at DESC 
LIMIT 10;
