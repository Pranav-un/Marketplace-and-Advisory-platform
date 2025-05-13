from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import Productaddform
from .models import ProductForCustomer,CustomerCheckout
from Home.models import UserData
from django.contrib.auth.decorators import login_required

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from datetime import datetime

razorpay_client = razorpay.Client(
  auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

@login_required(login_url="SignIn")
def ProductAdd(request):
    form = Productaddform
    products = ProductForCustomer.objects.filter(user = request.user)
    if request.method == "POST":
        form = Productaddform(request.POST,request.FILES)
        if form.is_valid():
            prod = form.save()
            prod.user = request.user
            prod.save()
            messages.info(request,"Product added to list")
            return redirect('ProductAdd')
    context = {
        "form":form,
        "products":products
    }
    return render(request,'farmer/myproducts.html',context)

@login_required(login_url="SignIn")
def DeleteCustomerProduct(request,pk):
    ProductForCustomer.objects.get(id = pk).delete()
    messages.info(request,"Item Deleted")
    return redirect('ProductAdd')

@login_required(login_url="SignIn")
def ProductSingleViewCustomer(request,pk):
    product = ProductForCustomer.objects.filter(id = pk)
    product1 = ProductForCustomer.objects.get(id = pk)
    userdata1 = UserData.objects.filter(user = request.user)
    if request.method == "POST":
        name = request.POST["name"]
        phone = request.POST["phone"]
        city = request.POST["city"]
        state = request.POST["state"]
        house = request.POST["house"]
        quantity = int(request.POST.get("quantity", 1))
        total_price = float(request.POST.get("total_price", product1.Product_price))
        
        # Validate quantity against stock
        if quantity > product1.Product_Stock:
            messages.error(request, "Requested quantity exceeds available stock!")
            return redirect("ProductSingleViewCustomer", pk=pk)
        
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
        
        # Create order with quantity and update stock
        checkout = CustomerCheckout.objects.create(
            product=product1,
            user=request.user,
            status="Customer Ordered",
            quantity=quantity,
            total_price=total_price
        )
        checkout.save()
        
        # Update stock
        product1.Product_Stock -= quantity
        product1.save()
        
        return redirect("CustomerPayment", pk=pk)
    
    context = {
        "product":product,
        "userdata1":userdata1,
        "datalen":len(userdata1)
    }
    return render(request,'productview.html',context)

@login_required(login_url="SignIn")
def CustomerMybooking(request):
    product = CustomerCheckout.objects.filter(user = request.user)
    context = {
       "product":product 
    }
    return render(request,"customerorder.html",context)



@login_required(login_url="SignIn")
def AllProducts(request):
    products = ProductForCustomer.objects.all()
    context = {
        "products":products
    }
    return render(request,"products.html",context)

@login_required(login_url="SignIn")
def CancelOrderCustomer(request,pk):
    order = CustomerCheckout.objects.get(id = pk)
    # Restore stock when order is cancelled
    if order.status != "Order Rejected" and order.status != "Cancelled By User":
        product = order.product
        product.Product_Stock += order.quantity
        product.save()
    order.status = "Cancelled By User"
    order.save()
    messages.info(request,"Item Cancelled")
    return redirect("CustomerMybooking")

@login_required(login_url="SignIn")
def DeleteOrderCustomer(request,pk):
    order = CustomerCheckout.objects.get(id = pk)
    # Restore stock if order is being deleted and wasn't rejected or cancelled
    if order.status != "Order Rejected" and order.status != "Cancelled By User":
        product = order.product
        product.Product_Stock += order.quantity
        product.save()
    order.delete()
    messages.info(request,"Item Deleted")
    return redirect("CustomerMybooking")

def CustomerOrderFarmerview(request):
    orders = CustomerCheckout.objects.all()
    context = {
        "orders":orders
    }
    return render(request,"farmer/customerordersfarmerview.html",context)


def AcceptOrderCustomer(request,pk):
    order = CustomerCheckout.objects.get(id = pk)
    order.status = "Order Accepted"
    order.save()
    return redirect("CustomerOrderFarmerview")

def DespachOrderCustomer(request,pk):
    order = CustomerCheckout.objects.get(id = pk)
    order.status = "Order Despached"
    order.save()
    return redirect("CustomerOrderFarmerview")

def RejectOrderCustomer(request,pk):
    order = CustomerCheckout.objects.get(id = pk)
    # Restore stock when order is rejected
    product = order.product
    product.Product_Stock += order.quantity
    product.save()
    order.status = "Order Rejected"
    order.save()
    return redirect("CustomerOrderFarmerview")

def CustomerPayment(request,pk):
    product1 = ProductForCustomer.objects.get(id = pk)
    # Get the latest order for this product and user
    order = CustomerCheckout.objects.filter(
        product=product1,
        user=request.user,
        status="Customer Ordered"
    ).latest('date')
    
    currency = 'INR'
    amount = int(order.total_price * 100)  # Convert to paise

    # Create a Razorpay Order Payment Integration
    razorpay_order = razorpay_client.order.create(dict(
        amount=amount,
        currency=currency,
        payment_capture='0'
    ))

    razorpay_order_id = razorpay_order["id"]
    callback_url = 'paymenthandlercus'

    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url 
    context['slotid'] = "1"
    
    return render(request,'makepayment.html',context)

@csrf_exempt
def paymenthandlercus(request):
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

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                try:
                    # Get the latest order
                    order = CustomerCheckout.objects.filter(
                        status="Customer Ordered"
                    ).latest('date')
                    
                    amount = int(order.total_price * 100)  # Convert to paise
                    
                    try:
                        razorpay_client.payment.capture(payment_id, amount)
                        order.Payment = True
                        order.save()
                        return redirect('Success1')
                    except:
                        # If payment capture fails, restore stock and mark order as failed
                        product = order.product
                        product.Product_Stock += order.quantity
                        product.save()
                        order.status = "Payment Failed"
                        order.save()
                        return render(request, 'paymentfail.html')
                except CustomerCheckout.DoesNotExist:
                    return render(request, 'paymentfail.html')
            else:
                # If signature verification fails, restore stock and mark order as failed
                try:
                    order = CustomerCheckout.objects.filter(
                        status="Customer Ordered"
                    ).latest('date')
                    product = order.product
                    product.Product_Stock += order.quantity
                    product.save()
                    order.status = "Payment Failed"
                    order.save()
                except CustomerCheckout.DoesNotExist:
                    pass
                return render(request, 'paymentfail.html')
        except:
            # If any error occurs, try to restore stock
            try:
                order = CustomerCheckout.objects.filter(
                    status="Customer Ordered"
                ).latest('date')
                product = order.product
                product.Product_Stock += order.quantity
                product.save()
                order.status = "Payment Failed"
                order.save()
            except:
                pass
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()
    
def Success1(request):
    return render(request,'Paymentconfirm.html')
        


    


