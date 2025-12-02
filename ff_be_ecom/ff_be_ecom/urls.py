"""
URL configuration for ff_be_ecom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from django.urls import include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import RegisterView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/ecommerce/', include('categories.urls')),
    path('api/ecommerce/', include('products.urls')),
    path('api/ecommerce/', include('orders.urls')),
    path('api/ecommerce/', include('variants.urls')),
    path('api/ecommerce/', include('reviews.urls')),
    path('api/ecommerce/', include('pricing_rules.urls')),
    path('api/ecommerce/', include('analytics.urls')),
    path('api/ecommerce/', include('inventory.urls')),
    path('api/ecommerce/', include('promotions.urls')),
]
