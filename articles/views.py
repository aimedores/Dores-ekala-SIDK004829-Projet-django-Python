from django.shortcuts import render
from django.views.generic import DetailView
from .models import Article

class DetailArticleView(DetailView):
    model = Article
    template_name = "articles/detail_article.html"

