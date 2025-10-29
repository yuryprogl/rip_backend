from django.urls import path
from .views import *

urlpatterns = [
    path('api/elements/', search_elements),  # GET
    path('api/elements/<int:element_id>/', get_element_by_id),  # GET
    path('api/elements/<int:element_id>/update/', update_element),  # PUT
    path('api/elements/<int:element_id>/update_image/', update_element_image),  # POST
    path('api/elements/<int:element_id>/delete/', delete_element),  # DELETE
    path('api/elements/create/', create_element),  # POST
    path('api/elements/<int:element_id>/add_to_forecast/', add_element_to_forecast),  # POST

    path('api/forecasts/', search_forecasts),  # GET
    path('api/forecasts/cart/', get_cart_info),  # GET
    path('api/forecasts/<int:forecast_id>/', get_forecast_by_id),  # GET
    path('api/forecasts/<int:forecast_id>/update/', update_forecast),  # PUT
    path('api/forecasts/<int:forecast_id>/update_status_user/', update_status_user),  # PUT
    path('api/forecasts/<int:forecast_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/forecasts/<int:forecast_id>/delete/', delete_forecast),  # DELETE

    path('api/forecasts/<int:forecast_id>/update_element/<int:element_id>/', update_element_in_forecast),  # PUT
    path('api/forecasts/<int:forecast_id>/delete_element/<int:element_id>/', delete_element_from_forecast),  # DELETE

    path('api/users/register/', register), # POST
    path('api/users/<int:user_id>/update/', update_user), # PUT
    path("api/users/info/", user_info), # GET
    path('api/users/login/', login), # POST
    path('api/users/logout/', logout), # POST
]
