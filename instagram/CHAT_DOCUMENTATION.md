# Chat System Documentation

## Overview
The chat system allows users to send and receive persistent messages that are stored in the database. Messages are fetched and displayed with real-time polling every 2 seconds.

## Architecture

### Backend
**Models** (`Chat/models.py`)
```python
class Message(models.Model):
    sender = ForeignKey(User)           # Who sent it
    recipient = ForeignKey(User)        # Who receives it
    content = TextField(max_length=1000) # Message body
    created_at = DateTimeField()         # Timestamp
    is_read = BooleanField(default=False) # Read status
```

**Views** (`Chat/views.py`)

1. **chat_with(request, user_uuid)**
   - Renders the chat room template
   - Marks all unread messages from target as read
   - Returns: HTML page with target user info

2. **send_message(request, user_uuid)**
   - POST endpoint to save a new message
   - Accepts JSON: `{content: "message text"}`
   - Validates: not empty, max 1000 chars
   - Returns: `{success: true, id, sender, content, created_at, is_read}`

3. **get_messages(request, user_uuid)**
   - GET endpoint to fetch conversation history
   - Returns all messages between current user and target (both directions)
   - Each message includes: `{id, sender, sender_uuid, content, created_at, is_from_me}`
   - Ordered by created_at (oldest first)

**URLs** (`Chat/urls.py`)
```
/chat/<user_uuid>/          → chat_with view (GET)
/chat/<user_uuid>/send/     → send_message view (POST)
/chat/<user_uuid>/get/      → get_messages view (GET)
```

### Frontend
**Template** (`templates/chat/room.html`)

HTML Structure:
- Chat header with target user info and profile link
- Messages container (scrollable)
- Input textarea + send button

JavaScript Functionality:
1. **loadMessages()** - Fetches all messages from `/chat/<uuid>/get/` endpoint
2. **sendMessage()** - POSTs new message to `/chat/<uuid>/send/`
3. **appendMessage()** - Adds message to DOM with formatting
4. **setInterval(loadMessages, 2000)** - Auto-refresh messages every 2 seconds

Message Display:
- Sent messages: right-aligned, gradient background (blue-purple)
- Received messages: left-aligned, white background with border
- Each message shows: text, timestamp (HH:MM format)
- Smooth fade-in animation on new messages

## Flow Diagram

```
User A (Profile View)
  ↓
Click "💬 Poruka" button
  ↓
GET /chat/<User B uuid>/
  ↓
Render chat/room.html with target=User B
  ↓
JavaScript loads messages
  ↓
GET /chat/<User B uuid>/get/
  ↓
Load previous messages
  ↓
Display message history
  ↓
User A types message
  ↓
Press Enter or click Send
  ↓
POST /chat/<User B uuid>/send/ with {content: "..."}
  ↓
Message saved to database
  ↓
Append to UI (optimistic)
  ↓
Auto-fetch updates every 2 seconds
  ↓
GET /chat/<User B uuid>/get/
  ↓
Display new messages from User B
```

## Database Queries

**Save message:**
```python
Message.objects.create(sender=user_a, recipient=user_b, content="Hello")
```

**Fetch conversation:**
```python
Message.objects.filter(
    Q(sender=user_a, recipient=user_b) | 
    Q(sender=user_b, recipient=user_a)
).order_by('created_at')
```

**Mark as read:**
```python
Message.objects.filter(
    sender=user_b, 
    recipient=user_a, 
    is_read=False
).update(is_read=True)
```

## Frontend JavaScript Reference

### Configuration
```javascript
const targetUuid = '{{ target.user_uuid }}';  // From Django template
const pollInterval = 2000;  // milliseconds
```

### Main Functions

**loadMessages()**
- Endpoint: `GET /chat/{targetUuid}/get/`
- Response: `{messages: [{id, sender, sender_uuid, content, created_at, is_from_me}, ...]}`
- Behavior: Clears container, renders all messages

**sendMessage()**
- Endpoint: `POST /chat/{targetUuid}/send/`
- Payload: `JSON.stringify({content: "text"})`
- Headers: `{'X-CSRFToken': csrf_token, 'Content-Type': 'application/json'}`
- Behavior: Disables send button, sends message, fetches updated history

**appendMessage(text, fromMe, timestamp)**
- Appends message to DOM
- Classes: `message` + `me` (sent) or `them` (received)
- Auto-scrolls to bottom
- Shows timestamp

## Usage Example

### Sending a message
```javascript
// In browser console
const uuid = 'target-user-uuid-here';
fetch(`/chat/${uuid}/send/`, {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrf_token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({content: 'Hello!'})
})
.then(r => r.json())
.then(data => console.log(data));
```

### Fetching messages
```javascript
const uuid = 'target-user-uuid-here';
fetch(`/chat/${uuid}/get/`)
  .then(r => r.json())
  .then(data => console.log(data.messages));
```

## Security Considerations

✅ **Implemented:**
- `@login_required` on all views - only authenticated users can chat
- CSRF token validation on POST requests
- Message content length validation (max 1000 chars)
- Empty message rejection
- User identity validation (can't chat with yourself)
- All messages indexed by sender.user_uuid (UUID, not integer ID)

⚠️ **Future Improvements:**
- Rate limiting on message sends
- Blocking users
- Message deletion
- Message editing
- Typing indicators
- WebSocket for real-time updates (instead of polling)

## Styling Classes

```css
.chat-card           /* Main container */
.chat-header         /* Header with user info */
.chat-target         /* User avatar + name + email */
.chat-messages       /* Message container (scrollable) */
.message             /* Individual message */
.message.me          /* Sent message (right-aligned, gradient) */
.message.them        /* Received message (left-aligned, white) */
.message-time        /* Timestamp below message */
.chat-input          /* Textarea + button */
.empty               /* Empty state message */
```

## Troubleshooting

**Messages not loading**
- Check browser console for fetch errors
- Verify target user UUID is valid
- Ensure logged in (check `/admin/`)
- Run `python manage.py migrate` to create Message table

**Send button not working**
- Check CSRF token exists: `document.querySelector('input[name="csrfmiddlewaretoken"]')`
- Check JSON payload format: `{content: "text"}`
- Check response for `success: true` field

**Messages not persisting**
- Verify Chat app is in INSTALLED_APPS
- Check database migrations ran: `python manage.py showmigrations Chat`
- Try `python manage.py migrate Chat` explicitly

**Real-time updates slow**
- Polling interval is 2 seconds (change in room.html: `setInterval(loadMessages, 2000)`)
- For instant updates, implement WebSocket/Channels
