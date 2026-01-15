# 🇭🇷 Interactions/views.py - Upravljanje interakcijama (like, dislike, follow)
# ========================================================================================================
# Svrha: AJAX API-ji za korisničke interakcije (like/dislike objava, follow korisnika)
# Funkcionalnosti:
#   - toggle_like(): Like/unlike objavu
#   - toggle_dislike(): Dislike/undislike objavu
#   - toggle_comment_like(): Like/unlike komentar
#   - toggle_follow(): Follow/unfollow korisnika
#
# 📝 Rute:
#   - POST /posts/<id>/like → Toggle like na objavu (JSON)
#   - POST /posts/<id>/dislike → Toggle dislike na objavu (JSON)
#   - POST /posts/comment/<id>/like → Toggle like na komentar (JSON)
#   - POST /users/<uuid>/follow → Toggle follow korisnika (JSON)
#
# 📊 Like/Dislike logika:
#   - Like i Dislike su međusobno isključivi (ne možeš oba istovremeno)
#   - Klik na like → Uklanja dislike ako postoji
#   - Klik na dislike → Uklanja like ako postoji
#
# 👥 Follow logika:
#   - Follow kreira relaciju između follower i following korisnika
#   - Klik na follow → Kreira ili briše Follow objekt
#   - Sprječava self-follow
#
# 🔒 Sigurnost: @login_required, @require_http_methods za POST
# ========================================================================================================

from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from Posts.models import PostModel
from .models import Like, Dislike, CommentLike, Follow


@require_http_methods(["POST"])
@login_required
def toggle_like(request, id):
    # 🔹 toggle_like() - Toggle like na objavu
    #    
    #    💼 Kako radi:
    #       1. Ako korisnik ima dislike na ovu objavu → Obriši dislike
    #       2. Ako korisnik ima like → Obriši ga (unlike)
    #       3. Ako korisnik nema like → Kreiraj ga (like)
    #    
    #    📊 Vraćeni podaci:
    #       - liked: True/False (je li korisnik dao like)
    #       - likes: Broj like-a na objavu
    #       - dislikes: Broj dislike-a na objavu
    #    
    post = get_object_or_404(PostModel, uuid_field=id)

    # ❌ Ako korisnik ima dislike, obriši ga (like i dislike su međusobno isključivi)
    from .models import Dislike, CommentLike
    Dislike.objects.filter(user=request.user, post=post).delete()

    # ✅ Toggle like
    existing = Like.objects.filter(user=request.user, post=post).first()
    if existing:
        # 👎 Korisnik već ima like → Obriši ga (unlike)
        existing.delete()
        liked = False
    else:
        # 👍 Korisnik nema like → Kreiraj ga
        Like.objects.create(user=request.user, post=post)
        liked = True

    # 📊 Prebrojaj like-e i dislike-e na objavu
    likes_count = Like.objects.filter(post=post).count()
    dislikes_count = Dislike.objects.filter(post=post).count()

    return JsonResponse({'liked': liked, 'likes': likes_count, 'dislikes': dislikes_count})


@require_http_methods(["POST"])
@login_required
def toggle_dislike(request, id):
    # 🔹 toggle_dislike() - Toggle dislike na objavu
    #    
    #    💼 Kako radi:
    #       1. Ako korisnik ima like na ovu objavu → Obriši like
    #       2. Ako korisnik ima dislike → Obriši ga (undislike)
    #       3. Ako korisnik nema dislike → Kreiraj ga (dislike)
    #    
    #    📊 Vraćeni podaci:
    #       - disliked: True/False (je li korisnik dao dislike)
    #       - likes: Broj like-a na objavu
    #       - dislikes: Broj dislike-a na objavu
    #    
    post = get_object_or_404(PostModel, uuid_field=id)

    # ❌ Ako korisnik ima like, obriši ga (dislike i like su međusobno isključivi)
    Like.objects.filter(user=request.user, post=post).delete()

    # 👎 Toggle dislike
    existing = Dislike.objects.filter(user=request.user, post=post).first()
    if existing:
        # Korisnik već ima dislike → Obriši ga (undislike)
        existing.delete()
        disliked = False
    else:
        # Korisnik nema dislike → Kreiraj ga
        Dislike.objects.create(user=request.user, post=post)
        disliked = True

    # 📊 Prebrojaj like-e i dislike-e na objavu
    likes_count = Like.objects.filter(post=post).count()
    dislikes_count = Dislike.objects.filter(post=post).count()

    return JsonResponse({'disliked': disliked, 'likes': likes_count, 'dislikes': dislikes_count})


@require_http_methods(["POST"])
@login_required
def toggle_comment_like(request, comment_id):
    # 🔹 toggle_comment_like() - Toggle like na komentar
    #    
    #    💼 Kako radi:
    #       1. Pronađi komentar po ID-u
    #       2. Ako korisnik ima like na komentar → Obriši ga
    #       3. Ako korisnik nema like → Kreiraj ga
    #    
    #    📊 Vraćeni podaci:
    #       - liked: True/False (je li korisnik dao like)
    #       - likes: Broj like-a na komentar
    #    
    # 🔌 Dinamički import za izbježivanje kružnih uvoza
    from Comments.models import CommentModel
    comment = get_object_or_404(CommentModel, id=comment_id)

    # ✅ Toggle like
    existing = CommentLike.objects.filter(user=request.user, comment=comment).first()
    if existing:
        # Korisnik već ima like → Obriši ga
        existing.delete()
        liked = False
    else:
        # Korisnik nema like → Kreiraj ga
        CommentLike.objects.create(user=request.user, comment=comment)
        liked = True

    # 📊 Prebrojaj like-e na komentar
    likes_count = CommentLike.objects.filter(comment=comment).count()

    return JsonResponse({'liked': liked, 'likes': likes_count})


@require_http_methods(["POST"])
@login_required
def toggle_follow(request, user_uuid):
    # 🔹 toggle_follow() - Toggle follow na korisnika
    #    
    #    💼 Kako radi:
    #       1. Pronađi korisnika po UUID-u
    #       2. Sprječava self-follow (ne možeš pratiti sebe)
    #       3. Ako korisnik već prati → Obriši follow
    #       4. Ako korisnik ne prati → Kreiraj follow
    #    
    #    📊 Vraćeni podaci:
    #       - following: True/False (je li korisnik sada following)
    #       - followers: Broj follower-a na ciljanog korisnika
    #       - following_count: Broj korisnika koje trenutni korisnik prati
    #    
    # 🔌 Dinamički import za izbježivanje kružnih uvoza
    from Users.models import User as AppUser
    target = get_object_or_404(AppUser, user_uuid=user_uuid)

    # 🚫 Sprječavanje self-follow
    if target == request.user:
        return JsonResponse({'error': 'Nije moguće pratiti sebe'}, status=400)

    # ✅ Toggle follow
    existing = Follow.objects.filter(follower=request.user, following=target).first()
    if existing:
        # Korisnik već prati → Obriši follow (unfollow)
        existing.delete()
        following = False
    else:
        # Korisnik ne prati → Kreiraj follow
        Follow.objects.create(follower=request.user, following=target)
        following = True

    # 📊 Prebrojaj follower-e
    followers_count = Follow.objects.filter(following=target).count()
    following_count = Follow.objects.filter(follower=target).count()

    return JsonResponse({'following': following, 'followers': followers_count, 'following_count': following_count})
