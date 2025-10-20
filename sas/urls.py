# sas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('strings/', views.create_analyze_string, name='create-string'),
    path('strings/<str:string_value>/', views.get_string, name='get-string'),
    path('strings/<str:string_value>/delete/', views.delete_string, name='delete-string'),
    path('strings-list/', views.get_all_strings, name='get-all-strings'),

    # keep your original natural-language endpoint
    path('strings/filter-by-natural-language/', views.filter_by_natural_language, name='natural-language-filter'),

    # alias to match tests that might hit this path
    path('strings/natural-language-filter/', views.filter_by_natural_language, name='natural-language-filter-alt'),
]
