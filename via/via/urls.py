"""via URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from via_operator import views as via_operator
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('superadmin/', include('via_superadmin.urls')),
    path('manager/', include('via_manager.urls')),
    path('operator/', include('via_operator.urls')),
    path('via_admin/', include('via_admin.urls')),
    path('via_image/', include('via_image.urls')),
    # path('', via_operator.vw_login_user),
    path('', via_operator.vw_landing),
    path('login/', via_operator.vw_login_user, name="main_login"),
    path('logout/', via_operator.vw_log, name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
