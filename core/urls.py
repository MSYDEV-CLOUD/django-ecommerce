from django.urls import path, include
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('register/', views.register_view, name='register'),  # Custom registration view
    path('logout/', views.logout_view, name='logout'),  # Custom logout view
    path('accounts/login/', LoginView.as_view(template_name='core/login.html'), name='login'),  # Custom login template
    path('accounts/', include('django.contrib.auth.urls')),  # Include Django's built-in auth views
]
