from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('history/', views.order_history, name='order_history'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),  # Success page
    path('cancel/', views.payment_cancel, name='payment_cancel'),  # Cancel page
]
