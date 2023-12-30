from django.urls import path
from . import views


urlpatterns = [
    
    path('api/vendors',views.vendors, name='vendors'),
    path('api/vendors/<str:id>',views.update_get_delete_vendor,name='update_get_delete_vendor'),
    path('api/purchase_orders', views.create_get_purchase_order, name='create_get_purchase_order'),
    path('api/purchase_orders/<str:id>',views.retrieve_update_delete_purchase_order, name='get_update_delete_purchase_orders'),
    path('api/vendors/<str:id>/performance',views.retrieve_vendor_details, name='retrieve_vendor_details'),
    path('api/purchase_orders/<str:id>/acknowledge', views.acknowledge_purchase_order, name="acknowledge")
]