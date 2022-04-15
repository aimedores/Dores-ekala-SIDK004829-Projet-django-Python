from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from autoslug import AutoSlugField
from django.urls import reverse
from django.utils.safestring import mark_safe
# Create your models here.

class Categorie(MPTTModel):
    parent = TreeForeignKey('self',blank=True, null=True ,related_name='categorie', on_delete=models.CASCADE)
    titre = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='titre', unique = True,  null = False)
    cree_le=models.DateTimeField(auto_now_add=True, verbose_name="CREER Le")
    maj_le=models.DateTimeField(auto_now=True, verbose_name="MIS A JOUR le")

    class MPTTMeta:
        order_insertion_by = ['-id']
    
    def __str__(self):                           # __str__ method elaborated later in
        full_path = [self.titre]                  # post.  use __unicode__ in place of
        k = self.parent
        while k is not None:
            full_path.append(k.titre)
            k = k.parent
        return ' / '.join(full_path[::-1])

    def get_absolute_url(self):
        return reverse('categorie', kwargs={'path': self.get_path()})

class Article(models.Model):
    plat = models.CharField(max_length = 25)
    prix = models.DecimalField(max_digits=12, decimal_places=2)
    composition = models.TextField()
    categorie = models.ForeignKey('Categorie', on_delete = models.CASCADE, related_name="article")
    quantite = models.IntegerField(default=1,verbose_name ="Quantité")
    image = models.ImageField(upload_to='images/')
    actif = models.BooleanField(default=True)
    slug = AutoSlugField(populate_from='plat', unique = True, null = False)
    cree_le=models.DateTimeField(auto_now_add=True, verbose_name="CREER Le")
    maj_le=models.DateTimeField(auto_now=True, verbose_name="MIS A JOUR le")
    
    def __str__(self):
        return self.plat
    
    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return ""
    

