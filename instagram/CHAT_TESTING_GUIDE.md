# Chat Testing Guide

## Prerequisites
1. Database migrations completed: `python manage.py migrate`
2. Django server running: `python manage.py runserver`
3. At least 2 user accounts created

## Step-by-Step Testing

### Test 1: Send First Message

**Setup:**
- Log in as User A
- Go to User B's profile

**Steps:**
1. On User B's profile, click the "💬 Poruka" button
2. Type: "Hello from User A"
3. Press Enter or click "Pošalji"
4. Verify message appears on screen (right side, gradient background)
5. Check database: `python manage.py shell`
   ```python
   from Chat.models import Message
   Message.objects.last()  # Should show your message
   ```

**Expected Result:** ✅ Message saved and displayed

---

### Test 2: Receive Message (Reverse Direction)

**Setup:**
- Log in as User B
- Go to User A's profile

**Steps:**
1. Click "💬 Poruka" to User A's chat
2. Verify you see User A's message from Test 1
3. Type: "Hello back User A"
4. Send message
5. Switch back to User A's chat
6. Verify you see User B's reply within 2 seconds

**Expected Result:** ✅ Bidirectional messaging works

---

### Test 3: Message Persistence

**Setup:**
- Both users have sent messages

**Steps:**
1. As User A, close the chat (navigate away)
2. Go to another page
3. Go back to User B's profile
4. Click "💬 Poruka"
5. Verify all previous messages load (full history)

**Expected Result:** ✅ Messages persist in database

---

### Test 4: Empty Message Validation

**Setup:**
- Open any chat

**Steps:**
1. Leave textarea empty
2. Click "Pošalji"
3. Verify nothing happens (error handled)
4. Try sending only spaces

**Expected Result:** ✅ Empty messages rejected

---

### Test 5: Message Length Limit

**Setup:**
- Open any chat

**Steps:**
1. Generate 1001 character string in console:
   ```javascript
   const longText = 'a'.repeat(1001);
   document.getElementById('message-input').value = longText;
   ```
2. Click "Pošalji"
3. Should see error in response

**Expected Result:** ✅ Messages > 1000 chars rejected

---

### Test 6: Real-time Polling

**Setup:**
- Two browser windows/tabs open
- Both logged in as different users
- Both in same chat room

**Steps:**
1. In Window A, send: "Test message from A"
2. Observe Window B
3. Within 2 seconds, message should appear in Window B
4. In Window B, send: "Reply from B"
5. Observe Window A gets update within 2 seconds

**Expected Result:** ✅ Polling fetches new messages every 2 seconds

---

### Test 7: Profile Link in Chat

**Setup:**
- Open chat with any user

**Steps:**
1. In chat header, click the username or "Pogledaj profil" button
2. Verify redirects to user's profile page
3. Go back to chat
4. Verify still in same chat room

**Expected Result:** ✅ Profile link works

---

### Test 8: Multiple Conversations

**Setup:**
- 3+ user accounts (A, B, C)
- All logged in from different instances/incognito

**Steps:**
1. As User A, send message to User B
2. As User A, open User C's chat
3. Send message to User C
4. Verify User B's chat still has only User B's messages
5. Verify User C's chat still has only User C's messages
6. As User B, verify only messages from User A

**Expected Result:** ✅ Conversations isolated per recipient

---

### Test 9: Message Formatting

**Steps:**
1. Send message with newlines:
   ```
   Line 1
   Line 2
   Line 3
   ```
2. Send message with special characters: `!@#$%^&*()`
3. Send message with emoji: `🎉 Hello 👋`
4. Send very short message: `Hi`

**Expected Result:** ✅ All formats preserved and displayed correctly

---

### Test 10: Keyboard Shortcuts

**Setup:**
- Open chat

**Steps:**
1. Type message
2. Press Shift+Enter (should newline in textarea)
3. Verify newline added, not sent
4. Press Enter without Shift
5. Verify message sent

**Expected Result:** ✅ Enter sends, Shift+Enter newlines

---

## Database Inspection

### Check all messages
```python
python manage.py shell
from Chat.models import Message
from Users.models import User

# All messages
Message.objects.all()

# Messages between two users
user_a = User.objects.first()
user_b = User.objects.last()
Message.objects.filter(sender=user_a, recipient=user_b)

# Unread messages
Message.objects.filter(is_read=False)

# Count
Message.objects.count()
```

### Clear messages for testing
```python
Message.objects.all().delete()
```

---

## Performance Testing

### High-volume message test
```python
from Chat.models import Message
from Users.models import User
import time

user_a = User.objects.first()
user_b = User.objects.last()

start = time.time()
for i in range(100):
    Message.objects.create(
        sender=user_a,
        recipient=user_b,
        content=f"Test message {i}"
    )
elapsed = time.time() - start
print(f"100 messages created in {elapsed:.2f}s")
```

---

## Common Issues & Solutions

### Issue: Messages not sending
**Solution:**
1. Check browser console (F12) for errors
2. Verify CSRF token exists: 
   ```javascript
   document.querySelector('input[name="csrfmiddlewaretoken"]')
   ```
3. Check Content-Type header is 'application/json'
4. Verify endpoint: `/chat/<uuid>/send/`

### Issue: Messages not loading
**Solution:**
1. Check `/chat/<uuid>/get/` response in Network tab
2. Verify database has messages: `Message.objects.count()`
3. Check user UUID format: should be UUID, not integer

### Issue: Polling too slow
**Solution:**
1. Reduce polling interval in room.html:
   ```javascript
   setInterval(loadMessages, 1000);  // 1 second instead of 2
   ```
2. Or implement WebSocket for real-time updates

### Issue: Messages appearing on wrong side
**Solution:**
1. Check `is_from_me` field in response
2. Verify current user != message sender

---

## Load Testing

### Simulate heavy usage
```bash
# Terminal 1: Run server
python manage.py runserver

# Terminal 2: Load test (requires Apache Bench)
ab -n 1000 -c 10 "http://localhost:8000/chat/<uuid>/get/"

# Or use Python requests library
python -c "
import requests
import concurrent.futures
import time

uuid = 'target-uuid-here'
csrf = 'token-from-browser'

def fetch():
    return requests.get(f'http://localhost:8000/chat/{uuid}/get/')

start = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    futures = [ex.submit(fetch) for _ in range(100)]
    results = [f.result() for f in futures]
elapsed = time.time() - start
print(f'100 requests in {elapsed:.2f}s')
print(f'Success: {sum(1 for r in results if r.status_code == 200)}/100')
"
```

---

## Browser Console Testing

### Quick message send
```javascript
const uuid = 'target-uuid-here';
const csrf = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

fetch(`/chat/${uuid}/send/`, {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrf,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({content: 'Console test message'})
})
.then(r => r.json())
.then(d => console.log('Response:', d))
.catch(e => console.error('Error:', e));
```

### Quick message fetch
```javascript
const uuid = 'target-uuid-here';

fetch(`/chat/${uuid}/get/`)
  .then(r => r.json())
  .then(d => {
    console.log('Messages:', d.messages);
    console.log('Count:', d.messages.length);
  })
  .catch(e => console.error('Error:', e));
```

---

## Checklist

- [ ] Database migrated
- [ ] Server running
- [ ] Can create accounts
- [ ] Can navigate to user profiles
- [ ] Chat button appears on profiles
- [ ] Can send messages
- [ ] Messages display correctly
- [ ] Messages persist on reload
- [ ] Real-time polling works
- [ ] Profile link in chat works
- [ ] Multiple conversations isolated
- [ ] Keyboard shortcuts work (Enter, Shift+Enter)
- [ ] Validation rejects empty messages
- [ ] Validation rejects long messages
- [ ] Performance acceptable (< 500ms per request)

---

## Performance Benchmarks

Target metrics:
- Send message: < 200ms
- Fetch messages: < 100ms (for < 100 messages)
- Page load: < 1s
- Polling interval: 2s (configurable)

If performance is poor:
1. Add database indexes: `Message.objects.filter(...).count()`
2. Implement pagination for old messages
3. Use WebSocket for real-time (replace polling)
4. Implement read receipts more efficiently
