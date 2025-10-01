from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('elements/<int:element_id>/', element_page, name="element_page"),
    path('calculations/<int:calculation_id>/', calculation_page, name="calculation_page"),
    path('elements/<int:element_id>/add_to_calculation/', add_element_to_draft_calculation, name="add_element_to_draft_calculation"),
    path('calculations/<int:calculation_id>/delete/', delete_calculation, name="delete_calculation")
]
