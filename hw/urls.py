from django.urls import path
from .views import assgn_delete_view,hw_list_view,hw_update_view, hw_detail_view, hw_create_view,assignment_create_view

urlpatterns = [
    path("", hw_list_view,name="list"),
    path("homework/<int:pk>/",hw_detail_view,name="hw_detail"),
    path("homework/createass/",assignment_create_view,name="ass_create"),
    path("homework/submithw/", hw_create_view,name="hw_submit"),
    path('homework/<int:pk>/update/', hw_update_view, name='homework_update'),
    path('homework/<int:pk>/delete_asgn/', assgn_delete_view, name="assignment_delete"),
]
