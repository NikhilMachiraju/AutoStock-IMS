from django.shortcuts import render
from .models import Customer


def customer_list(request):
    customers = Customer.objects.all()

    total_customers = customers.count()
    individual_customers = customers.filter(
        customer_type="INDIVIDUAL"
    ).count()
    business_customers = customers.filter(
        customer_type="BUSINESS"
    ).count()
    active_customers = customers.filter(
        status="ACTIVE"
    ).count()

    return render(
        request,
        "customers/customer_list.html",
        {
            "customers": customers,
            "total_customers": total_customers,
            "individual_customers": individual_customers,
            "business_customers": business_customers,
            "active_customers": active_customers,
        }
    )