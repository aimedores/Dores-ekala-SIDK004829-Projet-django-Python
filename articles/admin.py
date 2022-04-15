from django.contrib import admin
from.models import Categorie, Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['plat','prix','categorie','composition']


admin.site.register(Categorie)
admin.site.register(Article, ArticleAdmin)