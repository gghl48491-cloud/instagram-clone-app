# 🇭🇷 Posts/models.py - Model za objave (posts) s slikama
# ========================================================================================================
# Svrha: Struktura za čuvanje korisničkih objava s tekstom, slikom i meta-podacima
# Polja:
#   - title: Naslov objave (max 100 znakova)
#   - content: Sadržaj objave (max 5000 znakova)
#   - post_image: Slika koja ide uz objavu
#   - author: ForeignKey na User (vlasnik objave)
#   - uuid_field: Jedinstveni UUID za javne URL-ove
#   - created_at: Vrijeme kreiranja (automatski)
#   - updated_at: Vrijeme posljednje izmjene (automatski)
#
# 🌄 Upload putanja:
#   - Slike: media/posts/images/{uuid}.png
#   - Default: posts/images/egg.png
# ========================================================================================================

from django.db import models
import uuid
import os

from Users.models import User


def generate_image_uuid(n, m):
    # 🔹 generate_image_uuid() - Generiše jedinstveno ime za sliku objave
    #    
    #    💼 Kako radi:
    #       - Generiše novi UUID4 
    #       - Sprječava konflikt imena slika
    #       - Putanja: media/posts/images/{uuid}.png
    #    
    return os.path.join("posts/images/", f"{uuid.uuid4()}.png")


class PostModel(models.Model):
    # 🔹 PostModel - Model za objavu (post)
    #    
    #    📝 Polja:
    #       - title: Naslov od max 100 znakova (obavezno)
    #       - content: Tekst sadržaja od max 5000 znakova (obavezno)
    #       - post_image: ImageField s upload_to i default slikom
    #       - author: ForeignKey na User (briše objave ako se korisnik obriše)
    #       - uuid_field: Jedinstveni UUID za URL-ove
    #       - created_at: Vrijeme kreiranja (auto_now_add=True)
    #       - updated_at: Vrijeme posljednje izmjene (auto_now=True)
    #    
    #    🔗 Relacije:
    #       - likes: Relacija One-to-Many sa Like modelom (related_name='likes')
    #       - dislikes: Relacija One-to-Many sa Dislike modelom (related_name='dislikes')
    #       - comments: Relacija One-to-Many sa CommentModel (automatski related_name='commentmodel_set')
    #    
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField(max_length=5000, blank=False)
    post_image = models.ImageField(upload_to=generate_image_uuid, default="posts/images/egg.png")

    created_at = models.DateTimeField(auto_now_add=True)  # ⏰ Postavi se samo pri kreiranju
    updated_at = models.DateTimeField(auto_now=True)      # ⏰ Osvježava se pri svakoj izmjeni

    uuid_field = models.UUIDField(default=uuid.uuid4, blank=False, unique=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 🔐 Obriši objave s korisnikom

    def __str__(self):
        # 🔹 __str__ - Vraća naslov kao string reprezentaciju
        return self.title

    class Meta:
        db_table = "Post"  # 💾 Eksplicitno ime tablice u bazi
