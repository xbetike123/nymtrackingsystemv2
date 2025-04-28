from django import template

register = template.Library()

@register.simple_tag
def shipment_label(shipment):
    """
    Returns a formatted label: tracking_number — created_at date
    """
    if shipment.created_at:
        formatted_date = shipment.created_at.strftime("%d %B %Y")  # example: 22 April 2025
        return f"{shipment.tracking_number} — {formatted_date}"
    else:
        return shipment.tracking_number
