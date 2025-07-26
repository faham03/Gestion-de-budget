from django.urls import path
from . import views

app_name = 'expenses'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_expense, name='add'),
    path('delete/<int:pk>/', views.delete_expense, name='delete'),
    path('edit/<int:pk>/', views.edit_expense, name='edit'),
    path('export/', views.export_csv, name='export_csv'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('ajouter-multi/', views.add_multiple_expenses, name='add_multiple_expenses'),

]