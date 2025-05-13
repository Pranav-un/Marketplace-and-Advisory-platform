from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("",views.Index,name="Index"),
    path("FarmerHome",views.FarmerHome,name="FarmerHome"),
    path("SignUp",views.SignUp,name="SignUp"),
    path("SignIn",views.SignIn,name="SignIn"),
    path("SignOut",views.SignOut,name="SignOut"),
    path("UserConfirmation",views.UserConfirmation,name="UserConfirmation"),
    path("UserGroupChange/<str:value>",views.UserGroupChange,name="UserGroupChange"),
    path("AdminHome",views.AdminHome,name="AdminHome"),
    path("ExpertAdd",views.ExpertAdd,name="ExpertAdd"),
    path("UserList",views.UserList,name="UserList"),
    path("ExpertHome",views.ExpertHome,name="ExpertHome"),
    path("ProductList", views.ProductList, name="ProductList"),
    
    # Password Reset URLs
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password/password_reset_done.html'), 
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password/password_reset_confirm.html'), 
        name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password/password_reset_complete.html'), 
        name='password_reset_complete'),
]

