"""
URL configuration for erp_backoffice project.

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
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from common.views import CustomAuthToken
from common.router import router as common_router
from hr.router import router as hr_router
from identities.router import router as identities_router
from inventory.router import router as inventory_router
from purchasing.router import router as purchasing_router
from sales.router import router as sales_router
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="ERP API",
        default_version='v1',
        description="API documentation for ERP System",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="ardzyix@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=settings.BASE_URL
)


urlpatterns = [

    path('api/auth/login/', CustomAuthToken.as_view(), name='api-login'),
    path('api/common/', include(common_router.urls)),
    path('api/hr/', include(hr_router.urls)),
    path('api/identities/', include(identities_router.urls)),
    path('api/inventory/', include(inventory_router.urls)),
    path('api/purchasing/', include(purchasing_router.urls)),
    path('api/sales/', include(sales_router.urls)),

    path('i18n/setlang/', set_language, name='set_language'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    # ... your other i18n url patterns
)
