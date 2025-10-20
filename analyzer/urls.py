from django.urls import path
from .views import (
    CreateStringView,
    RetrieveStringView,
    ListStringsView,
    NaturalLanguageFilterView,
    DeleteStringView
)

app_name = 'analyzer'

urlpatterns = [
    # POST /api/strings/ -> Create a new string analysis
    path('strings/', CreateStringView.as_view(), name='create-string'),
    
    # GET /api/strings/ -> List and filter string analyses
    path('strings/', ListStringsView.as_view(), name='list-strings'),
    
    # GET /api/strings/filter-by-natural-language/ -> Natural language filter
    # This MUST come before the <path:string_value> pattern to avoid conflicts
    path('strings/filter-by-natural-language/', NaturalLanguageFilterView.as_view(), name='natural-language-filter'),
    
    # GET /api/strings/<str:string_value>/ -> Retrieve specific string analysis
    path('strings/<path:string_value>/', RetrieveStringView.as_view(), name='retrieve-string'),
    
    # DELETE /api/strings/<str:string_value>/ -> Delete specific string analysis
    path('strings/<path:string_value>/', DeleteStringView.as_view(), name='delete-string'),
]
