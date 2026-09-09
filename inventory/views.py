from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Brand, CarModel, Variant, Vehicle


# ============================================================
# API: GET MODELS
# ============================================================

def get_models(request):

    brand_id = request.GET.get('brand')

    models = CarModel.objects.filter(
        brand_id=brand_id
    ).order_by('name')

    data = {
        'models': [
            {
                'id': model.id,
                'name': model.name,
            }
            for model in models
        ]
    }

    return JsonResponse(data)


# ============================================================
# API: GET VARIANTS
# ============================================================

def get_variants(request):

    model_id = request.GET.get('model')

    variants = Variant.objects.filter(
        car_model_id=model_id
    ).order_by('name')

    data = {
        'variants': [
            {
                'id': variant.id,
                'name': variant.name,
            }
            for variant in variants
        ]
    }

    return JsonResponse(data)


# ============================================================
# VEHICLE INVENTORY
# SEARCH + FILTER + PAGINATION
# ============================================================

def vehicle_list(request):

    vehicles = Vehicle.objects.select_related(
        'brand',
        'car_model',
        'vehicle_variant',
        'current_location',
    ).all().order_by('-created_at')

    # ========================================================
    # SEARCH
    # ========================================================

    search = request.GET.get('search', '').strip()

    if search:

        vehicles = vehicles.filter(
            Q(vin_number__icontains=search)
            | Q(registration_number__icontains=search)
            | Q(engine_number__icontains=search)
            | Q(color__icontains=search)
            | Q(brand__name__icontains=search)
            | Q(car_model__name__icontains=search)
            | Q(vehicle_variant__name__icontains=search)
        )

    # ========================================================
    # BRAND FILTER
    # ========================================================

    selected_brand = request.GET.get('brand', '').strip()

    if selected_brand:

        vehicles = vehicles.filter(
            brand_id=selected_brand
        )

    # ========================================================
    # MODEL FILTER
    # ========================================================

    selected_model = request.GET.get('model', '').strip()

    if selected_model:

        vehicles = vehicles.filter(
            car_model_id=selected_model
        )

    # ========================================================
    # STATUS FILTER
    # ========================================================

    selected_status = request.GET.get('status', '').strip()

    if selected_status:

        vehicles = vehicles.filter(
            status=selected_status
        )

    # ========================================================
    # PAGINATION
    # ========================================================

    paginator = Paginator(
        vehicles,
        10
    )

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(
        page_number
    )

    # ========================================================
    # FILTER DATA
    # ========================================================

    brands = Brand.objects.all().order_by('name')

    car_models = CarModel.objects.all().order_by('name')

    status_choices = Vehicle.STATUS_CHOICES

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {

        'page_obj': page_obj,

        'brands': brands,

        'car_models': car_models,

        'status_choices': status_choices,

        'search': search,

        'selected_brand': selected_brand,

        'selected_model': selected_model,

        'selected_status': selected_status,
    }

    return render(
        request,
        'inventory/vehicle_list.html',
        context
    )


# ============================================================
# DASHBOARD
# ============================================================

@login_required(login_url="accounts:login")
def dashboard(request):

    from django.db.models import Sum
    from locations.models import Location
    from .models import VehicleMovement

    vehicles = Vehicle.objects.all()

    total_vehicles = vehicles.count()

    in_stock_vehicles = vehicles.filter(
        status='IN_STOCK'
    ).count()

    in_transit_vehicles = vehicles.filter(
        status='IN_TRANSIT'
    ).count()

    reserved_vehicles = vehicles.filter(
        status='RESERVED'
    ).count()

    test_drive_vehicles = vehicles.filter(
        status='TEST_DRIVE'
    ).count()

    sold_vehicles = vehicles.filter(
        status='SOLD'
    ).count()

    delivered_vehicles = vehicles.filter(
        status='DELIVERED'
    ).count()

    service_vehicles = vehicles.filter(
        status='SERVICE'
    ).count()

    damaged_vehicles = vehicles.filter(
        status='DAMAGED'
    ).count()

    active_locations = Location.objects.filter(
        is_active=True
    ).count()

    total_movements = VehicleMovement.objects.count()

    purchase_value = (
        vehicles.aggregate(
            total=Sum('purchase_price')
        )['total'] or 0
    )

    selling_value = (
        vehicles.aggregate(
            total=Sum('selling_price')
        )['total'] or 0
    )

    expected_profit = (
        selling_value - purchase_value
    )

    recent_vehicles = Vehicle.objects.select_related(
        'brand',
        'car_model',
        'vehicle_variant',
        'current_location'
    ).order_by('-created_at')[:5]

    recent_movements = VehicleMovement.objects.select_related(
        'vehicle',
        'from_location',
        'to_location'
    ).order_by('-transfer_date')[:5]

    context = {

        'total_vehicles': total_vehicles,

        'in_stock_vehicles': in_stock_vehicles,

        'in_transit_vehicles': in_transit_vehicles,

        'reserved_vehicles': reserved_vehicles,

        'test_drive_vehicles': test_drive_vehicles,

        'sold_vehicles': sold_vehicles,

        'delivered_vehicles': delivered_vehicles,

        'service_vehicles': service_vehicles,

        'damaged_vehicles': damaged_vehicles,

        'active_locations': active_locations,

        'total_movements': total_movements,

        'purchase_value': purchase_value,

        'selling_value': selling_value,

        'expected_profit': expected_profit,

        'recent_vehicles': recent_vehicles,

        'recent_movements': recent_movements,
    }

    return render(
        request,
        'inventory/dashboard.html',
        context
    )