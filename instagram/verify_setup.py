#!/usr/bin/env python
"""
Verification script for Instagram Clone setup
Run: python verify_setup.py
"""

import os
import sys
from pathlib import Path

# Add django to path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram.settings')

try:
    import django
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.apps import apps
from django.db import connection

print("\n" + "="*50)
print("INSTAGRAM CLONE - SETUP VERIFICATION")
print("="*50)

# Check installed apps
print("\n📦 Installed Apps:")
installed_apps = [app.name.split('.')[-1] for app in apps.get_app_configs()]
required_apps = ['Posts', 'Users', 'Comments', 'Interactions', 'Chat']
for app in required_apps:
    status = "✅" if app in installed_apps else "❌"
    print(f"  {status} {app}")

# Check models
print("\n📋 Models:")
models_to_check = {
    'Posts': ['PostModel'],
    'Users': ['User'],
    'Comments': ['CommentModel'],
    'Interactions': ['Like', 'Dislike', 'CommentLike', 'Follow'],
    'Chat': ['Message']
}

for app_name, model_names in models_to_check.items():
    try:
        app = apps.get_app_config(app_name)
        for model_name in model_names:
            try:
                model = app.get_model(model_name)
                print(f"  ✅ {app_name}.{model_name}")
            except LookupError:
                print(f"  ❌ {app_name}.{model_name} - NOT FOUND")
    except LookupError:
        print(f"  ❌ App '{app_name}' not found")

# Check database tables
print("\n🗄️  Database Tables:")
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
required_tables = {
    'chat_message': 'Chat messages',
    'interactions_like': 'Post likes',
    'interactions_dislike': 'Post dislikes',
    'interactions_commentlike': 'Comment likes',
    'interactions_follow': 'User follows',
    'comments_commentmodel': 'Comments',
    'posts_postmodel': 'Posts',
    'users_user': 'Custom users'
}

for table, description in required_tables.items():
    status = "✅" if table in tables else "⚠️ "
    print(f"  {status} {table} ({description})")

# Check templates
print("\n📄 Templates:")
templates = {
    'templates/account/profile.html': 'User profile page',
    'templates/chat/room.html': 'Chat room',
    'templates/posts/list.html': 'Posts feed',
    'templates/posts/create.html': 'Create post',
    'templates/posts/list_detail.html': 'Post detail'
}

for path, description in templates.items():
    full_path = Path(path)
    status = "✅" if full_path.exists() else "❌"
    print(f"  {status} {path}")

# Check URLs
print("\n🔗 URL Patterns:")
from django.urls import get_resolver
from django.urls.exceptions import Resolver404

urlpatterns = get_resolver().url_patterns
url_names = [p.name for p in urlpatterns if hasattr(p, 'name')]

required_urls = {
    'posts': 'Posts app',
    'users': 'Users app',
    'chat': 'Chat app'
}

for url_name, description in required_urls.items():
    status = "✅" if url_name in url_names else "❌"
    print(f"  {status} {url_name} ({description})")

# Check views
print("\n🎯 Views:")
try:
    from Posts.views import list_view, detail_view, create_view
    print("  ✅ Posts.views")
except ImportError as e:
    print(f"  ❌ Posts.views - {e}")

try:
    from Users.views import me, profile
    print("  ✅ Users.views")
except ImportError as e:
    print(f"  ❌ Users.views - {e}")

try:
    from Chat.views import chat_with, send_message, get_messages
    print("  ✅ Chat.views")
except ImportError as e:
    print(f"  ❌ Chat.views - {e}")

try:
    from Comments.views import add, get
    print("  ✅ Comments.views")
except ImportError as e:
    print(f"  ❌ Comments.views - {e}")

try:
    from Interactions.views import toggle_like, toggle_dislike, toggle_comment_like, toggle_follow
    print("  ✅ Interactions.views")
except ImportError as e:
    print(f"  ❌ Interactions.views - {e}")

# Summary
print("\n" + "="*50)
print("✅ VERIFICATION COMPLETE")
print("="*50)
print("\n📚 Documentation:")
print("  - SETUP_INSTRUCTIONS.md - Full setup guide")
print("  - CHAT_DOCUMENTATION.md - Chat system details")
print("\n🚀 Quick start:")
print("  1. python manage.py migrate (if not done)")
print("  2. python manage.py runserver")
print("  3. Go to http://localhost:8000")
print("\n💡 Next steps:")
print("  - Create a user account or login")
print("  - Create posts with images")
print("  - Visit other user profiles")
print("  - Send chat messages")
print("  - Like/dislike posts and comments")
