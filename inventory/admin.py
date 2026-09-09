from django import forms
from django.contrib import admin
from .models import Brand, CarModel, Variant, Vehicle, VehicleMovement

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand')
    list_filter = ('brand',)
    search_fields = ('name', 'brand__name')


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'car_model',
        'get_brand',
    )

    list_filter = (
        'car_model__brand',
        'car_model',
    )

    search_fields = (
        'name',
        'car_model__name',
        'car_model__brand__name',
    )

    ordering = (
        'car_model__brand',
        'car_model',
        'name',
    )

    def get_brand(self, obj):
        return obj.car_model.brand.name

    get_brand.short_description = 'Brand'

class VehicleAdminForm(forms.ModelForm):

    class Meta:
        model = Vehicle
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show ALL car models
        self.fields['car_model'].queryset = CarModel.objects.all()

        # Show ALL variants
        self.fields['vehicle_variant'].queryset = Variant.objects.all()

    def clean_vin_number(self):
        vin_number = self.cleaned_data.get('vin_number')

        if vin_number:
            queryset = Vehicle.objects.filter(
                vin_number=vin_number
            )

            if self.instance.pk:
                queryset = queryset.exclude(
                    pk=self.instance.pk
                )

            if queryset.exists():
                raise forms.ValidationError(
                    'A vehicle with this VIN number already exists.'
                )

        return vin_number

    def clean_registration_number(self):
        registration_number = self.cleaned_data.get(
            'registration_number'
        )

        if registration_number:
            queryset = Vehicle.objects.filter(
                registration_number=registration_number
            )

            if self.instance.pk:
                queryset = queryset.exclude(
                    pk=self.instance.pk
                )

            if queryset.exists():
                raise forms.ValidationError(
                    'A vehicle with this registration number already exists.'
                )

        return registration_number

    def clean_engine_number(self):
        engine_number = self.cleaned_data.get(
            'engine_number'
        )

        if engine_number:
            queryset = Vehicle.objects.filter(
                engine_number=engine_number
            )

            if self.instance.pk:
                queryset = queryset.exclude(
                    pk=self.instance.pk
                )

            if queryset.exists():
                raise forms.ValidationError(
                    'A vehicle with this engine number already exists.'
                )

        return engine_number

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):

    form = VehicleAdminForm

    list_display = (
        'vin_number',
        'brand',
        'car_model',
        'vehicle_variant',
        'manufacturing_year',
        'selling_price',
        'status',
        'mileage',
        'location',
        'current_location',
    )

    list_filter = (
        'brand',
        'car_model',
        'vehicle_variant',
        'fuel_type',
        'transmission',
        'status',
        'manufacturing_year',
        'is_featured',
        'current_location',
    )

    search_fields = (
        'vin_number',
        'registration_number',
        'engine_number',
        'variant',
        'vehicle_variant__name',
        'color',
        'location',
        'brand__name',
        'car_model__name',
    )

    ordering = ('-created_at',)

    list_per_page = 20

    fieldsets = (

        (
            'Vehicle Identification',
            {
                'fields': (
                    'vin_number',
                    'registration_number',
                    'engine_number',
                )
            }
        ),

        (
            'Vehicle Information',
            {
                'fields': (
                    'brand',
                    'car_model',
                    'vehicle_variant',
                    'manufacturing_year',
                    'color',
                    'fuel_type',
                    'transmission',
                    'mileage',
                )
            }
        ),

        (
            'Financial Information',
            {
                'fields': (
                    'purchase_price',
                    'selling_price',
                    'profit',
                )
            }
        ),

        (
            'Inventory Information',
            {
                'fields': (
                    'status',
                    'location',
                    'current_location',
                    'arrival_date',
                    'is_featured',
                )
            }
        ),

        (
            'Ownership & Registration',
            {
                'fields': (
                    'ownership_count',
                    'purchase_date',
                    'registration_date',
                )
            }
        ),

        (
            'Documents',
            {
                'fields': (
                    'insurance_expiry',
                    'puc_expiry',
                )
            }
        ),

        (
            'Media & Description',
            {
                'fields': (
                    'image_url',
                    'description',
                )
            }
        ),

        (
            'System Information',
            {
                'fields': (
                    'created_at',
                    'updated_at',
                )
            }
        ),
    )

    readonly_fields = (
        'profit',
        'created_at',
        'updated_at',
    )

@admin.register(VehicleMovement)
class VehicleMovementAdmin(admin.ModelAdmin):

    list_display = (
        'vehicle',
        'from_location',
        'to_location',
        'transfer_date',
        'reason',
    )

    list_filter = (
        'from_location',
        'to_location',
        'transfer_date',
    )

    search_fields = (
        'vehicle__vin_number',
        'vehicle__registration_number',
        'reason',
        'remarks',
    )

    readonly_fields = (
        'transfer_date',
        'created_at',
    )

    ordering = (
        '-transfer_date',
    )    