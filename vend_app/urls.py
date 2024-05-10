from django.urls import path
from .views import *

urlpatterns = [
    path('api/vendor-profiles/', vendor_profile_list_create, name='vendor-profile-list-create'),
    path('api/vendor-profiles/<int:vendor_id>/', vendor_profile_detail, name='vendor-profile-detail'),
    path('api/purchase_orders/', purchase_order_list_create, name='purchase-order-list-create'),
    path('api/purchase_orders/<int:po_id>/', purchase_order_detail, name='purchase-order-detail'),
    path('calculate-on-time-delivery-rate/', OnTimeDeliveryRateAPIView.as_view(), name='calculate_on_time_delivery_rate'),
    path('api/vendors/<int:vendor_id>/performance/', VendorPerformanceAPIView.as_view(), name='vendor_performance'),
    path('api/vendors/<int:vendor_id>/vendor_performance/', VendorPerformanceAPIView.as_view(), name='vendor_performance'),
    path('api/purchase_orders/<int:po_id>/acknowledge/', AcknowledgePurchaseOrderAPIView.as_view(), name='acknowledge_purchase_order'),

]