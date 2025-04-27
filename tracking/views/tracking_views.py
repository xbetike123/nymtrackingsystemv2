from django.shortcuts import render, get_object_or_404
from django.utils.timezone import localtime, is_naive, make_aware
from pytz import timezone as pytz_timezone
from tracking.models import Shipment

def track_shipment(request):
    tracking_number = request.GET.get('tracking_number')
    shipment = None
    error = None
    enriched_statuses = []

    if tracking_number:
        try:
            shipment = Shipment.objects.get(tracking_number=tracking_number)
            wat = pytz_timezone('Africa/Lagos')
            for status in shipment.statuses.all():
                ts = status.timestamp
                if is_naive(ts):
                    ts = make_aware(ts)
                status.local_time = localtime(ts, wat)
                enriched_statuses.append(status)
        except Shipment.DoesNotExist:
            error = "No shipment found with that admin_views number."

    return render(request, 'admin_views/track_result.html' if shipment else 'admin_views/track_shipment.html', {
        'shipment': shipment,
        'statuses': enriched_statuses,
        'error': error
    } if shipment or error else {})
