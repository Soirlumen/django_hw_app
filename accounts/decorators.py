from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from functools import wraps
from hw.models import Assignment, Homework

def teacher_required(view_func):
     @wraps(view_func)
     def _wrapped_view(request,*args,**kwargs):
          if request.user.is_authenticated and request.user.is_teacher:
               return view_func(request,*args,**kwargs)
          return HttpResponseForbidden("nemáte přístup k této stránce")
     return _wrapped_view


def student_required(view_func):
     @wraps(view_func)
     def _wrapped_view(request,*args,**kwargs):
          if request.user.is_authenticated and request.user.is_student:
               return view_func(request,*args,**kwargs)
          return HttpResponseForbidden("nemáte přístup k této stránce")
     return _wrapped_view