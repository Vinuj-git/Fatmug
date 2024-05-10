# from datetime import timezone
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import VendorProfile,PurchaseOrder,HistoricalPerformance
from rest_framework.views import APIView
from rest_framework import status
from .serializers import VendorProfileSerializer,PurchaseOrderSerializer,OnTimeDeliveryRateSerializer,HistoricalPerformanceSerializer
# from vend_app import models
from django.db.models import F
from django.utils import timezone

@api_view(['GET', 'POST'])
def vendor_profile_list_create(request):
    if request.method == 'GET':
        vendor_profiles = VendorProfile.objects.all()
        serializer = VendorProfileSerializer(vendor_profiles, many=True)
        return Response({'message': 'Vendor profiles retrieved successfully', 'data': serializer.data})
    
    elif request.method == 'POST':
        serializer = VendorProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Vendor profile created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET', 'PUT', 'DELETE'])
def vendor_profile_detail(request, vendor_id):
    try:
        vendor = VendorProfile.objects.get(pk=vendor_id)
    except VendorProfile.DoesNotExist:
        return Response({'error': 'Vendor does not exist'}, status=status.HTTP_404_NOT_FOUND)


    if request.method == 'GET':
        serializer = VendorProfileSerializer(vendor)
        return Response({'message': 'Vendor profile retrieved successfully', 'data': serializer.data})

    elif request.method == 'PUT':
        serializer = VendorProfileSerializer(vendor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Vendor profile updated successfully', 'data': serializer.data})
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        vendor.delete()
        return Response({'message': 'Vendor profile deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

@api_view(['POST', 'GET'])
def purchase_order_list_create(request):
    if request.method == 'GET':
        vendor = request.GET.get('vendor', None)
        if vendor:
            purchase_orders = PurchaseOrder.objects.filter(vendor_reference=vendor)
        else:
            purchase_orders = PurchaseOrder.objects.all()
        serializer = PurchaseOrderSerializer(purchase_orders, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PurchaseOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def purchase_order_detail(request, po_id):
    try:
        purchase_order = PurchaseOrder.objects.get(pk=po_id)
    except PurchaseOrder.DoesNotExist:
        return Response({'error': 'Purchase order does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PurchaseOrderSerializer(purchase_order)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PurchaseOrderSerializer(purchase_order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        purchase_order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from django.db.models import F

class OnTimeDeliveryRateAPIView(APIView):
    serializer_class = OnTimeDeliveryRateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            vendor_code = serializer.validated_data['vendor_code']
            completed_pos = PurchaseOrder.objects.filter(vendor_reference__vendor_code=vendor_code, status='True', delivery_date__lte=F('acknowledgment_date')).count()
            print("************",completed_pos)
            total_completed_pos = PurchaseOrder.objects.filter(vendor_reference__vendor_code=vendor_code, status='True').count()
            print("============",total_completed_pos)
            if total_completed_pos == 0:
                return Response({'on_time_delivery_rate': 0})
            on_time_delivery_rate = completed_pos / total_completed_pos * 100
            return Response({'on_time_delivery_rate': on_time_delivery_rate})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorPerformanceAPIView(APIView):
    def get(self, request, vendor_id):
        try:
            vendor = VendorProfile.objects.get(id=vendor_id)
        except VendorProfile.DoesNotExist:
            return Response({'error': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)
        
        performances = HistoricalPerformance.objects.filter(vendor=vendor)
        serializer = HistoricalPerformanceSerializer(performances, many=True)
        return Response(serializer.data)
    
class VendorPerformanceAPIView(APIView):
    def get(self, request, vendor_id):
        try:
            vendor = VendorProfile.objects.get(id=vendor_id)
        except VendorProfile.DoesNotExist:
            return Response({'error': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)
        
        data = {
            'on_time_delivery_rate': vendor.on_time_delivery_rate,
            'quality_rating_avg': vendor.quality_rating_avg,
            'average_response_time': vendor.average_response_time,
            'fulfillment_rate': vendor.fulfillment_rate,
        }
        return Response(data)
    

class AcknowledgePurchaseOrderAPIView(APIView):
    def post(self, request, po_id):
        try:
            purchase_order = PurchaseOrder.objects.get(id=po_id)
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'Purchase order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        purchase_order.acknowledgment_date = timezone.now()  # Assuming you import timezone
        purchase_order.save()

        return Response({'message': 'Purchase order acknowledged successfully'}, status=status.HTTP_200_OK)