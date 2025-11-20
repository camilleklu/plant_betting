from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:plant_id>/', views.create_bet, name='create_bet'),
]