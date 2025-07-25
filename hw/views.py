from django.views.generic import ListView, DetailView,CreateView,UpdateView

from .models import Homework, Assignment, Key
from .forms import HomeworkForm,AssignmentForm

from django.shortcuts import render,redirect
import datetime
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


class HwListView(ListView):
    model=Assignment
    template_name="list.html"
    
"""class HwDetailView(DetailView):
    model=Assignment
    template_name="hw_detail.html"
    """
    
"""class AssignmentCreateView(CreateView):
    model=Assignment
    form_class=AssignmentForm
    template_name="ass_create.html"
    """
    
"""class HwCreateView(CreateView):
    model=Homework
    form_class=HomeworkForm
    template_name="hw_create.html"
    """
def HwDetailView(request, pk):
    detail = get_object_or_404(Assignment, pk=pk)
    already_submitted = False

    if request.user.is_authenticated:
        key = Key.objects.filter(student=request.user, assignment=detail).first()
        if key:
            already_submitted = Homework.objects.filter(key=key).exists()

    return render(request, "homework/hw_detail.html", {
        'hwdetail': detail,
        'already_submitted': already_submitted
    })
def AssignmentCreateView(request):
    if request.method=="POST":
        form=AssignmentForm(request.POST)
        if form.is_valid():
            ass=form.save()
            return redirect("hw_detail",pk=ass.id)
    else:
        form=AssignmentForm()
    return render(request,"homework/ass_create.html",{"form":form})

def HwCreateView(request):
    assgn_id=request.GET.get("assgn_id")
    assignment=get_object_or_404(Assignment,pk=assgn_id)
    if request.method=="POST":
        form=HomeworkForm(request.POST)
        if form.is_valid():
            student=request.user
            key,created=Key.objects.get_or_create(student=student,assignment=assignment)
            hw=form.save(commit=False)
            hw.key=key
            hw.submitted=datetime.datetime.now()
            hw.save()
            return redirect("hw_detail", pk=assignment.pk)
    else:
            form=HomeworkForm()

    return render(request,"homework/hw_create.html",{"form":form,"hwdetail":assignment})
    