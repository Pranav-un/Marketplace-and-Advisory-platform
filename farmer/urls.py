from django.urls import path 
from .import views 

urlpatterns = [
    path("StartFarm",views.StartFarm,name="StartFarm"),
    path("AddNewSeedFarm",views.AddNewSeedFarm,name="AddNewSeedFarm"),
    path("DeleteFarm/<str:pk>",views.DeleteFarm,name="DeleteFarm"),
    path("FramStatusUpdate/<str:pk>",views.FramStatusUpdate,name="FramStatusUpdate"),
    path("UpdateFarmImage/<str:pk>",views.UpdateFarmImage,name="UpdateFarmImage"),
    path("DeleteOpinion/<str:pk><str:hk>",views.DeleteOpinion,name="DeleteOpinion"),
    path("UpdateAnswer/<str:pk>",views.UpdateAnswer,name="UpdateAnswer"),
    path("TogglePinStatus/<str:pk>",views.TogglePinStatus,name="TogglePinStatus"),
    path("FarmProducts",views.FarmProducts,name="FarmProducts"),
    path("ProductSignleView/<int:pk>",views.ProductSignleView,name="ProductSignleView"),
    path("FarmerMybooking",views.FarmerMybooking,name="FarmerMybooking"),
    path("MyProducts",views.MyProducts,name="MyProducts"),
    path("CancelOrderFarmer/<int:pk>",views.CancelOrderFarmer,name="CancelOrderFarmer"),
    path("DeleteOrderFarmer/<int:pk>",views.DeleteOrderFarmer,name="DeleteOrderFarmer"),
    path("CustomerView/<int:pk>",views.CustomerView,name="CustomerView"),
    path("MakePayment/<int:pk>",views.MakePayment,name="MakePayment"),
    path('MakePayment/paymenthandler', views.paymenthandler, name='MakePayment/paymenthandler'),
    path("Success",views.Success,name="Success"),
    path("CancelOrder/<str:pk>",views.CancelOrder,name="CancelOrder"),
]
