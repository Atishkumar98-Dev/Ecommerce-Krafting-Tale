# Krafting Tale - E-commerce Web Application

## Overview
Krafting Tale is a full-featured e-commerce web application built with **Django** and **Bootstrap 5**.  
It allows users to browse products, manage their cart, place orders, and make payments via **Razorpay**.  
Admins can manage products, view orders, and track order statuses.

---

## Features

### User Side
- User registration and authentication
- Browse products with images, descriptions, and prices
- Add/remove products to/from cart
- Update product quantity in cart
- Apply discount coupons
- Checkout with order summary
- View shipping address and total price interactively
- Razorpay payment integration
- View order history with delivery and transaction status

### Admin Side
- Manage products (Create, Read, Update, Delete)
- View all orders
- Update order and delivery status
- Access dashboard analytics

---

## Tech Stack
- **Backend:** Python 3, Django  
- **Frontend:** HTML5, CSS3, Bootstrap 5, Boxicons  
- **Database:** PostgreSQL (or SQLite for development)  
- **Payments:** Razorpay  
- **Other:** JavaScript for interactive UI, Lordicon for animations

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd krafting-tale
````

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file or add environment variables:

```
DEBUG=True
SECRET_KEY=your_django_secret_key
RAZORPAY_API_KEY=your_razorpay_key
RAZORPAY_SECRET_KEY=your_razorpay_secret
DATABASE_URL=your_database_url
```

### 5. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run Server

```bash
python manage.py runserver
```

Access: `http://127.0.0.1:8000/`

---

## Usage

### Browsing Products

* Navigate to the home page to see product list with images, names, prices.

### Cart Management

* Add products to cart
* Increase/decrease quantity
* Remove products from cart
* Apply discount coupon

### Checkout

* View order summary with product images
* Interactive blocks for Shipping Address and Total Price
* Click **Pay Now** to initiate Razorpay payment

### Order Management

* View past orders with status and product images
* Track delivery and transaction status
* Admin can update order status

---

## Razorpay Integration

* Razorpay Checkout JS is used
* Amount calculated in **paise** (`₹ * 100`)
* Redirects to order success page after payment

Example Checkout JS:

```javascript
var options = {
    key: '{{ settings.RAZORPAY_API_KEY }}',
    amount: '{{ total_price * 100 }}', // in paise
    currency: 'INR',
    name: 'Krafting Tale',
    description: 'Payment for your order',
    order_id: '{{ razor_pay_order.id }}',
    handler: function (response) {
        window.location.href = `/order_success/?razorpay_payment_id=${response.razorpay_payment_id}&razorpay_order_id=${response.razorpay_order_id}&razorpay_signature=${response.razorpay_signature}`;
    }
};
function openCheckout() {
    var rzp = new Razorpay(options);
    rzp.open();
}
```

---

## File Structure

```
krafting-tale/
│
├─ apps/
│  ├─ accounts/        # User authentication and profile
│  ├─ products/        # Product and variant management
│  ├─ orders/          # Order and cart management
│  └─ core/            # Common utilities
│
├─ templates/
│  ├─ root.html
│  ├─ checkout.html
│  ├─ cart.html
│  ├─ user_orders.html
│  └─ ...
│
├─ static/
│  ├─ css/
│  ├─ js/
│  ├─ images/          # Product and vector images
│  └─ ...
│
├─ manage.py
├─ requirements.txt
└─ README.md
```

---


## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit changes (`git commit -m "Add feature"`)
4. Push branch (`git push origin feature-name`)
5. Create a Pull Request

---

## License

This project is licensed under the MIT License.

---
