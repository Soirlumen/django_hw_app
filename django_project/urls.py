from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("hw/", include("hw.urls")),
    path("", include("accounts.urls")), 
    path("accounts/", include("django.contrib.auth.urls")), 
]
