# 🇭🇷 Chat/models.py - Model za poruke između korisnika
# ========================================================================================================
# Svrha: Čuvanje privatnih poruka između korisnika s time-stampom i read-status
# Polja:
#   - sender: ForeignKey na User (pošiljaoc poruke)
#   - recipient: ForeignKey na User (primaoć poruke)
#   - content: Tekst poruke (max 1000 znakova)
#   - created_at: Vrijeme slanja (default=timezone.now)
#   - is_read: Status je li primaoć pročitao poruku (default=False)
#
# 🔄 Redoslijed:
#   - Sortirane po created_at (najstarije prvo)
#   - Čuva se razgovor u oba smjera (sender→recipient i recipient→sender)
# ========================================================================================================

from django.db import models
from django.utils import timezone
from Users.models import User


class Message(models.Model):
    # 🔹 Message - Model za privatnu poruku
    #    
    #    📝 Polja:
    #       - sender: ForeignKey na User koji je poslao poruku (related_name='sent_messages')
    #       - recipient: ForeignKey na User koji je primio poruku (related_name='received_messages')
    #       - content: Tekst poruke (max 1000 znakova, obavezno)
    #       - created_at: Vrijeme slanja (default=current time)
    #       - is_read: Boolean (True ako je primaoć pročitao, default=False)
    #    
    #    🔗 Relacije:
    #       - sender.sent_messages: Sve poruke koje je User poslao
    #       - sender.received_messages: Sve poruke koje je User primio
    #    
    #    💬 Logika razgovora:
    #       - Razgovor između A i B = sve poruke gdje:
    #         * (sender=A, recipient=B) ILI (sender=B, recipient=A)
    #       - Sortirane po vremenu (oldest first)
    #    
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(max_length=1000, blank=False)
    created_at = models.DateTimeField(default=timezone.now)  # ⏰ Koristi Django timezone
    is_read = models.BooleanField(default=False)  # 👁️ Status čitanja poruke

    class Meta:
        ordering = ['created_at']  # 📋 Sortiranje: najstarije poruke prvo

    def __str__(self):
        # 🔹 __str__ - Prikazuje korisničko prikaz poruke
        #    Format: "sender → recipient: sadržaj (first 30 chars)"
        return f"{self.sender.username} → {self.recipient.username}: {self.content[:30]}"
