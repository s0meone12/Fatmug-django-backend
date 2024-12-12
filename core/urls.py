"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings
from core.apis.wordpress_webhook.wordpress_webhook_endpnt_view import WordpressWebhookView
from .views import View
from .temp_views import testing
from core.dynamic_api.schema.views import SchemaView
from core.dynamic_api.api_discovery.views import ApiDiscoveryView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('testing', testing, name='testing'),

    # wordpress webhook api gateway endpoint for data receive
    path('wordpress_webhook', WordpressWebhookView.as_view(
        {"post": "wordpress_webhooks"}), name='wordpress_webhook'),
    path('sku/sale-price/recommendation',
         View.amz_sku.pricing.get_recommendation, name='get_recommendation'),
    path('sku/sale-price/publish', View.amz_sku.pricing.publish, name='publish'),
    path('schema/', SchemaView.as_view()),
    path('api-discovery/', ApiDiscoveryView.as_view())
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

