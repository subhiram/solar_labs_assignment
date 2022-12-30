from .views import country_info
from django.urls import path

urlpatterns = [
    path('country_info/<str:pk>/', country_info.as_view()),
]