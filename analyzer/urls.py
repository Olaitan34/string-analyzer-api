from django.urls import path
from .views import (
    StringsView,
    StringDetailView,
    NaturalLanguageFilterView,
)

app_name = 'analyzer'

urlpatterns = [
    # POST: Create a new string analysis
    # GET: List all strings with optional filtering
    path('strings/', StringsView.as_view(), name='strings'),
    
    # GET: Natural language filter (must come before detail view)
    path('strings/filter-by-natural-language/', NaturalLanguageFilterView.as_view(), name='natural-language-filter'),
    
    # GET: Retrieve a specific string
    # DELETE: Delete a specific string
    path('strings/<path:string_value>/', StringDetailView.as_view(), name='string-detail'),
]
