from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tracking.models import Shipment, ShipmentCustomer
from tracking.forms import ShipmentForm
import csv
import io


@login_required
def add_shipment(request):
    print("🚀 Reached add_shipment view (REAL ONE)")

    form = ShipmentForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        print("📥 POST received:", request.POST)
        print("📎 FILE received:", request.FILES)

        if form.is_valid():
            shipment = form.save()
            print("✅ Shipment created:", shipment)

            csv_file = request.FILES.get('customer_csv')
            if csv_file:
                print("🟢 CSV FILE RECEIVED:", csv_file.name)
                decoded_file = csv_file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))

                for row in reader:
                    normalized_row = {k.strip().lower(): v.strip() for k, v in row.items()}
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

            messages.success(request, "✅ Shipment and customers uploaded successfully.")
            return redirect('view_shipments')

        else:
            print("❌ Form errors:", form.errors)

    return render(request, 'admin_views/add_shipment.html', {'form': form})


from tracking.forms import ShippingStatusTemplateForm
from tracking.models import ShippingStatusTemplate


@login_required
def add_shipping_status(request):
    form = ShippingStatusTemplateForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        shipment_type = form.cleaned_data['shipment_type']
        labels = [label.strip() for label in form.cleaned_data['status_labels'].split(',') if label.strip()]

        for label in labels:
            ShippingStatusTemplate.objects.create(shipment_type=shipment_type, label=label)

        messages.success(request, "✅ Shipping statuses added successfully.")
        return redirect('admin_dashboard')

    return render(request, 'admin_views/add_shipping_status.html', {'form': form})
from django.shortcuts import render, get_object_or_404
from tracking.models import Shipment

@login_required
def shipment_history_view(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    status_history = shipment.statuses.order_by('-timestamp')  # Most recent first

    return render(request, 'admin_views/shipment_history.html', {
        'shipment': shipment,
        'status_history': status_history
    })
from tracking.forms import ShipmentStatusForm
from tracking.models import ShipmentStatus
from django.contrib import messages

@login_required
def update_shipment_status(request):
    form = ShipmentStatusForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        ShipmentStatus.objects.create(
            shipment=form.cleaned_data['shipment'],
            location=form.cleaned_data['location'],
            status=form.cleaned_data['status']
        )
        messages.success(request, "✅ Shipment status updated successfully.")
        return redirect('shipment_history_view', shipment_id=form.cleaned_data['shipment'].id)

    return render(request, 'admin_views/update_status.html', {'form': form})
from django.http import JsonResponse
from tracking.models import Shipment, ShipmentStatus, ShippingStatusTemplate

@login_required
def shipment_options_api(request):
    shipment_id = request.GET.get('id')

    try:
        shipment = Shipment.objects.get(id=shipment_id)

        all_statuses = set(
            ShippingStatusTemplate.objects.filter(shipment_type=shipment.shipment_type)
            .values_list('label', flat=True)
        )

        used_statuses = set(
            ShipmentStatus.objects.filter(shipment=shipment)
            .values_list('status', flat=True)
        )

        remaining_statuses = sorted(list(all_statuses - used_statuses))

        return JsonResponse({'statuses': remaining_statuses})

    except Shipment.DoesNotExist:
        return JsonResponse({'statuses': []}, status=404)
from tracking.models import ShippingStatusTemplate

@login_required
def view_shipping_status_templates(request):
    templates = ShippingStatusTemplate.objects.all().order_by('shipment_type', 'label')
    return render(request, 'admin_views/view_status_templates.html', {
        'templates': templates
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from tracking.models import ShippingStatusTemplate

@login_required
def view_shipping_status_templates(request):
    templates = ShippingStatusTemplate.objects.all()
    return render(request, 'admin_views/view_status_templates.html', {'templates': templates})
