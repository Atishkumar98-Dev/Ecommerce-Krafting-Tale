# from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django_countries.data import COUNTRIES
from django.contrib.postgres.fields import ArrayField

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=False)

    def __str__(self):
        return self.name
    

class Brand(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, related_name='main_category_products', on_delete=models.CASCADE)
    sub_category = models.ForeignKey(Category, related_name='sub_category_products', on_delete=models.CASCADE)
    image_url = models.URLField(null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(unique=False,blank=True,null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/',null=True,blank=True)
    ratings = models.FloatField(blank=True,null=True,)
    no_of_ratings = models.PositiveIntegerField(blank=True,null=True,)
    discount_price = models.PositiveIntegerField(default=0,blank=True)
    actual_price = models.PositiveIntegerField(default=0,blank=True)
    # images = ArrayField(models.ImageField(upload_to='product_images/'), blank=True, null=True)
    

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant_name = models.CharField(max_length=255)
    variant_price = models.DecimalField(max_digits=10, decimal_places=2)
    variant_quantity = models.PositiveIntegerField(default=0)
    # image = models.ImageField(null=True)



state_choices = (("Andhra Pradesh","Andhra Pradesh"),("Arunachal Pradesh ","Arunachal Pradesh "),("Assam","Assam"),("Bihar","Bihar"),("Chhattisgarh","Chhattisgarh"),("Goa","Goa"),("Gujarat","Gujarat"),("Haryana","Haryana"),("Himachal Pradesh","Himachal Pradesh"),("Jammu and Kashmir ","Jammu and Kashmir "),("Jharkhand","Jharkhand"),("Karnataka","Karnataka"),("Kerala","Kerala"),("Madhya Pradesh","Madhya Pradesh"),("Maharashtra","Maharashtra"),("Manipur","Manipur"),("Meghalaya","Meghalaya"),("Mizoram","Mizoram"),("Nagaland","Nagaland"),("Odisha","Odisha"),("Punjab","Punjab"),("Rajasthan","Rajasthan"),("Sikkim","Sikkim"),("Tamil Nadu","Tamil Nadu"),("Telangana","Telangana"),("Tripura","Tripura"),("Uttar Pradesh","Uttar Pradesh"),("Uttarakhand","Uttarakhand"),("West Bengal","West Bengal"),("Andaman and Nicobar Islands","Andaman and Nicobar Islands"),("Chandigarh","Chandigarh"),("Dadra and Nagar Haveli","Dadra and Nagar Haveli"),("Daman and Diu","Daman and Diu"),("Lakshadweep","Lakshadweep"),("National Capital Territory of Delhi","National Capital Territory of Delhi"),("Puducherry","Puducherry"))
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shipping_address = models.TextField()
    email = models.EmailField()
    photo = models.ImageField(upload_to='',null=True,blank=False)
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(
        "State",
        max_length=1024,
        choices = state_choices,
        default="Maharashtra"
    )

    country = models.CharField(
        "Country",
        max_length=3,
        choices=sorted(COUNTRIES.items()),
        default="IN"
    )
    zip_code = models.CharField(max_length=10)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    check_me_out = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username
    # Add more customer-related fields as needed

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    status = models.CharField(max_length=255)
    delivery_address = models.TextField()
    delivery_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_razorpay_id = models.CharField(max_length=255,null=True)
    transaction_id = models.CharField(max_length=255,null=True)
    # Add fields for order status, shipping details, etc.

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(null=True)
    item_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)

class Discount(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    delivery_date = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True,default='Will be Arriving Soon')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery for Order #{self.order.id} - {self.status}"
    


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"