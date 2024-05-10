# serializers.py
from rest_framework import serializers
from .models import VendorProfile,PurchaseOrder,HistoricalPerformance



class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = '__all__'

class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

class HistoricalPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalPerformance
        fields = '__all__'


class OnTimeDeliveryRateSerializer(serializers.Serializer):
    vendor_code = serializers.CharField(max_length=20)