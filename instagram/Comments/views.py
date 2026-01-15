# 🇭🇷 Comments/views.py - Upravljanje komentarima na objavama
# ========================================================================================================
# Svrha: AJAX API-ji za dodavanje komentara i dohvaćanje svih komentara na objavu
# Funkcionalnosti:
#   - add(): Stvara novi komentar na objavu (s opcionalnom reply mogućnosti)
#   - get(): Dohvaća sve komentare na objavu sa odgovorima
#   - like(): Placeholder za like na komentar
#
# 📝 Rute:
#   - POST /posts/<id>/comment/add → Dodaj komentar (JSON)
#   - GET /posts/<id>/comment/get → Dohvati sve komentare (JSON)
#
# 💬 Komentari:
#   - Mogu biti top-level (parent=None) ili odgovori (parent=neki drugi komentar)
#   - Max 300 znakova
#   - Prate se like-ovi kroz CommentLike model
#
# 🔒 Sigurnost: @login_required za dodavanje, @require_http_methods za методе
# ========================================================================================================

from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .models import CommentModel
from Posts.models import PostModel


@require_http_methods(["POST"])
@login_required
def add(request, id):
    # 🔹 add() - Stvara novi komentar na objavu
    #    
    #    📝 Parametri:
    #       - POST 'content': Tekst komentara (iz forme ili JSON)
    #       - POST 'parent_id': (opciono) ID parent komentara ako je ovo reply
    #    
    #    💼 Kako radi:
    #       1. Dohvati objavu po UUID-u
    #       2. Validiraj da 'content' nije prazan
    #       3. Ako postoji parent_id, pronađi parent komentar
    #       4. Spremi novi komentar u bazu
    #    
    #    💾 Što se sprema:
    #       - author = request.user
    #       - content = korisnikov tekst
    #       - post = objava na koju se komentiraj
    #       - parent = parent komentar (ako je reply) ili None
    #       - created_at = automatski
    #    
    #    📤 Odgovor:
    #       - JSON s detaljima novog komentara (id, author, content, created_at itd.)
    #    
    # 🔍 Dohvati content iz POST-a (može biti 'content' ili 'comment')
    content = request.POST.get('content') or request.POST.get('comment')
    parent_id = request.POST.get('parent_id')
    # 📌 Prona postavu po UUID-u
    post = get_object_or_404(PostModel, uuid_field=id)

    # 🛡️ Validacija sadržaja
    if not content:
        return JsonResponse({'error': 'Nedostaje sadržaj komentara'}, status=400)

    # 👉 Ako je ovo reply, pronađi parent komentar
    parent = None
    if parent_id:
        try:
            parent = CommentModel.objects.get(id=int(parent_id), post=post)
        except Exception:
            return JsonResponse({'error': 'Nevalidan parent komentar'}, status=400)

    # 💾 Kreiraj i spremi komentar
    c = CommentModel.objects.create(author=request.user, content=content, post=post, parent=parent)

    # 📤 Vrati JSON s detaljima
    return JsonResponse({
        'id': c.id,
        'author': c.author.username,
        'author_uuid': str(c.author.user_uuid),
        'content': c.content,
        'created_at': c.created_at.strftime('%d.%m.%Y %H:%M') if c.created_at else '',
        'parent_id': c.parent.id if c.parent else None
    })


@require_http_methods(["GET"])
def get(request, id):
    # 🔹 get() - Dohvaća sve komentare na objavu (top-level + replies)
    #    
    #    💼 Kako radi:
    #       1. Pronađi objavu po UUID-u
    #       2. Dohvati sve top-level komentare (parent=None)
    #       3. Za svaki top-level komentar, dohvati sve replies (nested)
    #       4. Prebrojaj like-e za svaki komentar
    #    
    #    📝 Što se vraća:
    #       - JSON niz sa svim komentarima
    #       - Svaki komentar ima: id, author, content, created_at, likes, liked (od trenutnog korisnika), replies
    #       - Replies su ugnježđeni u replies array
    #    
    #    👤 Like-ovi:
    #       - Broj like-a prebrojava iz CommentLike modela
    #       - 'liked' = True ako je request.user dao like (za UI button state)
    #    
    # 🔌 Dinamički import za izbježivanje kružnih uvoza
    from Interactions.models import CommentLike

    # 📌 Pronađi objavu po UUID-u
    post = get_object_or_404(PostModel, uuid_field=id)

    # 📝 Dohvati sve top-level komentare (parent=None), sortirane po vremenu
    qs = CommentModel.objects.filter(post=post, parent__isnull=True).order_by('created_at')
    comments = []
    
    for c in qs:
        # 👶 Dohvati sve replies (odgovore) na ovaj top-level komentar
        replies = []
        for r in c.replies.all().order_by('created_at'):
            # ❤️ Prebrojaj like-e na reply
            r_likes = CommentLike.objects.filter(comment=r).count()
            r_user_liked = False
            # 🔍 Provjeri je li request.user dao like na reply
            if request.user.is_authenticated:
                r_user_liked = CommentLike.objects.filter(comment=r, user=request.user).exists()
            replies.append({
                'id': r.id,
                'author': r.author.username,
                'author_uuid': str(r.author.user_uuid),
                'content': r.content,
                'created_at': r.created_at.strftime('%d.%m.%Y %H:%M') if r.created_at else '',
                'likes': r_likes,
                'liked': r_user_liked,
                'parent_id': r.parent.id if r.parent else None
            })

        # ❤️ Prebrojaj like-e na top-level komentar
        c_likes = CommentLike.objects.filter(comment=c).count()
        c_user_liked = False
        # 🔍 Provjeri je li request.user dao like
        if request.user.is_authenticated:
            c_user_liked = CommentLike.objects.filter(comment=c, user=request.user).exists()

        comments.append({
            'id': c.id,
            'author': c.author.username,
            'author_uuid': str(c.author.user_uuid),
            'content': c.content,
            'created_at': c.created_at.strftime('%d.%m.%Y %H:%M') if c.created_at else '',
            'likes': c_likes,
            'liked': c_user_liked,
            'replies': replies  # 👶 Ugnježđeni odgovori
        })

    return JsonResponse({'comments': comments})


@require_http_methods(["POST"])
@login_required
def like(request, id):
    # 🔹 like() - TODO: Like na komentar
    #    
    #    📝 Svrha: Trebam implementirati toggle like-a za komentare
    #    
    pass
