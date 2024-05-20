from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import razorpay
import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils import get_plot
from .models import Product, Order, OrderItem, ProductVariant,Customer,Category,Delivery,Refund
from .serializers import OrderItemSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm ,CustomerForm,DeliveryForm,ExcelUploadForm,ProductFilterForm
from .models import Customer
from .serializers import *
from django.core.files.storage import FileSystemStorage 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import requests
import pandas as pd
from io import TextIOWrapper
from django.db.models import Q
from .serializers import ProductSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from .serializers import LoginSerializer


from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.pagination import PageNumberPagination

from rest_framework import generics
from .serializers import CustomerSerializer
import os
# from .serializers import CustomerSerializer
class CustomerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.customer  # Assuming 'customer' is the related name in User model
        serializer = CustomerSerializer(profile, context={'request': request})
        return Response(serializer.data)


class UserOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            customer = request.user.customer

            # Retrieve user orders excluding pending ones
            user_orders = Order.objects.filter(customer=customer).exclude(status='Pending').order_by('-id')

            paginator = PageNumberPagination()
            paginator.page_size = 5
            result_page = paginator.paginate_queryset(user_orders, request)
            
            # Serialize user orders
            serializer = OrderSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'message': 'No active orders found'}, status=404)
        except Exception as e:
            return Response({'message': str(e)}, status=500)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# class LoginAPIView(APIView):
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             user_data = {
#                 'id': user.id,
#                 'username': user.username,
#                 # 'email': user.email,
#                 # Add any other user information you want to pass
#             }
#             user = serializer.validated_data['user']
#             # You can now use the authenticated user object
#             return Response({"message": "User logged in successfully", "user": user_data, "username": user.username}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)




@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def product_detail_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    serializer = ProductSerializer(product)
    return Response(serializer.data)



def is_url_accessible(url):
    try:
        response = requests.head(url, allow_redirects=True)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False
    

def upload_csv(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']

            # Determine file type (CSV or Excel) based on file extension
            if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                # Handle CSV file
                csv_file = TextIOWrapper(uploaded_file.file, encoding='utf-8', errors='replace')
                df = pd.read_csv(csv_file)
            else:
                return render(request, 'upload_excel.html', {'form': form, 'error': 'Invalid file type'})

            # Process the DataFrame and create Product objects
            for index, row in df.iterrows():
                main_category_var = row['main_category']
                sub_category_var = row['sub_category']

                # Get or create main category
                main_category, created_main = Category.objects.get_or_create(name=main_category_var)

                # Get or create sub category only if it exists
                if sub_category_var:
                    sub_category, created_sub = Category.objects.get_or_create(name=sub_category_var)
                else:
                    sub_category = None
                image_url = row['image']
                if not is_url_accessible(image_url):
                    continue
                Product.objects.create(
                    name=row['name'],
                    description=row['name'],
                    price=row['actual_price'],
                    # ratings=row['ratings'],
                    # no_of_ratings = row['no_of_ratings'],
                    image_url=row['image'],
                    discount_price = row['discount_price'],
                    # actual_price = row['actual_price'],

                    category=main_category,
                    sub_category=sub_category
                    # ... add other fields
                )

            return redirect('success_page')  # Redirect to a success page

    else:
        form = ExcelUploadForm()

    return render(request, 'upload_excel.html', {'form': form})




def loginpage(request):

    if request.method == "POST" and 'form1' in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        # if user.is_superuser:
        #     print('superuser')
        #     login(request, user)
        #     return redirect('/dashboard/')
        if user is not None:
            # print('user')
            login(request, user)
            request.session.set_expiry(5000)
            return redirect('/')
        else:
            messages.error(request, 'INCORRECT USERNAME OR PASSWORD! TRY AGAIN')
       
    
    return render(request, 'login.html')
    
#         ###############----Registration----############################## #



def register(request):
    form = CreateUserForm()
    customer_form = CustomerForm()
    if request.method == 'POST' and 'form2' in request.POST:
        form = CreateUserForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if form.is_valid() and customer_form.is_valid():
            user = form.save()
            customer = customer_form.save(commit=False)
            customer = Customer(user=user, shipping_address=customer_form.cleaned_data['shipping_address'])
            customer.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account Created Successfully for ' + username)
            return redirect('login')
        else:
            for field, error in form.errors.items():
                messages.error(request, f"{field}: {error}")

    context = {'form': form,'customer_form': customer_form }
    return render(request, 'register.html', context)

@login_required(login_url='/login/')
def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/login/')
def home(request):
    all_products = Product.objects.all().order_by('-id')
    featured_products = Product.objects.filter(sub_category=4).order_by('-id')[:12]
    if request.method == 'GET':
        form = ProductFilterForm(request.GET)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            search_query = form.cleaned_data.get('search_query')
            if category:
                all_products = all_products.filter(Q(category=category) | Q(sub_category=category))
            if search_query:
                all_products = all_products.filter(
                    Q(name__icontains=search_query) | Q(description__icontains=search_query)
                )
    paginator = Paginator(all_products, 12)  # Set the number of products per page

    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, status='Pending')
    order_items = OrderItem.objects.filter(order=order)
    order_count = order_items.count()
    context = {'all_products': all_products,'form': form, 'order_count': order_count, 'products': products,'featured_product':featured_products}
    return render(request, 'home.html', context)






# @api_view(['GET', 'POST'])
# # @permission_classes([IsAuthenticated])
# def cart_api(request):
#     if request.method == 'GET':
#         order = Order.objects.filter(customer=request.user.customer, status='Pending').first()
#         serializer = OrderSerializer(order)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = OrderSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors)




# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def cart_detail_view(request):
#     try:
#         # Ensure the user is authenticated and has a customer profile
#         if not hasattr(request.user, 'customer'):
#             return Response({'message': 'User does not have a customer profile'}, status=400)

#         order = Order.objects.get(customer=request.user.customer, status='Pending')
#         serializer = OrderSerializer(order)
#         return Response(serializer.data)
#     except Order.DoesNotExist:
#         return Response({'message': 'No active order found'}, status=404)

@api_view(['GET'])
# @authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def cart_api(request):
    try:
        customer = request.user.customer

        # Retrieve or create the pending order for the customer
        try:
            order, created = Order.objects.get_or_create(customer=customer, status='Pending')
        except Order.MultipleObjectsReturned:
            orders = Order.objects.filter(customer=customer, status='Pending')
            order = orders.first() if orders.exists() else None
            created = False

        # Retrieve order items for the order
        order_items = OrderItem.objects.filter(order=order)
        total_price = 0

        # Calculate total price and handle errors
        items_with_errors = []
        order_items_data = []
        for item in order_items:
            item_price = 0
            product_variant = item.product_variant

            if product_variant.price is not None:
                try:
                    prod_price = product_variant.price
                    Price = int(prod_price)
                    if item.quantity is not None:
                        item_price = Price * int(item.quantity)
                    else:
                        item.quantity = 1
                        item_price = Price
                except ValueError:
                    print(f"Error: Unable to convert price for item {item} to a valid number. Skipping this item.")
                    items_with_errors.append(item)
                    continue
            else:
                print(f"Warning: Item {item} has no specified price. Skipping this item.")

            total_price += item_price
            order_items_data.append({
                'product_id': product_variant.id,
                'quantity': item.quantity,
                'name': product_variant.name,
                'price': product_variant.price,
                'image_url': product_variant.image_url,
            })

        return Response({'order_items': order_items_data, 'total_price': total_price, 'items_with_errors': items_with_errors})
    except ObjectDoesNotExist:
        return Response({'message': 'No active order found'}, status=404)
    except Exception as e:
        return Response({'message': str(e)}, status=500)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart_api(request):
    # Extract product_id and quantity from the request data
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)  # Default to 1 if not specified

    # Get or create a pending order for the user
    order, _ = Order.objects.get_or_create(customer=request.user.customer, status='Pending')

    # Get the product, or return a 404 error if it doesn't exist
    product = get_object_or_404(Product, pk=product_id)

    # Try to get an existing order item, or create a new one if it doesn't exist
    order_item, created = OrderItem.objects.get_or_create(order=order, product_variant=product,
                                                          defaults={'quantity': quantity})

    if not created:
        # If the item already exists, update the quantity
        order_item.quantity += int(quantity)
        order_item.save()

    # Serialize the order item to return it as a response
    serializer = OrderItemSerializer(order_item)
    return Response(serializer.data)
    

    
@login_required(login_url='/login/')
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product,})


@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    customer = request.user.customer
    try:
        order, created = Order.objects.get_or_create(customer=customer, status='Pending')
    except Order.MultipleObjectsReturned:
        orders = Order.objects.filter(customer=customer, status='Pending')
        order = orders.first() if orders.exists() else None
        created = False
    try:
        order_item, item_created = OrderItem.objects.get_or_create(order=order, product_variant=product)
    except OrderItem.MultipleObjectsReturned:
        order_item = OrderItem.objects.filter(order=order, product_variant=product).first()
        item_created = False

    if not item_created:
        try:
            order_item.quantity = order_item.quantity + 1 if order_item.quantity is not None else 1
            order_item.save()
        except Exception as e:
            print(f"Error updating quantity for order item: {e}")
    else:
        try:
            order_item.quantity = 1
            order_item.save()
            
        except Exception as e:
            print(f"Error updating quantity for order item: {e}")

    return redirect('cart_view')


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
@login_required(login_url='/login/')
def cart_view(request):
    items_with_errors = []
    customer = request.user.customer
    
    try:
        order, created = Order.objects.get_or_create(customer=customer, status='Pending')
    except Order.MultipleObjectsReturned:
        orders = Order.objects.filter(customer=customer, status='Pending')
        order = orders.first() if orders.exists() else None
        created = False

    order_items = OrderItem.objects.filter(order=order)
    total_price = 0

    for item in order_items:
        item_price = 0
        if item.product_variant.price is not None:
            try:
                prod_price = item.product_variant.price
                Price = int(prod_price)
                if item.quantity is not None:
                    item_price = Price * int(item.quantity)
                else:
                    item.quantity = 1
                    item_price = Price
            except ValueError:
                print(f"Error: Unable to convert price for item {item} to a valid number. Skipping this item.")
                items_with_errors.append(item)
                continue
        else:
            print(f"Warning: Item {item} has no specified price. Skipping this item.")
        total_price += item_price

    return render(request, 'cart.html', {'order_items': order_items, 'total_price': total_price})
    # if request.accepted_renderer.format == 'html':
        # Render HTML for regular views
    # else:
    # #     # Serialize data for API views
    #     serializer = OrderItemSerializer(order_items, many=True)
    #     return Response({'order_items': serializer.data, 'total_price': total_price})

# Other views...

# Make sure to replace 'your_app_name' with the actual name of your Django app.
# ... (Previous code)

def reduce_quantity(request, item_id):
    order_item = get_object_or_404(OrderItem, pk=item_id)
    
    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()

    messages.success(request, 'Item quantity reduced.')
    return redirect('cart_view')

def increase_quantity(request, item_id):
    order_item = get_object_or_404(OrderItem, pk=item_id)
    
    if order_item.quantity is not None:
        order_item.quantity += 1
    else:
        order_item.quantity = 1
    order_item.save()

    messages.success(request, 'Item quantity increased.')
    return redirect('cart_view')

def remove_from_cart(request, item_id):
    order_item = get_object_or_404(OrderItem, pk=item_id)
    order_item.delete()

    messages.success(request, 'Item removed from the cart.')
    return redirect('cart_view')



@login_required(login_url='/login/')
def checkout(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_SECRET_KEY))
    customer = request.user.customer

    try:
        order, created = Order.objects.get_or_create(customer=customer, status='Pending')
    except Order.MultipleObjectsReturned:
        orders = Order.objects.filter(customer=customer, status='Pending')
        order = orders.first() if orders.exists() else None
        created = False

    order_items = OrderItem.objects.filter(order=order)
    total_price = 0

    for item in order_items:
        if item.product_variant.price is not None:
            prod_price = item.product_variant.price
            Price = int(prod_price)
            item_quantity = item.quantity if item.quantity is not None and item.quantity > 0 else 1
            item_price = Price * item_quantity
            total_price += item_price
            item.item_price = Price
            item.quantity = item_quantity
            item.save()
        else:
            pass

    if total_price != 0:
        razor_pay_order = client.order.create({
            'amount': int(total_price),
            'currency': 'INR',
            'payment_capture': 1
        })
        order.transaction_id = razor_pay_order['id']
        order.total_price = total_price
        order.delivery_address = customer.shipping_address
        order.save()

    return render(request, 'checkout.html', {'order': order, 'total_price': total_price, 'razor_pay_order': razor_pay_order,'customer':customer})






@login_required(login_url='/login/')
def successMsg(request):
    user = request.user 
    profile = user.customer
    a = request.POST
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_SECRET_KEY))
    data = {}
    for key, val in a.items():
        if key == 'razorpay_order_id':
            data['razorpay_order_id'] = val
        if key == 'razorpay_payment_id':
            data['razorpay_payment_id'] = val
        if key == 'razorpay_signature':
            data['razorpay_signature'] = val
    order_id = request.GET.get('razorpay_order_id')
    signatuter_id = request.GET.get('razorpay_signature')
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    Update_order = Order.objects.get(transaction_id=order_id)
    Update_order.transaction_id = signatuter_id
    Update_order.status = 'Paid'
    Update_order.delivery_status = 'In Progress'
    Update_order.payment_razorpay_id = razorpay_payment_id
    Update_order.save()
    Delivery_order = Delivery.objects.create(order_id=Update_order.id,user_id=request.user.id,status='In Progress')
    Delivery_order.save()
    context = {"Update_order":Update_order,}
    return render(request, 'success.html',context)


@login_required(login_url='/login/')
def delivery_track(request):
    user = request.user.id
    full_order_details = []
    order_delivery = Delivery.objects.filter(user_id=user, status='In Progress')

    for check_d in order_delivery:
        check = check_d.order.id
        orders = Order.objects.filter(id=check, customer_id=request.user.customer.id, delivery_status='In Progress')
        full_order_details.extend(orders)

    context = {'order_delivery': order_delivery, 'full_order_details': full_order_details}
    return render(request, 'delivery_track.html', context)


# def delivery_status_update(request):
#     context = {}
#     return render(request,'delivery_status_update.html',context)


@login_required(login_url='/login/')
def All_order(request):
    all_order = Order.objects.all()
    context = { 'all_order':all_order}

    return render(request, 'all_order_details.html',context)


@login_required(login_url='/login/')
def delivery_status_update(request, order_id):
    delivery = get_object_or_404(Delivery, order__id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        form = DeliveryForm(request.POST, instance=delivery)
        if form.is_valid():
            order_update_for_delivery = Order.objects.get(id=order_id,customer_id=delivery.user.customer.id,status='Paid',delivery_status='In Progress')
            if status == 'Completed':
                order_update_for_delivery.delivery_status = 'Completed'
                order_update_for_delivery.save()
            form.save()
            # Redirect to a success page or URL
            return redirect('/all_orders_details/')  # Update with your success URL name
    else:
        form = DeliveryForm(instance=delivery)

    return render(request, 'delivery_status_update.html', {'form': form, 'order_id': order_id})


@login_required(login_url='/login/')
def user_orders(request):
    user_orders = Order.objects.filter(customer=request.user.customer).exclude(status='Pending').prefetch_related('orderitem_set__product_variant').order_by('-id')
    page = request.GET.get('page', 1)
    paginator = Paginator(user_orders, 5)
    try:
        user_orders = paginator.page(page)
    except PageNotAnInteger:
        user_orders = paginator.page(1)
    except EmptyPage:
        user_orders = paginator.page(paginator.num_pages) 
    order_items = OrderItem.objects.filter(order__in=user_orders)
    return render(request, 'user_orders.html', {'user_orders': user_orders, 'order_item': order_items})




def profile(request):
    state_choices = (("Andhra Pradesh","Andhra Pradesh"),("Arunachal Pradesh ","Arunachal Pradesh "),("Assam","Assam"),("Bihar","Bihar"),("Chhattisgarh","Chhattisgarh"),("Goa","Goa"),("Gujarat","Gujarat"),("Haryana","Haryana"),("Himachal Pradesh","Himachal Pradesh"),("Jammu and Kashmir ","Jammu and Kashmir "),("Jharkhand","Jharkhand"),("Karnataka","Karnataka"),("Kerala","Kerala"),("Madhya Pradesh","Madhya Pradesh"),("Maharashtra","Maharashtra"),("Manipur","Manipur"),("Meghalaya","Meghalaya"),("Mizoram","Mizoram"),("Nagaland","Nagaland"),("Odisha","Odisha"),("Punjab","Punjab"),("Rajasthan","Rajasthan"),("Sikkim","Sikkim"),("Tamil Nadu","Tamil Nadu"),("Telangana","Telangana"),("Tripura","Tripura"),("Uttar Pradesh","Uttar Pradesh"),("Uttarakhand","Uttarakhand"),("West Bengal","West Bengal"),("Andaman and Nicobar Islands","Andaman and Nicobar Islands"),("Chandigarh","Chandigarh"),("Dadra and Nagar Haveli","Dadra and Nagar Haveli"),("Daman and Diu","Daman and Diu"),("Lakshadweep","Lakshadweep"),("National Capital Territory of Delhi","National Capital Territory of Delhi"),("Puducherry","Puducherry"))
    if request.method == 'POST':
        # Assuming your form is named 'update_profile_form'
        email = request.POST.get('email')
        address = request.POST.get('address')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        shipping_address = request.POST.get('shipping_address')
        gender = request.POST.get('gender')
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        # Assuming you have a one-to-one relationship between User and Customer
        user = request.user
        profile = user.customer  # Adjust this according to your model structure
        if 'photo' in request.FILES:
            photo_file = request.FILES['photo']
            fs = FileSystemStorage()
            file_name = default_storage.save(photo_file.name, ContentFile(photo_file.read()))
            profile.photo = default_storage.url(file_name)
            profile.save()
        # Update the profile fields
        profile.email = email
        profile.address = address
        profile.address2 = address2
        profile.city = city
        profile.state = state
        profile.zip_code = zip_code
        profile.shipping_address = shipping_address
        profile.gender = gender
        # Update other profile fields similarly...

        # Save the changes
        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')  # Redirect to the profile page or any other desired page after successful update

    else:
        # Assuming you're passing the state_choices to the template
        
        # Assuming you have a one-to-one relationship between User and Customer
        user = request.user
        profile = user.customer  # Adjust this according to your model structure

    context = {
        'state_choices': state_choices,
        'profile': profile,
       
    }


    return render(request, 'profile.html', context)




@api_view(['POST'])
def update_profile_api(request):
    if request.method == 'POST':
        # Assuming your form is sent as JSON data
        data = request.data

        # Assuming you're passing the user's ID along with the request
        user_id = data.get('user_id')

        try:
            customer = Customer.objects.get(user_id=user_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        # Assuming you're using a serializer to handle the data
        serializer = CustomerSerializer(instance=customer, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






@login_required(login_url='/login/')
# def dashboard(request):
#     now = datetime.datetime.now()
#     format = '%H:%M:%S %p'
#     current_time = now.strftime(format)
#     current_date = now.strftime("%d-%m-%Y")
#     qs = Product.objects.all()
#     # _main = int(price_graph.price for price_graph in qs)
#     x = [x.name for x in qs]
#     y = [y.price for y in qs]
#     chart = get_plot(x, y)
#     cust = Customer.objects.all()
#     prod = Product.objects.all()
#     cat = Category.objects.all()
#     ord = Order.objects.filter(customer=request.user.customer).exclude(status='Pending').prefetch_related('orderitem_set__product_variant')
#     cust_count   = Customer.objects.count()
#     prod_count   = Product.objects.count()
#     cat_count    = Category.objects.count()
#     ord_count    = OrderItem.objects.count()
#     context = {'cc': cat, 'name': cust, 'prod': prod,'ord':ord, 'x': x, 'y': y,
#                'time': current_time, 'day': current_date,'cust_count':cust_count,'prod_count':prod_count,'cat_count':cat_count,'ord_count':ord_count}
#     return render(request, 'dashboard.html', context)

def dashboard(request):
    now = datetime.datetime.now()
    format = '%H:%M:%S %p'
    current_time = now.strftime(format)
    current_date = now.strftime("%d-%m-%Y")
    qs = Product.objects.all()
    # _main = int(price_graph.price for price_graph in qs)
    x = [x.name for x in qs]
    y = [y.price for y in qs]
    chart = get_plot(x, y)
    cust = Customer.objects.all()
    prod = Product.objects.all()
    cat = Category.objects.all()
    ord = Order.objects.filter(customer=request.user.customer).exclude(status='Pending').prefetch_related('orderitem_set__product_variant')
    cust_count   = Customer.objects.count()
    prod_count   = Product.objects.count()
    cat_count    = Category.objects.count()
    ord_count    = OrderItem.objects.count()
    context = {'cc': cat, 'cust': cust, 'prod': prod,'ord':ord, 'x': x, 'y': y,
               'time': current_time, 'day': current_date,'cust_count':cust_count,'prod_count':prod_count,'cat_count':cat_count,'ord_count':ord_count}
    return render (request,'dashboard-main.html',context)

def dashboard_order(request):
    # Retrieve user orders excluding 'Pending' status
    user_orders = Order.objects.exclude(status='Pending').prefetch_related('orderitem_set__product_variant').order_by('-id')

    # Count pending (In Progress) and completed orders manually
    pending_orders_count_manual = 0
    completed_orders_count_manual = 0

    for order in user_orders:
        if order.status == 'In Progress':
            pending_orders_count_manual += 1
        elif order.status == 'Completed':
            completed_orders_count_manual += 1

    # Count pending (In Progress) and completed orders using direct count
    pending_orders_count_direct = Order.objects.filter(status='In Progress').exclude(status='Pending').count()
    completed_orders_count_direct = Order.objects.filter(status='Completed').exclude(status='Pending').count()

    context = {
        'user_orders': user_orders,
        'pending_orders_count_manual': pending_orders_count_manual,
        'completed_orders_count_manual': completed_orders_count_manual,
        'pending_orders_count_direct': pending_orders_count_direct,
        'completed_orders_count_direct': completed_orders_count_direct,
    }

    return render(request, 'dashboard_order.html', context)


def contact_us(request):
    context = {}
    return render(request, 'contact_us.html',context)




# def refund(request):
#     import razorpay
#     client = razorpay.Client(auth=("YOUR_ID", "YOUR_SECRET"))

#     client.payment.refund(paymentId,{
#     "amount": "100",
#     "speed": "normal",
#     "notes": {
#         "notes_key_1": "Beam me up Scotty.",
#         "notes_key_2": "Engage"
#     },
#     "receipt": "Receipt No. 31"
#     })
#     context = {}
#     return render(request,context)