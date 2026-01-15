# 🇭🇷 Posts/views.py - Upravljanje objavama (postovima)
# ========================================================================================================
# Svrha: View funkcije za prikaz, stvaranje, ažuriranje i brisanje objava s paginacijom
# Funkcionalnosti:
#   - List(): Prikazuje feed svih objava s paginacijom (3 objave po stranici)
#   - Create(): Forma za stvaranje nove objave s slikom
#   - Update(): Uređivanje vlastite objave
#   - Delete(): Brisanje vlastite objave (placeholder)
#   - ListDetail(): Prikazuje detaljan pregled objave + like/dislike/komentari
#
# 📝 Rute:
#   - GET /posts/ → Feed svih objava
#   - GET /posts/create/ → Forma za novu objavu
#   - POST /posts/create/ → Spremi novu objavu
#   - POST /posts/<id>/update/ → Ažurira objavu
#   - GET /posts/<id>/ → Detalji objave s komentarima
#
# 🔒 Sigurnost: @login_required štiti sve osjetljive operacije (Create, Update, Delete)
# ========================================================================================================

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator

from .models import PostModel
from Users.models import User
from .forms import PostForm


# 🔹 List() - Prikazuje feed svih objava s paginacijom
#    
#    📊 Kako radi:
#       - Dohvaća sve objave iz baze (bez filtriranja)
#       - Sortira ih po vremenu ažuriranja (najnovije prvo)
#       - Primjenjuje paginaciju: 3 objave po stranici
#       - Parametar: page=1,2,3... (automatski se dodaje u GET)
#    
#    👁️ Što se prikazuje:
#       - 3 objave po stranici s informacijom trenutne stranice
#       - Linkovi na prethodnu/sljedeću stranicu (ako postoje)
#    
#    ⚠️ Napomena: Ova ruta je JAVNA - ne zahtijeva login

def List(request):
    if request.method != "GET":
        return HttpResponse("Samo GET metoda je dozvoljena")
    
    # 📚 Dohvati sve objave i sortiraj po vremenu ažuriranja (najnovije prvo)
    objects = PostModel.objects.filter().order_by("-updated_at")
    # 📄 Primijeni paginaciju: 3 objave po stranici
    p = Paginator(objects, 3)

    # 🔢 Dohvati broj stranice iz GET parametra
    page = request.GET.get("page")
    # 📋 Pronađi odgovarajuću stranicu (ili zadanu ako page nije validan)
    page_obj = p.get_page(page)
    
    return render(request, "posts/list.html", {"page_obj": page_obj})


@login_required
def Create(request):
    # 🔹 Create() - Forma i obrada stvaranja nove objave
    #    
    #    💼 Kako radi:
    #       - GET: Prikazuje praznu formu za unos title, content i slike
    #       - POST: Prima podatke iz forme, validira ih i sprema novu objavu
    #    
    #    🛡️ Što se validira (PostForm clean metode):
    #       - Veličina slike (max 50MB, greška ako premala)
    #       - Format slike (PNG, JPG itd.)
    #    
    #    💾 Što se sprema:
    #       - title, content, post_image iz forme
    #       - author automatski se postavlja na request.user
    #       - created_at i updated_at se postavljaju automatski
    #    
    #    ✅ Nakon uspješnog upisa: redirect na feed (/posts/)
    #
    if request.method == "GET":
        return render(request, "posts/create.html", {"form": PostForm})
    elif request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            # ✅ Forma je validna - spremi objavu
            post = form.save(commit=False)
            post.author = request.user  # 🔐 Postavi autora na trenutnog korisnika
            post.save()

            return redirect("list")

        return render(request, "posts/create.html", {"form": form})

    return HttpResponse("Samo GET i POST metode su dozvoljene")


@login_required
def Update(request, id):
    # 🔹 Update() - Ažuriranje postojeće objave
    #    
    #    🔒 Sigurnost:
    #       - Samo vlasnik objave može je ažurirati
    #       - Ako korisnik nije vlasnik → HTTP 403 (Not Authorized)
    #    
    #    💼 Kako radi:
    #       - GET: Prikazuje formu s trenutnim podacima
    #       - POST: Ažurira title, content i/ili sliku
    #    
    #    💾 Što se ažurira:
    #       - title, content, post_image (ako je nova slika učitana)
    #       - updated_at se automatski osvježava
    #    
    #    ✅ Nakon uspješnog upisa: redirect na feed
    #
    object = PostModel.objects.get(uuid_field=id)
    if object.author != request.user:
            return HttpResponse("Nije dozvoljeno")  # 🔐 Samo vlasnik može ažurirati

    if request.method == "POST":
    
        if not object:
            return HttpResponse("Objava ne postoji")
        
        form = PostForm(request.POST, request.FILES, instance=object)

        
        if form.is_valid():
            form.save()
            return redirect("list")
        
        return render(request, "posts/update.html", {"form": form})
    
    elif request.method == "GET":
        return render(request, "posts/update.html", {"form": PostForm(instance=object)})

        
    return HttpResponse("Metoda nije dozvoljena")




@login_required
def Delete(request, id):
    # 🔹 Delete() - Brisanje objave
    #    
    #    🔒 TODO: Implementacija - trebam provjeriti je li korisnik vlasnik
    #    
    pass


@login_required
def ListDetail(request, id):
    # 🔹 ListDetail() - Prikazuje detaljni pregled objave s komentarima, like/dislike brojačima
    #    
    #    📊 Što se prikazuje:
    #       - Naslov, sadržaj i slika objave
    #       - Broj like-a i dislike-a
    #       - Je li trenutni korisnik dao like/dislike
    #       - Svi komentari na objavu (dohvaćeni AJAX-om)
    #       - Forma za dodavanje novog komentara
    #    
    #    💬 Komentari:
    #       - Dohvaćeni JavaScript-om nakon učitavanja stranice
    #       - Refresh svakih 2 sekunde (auto-refresh)
    #       - Mogu biti odgovori na druge komentare (nested)
    #    
    #    ❤️ Interakcije:
    #       - Like/Dislike botuni su međusobno isključivi (ne možeš oboje)
    #       - Klik na like → Uklanja dislike ako postoji, sprema/uklanja like
    #    
    if request.method != "GET":
        return HttpResponse("Samo GET metoda je dozvoljena")
    
    obj = PostModel.objects.get(uuid_field=id)

    # ❤️ Brojač likes & dislikes
    likes_count = obj.likes.count() if hasattr(obj, 'likes') else 0
    from Interactions.models import Like, Dislike
    dislikes_count = obj.dislikes.count() if hasattr(obj, 'dislikes') else 0

    # 👤 Provjeri je li trenutni korisnik dao like/dislike
    user_liked = False
    user_disliked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, post=obj).exists()
        user_disliked = Dislike.objects.filter(user=request.user, post=obj).exists()
    
    return render(request, "posts/list_detail.html", context={"post":obj, "likes_count": likes_count, "dislikes_count": dislikes_count, "user_liked": user_liked, "user_disliked": user_disliked})
