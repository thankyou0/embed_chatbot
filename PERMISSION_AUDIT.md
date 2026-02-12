# Permission System Audit

## Overview

This document outlines the comprehensive permission system implemented across the application, including role-based access control (RBAC) and granular chatbot-level permissions.

## User Roles

### Admin (ADMIN)

- Full access to all tenant resources
- Can create chatbots
- Can manage team members
- Can view all analytics and billing information
- Can modify any chatbot settings

### Member (MEMBER)

- Limited access based on per-chatbot permissions
- Cannot create chatbots (enforced both frontend and backend)
- Can only access chatbots they have been explicitly assigned to
- Analytics/Usage tabs visible only if they have permission on at least one chatbot

### Organization Owner (is_org_owner flag)

- First admin user in a tenant
- Designated organization owner
- Currently has same permissions as admin, but flagged for future features

## Granular Permissions

Each chatbot has the following granular permissions that can be assigned to team members:

### 1. `can_manage_knowledge`

**Controls:** Knowledge source management

- Add/edit/delete crawled URLs
- Upload files
- Add/edit/delete QA pairs
- Schedule crawls
- Trigger manual crawls
- Also serves as proxy for general chatbot settings (name, status)

**Endpoints Protected:**

- `POST /chatbots/{chatbot_id}/crawl`
- `DELETE /knowledge-sources/{source_id}`
- `POST /chatbots/{chatbot_id}/knowledge-sources/bulk-delete`
- `POST /chatbots/{chatbot_id}/upload`
- `POST /chatbots/{chatbot_id}/qa`
- `POST /chatbots/{chatbot_id}/qa/upload`
- `PUT /qa-pairs/{qa_id}`
- `DELETE /qa-pairs/{qa_id}`
- `POST /knowledge-sources/{source_id}/schedule`
- `PATCH /knowledge-sources/{source_id}/schedule`
- `POST /knowledge-sources/{source_id}/crawl-now`

**Service Methods:**

- `ChatbotService.create_crawl_source()`
- `ChatbotService.delete_knowledge_source()`
- `ChatbotService.create_file_upload()`
- `ChatbotService.create_qa_pair()`
- `ChatbotService.update_qa_pair()`
- `ChatbotService.delete_qa_pair()`

### 2. `can_manage_appearance`

**Controls:** Chatbot appearance and styling

- Update theme colors
- Modify widget position
- Change initial messages
- Update avatars
- Configure initial suggestions

**Endpoints Protected:**

- `PATCH /chatbots/{chatbot_id}/appearance`
- `POST /chatbots/{chatbot_id}/avatar`

**Service Methods:**

- `ChatbotService.update_appearance()`
- `ChatbotService.upload_avatar()`

### 3. `can_resolve_queries`

**Controls:** Query resolution and analytics actions

- Mark unanswered queries as resolved
- Requires both viewing and acting on analytics data

**Endpoints Protected:**

- `POST /chatbots/{chatbot_id}/analytics/unanswered/resolve`

**Service Methods:**

- `AnalyticsService.resolve_queries()`

**Frontend Behavior:**

- When enabled in assignment UI, automatically enables `can_view_analytics_billing`
- Users with this permission can see and interact with unanswered query lists

### 4. `can_view_analytics_billing`

**Controls:** View analytics and usage data

- View analytics overview
- View unanswered queries
- View usage statistics
- View conversation history

**Endpoints Protected:**

- `GET /chatbots/analytics/overview` (with chatbot_id)
- `GET /chatbots/{chatbot_id}/analytics/unanswered`
- `GET /usage/overview` (with chatbot_id for members)
- `GET /chatbots/{chatbot_id}/stats`

**Service Methods:**

- `AnalyticsService.get_analytics_overview()`
- `AnalyticsService.get_unanswered_queries()`
- `ChatbotService.get_chatbot_stats()`

**Frontend Behavior:**

- Controls visibility of "Analytics" and "Usage & Billing" tabs in sidebar
- Members with this permission on ANY chatbot can see these tabs
- Tab content filters to show only data for chatbots they have permission for

## Admin-Only Endpoints

These endpoints are restricted to admin users only, regardless of chatbot permissions:

### Billing Management

- `GET /billing/overview` - View billing overview and subscription
- `POST /billing/change-plan` - Change subscription plan

### Team Management

- `GET /team/members` - List team members
- `POST /team/members` - Invite new team members
- `DELETE /team/members/{user_id}` - Remove team members
- `PATCH /team/members/{user_id}/role` - Update member role
- Team page in frontend shows management UI only for admins

### Chatbot Creation

- `POST /chatbots` - Create new chatbot
  - Frontend: Create button disabled for members
  - Backend: Explicitly checks `user.role == UserRole.ADMIN`
  - Empty state shows different message for members

### Global Analytics

- `GET /chatbots/analytics/overview` (without chatbot_id) - View analytics for all chatbots

### Tenant Settings

- `GET /dashboard/settings` - Tenant settings page (admin-only in frontend)
- `GET /dashboard/pricing` - Pricing page (admin-only in frontend)

## Permission Validation Flow

### Backend Validation

1. **Endpoint Level**: Most endpoints accept `current_user` dependency
2. **Service Level**: Services call `ChatbotService.has_permission()` to validate
3. **Permission Check**:
   ```python
   if not await ChatbotService.has_permission(db, chatbot_id, user, "permission_name"):
       raise ForbiddenError("Insufficient permissions")
   ```
4. **Admin Bypass**: Admins automatically pass all permission checks

### Frontend Validation

1. **Route Level**: AuthContext provides `isAdmin` flag
2. **Component Level**: Components check permissions before rendering actions
3. **Sidebar Navigation**: Dynamically shows/hides tabs based on:
   - Admin status (see everything)
   - User permissions (fetch chatbots, check if any have analytics permission)

## Permission Assignment

### Assignment Process

1. Admin navigates to chatbot's "Team" tab
2. Assigns member to chatbot with granular permissions
3. No longer uses permission_level presets (CUSTOM only)
4. Each permission is an explicit boolean checkbox
5. Auto-enables `can_view_analytics_billing` when `can_resolve_queries` is checked

### Database Schema

```python
class ChatbotPermission:
    user_id: int
    chatbot_id: UUID
    permission_level: PermissionLevel  # Always CUSTOM now
    can_manage_knowledge: bool
    can_manage_appearance: bool
    can_resolve_queries: bool
    can_view_analytics_billing: bool
```

## Security Considerations

### ✅ Protected Operations

- All mutating operations (POST/PUT/PATCH/DELETE) check permissions
- Analytics and usage endpoints validate access
- Chatbot creation restricted to admins
- Team management restricted to admins
- Billing operations restricted to admins

### ✅ Frontend-Backend Consistency

- Frontend hides UI elements user can't access
- Backend always validates permissions (never trusts frontend)
- Empty states and disabled buttons guide users appropriately

### ✅ Granular Access Control

- Members can be given specific responsibilities per chatbot
- Analytics permission allows monitoring without edit access
- Knowledge management separate from appearance/styling
- Query resolution separate from viewing analytics

## Future Enhancements

### Potential Additions

1. **Read-Only Knowledge Access** - View knowledge sources without editing
2. **Chat History Access** - Separate permission for viewing conversations
3. **Export Permissions** - Control who can export data
4. **Bulk Operations** - Permission to perform bulk actions
5. **Organization Owner Features** - Special capabilities for org owner flag

### Permission Combinations

Consider adding permission templates:

- **Content Manager**: can_manage_knowledge only
- **Designer**: can_manage_appearance only
- **Analyst**: can_view_analytics_billing + can_resolve_queries
- **Support**: can_view_analytics_billing + chat history access

## Testing Checklist

When testing permissions:

- [ ] Non-admin cannot create chatbot (frontend + backend)
- [ ] Non-admin without permission cannot access endpoints
- [ ] Member with analytics permission sees Analytics/Usage tabs
- [ ] Member without analytics permission does NOT see tabs
- [ ] Admin always sees all tabs and can perform all actions
- [ ] Permission changes reflect immediately in UI
- [ ] Backend always validates permissions (test with API calls directly)
- [ ] Proper error messages when permission denied

## Migration Notes

Database migration `024_add_org_owner_and_rename_analytics.py` includes:

- Added `is_org_owner` field to users table
- Renamed `can_view_analytics` to `can_view_analytics_billing`
- Set first admin in each tenant as organization owner
- Migrated existing permission values to new field name
