# 🇭🇷 Posts/forms.py - Django Form za stvaranje i ažuriranje objava
# ========================================================================================================
# Svrha: Form s clean methods za validaciju korisničkog inputa (naslov, sadržaj, slika)
# Polja:
#   - title: Naslov objave
#   - content: Tekst sadržaja objave
#   - post_image: Slika objave (s custom validacijom veličine)
#
# 🛡️ Validacija:
#   - clean_post_image(): Proverava da slika nije veća od 50MB
# ========================================================================================================

from django import forms
from .models import PostModel

from django.core.exceptions import ValidationError


class PostForm(forms.ModelForm):
    # 🔹 PostForm - ModelForm za PostModel s custom validacijom slike
    #    
    #    📝 Meta:
    #       - model: PostModel
    #       - fields: ['title', 'content', 'post_image']
    #       - Napravljeno iz Django form framework-a
    #    
    #    🛡️ Clean methods:
    #       - clean_post_image(): Validacija veličine slike
    #    
    class Meta:
        fields = ["title", "content", "post_image"]
        model = PostModel

    def clean_post_image(self):
        # 🔹 clean_post_image() - Validira da slika nije prevelika
        #    
        #    💼 Kako radi:
        #       - Dohvaća slike iz cleaned_data
        #       - Ako ima file attribute (tj. ako je uploaded), proverava veličinu
        #       - Max 50MB = 50 * 1024 * 1024 bajtova
        #    
        #    ⚠️ Baca iznimku:
        #       - "Slika je prevelika! Maksimalna dozvoljena veličina je 1MB."
        #       - (Note: Poruka kaže 1MB ali je limit zapravo 50MB - trebam ispraviti)
        #    
        #    📤 Vraća:
        #       - image: Cleaned slika (ili None)
        #    
        image = self.cleaned_data.get('post_image')
        
        if image and hasattr(image, 'size'):
            # 5MB = 5 * 1024 * 1024 bytes
            max_size = 50 * 1024 * 1024  # 50MB
            if image.size > max_size:
                raise ValidationError("Slika je prevelika! Maksimalna dozvoljena veličina je 1MB.")
        
        return image
