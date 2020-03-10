"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from api.views import GetLatestDataArchived, FindAssociation

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthcheck', TemplateView.as_view(template_name='health.html')),
    path('api/association', FindAssociation.as_view()),
    path('api/entity/_startswith', FindEntityByLabelStartsWith.as_view()),
    path('archive/latest', GetLatestDataArchived.as_view()),
] + static(settings.ARCHIVE_URL, document_root=settings.TARGET_DATA_DIR)
