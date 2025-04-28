import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from tracking.forms import ShipmentForm, ShippingLocationForm
from tracking.models import Shipment, ShipmentCustomer, ShippingLocation

# 1. Add Shipment
@login_required
def add_shipment(request):
    form = ShipmentForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        try:
            shipment = form.save()

            csv_file = request.FILES.get('customer_csv')
            if csv_file:
                decoded_file = csv_file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))

                for row in reader:
                    normalized_row = {
                        k.strip().lower().replace(" ", "_"): v.strip()
                        for k, v in row.items()
                    }

                    ShipmentCustomer.objects.create(
                        shipment=shipment,
                        name=normalized_row.get('customer_name', ''),
                        phone=normalized_row.get('customer_phone', ''),
                        email=normalized_row.get('customer_email', ''),
                        weight=float(normalized_row.get('weight', 0) or 0),
                        shipping_cost=float(normalized_row.get('shipping_cost', 0) or 0),
                        clearing_cost=float(normalized_row.get('clearing_cost', 0) or 0),
                        total=float(normalized_row.get('total', 0) or 0),
                    )

            messages.success(request, "✅ Shipment and customers saved successfully.")
            return redirect('view_shipments')

        except Exception as e:
            messages.error(request, f"⚠️ Error: {e}")
            return redirect('add_shipment')

    return render(request, 'admin_views/add_shipment.html', {'form': form})

# 2. Add Shipping Location
@login_required
def add_shipping_location(request):
    form = ShippingLocationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "✅ Shipping location added successfully.")
        return redirect('view_shipments')

    return render(request, 'admin_views/add_shipping_location.html', {'form': form})

# 3. View Shipments
@login_required
def view_shipments(request):
    shipments = Shipment.objects.all().order_by('-created_at')
    return render(request, 'admin_views/view_shipments.html', {'shipments': shipments})

# 4. Delete Shipment
@login_required
def delete_shipment(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    shipment.delete()
    messages.success(request, "✅ Shipment deleted successfully.")
    return redirect('view_shipments')

# 5. Edit Shipment
@login_required
def edit_shipment(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    form = ShipmentForm(request.POST or None, instance=shipment)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "✅ Shipment updated successfully.")
        return redirect('view_shipments')

    return render(request, 'admin_views/edit_shipment.html', {'form': form, 'shipment': shipment})

# 6. View Customers under a Shipment
@login_required
def view_customers(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    customers = ShipmentCustomer.objects.filter(shipment=shipment)
    return render(request, 'admin_views/view_customers.html', {'shipment': shipment, 'customers': customers})

# 7. Delete Customer
@login_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(ShipmentCustomer, id=customer_id)
    shipment_id = customer.shipment.id
    customer.delete()
    messages.success(request, "✅ Customer deleted successfully.")
    return redirect('view_customers', shipment_id=shipment_id)
