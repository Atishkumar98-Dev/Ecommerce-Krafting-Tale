from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Product, Order, OrderItem,ProductVariant
from django.contrib import messages
import razorpay
from django.conf import settings

# Create your views here.
def home(request):
    product = Product.objects.all()
    context = {'product':product}
    return render(request,'home.html',context)



def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})



@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    customer = request.user.customer
    # Check if the user already has an active order, if not, create one
    
    try:
    # Get or create an Order object with the specified customer and status='Pending'
        order, created = Order.objects.get_or_create(customer=customer, status='Pending')
    except Order.MultipleObjectsReturned:
        # Handle the case where multiple objects are returned
        # For example, you can choose the first object in the queryset
        orders = Order.objects.filter(customer=customer, status='Pending')
        order = orders.first() if orders.exists() else None
        created = False  # Since the object already exists

    # Check if the product is already in the order, if yes, update quantity
    try:
        order_item, item_created = OrderItem.objects.get_or_create(order=order, product_variant=product)
    except OrderItem.MultipleObjectsReturned:
    # Handle the case where multiple objects are returned
    # For example, you can choose the first object in the queryset
        order_item = OrderItem.objects.filter(order=order, product_variant=product).first()
        item_created = False 
    if not item_created:
        try:
            # Attempt to increment the quantity by 1, handling the case where quantity is None
            order_item.quantity = order_item.quantity + 1 if order_item.quantity is not None else 1
            order_item.save()
        except Exception as e:
            # Handle the exception (you can customize the exception type based on your needs)
            print(f"Error updating quantity for order item: {e}")
    else:
        try:
            # Attempt to increment the quantity by 1
            order_item.quantity = order_item.quantity + 1
        except Exception as e:
            # Handle the exception (you can customize the exception type based on your needs)
            print(f"Error updating quantity for order item: {e}")
    
    return redirect('cart_view')  # Redirect to the cart view





@login_required
def cart_view(request):
    items_with_errors = []
    customer = request.user.customer
    # Check if the user already has an active order, if not, create one
    
    try:
    # Get or create an Order object with the specified customer and status='Pending'
        order, created = Order.objects.get_or_create(customer=customer, status='Pending')
    except Order.MultipleObjectsReturned:
        # Handle the case where multiple objects are returned
        # For example, you can choose the first object in the queryset
        orders = Order.objects.filter(customer=customer, status='Pending')
        order = orders.first() if orders.exists() else None
        created = False  # Since the object already exists


    order_items = OrderItem.objects.filter(order=order)
    total_price = 0  # Initialize total_price to zero
    for item in order_items:
        item_price = 0
        if item.product_variant.price is not None:
            # Calculate the item price by converting the price to float, rounding it, and multiplying by the quantity
            try:
                print(item.product_variant.price,'item.product_variant.price')
                prod_price= item.product_variant.price
                Price = int(prod_price)
                print(Price)
                if item.quantity is not None:
                    item_price = Price * int(item.quantity)
                    total_price += item_price
                else:
                    item.quantity = 1
                    item_price = Price
                    
            except ValueError:
                print(f"Error: Unable to convert price for item {item} to a valid number. Skipping this item.")
                items_with_errors.append(item)
                continue  # Skip to the next item if there's an error
            
        else:
            print(f"Warning: Item {item} has no specified price. Skipping this item.")
        total_price += item_price
    return render(request, 'cart.html', {'order_items': order_items, 'total_price': total_price})

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
    print(order_item.quantity,'order_item.quantity')
    
    if order_item.quantity is not None:
        order_item.quantity += 1
    else:
        # If quantity is None, set it to 1
        order_item.quantity = 1
    order_item.save()

    messages.success(request, 'Item quantity increased.')
    return redirect('cart_view')

def remove_from_cart(request, item_id):
    order_item = get_object_or_404(OrderItem, pk=item_id)
    order_item.delete()

    messages.success(request, 'Item removed from the cart.')
    return redirect('cart_view')

@login_required
def checkout(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_SECRET_KEY))
    customer = request.user.customer
    try:
        # Get or create an Order object with the specified customer and status='Pending'
        order, created = Order.objects.get_or_create(customer=customer, status='Pending')
    except Order.MultipleObjectsReturned:
        # Handle the case where multiple objects are returned
        # For example, you can choose the first object in the queryset
        orders = Order.objects.filter(customer=customer, status='Pending')
        order = orders.first() if orders.exists() else None
        created = False  # Since the object already exists
    order_items = OrderItem.objects.filter(order=order)
    total_price = 0

    for item in order_items:
        # Update order_items.item_price and order_items.quantity
        if item.product_variant.price is not None:
            prod_price= item.product_variant.price
            Price = int(prod_price)
            if item.quantity is not None:
                item_price = Price * int(item.quantity)
                total_price += item_price
                order.total_price = total_price
                order.save()
                item.item_price = Price
                item.quantity = item.quantity
                item.save()
            else:
                item.quantity += 1
                item_price = Price  # Save the changes to the database
                item.item_price = Price
                item.quantity = item.quantity
                item.save()
        else:
        # Handle the case where item.product_variant.price is None
        # You might want to log a warning or handle it differently based on your needs
            pass
        # Calculate the total_price
        price = item.product_variant.price
        print(item.quantity)
        print(price)
        print('item.quantity')
        total_price += int(item.product_variant.price) * item.quantity
        print(total_price,'saving...')
    # Assuming a simple payment confirmation process
        # if request.method == 'POST':
        if total_price != 0:
            print(total_price,'checkout')
            razor_pay_order = client.order.create({
                'amount': int(total_price),  # Amount in paise (e.g., 50000 paise = 500 INR)
                'currency': 'INR',
                'payment_capture': 1  # Auto capture payments
            })
            # Perform payment processing logic here

            # Mark the order as paid and create a new order
            order.status = 'Paid'
            order.total_price = total_price
            order.save()

            new_order = Order.objects.create(customer=request.user.customer, status='Pending',)

    return render(request, 'checkout.html', {'order': order,'total_price':total_price,'razor_pay_order':razor_pay_order})

def successMsg(request):
    # if request.user.is_authenticated:
    #         customer = request.user.customer
    #         order , created  = Order.objects.get_or_create(customer=customer,complete=False)
    #         orderItem , created  = OrderItem.objects.get_or_create(order=order) 
    #         orderItem=order.orderitem_set.all()
    # else:
    #     orderItem=[]
    #     orderItem.save()
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
    for key, value in request.GET.items():
        print(f"{key}: {value}")
        print()
    return render(request, 'success.html',)


def user_orders(request):
    # Assuming 'request.user' is authenticated
    user_orders = Order.objects.filter(customer=request.user.customer)
    order_items = OrderItem.objects.filter(order__in=user_orders)
    for order_item in order_items:
        print(f"OrderItem ID: {order_item.id}")
        print(f"Order ID: {order_item.order.id}")
        print(f"Product: {order_item.product_variant.name}")
        print(f"Quantity: {order_item.quantity}")
        print(f"Price: {order_item.product_variant.price}")
        print("\n")  # Add a line break for better readability
    print(order_items)
    return render(request, 'user_orders.html', {'user_orders': user_orders,'order_item':order_items})