from django.urls import path 
from .import views 

urlpatterns = [
    path("FarmersProducts",views.FarmersProducts,name= "FarmersProducts"),
    path("DeleteFarmProducts/<int:pk>",views.DeleteFarmProducts,name="DeleteFarmProducts"),
    path("FramersOrder",views.FramersOrder,name="FramersOrder"),
    path("AcceptOrder/<int:pk>",views.AcceptOrder,name="AcceptOrder"),
    path("DespachOrder/<int:pk>",views.DespachOrder,name="DespachOrder"),
    path("RejectOrder/<int:pk>",views.RejectOrder,name="RejectOrder"),
    path("DeleteOrder/<int:pk>",views.DeleteOrder,name="DeleteOrder"),
    path("UpdateDeliveryStatus/<int:pk>",views.UpdateDeliveryStatus,name="UpdateDeliveryStatus"),
    path("UpdateOrderStatus/<int:pk>/<str:status>",views.UpdateOrderStatus,name="UpdateOrderStatus"),
]
