from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('cookies/', views.cookies, name='cookies'),
    path('cheremo-gpt/', views.cheremo_gpt_page, name='cheremo_gpt'),
    path('cheremo-gpt/chat/', views.cheremo_gpt_chat, name='cheremo_gpt_chat'),
]
