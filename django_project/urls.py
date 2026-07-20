from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from accounts.views import CustomLoginView
from django.conf.urls.i18n import i18n_patterns
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')), 
]
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path("accounts/login/", CustomLoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")), 
    path("hw/", include("hw.urls")),
    path("", include("accounts.urls")), 
    path("news/", include("news.urls")),
)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)