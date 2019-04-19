from django.urls import path
from . import views

app_name = 'tournament'
urlpatterns = [
    # ex /
    path('', views.index, name='index'),
    # ex /add/
    path('add/', views.add, name='add'),
    # ex /10/
    path('<int:tournament_id>/', views.display, name='display'),
    # ex /10/edit/
    #path('<int:tournament_id>/edit/', views.edit, name='edit'),
    path('delete/<int:tournament_id>/', views.delete, name='delete')
]