from django.urls import path
from tracking.frontend_views import cbm_calculator, address_generator, contact_us
from tracking.views import (
    tracking_views,
    auth_views,
    dashboard_views,
    shipment_views,
    status_views,
    customer_views,
    notification_views,
    quote_views,
    billings_views,
    newsletter_views
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Public access
    path('', tracking_views.track_shipment, name='home'),  # ✅ Form submission (POST)
    path('track/', tracking_views.track_shipment, name='track_shipment'),  # ✅ URL query tracking (GET)

    path('cbm-calculator/', cbm_calculator, name='cbm_calculator'),
    path('address-generator/', address_generator, name='address_generator'),
    path('contact-us/', contact_us, name='contact_us'),

    # Authentication
    path('login/', auth_views.login_view, name='login_view'),
    path('logout/', auth_views.logout_view, name='logout_view'),

    # Dashboard
    path('admin/', dashboard_views.admin_dashboard, name='admin_dashboard'),
    path('admin/coming-soon/', dashboard_views.dummy_view, name='coming_soon'),

    # Shipment Management
    path('admin/add-shipping-location/', shipment_views.add_shipping_location, name='add_shipping_location'),
    path('admin/add-shipment-status/', status_views.add_shipping_status, name='add_shipment_status'),
    path('admin/add-shipment/', shipment_views.add_shipment, name='add_shipment'),
    path('admin/shipments/', shipment_views.view_shipments, name='view_shipments'),
    path('admin/shipments/delete/<int:shipment_id>/', shipment_views.delete_shipment, name='delete_shipment'),

    # Status Tracking
    path('admin/shipment-history/<int:shipment_id>/', status_views.shipment_history_view, name='shipment_history_view'),
    path('admin/update-status/', status_views.update_shipment_status, name='update_shipment_status'),
    path('api/shipment-options/', status_views.shipment_options_api, name='shipment_options_api'),

    # Customer Management
    path('admin/view-customers/<int:shipment_id>/', customer_views.view_customers, name='view_customers'),
    path('admin/add-user/', customer_views.add_user_view, name='add_user'),

    # Notifications
    path('admin/send-notification/', notification_views.send_notifications_view, name='send_notification'),
    path('admin/preview-notification/', notification_views.preview_notification_view, name='preview_notification'),
    path('admin/send-messages/', notification_views.send_notifications, name='send_notifications'),

    # Tools
    path('admin/quote/', quote_views.instant_quote_view, name='instant_quote'),
    path('admin/shipping-billing/', billings_views.shipping_billing_view, name='shipping_billing'),
    path('api/customers/', billings_views.fetch_customers_api, name='fetch_customers_api'),
    path('api/get-customers/', billings_views.fetch_customers_api, name='get_customers'),
    path('admin/shipping-billing/preview/', billings_views.shipping_billing_preview, name='shipping_billing_preview'),
    path('admin/shipping-billing-preview/', billings_views.shipping_billing_preview, name='shipping_billing_preview'),
    path('admin/view-status-templates/', status_views.view_shipping_status_templates, name='view_status_templates'),
    path('admin/send-shipping-bill/', billings_views.send_shipping_bill, name='send_shipping_bill'),
    path('admin/delivery-status/', dashboard_views.delivery_status_view, name='delivery_status'),

    # Newsletter Management
    path('admin/upload-subscribers/', newsletter_views.upload_subscribers_view, name='upload_subscribers'),
    path('admin/assign-segment/', newsletter_views.assign_segment_view, name='assign_segment'),
    path('admin/send-newsletter/', newsletter_views.send_newsletter_view, name='send_newsletter'),
    path('admin/create-segment/', newsletter_views.create_segment_view, name='create_segment'),
    path('admin/newsletter-dashboard/', newsletter_views.newsletter_dashboard_view, name='newsletter_dashboard'),
    path('admin/all-subscribers/', newsletter_views.view_all_subscribers_view, name='view_all_subscribers'),
    path('admin/bulk-action/', newsletter_views.bulk_action_subscribers_view, name='bulk_action_subscribers'),

    # Segments
    path('admin/segments/', newsletter_views.view_segments, name='view_segments'),
    path('admin/segments/create/', newsletter_views.create_segment_view, name='create_segment'),
    path('admin/segments/<int:segment_id>/subscribers/', newsletter_views.view_segment_subscribers, name='view_segment_subscribers'),
    path('admin/segments/<int:segment_id>/bulk-remove/', newsletter_views.bulk_remove_from_segment, name='bulk_remove_from_segment'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
