from django.urls import path
from . import views

urlpatterns = [
    path('', views.plant_list, name='plant_list'),
    path('<int:pk>/', views.plant_detail, name='plant_detail'),
    path('add/', views.add_plant, name='add_plant'),
    path('<int:plant_id>/add-measurement/', views.add_measurement, name='add_measurement'),
]