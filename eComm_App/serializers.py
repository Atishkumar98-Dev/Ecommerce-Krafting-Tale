# serializers.py
from rest_framework import serializers
from .models import Product, Order, OrderItem, Customer, Category
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Product
from rest_framework.response import Response


# class AddToCartAPI(APIView):
#     def post(self, request, product_id):
#         product = get_object_or_404(Product, pk=product_id)
#         # Add your logic for adding the product to the cart
#         return Response({"message": "Product added to cart successfully."}, status=status.HTTP_200_OK)



class ProductSerializer(serializers.ModelSerializer):
    # image = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'discount_price', 'actual_price', 
                  'image', 'brand', 'category', 'sub_category', 'slug', 
                  'stock_quantity', 'ratings', 'no_of_ratings']
    
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            print(obj.image.url)
            return request.build_absolute_uri(obj.image.url)
        return None



class OrderItemSerializer(serializers.ModelSerializer):
    product_variant = ProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'item_price', 'product_variant']



class OrderSerializer(serializers.ModelSerializer):
    orderitem_set = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'




class CustomerSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = '__all__'

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and hasattr(obj.photo, 'url'):
            photo_url = obj.photo.url
            if request is not None:
                return request.build_absolute_uri(photo_url)
            return photo_url
        return None






class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'






class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        authenticate_kwargs = {
            'username': attrs.get('username'),
            'password': attrs.get('password')
        }
        user = authenticate(**authenticate_kwargs)

        if not user:
            raise serializers.ValidationError('No active account found with the given credentials')

        # You can add custom claims here if needed
        data = super().validate(attrs)
        data['username'] = user.username
        # Add more data to the payload if needed

        return data
