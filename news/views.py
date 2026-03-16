from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import teacher_required, student_required, own_required
from django.http import Http404
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from .models import NewsPost
from .forms import CreateEditPost

@login_required
def posts_view(request):
     posts=NewsPost.objects.order_by("-date")
     context={
          "posts":posts,
     }
     return render(request,"newspost/posts.html",context)

@login_required
def create_post_view(request):
     if not request.user.is_superuser:
          raise Http404()
     if request.method=="POST":
          form = CreateEditPost(request.POST)
          if form.is_valid():
               cr_post = form.save(commit=False)
               cr_post.date = timezone.now()
               cr_post.save()
               messages.success(request,_("Oznámení bylo úspěšně vytvořeno."))
               return redirect("news-post")
          else:
            messages.warning(request, _("Formulář se nepodařilo odeslat. Zkontroluj prosím vyplněná pole."))
            print(form.errors)
            print(form.non_field_errors())
     else:
          form = CreateEditPost()
     return render(request, "newspost/create_post.html", {"form": form})        

@login_required
def edit_post_view(request,pk):
     if not request.user.is_superuser:
          raise Http404()
     post=get_object_or_404(NewsPost, pk=pk)
     if request.method=="POST":
          form = CreateEditPost(request.POST, instance=post)
          if form.is_valid():
               cr_post = form.save(commit=False)
               cr_post.date = timezone.now()
               cr_post.save()
               messages.success(request,_("Oznámení bylo úspěšně upraveno."))
               return redirect("news-post")
          else:
            messages.warning(request, _("Formulář se nepodařilo odeslat. Zkontroluj prosím vyplněná pole."))
            print(form.errors)
            print(form.non_field_errors())
     else:
          form = CreateEditPost(instance=post)
     return render(request, "newspost/edit_post.html", {"form": form, "post":post})        