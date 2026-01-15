# 🇭🇷 Users/views.py - Upravljanje korisničkim profilima
# ========================================================================================================
# Svrha: View funkcije za prikaz vlastitog profila korisnika, upload profilne slike i pregled tuđih profila
# Funkcionalnosti:
#   - me(): Prikazuje vlastiti profil s postama, razgovorima, followerima i following korisnicicima
#   - profile(): Prikazuje javni profil drugog korisnika
#
# 📝 Kako koristi:
#   1. /users/me/ → Vlastiti profil (zahtijeva login)
#   2. /users/<uuid>/ → Profil drugog korisnika (javno dostupno)
#
# 🔐 Sigurnost: @login_required dekorator štiti sve osjetljive view-e
# ========================================================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from Posts.models import PostModel
from .models import User, validate_size


@login_required
def me(request):
    # 🔹 me() - Prikazuje dashboard korisnika s postama, razgovorima, followerima i following
    #    
    #    💼 Kako radi:
    #       - POST metoda: Upload profilne slike (validacija veličine do 2MB)
    #       - GET metoda: Dohvaća sve podatke korisnika za renderiranje template-a
    #    
    #    📊 Što se prikazuje:
    #       - Sve objave autora (sortirane po vremenu ažuriranja)
    #       - Jedinstveni korisnici s kojima ima razgovora
    #       - Lista follower-a (do 100) s avatarima
    #       - Lista following korisnika (do 100) s avatarima
    #       - Brojač follower-a i following
    #    
    #    ⚠️ Napomena: Ako upload slike ne uspije, vraćam HttpResponse s greškom (status 400)
    #
    # 📸 Obrada upload-a profilne slike
    if request.method == "POST":
        image = request.FILES.get("profile_image")
        if image:
            try:
                # 1️⃣ Pokreni validator veličine slike (max 2MB)
                validate_size(image)

                # 2️⃣ Ako validacija prođe, spremi novu sliku i refresh page
                user = request.user
                user.profile_image = image
                user.save()
                return redirect(request.path)
            except Exception as e:
                # 3️⃣ Uhvati grešku (prevelika slika, format itd.) i vrati HTTP 400
                error_msg = getattr(e, 'message', str(e))
                return HttpResponse(f"Greška pri uploadu: {error_msg}", status=400)
        return HttpResponse("Nema učitane slike", status=400)

    if request.method != "GET":
        return HttpResponse("Metoda nije dozvoljena")

    # 🔄 Učitaj dodatne modele dinamički (izbjegni kružne import-e)
    from Chat.models import Message
    from Interactions.models import Follow

    user = request.user
    # 📝 Dohvati sve objave autora, sortirane po vremenu ažuriranja (najnovije prvo)
    posts = PostModel.objects.filter(author=user).order_by("-updated_at")

    # 💬 Pronađi korisnike s kojima korisnik ima razgovore
    # Kombinira sve korisnike kojima je poslao poruku + sve koji su mu poslali poruku
    sent_to = Message.objects.filter(sender=user).values_list('recipient', flat=True).distinct()
    received_from = Message.objects.filter(recipient=user).values_list('sender', flat=True).distinct()
    conversation_user_ids = set(sent_to) | set(received_from)  # Unija: izbjegni duplikate
    conversations = User.objects.filter(id__in=conversation_user_ids).order_by('username')

    # 👥 Dohvati follower-e i following (ograničeno na 100 za performanse)
    followers_qs = Follow.objects.filter(following=user).select_related('follower')[:100]
    following_qs = Follow.objects.filter(follower=user).select_related('following')[:100]

    # 📋 Pretvaranje u jednostavne dictionary strukture za template
    followers = [{'username': f.follower.username, 'uuid': str(f.follower.user_uuid), 'image': f.follower.profile_image.url if f.follower.profile_image else None} for f in followers_qs]
    following = [{'username': f.following.username, 'uuid': str(f.following.user_uuid), 'image': f.following.profile_image.url if f.following.profile_image else None} for f in following_qs]

    # 📦 Pripremi context za template
    context = {
        'posts': posts,
        'user': request.user,
        'conversations': conversations,
        'followers': followers,
        'following': following,
        'followers_count': Follow.objects.filter(following=user).count(),
        'following_count': Follow.objects.filter(follower=user).count()
    }

    return render(request, "account/me.html", context)


@login_required
def profile(request, user_uuid):
    # 🔹 profile() - Prikazuje javni profil drugog korisnika
    #    
    #    👁️ Što se vidi:
    #       - Sve objave ciljanog korisnika
    #       - Sve komentare koje je napisao
    #       - Je li trenutni korisnik pratio ciljanog korisnika (is_following flag)
    #       - Lista follower-a i following korisnika
    #    
    #    🔐 Sigurnost:
    #       - Samo prijavljeni korisnici mogu vidjeti profil
    #       - Profil je javno dostupan (ne provjeravamo vlasništvo)
    #    
    #    📊 Brojčani podaci:
    #       - Ukupan broj follower-a
    #       - Ukupan broj following
    #       - Broj objava i komentara
    #
    from Comments.models import CommentModel
    from Interactions.models import Follow

    # 🔍 Pronađi korisnika po UUID
    target = get_object_or_404(User, user_uuid=user_uuid)

    # 📝 Dohvati sve objave tog korisnika
    posts = PostModel.objects.filter(author=target).order_by('-updated_at')
    # 💬 Dohvati sve komentare koje je napisao
    comments = CommentModel.objects.filter(author=target).order_by('-created_at')

    # 👁️ Provjeri je li trenutni korisnik pratio ciljanog korisnika
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=target).exists()

    # 👥 Dohvati follower-e i following (ograničeno na 50 za performanse)
    followers_qs = Follow.objects.filter(following=target).select_related('follower')[:50]
    following_qs = Follow.objects.filter(follower=target).select_related('following')[:50]

    # 📋 Pretvori u jednostavne dict strukture
    followers = [{'username': f.follower.username, 'uuid': str(f.follower.user_uuid)} for f in followers_qs]
    following = [{'username': f.following.username, 'uuid': str(f.following.user_uuid)} for f in following_qs]

    # 📦 Pripremi context za template
    context = {
        'target': target,
        'posts': posts,
        'comments': comments,
        'is_following': is_following,
        'followers': followers,
        'following': following,
        'followers_count': Follow.objects.filter(following=target).count(),
        'following_count': Follow.objects.filter(follower=target).count()
    }

    return render(request, 'account/profile.html', context)