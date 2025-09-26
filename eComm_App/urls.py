"""
URL configuration for eComm_Main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from . import views
from simple_chatbot.views import SimpleChatbot
# from .views import LoginAPIView   
from rest_framework_simplejwt.views import TokenRefreshView 
from .views import CustomTokenObtainPairView
# from .views import AddToCartAPI
from .views import UserOrdersAPIView
from .views import CustomerProfileView

urlpatterns = [
    path('',views.home,name='homepage'),
    path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path("simple_chatbot/", SimpleChatbot.as_view()),
    path('login/',views.loginpage,name='login'),
    path('register/', views.register,name='register'),
    path('logout/',views.logoutUser, name='logout'),
    path('user_orders/', views.user_orders, name='user_orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard_home/', views.dashboard,name='dashboard'),
    path('dashboard_order/', views.dashboard_order,name='dashboard_order'),
    path('contact_us/', views.contact_us,name='contact_us'),
    path('delivery_track/', views.delivery_track,name='delivery_track'),
    path('all_orders_details/',views.All_order,name='all_order_details'),
    path('upload-excel/', views.upload_csv, name='upload_excel'),
    path('update_delivery/<int:order_id>/', views.delivery_status_update,name='update_delivery'),
    path('reduce_quantity/<int:item_id>/', views.reduce_quantity, name='reduce_quantity'),
    path('increase_quantity/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order_success/', views.successMsg, name='successMsg'),
    path('api/cart/', views.cart_api, name='api-cart-detail'),
    path('api/add-to-cart/', views.add_to_cart_api, name='api-add-to-cart'),
    path('api/remove-from-cart/', views.remove_from_cart_api, name='api-add-to-cart'),
    path('api/delete-from-cart/', views.delete_from_cart_api, name='api-add-to-cart'),
    path('api/user_orders/', UserOrdersAPIView.as_view(), name='user_orders_api'),
    path('api/products/<int:product_id>/', views.product_detail_view, name='product-detail'),
    path('api/products/', views.product_list, name='product-list'),
    path('api/profile/', CustomerProfileView.as_view(), name='profile_api'),
    path('api/update_profile/', views.update_profile_api, name='update_profile_api'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', views.csrf_exempt_token_refresh_view, name='token_refresh')
    
]
