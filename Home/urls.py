from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.Index, name = "Index"),
    path("farmerhome",views.FarmerHome,name="farmerHome"),
    path("experthome",views.ExpertHome,name="ExpertHome"),
    path("adminhome",views.AdminHome,name="AdminHome"),
    path("userconfirmation",views.UserConfirmation,name="UserConfirmation"),
    path("userlist",views.UserList,name="UserList"),
    path("usergroupchange/<str:value>",views.UserGroupChange,name="UserGroupChange"),
    path("addexpert",views.ExpertAdd,name="ExpertAdd"),
    path("signin", views.SignIn, name = "SignIn"),
    path("signup", views.SignUp, name = "SignUp"),
    path("signout", views.SignOut, name = "SignOut"),
    path("productlist",views.ProductList,name="ProductList"),
    
    # Health check endpoint for Render
    path("health/", views.health_check, name="health_check"),
    
    # Password reset endpoints
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'), name='password_reset_complete'),
]

