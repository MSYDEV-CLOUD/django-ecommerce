from django.shortcuts import render, redirect
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse
from django.template.loader import render_to_string
import stripe

# Stripe setup (even if you're not connecting, you can keep this structure)
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()

            # Render email template (both text and HTML)
            email_message_text = render_to_string('orders/order_confirmation_email.txt', {'order': order})
            email_message_html = render_to_string('orders/order_confirmation_email.html', {'order': order})

            try:
                # Send both plain text and HTML email versions
                email = EmailMultiAlternatives(
                    'Order Confirmation',
                    email_message_text,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email]
                )
                email.attach_alternative(email_message_html, "text/html")
                email.send()

            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            except Exception as e:
                # Log or handle the error
                print(f"Error sending email: {e}")

            return render(request, 'orders/order_created.html', {'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})

def create_checkout_session(request):
    cart = Cart(request)
    total_amount = int(cart.get_total_price() * 100)  # Convert to cents for Stripe

    try:
        # Dynamic URLs for success and cancel, works even in a demo
        success_url = request.build_absolute_uri(reverse('payment_success'))
        cancel_url = request.build_absolute_uri(reverse('payment_cancel'))

        # Simulated Stripe checkout session (works even if you're not connecting to Stripe)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Order Payment',
                        },
                        'unit_amount': total_amount,  # Stripe expects the amount in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success_url,  # Dynamic success URL
            cancel_url=cancel_url,    # Dynamic cancel URL
        )

        return JsonResponse({'sessionId': session.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# View for Payment Success
def payment_success(request):
    return render(request, 'orders/payment_success.html')

# View for Payment Cancel
def payment_cancel(request):
    return render(request, 'orders/payment_cancel.html')