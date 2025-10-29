from django.http import HttpResponseForbidden
from functools import wraps
from django.shortcuts import get_object_or_404
from hw.models import Assignment, Homework

def teacher_required(view_func):
     @wraps(view_func)
     def _wrapped_view(request,*args,**kwargs):
          if request.user.is_authenticated and request.user.is_teacher:
               return view_func(request,*args,**kwargs)
          return HttpResponseForbidden("K této stránce mají přístup pouze učitelé.")
     return _wrapped_view


def student_required(view_func):
     @wraps(view_func)
     def _wrapped_view(request,*args,**kwargs):
          if request.user.is_authenticated and request.user.is_student:
               return view_func(request,*args,**kwargs)
          return HttpResponseForbidden("K této stránce mají přístup pouze studenti")
     return _wrapped_view


def own_required(model, owner_field):
     def decorator(view_func):
          @wraps(view_func)
          def _wrapped_view(request,*args,**kwargs):
               object_id=kwargs.get('pk')
               if not object_id:
                    return HttpResponseForbidden("Nenalezeno ID stránky.")
               obj=get_object_or_404(model,pk=object_id)
               owner=obj
               for part in owner_field.split("__"):
                    owner=getattr(owner,part)
          
               if owner!=request.user:
                    return HttpResponseForbidden("Přístup odepřen, nejsi vlastník databázového zápisu.")
               return view_func(request,*args,**kwargs)
          return _wrapped_view
     return decorator
          
          