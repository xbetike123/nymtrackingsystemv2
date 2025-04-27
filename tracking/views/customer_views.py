from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from tracking.models import Shipment, ShipmentCustomer
import csv
import io

# ✅ View customers under a shipment
@login_required
def view_customers(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    customers = shipment.customers.all()
    return render(request, 'admin_views/view_customers.html', {
        'shipment': shipment,
        'customers': customers
    })

# ✅ Add new user via admin_views panel
@login_required
def add_user_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_level = request.POST.get('user_level')  # "superadmin" or "staff"

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, password=password)
            user.is_staff = True
            user.is_superuser = (user_level == 'superadmin')
            user.save()
            messages.success(request, "User created successfully.")
            return redirect('add_user')

    return render(request, 'admin_views/add_user.html')

# ✅ (Optional Utility) Upload customers via CSV file
@login_required
def upload_customers_csv(request, shipment):
    csv_file = request.FILES.get('customer_csv')
    if not csv_file:
        return

    decoded_file = csv_file.read().decode('utf-8')
    io_string = io.StringIO(decoded_file)
    reader = csv.DictReader(io_string)

    for row in reader:
        ShipmentCustomer.objects.create(
            shipment=shipment,
            name=row.get('customer name', '').strip(),
            phone=row.get('customer phone number', '').strip(),
            weight=float(row.get('weight', 0) or 0),
            shipping_cost=float(row.get('shipping cost', 0) or 0),
            clearing_cost=float(row.get('clearing cost', 0) or 0),
            total=float(row.get('total payable', 0) or 0),
        )
