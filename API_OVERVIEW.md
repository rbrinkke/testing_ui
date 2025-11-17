# Notifications API - Service Overview

**Version**: 1.0.0
**Base URL**: http://localhost:8006
**Documentation**: http://localhost:8006/docs (Swagger UI)

## Service Description

Real-time notification service with multi-channel delivery (push, email, SMS).

Features subscription management, notification preferences, and delivery status tracking.

### Key Features
- Multi-channel notifications (push/email/SMS)
- User preference management
- Delivery status tracking
- Subscription tiers (free/premium)
- Template-based notification rendering

### Architecture
- **Database**: PostgreSQL with `activity` schema
- **Queue**: Redis for async delivery
- **Auth**: JWT Bearer + service tokens

---

## Authentication

### User Endpoints
- **Type**: JWT Bearer Token
- **Header**: `Authorization: Bearer {token}`
- **Token Source**: Obtained from auth-api service
- **Token Contains**: user_id, email, subscription_level

### Service Endpoints
- **Type**: Service Token (internal service-to-service)
- **Header**: `X-Service-Token: {service_token}`
- **Purpose**: Allow other services to create notifications

---

## API Endpoints

### Health Check

#### `GET /health`
Health check endpoint. Returns 200 if API is healthy, 503 if degraded.

**Authentication**: None required

**Response**: 200 OK
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

### Notifications Management

#### `GET /api/v1/notifications`
Get paginated list of user's notifications.

**Authentication**: JWT Bearer Token (required)

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| status | string | No | - | Filter by status: `unread`, `read`, `archived` |
| type | string | No | - | Filter by notification type (see types below) |
| limit | integer | No | 20 | Page size (1-100) |
| offset | integer | No | 0 | Pagination offset (min: 0) |

**Response**: 200 OK
```json
{
  "notifications": [
    {
      "notification_id": "uuid",
      "user_id": "uuid",
      "actor": {
        "user_id": "uuid",
        "username": "string",
        "first_name": "string",
        "last_name": "string",
        "main_photo_url": "string"
      },
      "notification_type": "comment",
      "target_type": "post",
      "target_id": "uuid",
      "title": "New comment on your post",
      "message": "Someone commented on your post",
      "status": "unread",
      "created_at": "2025-11-17T12:00:00Z",
      "read_at": null,
      "payload": {}
    }
  ],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

**Example Requests**:
```bash
# Get all notifications (default: 20 unread)
curl -H "Authorization: Bearer {token}" \
  http://localhost:8006/api/v1/notifications

# Get only unread notifications
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8006/api/v1/notifications?status=unread"

# Get comment notifications
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8006/api/v1/notifications?type=comment&limit=50"

# Paginate through results
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8006/api/v1/notifications?limit=20&offset=20"
```

---

#### `GET /api/v1/notifications/{notification_id}`
Get single notification by ID.

**Authentication**: JWT Bearer Token (required)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| notification_id | uuid | Yes | Notification UUID |

**Response**: 200 OK
```json
{
  "notification_id": "uuid",
  "user_id": "uuid",
  "actor": {
    "user_id": "uuid",
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "main_photo_url": "https://..."
  },
  "notification_type": "comment",
  "target_type": "post",
  "target_id": "uuid",
  "title": "New comment",
  "message": "John commented on your post",
  "status": "unread",
  "created_at": "2025-11-17T12:00:00Z",
  "read_at": null,
  "payload": {
    "comment_text": "Great post!"
  }
}
```

**Error Responses**:
- `404`: Notification not found or doesn't belong to user
- `401`: Invalid or missing JWT token

---

#### `POST /api/v1/notifications`
Create new notification (internal service-to-service).

**Authentication**: Service Token (required)
**Header**: `X-Service-Token: {service_token}`

**Request Body**:
```json
{
  "user_id": "uuid",
  "actor_user_id": "uuid",
  "notification_type": "comment",
  "target_type": "post",
  "target_id": "uuid",
  "title": "New comment on your post",
  "message": "Optional message text",
  "payload": {
    "custom_key": "custom_value"
  }
}
```

**Field Descriptions**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | uuid | Yes | Recipient user ID |
| actor_user_id | uuid | No | User who triggered the notification |
| notification_type | string | Yes | Type of notification (see types below) |
| target_type | string | Yes | Type of target entity: `activity`, `post`, `comment`, `user` |
| target_id | uuid | Yes | UUID of target entity |
| title | string | Yes | Notification title (max 255 chars) |
| message | string | No | Optional notification message |
| payload | object | No | Additional custom data (JSONB) |

**Response**: 201 Created
```json
{
  "notification_id": "uuid",
  "created_at": "2025-11-17T12:00:00Z",
  "status": "created",
  "reason": null
}
```

**Response Status Values**:
- `created`: Notification created successfully
- `skipped`: Not created (user preferences, quiet hours, etc.)

**Example**:
```bash
curl -X POST \
  -H "X-Service-Token: shared-secret-token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "actor_user_id": "987e6543-e21b-32d1-b654-321456789000",
    "notification_type": "comment",
    "target_type": "post",
    "target_id": "456e7890-e12b-34d5-c789-012345678000",
    "title": "New comment on your post"
  }' \
  http://localhost:8006/api/v1/notifications
```

---

#### `PATCH /api/v1/notifications/{notification_id}/read`
Mark single notification as read.

**Authentication**: JWT Bearer Token (required)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| notification_id | uuid | Yes | Notification UUID |

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

**Example**:
```bash
curl -X PATCH \
  -H "Authorization: Bearer {token}" \
  http://localhost:8006/api/v1/notifications/123e4567-e89b-12d3-a456-426614174000/read
```

---

#### `POST /api/v1/notifications/mark-read`
Mark multiple notifications as read (bulk operation).

**Authentication**: JWT Bearer Token (required)

**Request Body Options**:

**Option 1: Mark specific notifications**
```json
{
  "notification_ids": [
    "uuid1",
    "uuid2",
    "uuid3"
  ]
}
```

**Option 2: Mark all unread notifications**
```json
{
  "mark_all": true
}
```

**Option 3: Mark all of specific type**
```json
{
  "mark_all": true,
  "notification_type": "comment"
}
```

**Response**: 200 OK
```json
{
  "updated_count": 5,
  "message": "5 notifications marked as read"
}
```

**Examples**:
```bash
# Mark specific notifications
curl -X POST \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "notification_ids": ["uuid1", "uuid2"]
  }' \
  http://localhost:8006/api/v1/notifications/mark-read

# Mark all unread
curl -X POST \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"mark_all": true}' \
  http://localhost:8006/api/v1/notifications/mark-read

# Mark all comment notifications
curl -X POST \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "mark_all": true,
    "notification_type": "comment"
  }' \
  http://localhost:8006/api/v1/notifications/mark-read
```

---

#### `DELETE /api/v1/notifications/{notification_id}`
Archive or permanently delete notification.

**Authentication**: JWT Bearer Token (required)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| notification_id | uuid | Yes | Notification UUID |

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| permanent | boolean | No | false | If true: hard delete. If false: archive (soft delete) |

**Response**: 200 OK
```json
{
  "success": true,
  "message": "Notification archived"
}
```

**Examples**:
```bash
# Archive notification (soft delete - default)
curl -X DELETE \
  -H "Authorization: Bearer {token}" \
  http://localhost:8006/api/v1/notifications/uuid

# Permanently delete notification
curl -X DELETE \
  -H "Authorization: Bearer {token}" \
  "http://localhost:8006/api/v1/notifications/uuid?permanent=true"
```

---

#### `GET /api/v1/notifications/unread/count`
Get count of unread notifications by type.

**Authentication**: JWT Bearer Token (required)

**Response**: 200 OK
```json
{
  "total": 15,
  "by_type": {
    "comment": 5,
    "reaction": 3,
    "activity_invite": 4,
    "mention": 2,
    "new_favorite": 1
  }
}
```

**Example**:
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:8006/api/v1/notifications/unread/count
```

---

### Settings Management

#### `GET /api/v1/settings`
Get user's notification settings. Returns defaults if settings don't exist yet.

**Authentication**: JWT Bearer Token (required)

**Response**: 200 OK
```json
{
  "user_id": "uuid",
  "email_enabled": true,
  "push_enabled": true,
  "in_app_enabled": true,
  "enabled_types": [
    "comment",
    "reaction",
    "mention",
    "activity_invite"
  ],
  "quiet_hours_start": "22:00:00",
  "quiet_hours_end": "08:00:00",
  "ghost_mode": false,
  "created_at": "2025-11-17T12:00:00Z",
  "updated_at": "2025-11-17T12:00:00Z"
}
```

**Field Descriptions**:
| Field | Type | Description |
|-------|------|-------------|
| email_enabled | boolean | Enable email notifications |
| push_enabled | boolean | Enable push notifications |
| in_app_enabled | boolean | Enable in-app notifications |
| enabled_types | array | List of enabled notification types |
| quiet_hours_start | time | Start of quiet hours (no notifications) |
| quiet_hours_end | time | End of quiet hours |
| ghost_mode | boolean | Premium only: disable profile_view notifications |

**Example**:
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:8006/api/v1/settings
```

---

#### `PATCH /api/v1/settings`
Update user's notification settings. All fields are optional - only send fields to update.

**Authentication**: JWT Bearer Token (required)

**Request Body** (all fields optional):
```json
{
  "email_enabled": false,
  "push_enabled": true,
  "in_app_enabled": true,
  "enabled_types": [
    "comment",
    "reaction",
    "mention"
  ],
  "quiet_hours_start": "23:00:00",
  "quiet_hours_end": "07:00:00",
  "ghost_mode": true
}
```

**Field Validation**:
- `enabled_types`: Must be valid notification types (see types below)
- `quiet_hours_start/end`: Format: HH:MM:SS (24-hour time)
- `ghost_mode`: Requires Premium subscription (validated against JWT token)

**Response**: 200 OK
```json
{
  "user_id": "uuid",
  "email_enabled": false,
  "push_enabled": true,
  "in_app_enabled": true,
  "enabled_types": ["comment", "reaction", "mention"],
  "quiet_hours_start": "23:00:00",
  "quiet_hours_end": "07:00:00",
  "ghost_mode": true,
  "created_at": "2025-11-17T12:00:00Z",
  "updated_at": "2025-11-17T14:30:00Z"
}
```

**Error Responses**:
- `403`: Ghost mode requires Premium subscription (if user is not premium)
- `422`: Validation error (invalid notification types, invalid time format)

**Examples**:
```bash
# Disable email notifications
curl -X PATCH \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"email_enabled": false}' \
  http://localhost:8006/api/v1/settings

# Update quiet hours
curl -X PATCH \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "quiet_hours_start": "22:00:00",
    "quiet_hours_end": "08:00:00"
  }' \
  http://localhost:8006/api/v1/settings

# Enable ghost mode (Premium only)
curl -X PATCH \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"ghost_mode": true}' \
  http://localhost:8006/api/v1/settings

# Update enabled notification types
curl -X PATCH \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled_types": ["comment", "reaction", "mention", "activity_invite"]
  }' \
  http://localhost:8006/api/v1/settings
```

---

## Data Models

### Notification Types

Valid values for `notification_type` field:

| Type | Description | Premium Only |
|------|-------------|--------------|
| `activity_invite` | Invitation to activity | No |
| `activity_reminder` | Activity reminder | No |
| `activity_update` | Activity details changed | No |
| `community_invite` | Community invitation | No |
| `new_member` | New community member | No |
| `new_post` | New community post | No |
| `comment` | Comment on content | No |
| `reaction` | Reaction to content | No |
| `mention` | User mention | No |
| `profile_view` | Profile view | **Yes** |
| `new_favorite` | New favorite | **Yes** |
| `system` | System notification | No |

**Premium-only notifications**: Users with `free` subscription level won't receive `profile_view` and `new_favorite` notifications.

---

### Notification Status

Valid values for `status` field:

| Status | Description |
|--------|-------------|
| `unread` | Not yet read by user |
| `read` | Read by user (read_at timestamp set) |
| `archived` | Archived/deleted by user (soft delete) |

---

### Target Types

Valid values for `target_type` field:

| Type | Description | Example |
|------|-------------|---------|
| `activity` | Activity/event | Activity invitation, reminder |
| `post` | Community post | New post, comment on post |
| `comment` | Comment | Reply to comment |
| `user` | User profile | Profile view, new follower |

---

### Subscription Levels

Extracted from JWT token `subscription_level` claim:

| Level | Features |
|-------|----------|
| `free` | Standard notifications only (no profile_view, new_favorite) |
| `club` | All notification types + ghost mode option |
| `premium` | All notification types + ghost mode option |

---

## Error Responses

All endpoints may return these standard error responses:

### 401 Unauthorized
Missing or invalid JWT token.

```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
Access denied (e.g., premium feature with free subscription).

```json
{
  "detail": "Ghost mode requires Premium subscription"
}
```

### 404 Not Found
Resource not found or doesn't belong to user.

```json
{
  "detail": "Notification not found"
}
```

### 422 Validation Error
Request validation failed.

```json
{
  "detail": [
    {
      "loc": ["body", "notification_type"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

### 503 Service Unavailable
Service unhealthy (database connection failed, etc.).

```json
{
  "status": "unhealthy",
  "database": "disconnected"
}
```

---

## Integration Examples

### Create Notification from Another Service

```python
import httpx
from typing import Optional

async def create_notification(
    user_id: str,
    notification_type: str,
    target_type: str,
    target_id: str,
    title: str,
    actor_user_id: Optional[str] = None,
    message: Optional[str] = None,
    payload: Optional[dict] = None
) -> dict:
    """Create notification via service-to-service call"""

    response = await httpx.post(
        "http://notifications-api:8000/api/v1/notifications",
        headers={
            "X-Service-Token": "shared-secret-token-change-in-production",
            "Content-Type": "application/json"
        },
        json={
            "user_id": user_id,
            "actor_user_id": actor_user_id,
            "notification_type": notification_type,
            "target_type": target_type,
            "target_id": target_id,
            "title": title,
            "message": message,
            "payload": payload
        },
        timeout=5.0
    )
    response.raise_for_status()
    return response.json()

# Example usage:
# New comment notification
await create_notification(
    user_id="post-author-uuid",
    actor_user_id="commenter-uuid",
    notification_type="comment",
    target_type="post",
    target_id="post-uuid",
    title="New comment on your post",
    message="Someone commented on your post",
    payload={"comment_text": "Great post!"}
)
```

---

### Fetch User Notifications

```python
import httpx
from typing import List, Dict

async def get_user_notifications(
    jwt_token: str,
    status: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict:
    """Fetch user's notifications"""

    params = {
        "limit": limit,
        "offset": offset
    }
    if status:
        params["status"] = status
    if type:
        params["type"] = type

    response = await httpx.get(
        "http://notifications-api:8000/api/v1/notifications",
        headers={"Authorization": f"Bearer {jwt_token}"},
        params=params,
        timeout=5.0
    )
    response.raise_for_status()
    return response.json()

# Example usage:
# Get unread comment notifications
notifications = await get_user_notifications(
    jwt_token="user-jwt-token",
    status="unread",
    type="comment",
    limit=50
)

print(f"Total unread comments: {notifications['pagination']['total']}")
for notif in notifications['notifications']:
    print(f"- {notif['title']} from {notif['actor']['username']}")
```

---

## Testing

### Generate Test JWT Token

```python
import jwt
from datetime import datetime, timedelta

def generate_test_token(
    user_id: str,
    email: str,
    subscription_level: str = "premium"
) -> str:
    """Generate JWT token for testing"""

    secret = "dev-secret-key-change-in-production"
    payload = {
        "sub": user_id,
        "email": email,
        "subscription_level": subscription_level,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, secret, algorithm="HS256")

# Generate token
token = generate_test_token(
    user_id="123e4567-e89b-12d3-a456-426614174000",
    email="test@example.com",
    subscription_level="premium"
)
print(f"Test token: {token}")
```

### Test Health Check

```bash
# Check API health
curl http://localhost:8006/health

# Expected response:
# {"status":"healthy","database":"connected"}
```

### Test Complete Flow

```bash
# 1. Generate test token
export TOKEN=$(python3 -c "
import jwt
from datetime import datetime, timedelta
secret = 'dev-secret-key-change-in-production'
payload = {
    'sub': '123e4567-e89b-12d3-a456-426614174000',
    'email': 'test@example.com',
    'subscription_level': 'premium',
    'exp': datetime.utcnow() + timedelta(days=1)
}
print(jwt.encode(payload, secret, algorithm='HS256'))
")

# 2. Get notifications
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8006/api/v1/notifications

# 3. Get unread count
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8006/api/v1/notifications/unread/count

# 4. Get settings
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8006/api/v1/settings

# 5. Update settings
curl -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email_enabled": false}' \
  http://localhost:8006/api/v1/settings
```

---

## Rate Limiting

*Currently not implemented - future enhancement*

Planned rate limits:
- User endpoints: 100 requests/minute per user
- Service endpoints: 1000 requests/minute per service

---

## Monitoring

### Metrics
- Prometheus metrics available at `/metrics` (future enhancement)
- Key metrics: request count, response time, error rate

### Logging
- Structured JSON logging with correlation IDs
- Logs aggregated in Loki (observability stack)
- Query logs: `{service_name="notifications-api"} |= "ERROR"`

### Health Monitoring
```bash
# Check service health
curl http://localhost:8006/health

# Expected responses:
# Healthy: {"status":"healthy","database":"connected"}
# Unhealthy: {"status":"unhealthy","database":"disconnected"} (503)
```

---

## Environment Configuration

Required environment variables:

```bash
# Database
DB_HOST=activity-postgres-db
DB_PORT=5432
DB_NAME=activitydb
DB_USER=postgres
DB_PASSWORD=postgres_secure_password_change_in_prod

# Authentication
JWT_SECRET=dev-secret-key-change-in-production  # MUST match auth-api
JWT_ALGORITHM=HS256
SERVICE_TOKEN=shared-secret-token-change-in-production

# Redis
REDIS_HOST=auth-redis
REDIS_PORT=6379
REDIS_DB=0

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=Notifications API
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=*
ENABLE_DOCS=true
```

---

## Production Checklist

Before deploying to production:

- [ ] Change `JWT_SECRET` to strong random string (32+ chars)
- [ ] Change `SERVICE_TOKEN` to secure random string
- [ ] Change `DB_PASSWORD` to secure password
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Set `LOG_LEVEL=INFO` or `WARNING`
- [ ] Configure proper `CORS_ORIGINS` (not `*`)
- [ ] Set `ENABLE_DOCS=false` (disable Swagger UI)
- [ ] Setup monitoring alerts (Grafana/Prometheus)
- [ ] Configure log aggregation
- [ ] Implement rate limiting
- [ ] Setup database connection pooling monitoring
- [ ] Configure automated backups

---

## Additional Resources

- **Swagger UI**: http://localhost:8006/docs
- **ReDoc**: http://localhost:8006/redoc
- **OpenAPI JSON**: http://localhost:8006/openapi.json
- **Service Documentation**: See CLAUDE.md in repository root
- **Database Schema**: See sqlschema.sql
- **Migration Guide**: See MIGRATION_TO_CENTRAL_DB.md

---

## Support

For issues or questions:
- Check service logs: `docker compose logs -f notifications-api`
- Review CLAUDE.md for troubleshooting
- Check database connectivity: `docker exec activity-postgres-db psql -U postgres -d activitydb -c "SELECT 1;"`
- Verify infrastructure running: `docker ps | grep activity-postgres-db`

---

**Last Updated**: 2025-11-17
**API Version**: 1.0.0
**Service Port**: 8006 (external) → 8000 (internal)
