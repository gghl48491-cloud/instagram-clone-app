# 🇭🇷 Chat/views.py - Upravljanje porukama i razgovorima
# ========================================================================================================
# Svrha: AJAX i JSON API-ji za real-time razmjenu poruka između korisnika
# Funkcionalnosti:
#   - chat_with(): Prikazuje chat stranicu s drugim korisником
#   - send_message(): Stvara novu poruku između dva korisnika (JSON)
#   - get_messages(): Dohvaća sve poruke razgovora (JSON)
#
# 📝 Rute:
#   - GET /chat/<uuid>/ → Chat stranica s Javascriptom za real-time
#   - POST /chat/<uuid>/send/ → Spremi novu poruku (AJAX)
#   - GET /chat/<uuid>/get/ → Dohvati sve poruke (AJAX polling)
#
# ⏱️ Real-time logika:
#   - JavaScript pokreće GET /chat/<uuid>/get/ svaki 2 sekunde
#   - Poruke se dohvaćaju kao JSON
#   - Nove poruke se dinamički dodaju u stranicu
#
# 🔒 Sigurnost: @login_required, @require_http_methods, ne može chat sa sobom
# ========================================================================================================

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import models
import json

from Users.models import User
from .models import Message


@login_required
def chat_with(request, user_uuid):
    # 🔹 chat_with() - Prikazuje HTML stranicu za chat s drugim korisником
    #    
    #    💼 Kako radi:
    #       - Pronalazi korisnika po UUID-u
    #       - Proverava da li korisnik pokušava chatati sa sobom (blokirano)
    #       - Označava sve nepročitane poruke kao pročitane (is_read=True)
    #    
    #    📝 Što se prikazuje:
    #       - Chat stranicu s JavaScript-om za slanje/primanje poruka
    #       - Agentu se prosljeđuje `target` korisnik (podaci o drugom učesniku)
    #    
    #    🔄 Real-time refresh:
    #       - JavaScript pokreće GET /chat/<uuid>/get/ svakih 2 sekunde
    #       - Nove poruke se ažuriraju automatski bez osvježavanja stranice
    #    
    target = get_object_or_404(User, user_uuid=user_uuid)
    if target == request.user:
        return render(request, 'chat/room.html', {'error': 'Nije moguće chatati sa sobom'})
    
    # ✅ Označi sve poruke od tog korisnika kao pročitane
    Message.objects.filter(sender=target, recipient=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'chat/room.html', {'target': target})


@require_http_methods(["POST"])
@login_required
def send_message(request, user_uuid):
    # 🔹 send_message() - Stvara novu poruku i sprema je u bazu
    #    
    #    💼 Kako radi:
    #       - Prima `content` iz JSON ili POST podataka
    #       - Validira da poruka nije prazna i nije duža od 1000 znakova
    #       - Sprema Message objekt u bazu
    #    
    #    📨 Što se sprema:
    #       - sender = request.user (trenutni korisnik)
    #       - recipient = target (drugi korisnik)
    #       - content = poruka
    #       - created_at = trenutno vrijeme
    #       - is_read = False (sámo-inicijazo)
    #    
    #    📤 Odgovor:
    #       - JSON s podacima poruke (id, sender, content, created_at itd.)
    #       - Status 400 ako je poruka prazna ili prveduga
    #    
    target = get_object_or_404(User, user_uuid=user_uuid)
    
    try:
        # 🔍 Pokušaj parsirati JSON, ako ne uspije koristi POST podatke
        data = json.loads(request.body)
        content = data.get('content', '').strip()
    except:
        content = request.POST.get('content', '').strip()

    # 🛡️ Validacija
    if not content:
        return JsonResponse({'success': False, 'error': 'Prazna poruka'}, status=400)
    if len(content) > 1000:
        return JsonResponse({'success': False, 'error': 'Poruka je previše dugačka'}, status=400)

    # 💾 Spremi poruku u bazu
    msg = Message.objects.create(sender=request.user, recipient=target, content=content)

    # 📤 Vrati JSON s detaljima poruke
    return JsonResponse({
        'success': True,
        'id': msg.id,
        'sender': msg.sender.username,
        'content': msg.content,
        'created_at': msg.created_at.isoformat(),
        'is_read': msg.is_read
    })


@require_http_methods(["GET"])
@login_required
def get_messages(request, user_uuid):
    # 🔹 get_messages() - Dohvaća sve poruke razgovora između dva korisnika
    #    
    #    💼 Kako radi:
    #       - Pronalazi sve poruke gdje je request.user pošiljaoc ili primaoć
    #       - Filtrira samo poruke s targetom korisnikom
    #       - Sortira po vremenu kreiranja (oldest first)
    #    
    #    📝 Što se vraća:
    #       - JSON niz sa svim porukama
    #       - Svaka poruka ima: id, sender, sender_uuid, content, created_at, is_from_me
    #       - is_from_me = True ako je poruka od request.user-a (za CSS styling)
    #    
    #    🔄 Korištenje:
    #       - JavaScript pokreće ovaj endpoint svakih 2 sekunde
    #       - Prikazuje samo nove poruke (one koje nisu već renderirene)
    #    
    target = get_object_or_404(User, user_uuid=user_uuid)
    
    # 🔍 Dohvati sve poruke između request.user-a i target-a (u oba smjera)
    messages = Message.objects.filter(
        models.Q(sender=request.user, recipient=target) | 
        models.Q(sender=target, recipient=request.user)
    ).order_by('created_at')  # Od najstarije prema najnovijoj

    # 📋 Pretvori u JSON-kompatibilan format
    msgs = []
    for m in messages:
        msgs.append({
            'id': m.id,
            'sender': m.sender.username,
            'sender_uuid': str(m.sender.user_uuid),
            'content': m.content,
            'created_at': m.created_at.isoformat(),  # ISO 8601 format za parsing u JS
            'is_from_me': m.sender == request.user  # Za CSS bubble styling
        })

    return JsonResponse({'messages': msgs})
