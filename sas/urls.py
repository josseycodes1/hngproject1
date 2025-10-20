from django.urls import path
from . import views

urlpatterns = [
    # POST - Create new string analysis
    path('strings', views.create_analyze_string, name='create-string'),
    # GET - Get specific string by value
    path('strings/<str:string_value>', views.get_string, name='get-string'),
    # DELETE - Delete specific string by value  
    path('strings/<str:string_value>/delete', views.delete_string, name='delete-string'),
    # GET - Get all strings with filters (using query params)
    path('strings-list', views.get_all_strings, name='get-all-strings'),
    # GET - Natural language filtering
    path('strings/filter-by-natural-language', views.filter_by_natural_language, name='natural-language-filter'),
]