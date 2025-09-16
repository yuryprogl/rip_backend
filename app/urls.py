from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('elements/<int:element_id>/', element_page),
    path('calculations/<int:calculation_id>/', calculation_page),
]