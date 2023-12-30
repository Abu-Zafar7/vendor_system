from django.shortcuts import render,HttpResponse, get_object_or_404
from .serializers import CreateVendorSerializer, HistoricalPerformanceSerializer, CreatePurchaseOrderSerializer
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from rest_framework.decorators import api_view 
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.utils import timezone 
from django.db.models import F, Avg
from django.db import models


@api_view(['POST','GET'])
@csrf_exempt
def vendors(request):
    if request.method == 'POST':
        serializer = CreateVendorSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save()
        return Response({"message": "Vendor added", "vendor": serializer.data})
    

    if request.method == 'GET':
        vendors = Vendor.objects.all()
        data = [{'id': vendor.id, 'name': vendor.name, 'vendor_code': vendor.vendor_code, 'contact_details': vendor.contact_details, 'address':vendor.address } for vendor in vendors]
        return Response(data)

    return Response({'error': 'Invalid method'})



@api_view(['POST','GET','DELETE'])
@csrf_exempt
def update_get_delete_vendor(request,id):
    
    if request.method == 'POST':
        vendor = get_object_or_404(Vendor, id=id)
        serializer = CreateVendorSerializer(instance=vendor, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response({'message': 'Vendor updated successfully', 'vendor detail': serializer.data})
    
    if request.method == 'GET':
        vendor = get_object_or_404(Vendor, id=id)
        data = {
        'id': vendor.id,
        'name': vendor.name,
        'contact_details': vendor.contact_details,
        'address': vendor.address,
        'vendor_code': vendor.vendor_code,
    }
        return Response(data)
    
    if request.method == 'DELETE':
         vendor = get_object_or_404(Vendor, id=id)
         vendor.delete()
         return Response({'message': 'Vendor deleted successfully'})

    return Response({'error': 'Invalid method'})




@api_view(['POST','GET'])
@csrf_exempt
def create_get_purchase_order(request):
    if request.method == 'POST':
       serializer = CreatePurchaseOrderSerializer(data=request.data,context={'request': request})
       if serializer.is_valid():
           serializer.save()
       else:
           return Response({'error': serializer.errors})    
       return Response({'message': 'Order Placed!', 'order_details': serializer.data})
    
    if request.method == 'GET':
        purchase_orders = PurchaseOrder.objects.all()
        data = [{'po_id': po.id, 'po_number': po.po_number, 'vendor': po.vendor.name, 'status': po.status, 'order_date':po.order_date, 'delivery_date': po.delivery_date, 'items': po.items} for po in purchase_orders]
        return Response(data)
    return Response({'error': 'Invalid method'})



@api_view(['GET','POST','DELETE'])
@csrf_exempt
def retrieve_update_delete_purchase_order(request, id):
    if request.method == 'GET':
        po = get_object_or_404(PurchaseOrder, id=id)
        data = {
            'po_id': po.id,
            'po_number': po.po_number,
            'vendor': po.vendor.name,
            'order_date': po.order_date,
            'items': po.items,
            'quantity': po.quantity,
            'status': po.status,
            'delivery_date': po.delivery_date,
            'quality_rating': po.quality_rating,
            'issue_date': po.issue_date,
            'acknowledgment_date': po.acknowledgment_date,
        }
        return Response(data)
    
    if request.method == 'POST':
        po = get_object_or_404(PurchaseOrder, id=id)
        
        data = request.data  
        po.status = data.get('status', po.status)
        if po.status == 'completed':
            po.delivery_date = timezone.now()

        if 'acknowledgment_date' in data:
            po.acknowledgment_date = data['acknowledgment_date']

        po.save()

        
        vendor = po.vendor

    
        completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
        on_time_deliveries = completed_pos.filter(delivery_date__lte=models.F('acknowledgment_date')).count()
        total_completed_pos = completed_pos.count()
        vendor.on_time_delivery_rate = (on_time_deliveries / total_completed_pos) * 100 if total_completed_pos > 0 else 0

        
        acknowledged_pos = completed_pos.filter(acknowledgment_date__isnull=False)
        avg_response_time = acknowledged_pos.aggregate(avg_response=Avg(models.F('acknowledgment_date') - models.F('issue_date')))['avg_response']
        vendor.average_response_time = avg_response_time.total_seconds() / 3600 if avg_response_time is not None else 0

        
        fulfilled_pos = completed_pos.filter(issue_date__isnull=False)
        fulfilment_rate = (fulfilled_pos.count() / completed_pos.count()) * 100 if completed_pos.count() > 0 else 0
        vendor.fulfillment_rate = fulfilment_rate

        vendor.save()

        return Response({'message': 'Purchase Order updated successfully'})
    
    if request.method == 'DELETE':
        po = get_object_or_404(PurchaseOrder, id=id)
        po.delete()
        return Response({'message': 'Purchase Order deleted successfully'})

    return Response({'error': 'Invalid method'})





@api_view(['GET'])
@csrf_exempt
def retrieve_vendor_details(request, id):
    if request.method == 'GET':
        vendor = get_object_or_404(Vendor, id=id)
        data = {
            'on_time_delivery_rate': vendor.on_time_delivery_rate,
            'average_response_time': vendor.avg_response_time,
            'fulfillment_rate': vendor.fulfillment_rate,
            'quality_rating_avg': vendor.quality_rating_avg
        }
        return Response(data)
    return Response({'error': 'Invalid method'})


@api_view(['POST'])
@csrf_exempt
def acknowledge_purchase_order(request, id):
    po = get_object_or_404(PurchaseOrder, id=id)

    if po.acknowledgment_date is None:
        
        po.acknowledgment_date = timezone.now()
        po.save()

        # Recalculate metrics for the vendor
        vendor = po.vendor

        # Average Response Time
        completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
        acknowledged_pos = completed_pos.filter(acknowledgment_date__isnull=False)
        avg_response_time = acknowledged_pos.aggregate(avg_response=(F('acknowledgment_date') - F('issue_date')))['avg_response']
        vendor.average_response_time = avg_response_time.total_seconds() / 3600 if avg_response_time is not None else 0

        vendor.save()

        return Response({'message': 'Purchase Order acknowledged successfully'})

    return Response({'error': 'Purchase Order already acknowledged'})