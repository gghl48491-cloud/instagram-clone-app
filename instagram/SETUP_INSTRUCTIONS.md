# Instagram Clone - Setup Instructions

## Recent Updates

### 1. ✅ Profile UI Redesign
- Modern hero section with gradient background and large avatar
- Stats section showing posts, followers, following, comments
- Tabbed interface for Posts, Comments, Followers, Following
- Grid layout for posts with image previews
- User list with profile links
- Responsive mobile design

**File:** `templates/account/profile.html`

### 2. ✅ Persistent Chat System
- Messages saved to database with sender, recipient, content, timestamp
- Fetch existing message history on page load
- Send new messages via AJAX POST to `/chat/<uuid>/send/`
- Auto-fetch new messages every 2 seconds
- Distinguish sent vs received messages with styling
- Timestamps for each message
- Message counter and empty state

**Files:**
- `Chat/models.py` - Message model with FK to User
- `Chat/views.py` - chat_with(), send_message(), get_messages() endpoints
- `Chat/urls.py` - URL routing for chat operations
- `templates/chat/room.html` - Chat UI with AJAX integration

## Database Setup

Run these commands to initialize the database:

```bash
cd /path/to/instagram
python manage.py makemigrations
python manage.py migrate
```

This will create tables for:
- Message (Chat app)
- Follow, Like, Dislike, CommentLike (Interactions app)
- Comment (Comments app)
- All other app models

## API Endpoints

### Chat Endpoints
- `GET /chat/<user_uuid>/` - Load chat view with message history
- `POST /chat/<user_uuid>/send/` - Send message (JSON: `{content: "..."}`)
- `GET /chat/<user_uuid>/get/` - Fetch all messages in conversation

### Other Endpoints
- `POST /posts/<uuid>/toggle_like/` - Like/unlike a post
- `POST /posts/<uuid>/toggle_dislike/` - Dislike/like a post
- `POST /posts/<uuid>/add_comment/` - Add comment or reply
- `GET /posts/<uuid>/get_comments/` - Fetch comments with replies
- `POST /comments/<comment_id>/toggle_like/` - Like/unlike a comment
- `POST /users/<user_uuid>/toggle_follow/` - Follow/unfollow user

## Features Implemented

✅ User Authentication & Profiles
- Custom User model with UUID routing
- Profile image upload with hover preview
- Public profile page with user stats
- Follow/unfollow system

✅ Posts & Comments
- Create, edit, delete posts with images
- Comments on posts
- One-level nested replies to comments
- Comment editing

✅ Interactions
- Like/dislike posts (mutually exclusive)
- Like comments
- Like comment replies
- Follow/unfollow users

✅ Chat System
- Persistent message storage in database
- Real-time message fetching (2s polling)
- Message history on load
- Sent/received message distinction
- User profile link in chat header

## Known Limitations

- Chat uses polling (2s interval) instead of WebSocket
- One-level nested replies (no deep threading)
- Like/dislike counts shown for posts and comments only

## Styling

Uses CSS variables for theming:
- `--primary-color` - Main accent (default: #3b82f6)
- `--secondary-color` - Secondary accent (default: #8b5cf6)
- `--bg-color` - Light background
- `--text-primary` - Main text color
- `--text-secondary` - Secondary text color
- `--border-color` - Border color
- `--shadow-md`, `--shadow-lg` - Shadow effects

## Next Steps

1. **Test Chat**: Go to any user profile and click "💬 Poruka" to open chat
2. **Send Messages**: Type in the textarea and press Enter or click "Pošalji"
3. **View Profile**: Click on any username to view their public profile
4. **Follow Users**: Click "+ Prati" to follow/unfollow
5. **Like Posts**: Click thumbs up/down on posts in the feed

## Mobile Support

All pages are responsive and work on:
- Desktop (1920px+)
- Tablet (768px - 1024px)
- Mobile (below 768px)

## Static Files

If styles don't load:
```bash
python manage.py collectstatic
```

Then restart the development server:
```bash
python manage.py runserver
```
