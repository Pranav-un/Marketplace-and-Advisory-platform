from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from .forms import UserAddForm
from django.contrib.auth.models import User,Group
from .decorators import admin_only,NullGroup
from django.http import HttpResponse, JsonResponse
from django.db import connection
from farmer.models import FarmStatus
from Products.models import ProductForCustomer
from Expert.models import FarmerProducts
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
import os
import sys
import django


@admin_only
def Index(request):
    products = ProductForCustomer.objects.all()
    context = {
        "products":products
    }
    
    # Check if we're on Render and use the ultra-simple landing page
    if 'RENDER' in os.environ:
        try:
            # Try the simplified template first
            return render(request, "landing.html")
        except:
            # If that fails, return a simple HTML response
            return HttpResponse("""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>AgriConnect</title>
                    <style>
                        body { font-family: Arial; text-align: center; padding: 50px; }
                        h1 { color: #28a745; }
                        .btn { 
                            display: inline-block;
                            background: #28a745;
                            color: white;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px;
                            margin: 10px;
                        }
                    </style>
                </head>
                <body>
                    <h1>Welcome to AgriConnect</h1>
                    <p>Connecting farmers, experts, and customers</p>
                    <div>
                        <a href="/signin" class="btn">Login</a>
                        <a href="/signup" class="btn">Register</a>
                    </div>
                </body>
            </html>
            """)
    else:
        return render(request, "index.html", context)

def FarmerHome(request):
    products = FarmerProducts.objects.all()
    context = {
        "products":products
    }
    return render(request,'farmerhome.html',context)

def AdminHome(request):
    return render(request,"admin/adminhome.html")

def ExpertHome(request):
    Farm = FarmStatus.objects.all()
    context = {
        "farm":Farm
    }
    return render(request,'expert/expertHome.html',context)

def UserList(request):
    role = request.GET.get('role', None)
    
    # Get all users
    users = User.objects.all()
    
    # Filter by role if specified
    if role:
        users = [user for user in users if user.groups.filter(name__iexact=role).exists()]
    
    # Count users by role
    user_stats = {
        'total': User.objects.count(),
        'customer': User.objects.filter(groups__name='customer').count(),
        'farmer': User.objects.filter(groups__name='farmer').count(),
        'expert': User.objects.filter(groups__name='expert').count(),
    }
    
    context = {
        "user": users,
        "stats": user_stats,
        "active_role": role
    }
    
    return render(request, "admin/userslist.html", context)

@NullGroup
def UserConfirmation(request):
    return render(request,"userconfirmation.html")

def UserGroupChange(request,value):
    user = request.user
    if value == 'customer':
        group = Group.objects.get(name='customer')
        user.groups.add(group)
        return redirect("Index")
        
    elif value == 'farmer':
        group = Group.objects.get(name='farmer')
        user.groups.add(group)
        return redirect("Index")
    
    return redirect("Index")

def ExpertAdd(request):
    form = UserAddForm()
    if request.method == "POST":
        form = UserAddForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get("email")
            if User.objects.filter(username = username).exists():
                messages.info(request,"Username Exists")
                return redirect('ExpertAdd')
            if User.objects.filter(email = email).exists():
                messages.info(request,"Email Exists")
                return redirect('ExpertAdd')
            else:
                new_user = form.save()
                new_user.save()
                
                group = Group.objects.get(name='expert')
                new_user.groups.add(group) 
                
                messages.success(request,"User Created")
                return redirect('ExpertAdd')
            
    return render(request,"admin/addexpert.html",{"form":form})
    
    

def SignIn(request):
    # Clear any pin_status messages from previous sessions
    storage = messages.get_messages(request)
    for message in list(storage):
        if 'pin_status' in getattr(message, 'extra_tags', ''):
            storage.used = True
    
    if request.method == "POST":
        username = request.POST['uname']
        password = request.POST['pswd']
        user1 = authenticate(request, username = username , password = password)
        
        if user1 is not None:
            request.session['username'] = username
            request.session['password'] = password
            login(request, user1)
            return redirect('Index')
        
        else:
            messages.info(request,'Username or Password Incorrect')
            return redirect('SignIn')
    return render(request,"login.html")

def SignUp(request):
    form = UserAddForm()
    if request.method == "POST":
        form = UserAddForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get("email")
            if User.objects.filter(username = username).exists():
                messages.info(request,"Username Exists")
                return redirect('SignUp')
            if User.objects.filter(email = email).exists():
                messages.info(request,"Email Exists")
                return redirect('SignUp')
            else:
                new_user = form.save()
                new_user.save()
                
                # group = Group.objects.get(name='user')
                # new_user.groups.add(group) 
                
                messages.success(request,"User Created")
                return redirect('SignIn')
            
    return render(request,"register.html",{"form":form})



def ProductList(request):
    from collections import defaultdict
    from django.db.models import Count, Sum
    
    # Get query parameters
    group_by = request.GET.get('group', 'expert')
    product_type = request.GET.get('type', 'all')
    
    # Import models
    try:
        from Products.models import ProductForCustomer
        from Expert.models import FarmerProducts
    except ImportError:
        ProductForCustomer = None
        FarmerProducts = None
    
    # Get all products
    customer_products = ProductForCustomer.objects.all() if ProductForCustomer else []
    farmer_products = FarmerProducts.objects.all() if FarmerProducts else []
    
    # Prepare data structures
    products_by_expert = defaultdict(list)
    products_by_farmer = defaultdict(list)
    
    # Filter by product type if specified
    if product_type == 'customer' or product_type == 'all':
        for product in customer_products:
            if hasattr(product, 'user') and product.user:
                products_by_farmer[product.user].append({
                    'product': product,
                    'type': 'customer'
                })
    
    if product_type == 'farmer' or product_type == 'all':
        for product in farmer_products:
            if hasattr(product, 'user') and product.user:
                products_by_expert[product.user].append({
                    'product': product,
                    'type': 'farmer'
                })
    
    # Product statistics
    stats = {
        'total_products': len(customer_products) + len(farmer_products),
        'customer_products': len(customer_products),
        'farmer_products': len(farmer_products),
        'categories': {
            'Fruits': ProductForCustomer.objects.filter(Product_Category='Fruits').count() if ProductForCustomer else 0,
            'Vegetable': ProductForCustomer.objects.filter(Product_Category='Vegetable').count() if ProductForCustomer else 0,
            'Fertilizer': FarmerProducts.objects.filter(Product_Category='Fertilizer').count() if FarmerProducts else 0,
            'Seeds': FarmerProducts.objects.filter(Product_Category='Seeds').count() if FarmerProducts else 0,
            'Accessories': FarmerProducts.objects.filter(Product_Category='Accessories').count() if FarmerProducts else 0,
        }
    }
    
    context = {
        'products_by_expert': products_by_expert,
        'products_by_farmer': products_by_farmer,
        'group_by': group_by,
        'product_type': product_type,
        'stats': stats,
        'customer_products': customer_products,
        'farmer_products': farmer_products
    }
    
    return render(request, 'admin/productlist.html', context)

def SignOut(request):
    # Clear any pin_status messages before logout
    storage = messages.get_messages(request)
    for message in list(storage):
        if 'pin_status' in getattr(message, 'extra_tags', ''):
            storage.used = True
    
    logout(request)
    return redirect('Index')

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password/password_reset_email.txt"
                    context = {
                        "email": user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'AgriConnect',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }
                    email = render_to_string(email_template_name, context)
                    try:
                        # Randomly select a display name to use with the email
                        import random
                        from django.conf import settings
                        
                        # Get a random display name from settings, or use default
                        display_names = getattr(settings, 'EMAIL_DISPLAY_NAMES', ['AgriConnect'])
                        display_name = random.choice(display_names)
                        
                        # Format the from_email with the display name
                        email_user = settings.EMAIL_HOST_USER
                        from_email = f"{display_name} <{email_user}>"
                        
                        # Send email with the formatted from_email
                        send_mail(
                            subject=subject,
                            message=email,
                            from_email=from_email,
                            recipient_list=[user.email],
                            fail_silently=False
                        )
                        # Log this action (optional)
                        print(f"Password reset email sent to {user.email} from {from_email}")
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    except Exception as e:
                        # Log the error but don't tell the user (security measure)
                        print(f"Error sending password reset email: {e}")
                        messages.error(request, "There was an error sending the email. Please try again later.")
                        return render(request, "password/password_reset.html", {"form": password_reset_form})
                    
                    return redirect("password_reset_done")
            else:
                messages.error(request, "No user with this email address exists.")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html", context={"form": password_reset_form})

def health_check(request):
    """
    A simple health check endpoint that Render can use to monitor the application
    """
    # Check database connection
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "ok"
    except Exception as e:
        db_status = str(e)
    
    # Return simple HTML directly, without using templates or static files
    html = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>AgriConnect Health Check</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .status {{ background: #e8f5e9; padding: 15px; border-radius: 5px; }}
                h1 {{ color: #2e7d32; }}
            </style>
        </head>
        <body>
            <h1>AgriConnect Health Check</h1>
            <div class="status">
                <p><strong>Status:</strong> Service is running</p>
                <p><strong>Database:</strong> {db_status}</p>
                <p><strong>Render:</strong> {'Yes' if 'RENDER' in os.environ else 'No'}</p>
                <p><strong>Python Version:</strong> {sys.version.split()[0]}</p>
                <p><strong>Django Version:</strong> {django.get_version()}</p>
            </div>
        </body>
    </html>
    """
    return HttpResponse(html)

