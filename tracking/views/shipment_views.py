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
                    # Normalize keys: lowercase, strip spaces, replace spaces with underscores
                    normalized_row = {
                        k.strip().lower().replace(" ", "_"): v.strip()
                        for k, v in row.items()
                    }

                    print("Saving row:", normalized_row)  # ✅ Debug print

                    ShipmentCustomer.objects.create(
                        shipment=shipment,
                        name=normalized_row.get('customer_name', ''),
                        phone=normalized_row.get('customer_phone', ''),  # ✅ Corrected here
                        email=normalized_row.get('customer_email', ''),
                        weight=float(normalized_row.get('weight', 0) or 0),
                        shipping_cost=float(normalized_row.get('shipping_cost', 0) or 0),
                        clearing_cost=float(normalized_row.get('clearing_cost', 0) or 0),
                        total=float(normalized_row.get('total', 0) or 0),
                    )

            messages.success(request, "✅ Shipment and customers saved successfully.")
            return redirect('admin_dashboard')

        except Exception as e:
            messages.error(request, f"⚠️ Error: {e}")
            return redirect('add_shipment')

    return render(request, 'admin_views/add_shipment.html', {'form': form})
