SELECT LEFT(cm.content, 100) as response,
       cm.metadata_json->>'is_missing_info' as is_missing,
       cm.metadata_json->>'was_answered' as was_answered,
       cm.metadata_json->>'is_irrelevant' as is_irrelevant,
       cm.metadata_json->>'scope_gated' as scope_gated,
       cs.id as session_uuid
FROM chat_messages cm
JOIN chat_sessions cs ON cm.session_id = cs.id
WHERE cm.role = 'assistant'
  AND cm.created_at > NOW() - INTERVAL '10 minutes'
ORDER BY cm.created_at DESC
LIMIT 20;
