from rest_framework import serializers
from .models import Vendor, PurchaseOrder, HistoricalPerformance

class CreateVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['name', 'contact_details', 'address','vendor_code']


class CreatePurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ['po_number', 'vendor', 'order_date', 'delivery_date', 'status', 'items', 'quantity', 'quality_rating', 'issue_date', 'acknowledgment_date']

class PurcharseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ['po_number', 'vendor', 'order_date', 'delivery_date', 'status', 'items', 'quantity', 'quality_rating', 'issue_date', 'acknowledgment_date' ]   


class HistoricalPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalPerformance
        fields = "__all__"
