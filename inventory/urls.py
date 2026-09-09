from django.urls import path
from . import views


urlpatterns = [

    # Vehicle Inventory
    path(
        'vehicles/',
        views.vehicle_list,
        name='vehicle_list'
    ),

    # Dashboard
    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    # Existing APIs
    path(
        'api/models/<int:brand_id>/',
        views.get_models,
        name='get_models'
    ),

    path(
        'api/variants/<int:model_id>/',
        views.get_variants,
        name='get_variants'
    ),
]