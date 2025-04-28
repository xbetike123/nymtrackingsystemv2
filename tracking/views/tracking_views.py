from django.shortcuts import render
from django.utils.timezone import localtime, is_naive, make_aware
from pytz import timezone as pytz_timezone
from tracking.models import Shipment

def track_shipment(request):
    print("✅ track_shipment view called!")  # Debug

    if request.method == "POST":
        tracking_number = request.POST.get('tracking_number')
    else:
        tracking_number = request.GET.get('tracking_number')

    if tracking_number:
        tracking_number = tracking_number.strip()

    print("🚀 Submitted Tracking Number:", repr(tracking_number))  # ✅ PRINT FULL RAW STRING

    shipment = None
    error = None
    enriched_statuses = []

    # PRINT ALL tracking numbers in DB for comparison
    print("\n📦 All Shipments in Database:")
    for s in Shipment.objects.all():
        print(f"- DB: {repr(s.tracking_number)}")

    if tracking_number:
        try:
            shipment = Shipment.objects.get(tracking_number=tracking_number)
            print("✅ Shipment Found:", shipment.tracking_number)
            wat = pytz_timezone('Africa/Lagos')
            for status in shipment.statuses.all():
                ts = status.timestamp
                if is_naive(ts):
                    ts = make_aware(ts)
                status.local_time = localtime(ts, wat)
                enriched_statuses.append(status)
        except Shipment.DoesNotExist:
            print("❌ Shipment not found matching:", repr(tracking_number))
            error = "❌ Shipment not found for the provided tracking number."

    return render(
        request,
        'admin_views/track_result.html' if shipment else 'admin_views/track_shipment.html',
        {
            'shipment': shipment,
            'statuses': enriched_statuses,
            'error': error
        }
    )
