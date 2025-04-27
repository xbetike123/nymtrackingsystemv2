from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from tracking.models import Shipment, ShipmentStatus, ShippingStatusTemplate, ShipmentCustomer, NotificationLog
from tracking.forms import ShippingLocationForm, ShippingStatusTemplateForm, ShipmentStatusForm, ShipmentForm
import csv
import io


@login_required
def add_shipment(request):
    print("🚀 Reached add_shipment view")  # Debug entry point

    form = ShipmentForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        print("📥 POST received:", request.POST)
        print("📎 FILE received:", request.FILES)

        print("⚠️ Skipping form.is_valid() for debugging")

        # TEMP: create the shipment record without validation
        shipment = Shipment.objects.create(
            shipment_type=request.POST.get('shipment_type'),
            location=request.POST.get('location'),
            tracking_number=request.POST.get('tracking_number'),
            eta=request.POST.get('eta')
        )

        # Process uploaded CSV for customers
        csv_file = request.FILES.get('customer_csv')
        if csv_file:
            print("🟢 CSV FILE RECEIVED:", csv_file.name)
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            for row in reader:
                # Normalize keys
                normalized_row = {key.strip().lower(): value.strip() for key, value in row.items()}
                print("Row being saved:", normalized_row)

                ShipmentCustomer.objects.create(
                    shipment=shipment,
                    name=normalized_row.get('customer_name', ''),
                    phone=normalized_row.get('customer_phone', ''),
                    email=normalized_row.get('customer_email', ''),
                    weight=float(normalized_row.get('weight', 0) or 0),
                    shipping_cost=float(normalized_row.get('shipping_cost_usd', 0) or 0),
                    clearing_cost=float(normalized_row.get('clearing_cost', 0) or 0),
                    total=float(normalized_row.get('total', 0) or 0),
                )

        messages.success(request, "Shipment and client list uploaded successfully.")
        return redirect('admin_dashboard')

    return render(request, 'admin_views/add_shipment.html', {'form': form})


from django.shortcuts import render, get_object_or_404
from tracking.models import Shipment
from django.contrib.auth.decorators import login_required

@login_required
def view_customers(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    customers = shipment.customers.all()

    print(f"📦 Shipment #{shipment.id} - {shipment.tracking_number}")
    print(f"👥 Total customers: {customers.count()}")

    for customer in customers:
        print(f"➡️ {customer.name} | {customer.phone} | {customer.email} | Weight: {customer.weight}")

    return render(request, 'admin_views/view_customers.html', {
        'shipment': shipment,
        'customers': customers
    })
from django.shortcuts import render

def cbm_calculator(request):
    return render(request, 'cbm_calculator.html')

def address_generator(request):
    return render(request, 'address_generator.html')

def contact_us(request):
    return render(request, 'contact_us.html')
