from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

def teacher_required(view_func):
     @login_required
     @wraps(view_func)
     def _wrapped_view(request,*args,**kwargs):
          if not request.user.is_teacher:
               raise PermissionError(
                    _("K této stránce mají přístup pouze učitelé.")
               )
          return view_func(request,*args,**kwargs)
     return _wrapped_view


def student_required(view_func):
     @login_required
     @wraps(view_func)
     def _wrapped_view(request,*args,**kwargs):
          if not request.user.is_student:
               
               return PermissionDenied(
                    _("K této stránce mají přístup pouze studenti.")
               )
          return view_func(request,*args,**kwargs)
     return _wrapped_view


def own_required(model, owner_field):
     def decorator(view_func):
          @login_required
          @wraps(view_func)
          def _wrapped_view(request,*args,**kwargs):
               object_id=kwargs.get('pk')
               if object_id is None:
                    raise PermissionDenied(
                         _("Nenalezeno ID stránky.")
                    )
               obj=get_object_or_404(model,pk=object_id)
               owner=obj
               for part in owner_field.split("__"):
                    owner=getattr(owner,part)
          
               if owner!=request.user:
                    raise PermissionDenied(
                         _("Přístup odepřen, nejsi vlastník databázového zápisu.")
                    )
               return view_func(request,*args,**kwargs)
          return _wrapped_view
     return decorator
          
          