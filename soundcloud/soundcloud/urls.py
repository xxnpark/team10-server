"""soundcloud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from user.googleapi import *
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs', SpectacularJSONAPIView.as_view(), name='schema-json'),
    path('docs/swagger', SpectacularSwaggerView.as_view(url_name='schema-json'), name='swagger-ui'),
    path('docs/redoc', SpectacularRedocView.as_view(url_name='schema-json'), name='redoc'),
    path('', include('user.urls')),
    path('', include('comment.urls')),
    path('', include('track.urls')),
    path('', include('reaction.urls')),
    path('', include('utility.urls')),
    path('', include('track.urls')),
    path('', include('set.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__', include(debug_toolbar.urls)),
    ]
