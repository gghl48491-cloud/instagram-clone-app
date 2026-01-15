# 🇭🇷 Users/models.py - Model za korisnički račun s profilnom slikom
# ========================================================================================================
# Svrha: Prošireni User model koji nasleđuje Django AbstractUser
# Dodatna polja:
#   - user_uuid: Jedinstveni UUID za javne profile URL-ove
#   - profile_image: Slika profila s validacijom veličine
#   - email: Obavezno, jedinstveno
#
# 🔐 Validacija:
#   - validate_size(): Proverava da slika nije veća od 2MB
#
# 🌄 Upload putanje:
#   - Slike se skladište u: media/users/images/{uuid}.png
#   - Default slika: egg.png (ako korisnik nema profilnu sliku)
# ========================================================================================================

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

import uuid
import os


def generate_image_uuid(instance, filename):
    # 🔹 generate_image_uuid() - Generiše jedinstveno ime za svaku učitanu sliku
    #    
    #    💼 Kako radi:
    #       - Generiše novi UUID4 za svaku sliku
    #       - Sprječava konflikt imena slika
    #       - Putanja: media/users/images/{uuid}.png
    #    
    return os.path.join("users/images/", f"{uuid.uuid4()}.png")


def validate_size(image):
    # 🔹 validate_size() - Validira da slika nije veća od 2MB
    #    
    #    💼 Kako radi:
    #       - Proverava image.size atribut
    #       - Max 2MB = 2 * 1024 * 1024 bajtova
    #       - Baca ValidationError ako je prevelika
    #    
    #    ⚠️ Baca iznimku:
    #       - "Slika je prevelika! Maksimalno 2MB."
    #    
    max_size = 2 * 1024 * 1024  # 2MB u bajtovima
    if image.size > max_size:
        raise ValidationError("Slika je prevelika! Maksimalno 2MB.")


class User(AbstractUser):
    # 🔹 User - Prošireni Django korisnik s UUID-om i profilnom slikom
    #    
    #    📝 Polja:
    #       - email (obavezno, jedinstveno): Emailadresa korisnika
    #       - profile_image: ImageField s upload_to i default vrijednosti
    #       - user_uuid: UUID za javne profile URL-ove
    #    
    #    🛡️ Validacija:
    #       - profile_image koristi validate_size validator
    #       - email mora biti jedinstveno (unique=True)
    #    
    #    📁 Upload:
    #       - Nove slike: media/users/images/{uuid}.png
    #       - Default: egg.png
    #    
    email = models.EmailField(blank=False, unique=True)
    profile_image = models.ImageField(
        upload_to=generate_image_uuid,
        default="egg.png",
        validators=[validate_size]
    )

    user_uuid = models.UUIDField(default=uuid.uuid4, blank=False, unique=True)

    def __str__(self):
        # 🔹 __str__ - Vraća korisničko ime kao string reprezentaciju
        return self.username
