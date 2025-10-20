from django.urls import path
from . import views

urlpatterns = [
    path('strings', views.create_analyze_string, name='create-string'),
    path('strings/<str:string_value>', views.get_string, name='get-string'),
    path('strings', views.get_all_strings, name='get-all-strings'),
    path('strings/filter-by-natural-language', views.filter_by_natural_language, name='natural-language-filter'),
    path('strings/<str:string_value>', views.delete_string, name='delete-string'),
]