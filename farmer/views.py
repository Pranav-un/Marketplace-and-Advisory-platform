from django.shortcuts import render,redirect
from django.contrib import messages
from .models import SeedFarm,FarmStatus
from Expert.models import FarmerProducts
from Home.models import UserData
from Expert.models import FramemerCheckout
from django.contrib.auth.models import User

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from datetime import datetime

razorpay_client = razorpay.Client(
  auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))



def StartFarm(request):
    farm = SeedFarm.objects.filter(user = request.user)
    farmstatus = []
    for i in farm:
        fm = FarmStatus.objects.filter(Farm = i)
    
    context = {
        "farm":farm,
        # "farmstatus":fm
        
    }
    return render(request,"farmer/startfarm.html",context)

def AddNewSeedFarm(request):
    if request.method == "POST":
        name = request.POST["seed"]
        field = request.POST["farmfields"]
        area = request.POST["area"]
        status = request.POST["status"]
        img = request.FILES["img"]
        
        farm = SeedFarm.objects.create(seedname=name,farmfield=field,framarea=area,framstatus=status,image=img,user=request.user)
        farm.save()
        messages.info(request,"New Seed Farm Created")
        return redirect('StartFarm')
    return redirect('StartFarm')

def FramStatusUpdate(request,pk):
    Farm = SeedFarm.objects.filter(id = pk)
    farm = SeedFarm.objects.get(id = pk)
    if request.method == "POST":
        status = request.POST["status"]
        questions = request.POST['questions']
        status_image = request.FILES.get('status_image')
        
        # Create farm status update
        farm_status = FarmStatus.objects.create(
            Farm=farm,
            Status=status,
            questions=questions
        )
        
        # If an image was uploaded, only update the status image
        if status_image:
            farm_status.status_image = status_image
            farm_status.save()
            
        farm.framstatus = status
        farm.save()
        messages.info(request,"Status Updated")   
    
    farmstatus = FarmStatus.objects.filter(Farm = farm) 
    
    context = {
        "Farm":Farm,
        "farmstatus":farmstatus
    }
    return render(request,'farmer/farmstatusupdate.html',context)

def DeleteOpinion(request,pk,hk):
    FarmStatus.objects.get(id =pk).delete()
    messages.info(request,"item deleted")
    return redirect('FramStatusUpdate',pk = hk)

def UpdateAnswer(request,pk):
    farmstatus = FarmStatus.objects.get(id = pk)
    if request.method == "POST":
        ans = request.POST['ans']
        farmstatus.answers = ans
        farmstatus.save()
        return redirect("ExpertHome")
        
    return redirect("ExpertHome")

def TogglePinStatus(request, pk):
    """
    Toggle the pinned status of a farm status request
    """
    try:
        farmstatus = FarmStatus.objects.get(id=pk)
        # Toggle the is_pinned status
        farmstatus.is_pinned = not farmstatus.is_pinned
        farmstatus.save()
        
        # Create the success message with a tag to identify it in the template
        message = f"Status {'pinned to top' if farmstatus.is_pinned else 'unpinned'}"
        messages.success(request, message, extra_tags='pin_status')
    except FarmStatus.DoesNotExist:
        messages.error(request, "Farm status not found", extra_tags='pin_status')
    
    return redirect("ExpertHome")

def FarmProducts(request):
    products = FarmerProducts.objects.all()
    context = {
        "products":products
    }
    return render(request,'farmer/productforfarm.html',context)

def FarmerMybooking(request):
    product = FramemerCheckout.objects.filter(user=request.user)
    total_price = sum(p.product.Product_price * p.quantity for p in product)
    context = {
        'product': product,
        'total_price': total_price
    }
    return render(request, "farmer/mybooking.html", context)

def ProductSignleView(request,pk):
    product = FarmerProducts.objects.filter(id = pk)
    userdata1 = UserData.objects.filter(user = request.user)
    product1 = FarmerProducts.objects.get(id = pk)
    
    if request.method == "POST":
        name = request.POST["name"]
        phone = request.POST["phone"]
        city = request.POST["city"]
        state = request.POST["state"]
        house = request.POST["house"]
        quantity = int(request.POST.get("quantity", 1))  # Get quantity from form
        
        if UserData.objects.filter(user = request.user).exists():
            userdata = UserData.objects.get(user = request.user)
            userdata1 = UserData.objects.filter(user = request.user)
            
            userdata.name = name
            userdata.phone = phone
            userdata.city = city
            userdata.state = state
            userdata.house = house
            userdata.save()
        else:
            userdata = UserData.objects.create(name = name, house = house,phone = phone,city = city,state = state,user = request.user)
            userdata.save()
        
        # Delete any existing unpaid orders for this product and user
        FramemerCheckout.objects.filter(
            product=product1,
            user=request.user,
            status="Customer Ordered",
            Payment=False
        ).delete()
        
        # Create new checkout with quantity
        checkout = FramemerCheckout.objects.create(
            product=product1,
            user=request.user,
            status="Customer Ordered",
            quantity=quantity,
            Payment=False
        )
        checkout.save()
        
        return redirect("MakePayment", pk=pk)
        
    context = {
        "product": product,
        "userdata1": userdata1,
        "datalen": len(userdata1)
    }
    
    return render(request,"farmer/farmerproductview.html",context)

def CancelOrderFarmer(request,pk):
    FRCKOT = FramemerCheckout.objects.get(id = pk)
    FRCKOT.status = "Cancelled By User"
    FRCKOT.save()
    messages.info(request,"Item Cancelled")
    return redirect("FarmerMybooking")

def DeleteOrderFarmer(request,pk):
    FramemerCheckout.objects.get(id = pk).delete()
    messages.info(request,"Item Deleted")
    return redirect("FarmerMybooking")
    
    
def MyProducts(request):
    return render(request,"farmer/myproducts.html")


def CustomerView(request,pk):
    user  = User.objects.get(id = pk)
    userdata = UserData.objects.filter(user = user)
    return render(request,'farmer/viewcustomer.html',{"udata":userdata})


def MakePayment(request,pk):
    product1 = FarmerProducts.objects.get(id = pk)
    
    try:
        # Get the latest unpaid order for this product and user
        checkout = FramemerCheckout.objects.filter(
            product=product1,
            user=request.user,
            status="Customer Ordered",
            Payment=False
        ).latest('date')
        
        # Get quantity and calculate prices
        quantity = checkout.quantity
        base_price = float(product1.Product_price)
        total_price = base_price * quantity
        total_amount_paise = int(total_price * 100)  # Convert to paise for Razorpay
        
        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(
            amount=total_amount_paise,
            currency='INR',
            payment_capture='0'
        ))
        
        # Prepare context for template
        context = {
            'razorpay_order_id': razorpay_order["id"],
            'razorpay_merchant_key': settings.RAZOR_KEY_ID,
            'razorpay_amount': total_amount_paise,
            'currency': 'INR',
            'callback_url': 'paymenthandler',
            'product': product1,
            'quantity': quantity,
            'base_price': base_price,
            'total_price': total_price  # Regular price in rupees
        }
        
        return render(request, "farmer/makepayment.html", context)
        
    except FramemerCheckout.DoesNotExist:
        messages.error(request, "No pending order found")
        return redirect('ProductSignleView', pk=pk)

@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # Verify payment signature
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                try:
                    # Get the latest unpaid order
                    checkout = FramemerCheckout.objects.filter(
                        status="Customer Ordered",
                        Payment=False,
                        user=request.user  # Add user filter for safety
                    ).latest('date')
                    
                    # Calculate amount in paise
                    base_price = float(checkout.product.Product_price)
                    total_price = base_price * checkout.quantity
                    amount_paise = int(total_price * 100)
                    
                    # Capture payment
                    razorpay_client.payment.capture(payment_id, amount_paise)
                    
                    # Update order status
                    checkout.Payment = True
                    checkout.status = "Payment Completed"
                    checkout.save()
                    
                    # Update product stock
                    product = checkout.product
                    product.Product_stock = max(0, product.Product_stock - checkout.quantity)
                    product.save()
                    
                    return redirect('Success')
                except Exception as e:
                    print(f"Payment error: {str(e)}")
                    return redirect('Success')
            else:
                return render(request, 'paymentfail.html')
        except Exception as e:
            print(f"Payment handler error: {str(e)}")
            return HttpResponseBadRequest()
    return HttpResponseBadRequest()
    
def Success(request):
    return render(request,'farmer/Paymentconfirm.html')

def UpdateFarmImage(request, pk):
    if request.method == "POST":
        farm = SeedFarm.objects.get(id=pk)
        farm_image = request.FILES.get('farm_image')
        if farm_image:
            farm.image = farm_image
            farm.save()
            messages.info(request, "Farm image updated successfully")
    return redirect('FramStatusUpdate', pk=pk)

def DeleteFarm(request, pk):
    try:
        farm = SeedFarm.objects.get(id=pk, user=request.user)
        farm.delete()
        messages.success(request, "Farm deleted successfully")
    except SeedFarm.DoesNotExist:
        messages.error(request, "Farm not found")
    return redirect('StartFarm')

def CancelOrder(request, pk):
    try:
        order = FramemerCheckout.objects.get(id=pk, user=request.user)
        
        # Only allow cancellation if order is not already processed
        if order.status in ["Customer Ordered", "Order Accepted"]:
            # Don't update stock here - it will be handled when expert rejects the order
            order.status = "Cancelled by Customer"
            order.save()
            messages.info(request, "Your order has been cancelled. The expert will process your cancellation.")
        else:
            messages.warning(request, "This order cannot be cancelled at this stage.")
        
        return redirect('home')  # or wherever you want to redirect after cancellation
        
    except FramemerCheckout.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('home')
        



