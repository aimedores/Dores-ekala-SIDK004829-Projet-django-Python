from argparse import Namespace
from django.urls import URLPattern, path
from . import views
import articles
urlpatterns = [
    path('detail_article/<slug:slug>', views.DetailArticleView.as_view(), name="detail_article"),
]