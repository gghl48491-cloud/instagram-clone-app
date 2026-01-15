# 🇭🇷 Comments/models.py - Model za komentare na objavama
# ========================================================================================================
# Svrha: Čuvanje komentara na objavama s podrškom za nested replies
# Polja:
#   - content: Tekst komentara (max 300 znakova, obavezno)
#   - likes: Brojač like-a (sadržan u CommentLike modelu)
#   - author: ForeignKey na User (pišač komentara)
#   - post: ForeignKey na PostModel (objava na koju se komentiraj)
#   - parent: ForeignKey na sebe (self-reference za replies/nested komentare)
#   - created_at: Vrijeme kreiranja (automatski)
#
# 📋 Redoslijed:
#   - Sortirani po vremenu kreiranja
#
# 👶 Nested struktura:
#   - Top-level komentar: parent=None
#   - Reply na komentar: parent=neki drugi komentar
# ========================================================================================================

from django.db import models

from Users.models import User
from Posts.models import PostModel


class CommentModel(models.Model):
    # 🔹 CommentModel - Model za komentar na objavu
    #    
    #    📝 Polja:
    #       - content: Tekst komentara (max 300 znakova, obavezno)
    #       - likes: Integer brojač (legacy polje, now computed from CommentLike model)
    #       - author: ForeignKey na User koji je napisao komentar
    #       - post: ForeignKey na PostModel (objava na koju se komentiraj)
    #       - parent: ForeignKey na sebe (self-reference za replies)
    #       - created_at: Vrijeme kreiranja (automatski)
    #    
    #    🔗 Relacije:
    #       - author.commentmodel_set: Svi komentari od tog korisnika
    #       - post.commentmodel_set: Svi komentari na tu objavu
    #       - replies: Ugnježđeni komentari (parent=this)
    #       - parent.replies: Sve replies na ovaj komentar
    #    
    #    👶 Struktura replies:
    #       - Top-level: parent=None
    #       - Reply: parent={neki komentar}
    #       - Brisanje parent-a briše sve replies (on_delete=CASCADE)
    #    
    content = models.TextField(max_length=300, null=False, blank=False)
    # ❤️ 'likes' - legacy polje, real likes trebam pratiti u CommentLike modelu
    likes = models.IntegerField(blank=False, default=0)

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE)
    # 👶 Parent za self-referential relationship (replies na komentar)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)  # ⏰ Postavi se samo pri kreiranju

    class Meta:
        db_table = "Comment"  # 💾 Eksplicitno ime tablice

    def __str__(self):
        # 🔹 __str__ - Prikazuje osnove komentara
        return f"{self.author.username} na {self.post.title}: {self.content[:50]}"
