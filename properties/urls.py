from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('<int:pk>/', views.property_detail, name='property_detail'),
    path('add/', views.property_create, name='property_create'),
    path('<int:pk>/edit/', views.property_update, name='property_update'),
    path('<int:pk>/delete/', views.property_delete, name='property_delete'),
    path('<int:pk>/book/', views.book_viewing, name='book_viewing'),
    path('<int:pk>/apply/', views.apply_rental, name='apply_rental'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<int:pk>/review/', views.add_review, name='add_review'),
    path('approve/<int:pk>/', views.approve_property, name='approve_property'),
    path('verify-user/<int:pk>/', views.verify_user, name='verify_user'),
    path('booking/<int:pk>/<str:status>/', views.manage_booking, name='manage_booking'),
    path('application/<int:pk>/<str:status>/', views.manage_application, name='manage_application'),
]
