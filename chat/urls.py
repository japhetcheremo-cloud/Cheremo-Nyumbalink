from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('thread/<int:user_id>/', views.chat_thread, name='chat_thread'),
    path('send/', views.send_message, name='send_message'),
    path('messages/<int:user_id>/', views.get_messages, name='get_messages'),
]
