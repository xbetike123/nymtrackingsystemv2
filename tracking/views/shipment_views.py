import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from tracking.forms import ShipmentForm
from tracking.models import Shipment, ShipmentCustomer

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
                    # Normalize keys: lowercase, strip spaces, and replace spaces with underscores
                    normalized_row = {
                        k.strip().lower().replace(" ", "_"): v.strip()
                        for k, v in row.items()
                    }

                    print("Saving row:", normalized_row)  # ✅ Debug print

                    ShipmentCustomer.objects.create(
                        shipment=shipment,
                        name=normalized_row.get('customer_name', ''),
                        phone=normalized_row.get('customer_phone_number', ''),
                        email=normalized_row.get('customer_email', ''),
                        weight=float(normalized_row.get('weight', 0) or 0),
                        shipping_cost=float(normalized_row.get('shipping_cost_usd', 0) or 0),
                        clearing_cost=float(normalized_row.get('clearing_cost', 0) or 0),
                        total=float(normalized_row.get('total', 0) or 0),
                    )

            messages.success(request, "✅ Shipment and customers saved successfully.")
            return redirect('admin_dashboard')

        except Exception as e:
            messages.error(request, f"⚠️ Error: {e}")
            return redirect('add_shipment')

    return render(request, 'admin_views/add_shipment.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from tracking.forms import ShippingLocationForm

@login_required
def add_shipping_location(request):
    form = ShippingLocationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "✅ Shipping location added successfully.")
        return redirect('add_shipping_location')

    return render(request, 'admin_views/add_shipping_location.html', {'form': form})
from tracking.forms import ShippingStatusTemplateForm
from tracking.models import ShippingStatusTemplate

@login_required
def add_shipping_status(request):
    form = ShippingStatusTemplateForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        shipment_type = form.cleaned_data['shipment_type']
        status_labels = form.cleaned_data['status_labels']
        statuses = [s.strip() for s in status_labels.split(',') if s.strip()]
        for label in statuses:
            ShippingStatusTemplate.objects.create(shipment_type=shipment_type, label=label)
        messages.success(request, "✅ Shipping statuses added successfully.")
        return redirect('add_shipping_status')

    return render(request, 'admin_views/add_shipping_status.html', {'form': form})
from django.db.models import Q
from tracking.models import Shipment
from django.utils.timezone import now

@login_required
def view_shipments(request):
    search_query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('type', '')
    sort = request.GET.get('sort', 'created_at')

    shipments = Shipment.objects.all()

    if search_query:
        shipments = shipments.filter(
            Q(tracking_number__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    if filter_type:
        shipments = shipments.filter(shipment_type=filter_type)

    if sort == 'eta':
        shipments = shipments.order_by('eta')
    else:
        shipments = shipments.order_by('-created_at')

    return render(request, 'admin_views/view_shipments.html', {
        'shipments': shipments
    })
from django.shortcuts import get_object_or_404
from tracking.models import Shipment

@login_required
def delete_shipment(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)

    if request.method == 'POST':
        shipment.delete()
        messages.success(request, "✅ Shipment deleted successfully.")
        return redirect('view_shipments')

    return render(request, 'admin_views/confirm_delete.html', {'shipment': shipment})
from tracking.models import Shipment, ShipmentStatus

from tracking.models import Shipment, ShipmentStatus

def view_shipments(request):
    shipments = Shipment.objects.all().order_by('-id')  # Latest first

    for shipment in shipments:
        latest_status = ShipmentStatus.objects.filter(shipment=shipment).order_by('-timestamp').first()
        shipment.latest_status = latest_status.status if latest_status else None

    return render(request, 'admin_views/view_shipments.html', {
        'shipments': shipments,
    })
from tracking.models import Shipment, ShipmentStatus

def view_shipments(request):
    shipments = Shipment.objects.all().order_by('-id')

    for shipment in shipments:
        # Fetch latest status per shipment based on timestamp
        latest_status_obj = ShipmentStatus.objects.filter(shipment=shipment).order_by('-timestamp').first()
        shipment.latest_status = latest_status_obj.status if latest_status_obj else None

    return render(request, 'admin_views/view_shipments.html', {
        'shipments': shipments,
    })
