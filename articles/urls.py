from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('articles/', views.article_list, name='article_list'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('destinations/', views.destinations, name='destinations'),
    path('destination/<str:destination_slug>/', views.destination_detail, name='destination_detail'),
    path('about/', views.about, name='about'),
    path('points-guide/', views.points_guide, name='points_guide'),
    path('travel-tips/', views.travel_tips, name='travel_tips'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
] 