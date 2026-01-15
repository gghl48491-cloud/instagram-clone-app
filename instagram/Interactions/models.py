# 🇭🇷 Interactions/models.py - Modeli za interakcije (Like, Dislike, Follow)
# ========================================================================================================
# Svrha: Čuvanje interakcija između korisnika (like/dislike objava i komentara, praćenje)
#
# Modeli:
#   1. Like: Like na objavu (mutual_exclusive sa Dislike)
#   2. Dislike: Dislike na objavu (mutual_exclusive sa Like)
#   3. CommentLike: Like na komentar
#   4. Follow: Follow relacija između korisnika
#
# ⚠️ Pravilo: Like i Dislike su međusobno isključivi za objave (ne možeš oba)
# ========================================================================================================

from django.db import models
from django.utils import timezone

from Users.models import User
from Posts.models import PostModel


class Like(models.Model):
    # 🔹 Like - Like na objavu
    #    
    #    📝 Polja:
    #       - user: ForeignKey na User koji je dao like
    #       - post: ForeignKey na PostModel (objava)
    #       - created_at: Vrijeme kada je dao like
    #    
    #    🔐 Constraint:
    #       - unique_together: (user, post) - Korisnik može dati samo jedan like po objavi
    #    
    #    💬 Related name:
    #       - post.likes: Svi like-ovi na objavu
    #    
    #    ⚠️ Logika:
    #       - Ako korisnik ima dislike na objavu i klikne like → dislike se briše
    #       - Klik na like → toggle (create ili delete)
    #    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'post')  # 🔒 Samo jedan like po korisniku po objavi
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


class Dislike(models.Model):
    # 🔹 Dislike - Dislike na objavu (međusobno isključivo sa Like)
    #    
    #    📝 Polja:
    #       - user: ForeignKey na User koji je dao dislike
    #       - post: ForeignKey na PostModel (objava)
    #       - created_at: Vrijeme kada je dao dislike
    #    
    #    🔐 Constraint:
    #       - unique_together: (user, post) - Korisnik može dati samo jedan dislike po objavi
    #    
    #    💬 Related name:
    #       - post.dislikes: Svi dislike-ovi na objavu
    #    
    #    ⚠️ Logika:
    #       - Ako korisnik ima like na objavu i klikne dislike → like se briše
    #       - Klik na dislike → toggle (create ili delete)
    #    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='dislikes')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'post')  # 🔒 Samo jedan dislike po korisniku po objavi
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} dislikes {self.post.title}"


class CommentLike(models.Model):
    # 🔹 CommentLike - Like na komentar
    #    
    #    📝 Polja:
    #       - user: ForeignKey na User koji je dao like
    #       - comment: ForeignKey na CommentModel (komentar)
    #       - created_at: Vrijeme kada je dao like
    #    
    #    🔐 Constraint:
    #       - unique_together: (user, comment) - Samo jedan like po komnentaru po korisniku
    #    
    #    💬 Related name:
    #       - comment.comment_likes: Svi like-ovi na komentar
    #    
    #    ⚠️ Napomena:
    #       - CommentLike koristi distinct related_name kako bi se izbjegao konflikt sa CommentModel.likes poljem
    #    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Koristi distinct related_name za izbježivanje konflikta sa CommentModel.likes poljem
    comment = models.ForeignKey('Comments.CommentModel', on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'comment')  # 🔒 Samo jedan like po korisniku po komentaru
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} likes comment {self.comment_id}"


class Follow(models.Model):
    # 🔹 Follow - Follow relacija između korisnika
    #    
    #    📝 Polja:
    #       - follower: ForeignKey na User koji prati (related_name='following_set')
    #       - following: ForeignKey na User kojeg prati (related_name='followers_set')
    #       - created_at: Vrijeme kada je krenuo pratiti
    #    
    #    🔐 Constraint:
    #       - unique_together: (follower, following) - Korisnik može pratiti drugoga samo jednom
    #    
    #    💬 Primjer:
    #       - User A prati User B → Follow(follower=A, following=B)
    #       - A.following_set.all() → Svi korisnici koje A prati
    #       - B.followers_set.all() → Svi korisnici koji prate B
    #    
    #    ⚠️ Logika:
    #       - Klik na follow → toggle (create ili delete)
    #       - Sprječava self-follow (korisniku se ne dozvoljava pratiti sebe)
    #    
    follower = models.ForeignKey(User, related_name='following_set', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('follower', 'following')  # 🔒 Samo jedan follow po relaciji
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
