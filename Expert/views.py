from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import ProductAddform
from .models import FarmerProducts,FramemerCheckout
from django.http import JsonResponse
from datetime import datetime, timedelta
import json


def FarmersProducts(request):
    form = ProductAddform()
    # Filter products by the current user (expert)
    prod = FarmerProducts.objects.filter(user=request.user)
    
    if request.method == "POST":
        form = ProductAddform(request.POST,request.FILES)
        if form.is_valid():
            val = form.save(commit=False)  # Don't save to DB yet
            val.user = request.user  # Set the user
            val.save()  # Now save to DB
            messages.info(request,"Product Added to List")
            return redirect('FarmersProducts')
    context = {
        "form": form,
        'products': prod
    }
    return render(request,'expert/products.html',context)

def DeleteFarmProducts(request,pk):
    FarmerProducts.objects.get(id = pk).delete()
    messages.info(request,"Product Deleted")
    return redirect('FarmersProducts')

def FramersOrder(request):
    # Filter orders to show only those for products added by the current expert
    orders = FramemerCheckout.objects.filter(product__user=request.user)
    context = {
        "orders": orders
    }
    return render(request,'expert/farmersorder.html',context)

def AcceptOrder(request,pk):
    order = FramemerCheckout.objects.get(id = pk)
    order.status = "Order Accepted"
    order.save()
    messages.success(request, "Order has been accepted.")
    return redirect("FramersOrder")

def DespachOrder(request, pk):
    if request.method == "POST":
        order = FramemerCheckout.objects.get(id=pk)
        
        # Update delivery details
        order.tracking_number = request.POST.get('tracking_number')
        order.delivery_service = request.POST.get('delivery_service')
        order.delivery_notes = request.POST.get('delivery_notes')
        
        # Parse and set estimated delivery date
        try:
            est_delivery = request.POST.get('estimated_delivery')
            if est_delivery:
                order.estimated_delivery = datetime.strptime(est_delivery, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format")
            return redirect("FramersOrder")
        
        order.status = "Order Despached"
        order.delivery_status = "In Transit"
        order.save()
        
        messages.success(request, "Order has been dispatched with tracking details.")
        return redirect("FramersOrder")
    
    # If GET request, show the dispatch form
    order = FramemerCheckout.objects.get(id=pk)
    context = {
        "order": order
    }
    return render(request, 'expert/dispatch_order.html', context)

def RejectOrder(request,pk):
    order = FramemerCheckout.objects.get(id = pk)
    
    # Update the product stock by adding back the ordered quantity
    product = order.product
    product.Product_stock += order.quantity
    product.save()
    
    # Update order status
    order.status = "Order Rejected"
    order.save()
    
    messages.warning(request, "Order has been rejected and stock has been restored.")
    return redirect("FramersOrder")

def DeleteOrder(request,pk):
    FramemerCheckout.objects.get(id = pk).delete()
    messages.info(request,"Order deleted")
    return redirect("FramersOrder")

def UpdateDeliveryStatus(request, pk):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order = FramemerCheckout.objects.get(id=pk)
            
            # Update delivery status
            new_status = data.get('delivery_status')
            order.delivery_status = new_status
            
            # Add status update to delivery notes
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            new_note = f"[{timestamp}] Status updated to: {new_status}"
            if order.delivery_notes:
                order.delivery_notes = new_note + "\n" + order.delivery_notes
            else:
                order.delivery_notes = new_note
            
            order.save()
            return JsonResponse({"status": "success"})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
            
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def UpdateOrderStatus(request, pk, status):
    try:
        order = FramemerCheckout.objects.get(id=pk)
        
        # Update delivery status
        order.delivery_status = status
        
        # Add status update to delivery notes
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_note = f"[{timestamp}] Status updated to: {status}"
        if order.delivery_notes:
            order.delivery_notes = new_note + "\n" + order.delivery_notes
        else:
            order.delivery_notes = new_note
        
        order.save()
        messages.success(request, f"Order status updated to {status}")
        
    except FramemerCheckout.DoesNotExist:
        messages.error(request, "Order not found")
    except Exception as e:
        messages.error(request, f"Error updating status: {str(e)}")
    
    return redirect("FramersOrder")
    
    
    
