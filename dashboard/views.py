from django.shortcuts import render, redirect
from eComm_App.models import *
from .forms import *


# Create your views here.
def dash_index(request):
    full_order_details = []
    order_delivery = Delivery.objects.all()
    
    for check_d in order_delivery:
        check = check_d.order.id
        orders = Order.objects.all()
        full_order_details.extend(orders)
    context = {'order_delivery': order_delivery, 'full_order_details': full_order_details}
    return render(request, 'dashboard/index.html', context)


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/')  # replace with your desired redirect
    else:
        form = ProductForm()
    context = {'form':form}
    return render(request,'dashboard/product-add.html',context)


def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')  # replace with your desired redirect
    else:
        form = CategoryForm()
    return render(request, 'dashboard/create_category.html', {'form': form})

def create_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')  # replace with your desired redirect
    else:
        form = BrandForm()
    return render(request, 'dashboard/create_brand.html', {'form': form})