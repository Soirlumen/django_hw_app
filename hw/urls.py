from django.urls import path
from .views import HwListView, HwDetailView, HwCreateView,AssignmentCreateView

urlpatterns = [
    path("", HwListView.as_view(),name="list"),
    path("homework/<int:pk>/",HwDetailView,name="hw_detail"),
    path("homework/createass/",AssignmentCreateView,name="ass_create"),
    path("homework/submithw/", HwCreateView,name="hw_submit")
]
