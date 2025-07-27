from django.views.generic import ListView, DetailView,CreateView,UpdateView

from .models import Homework, Assignment, Key
from .forms import HomeworkForm,AssignmentForm

from django.shortcuts import render,redirect
import datetime
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
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
    assignment = get_object_or_404(Assignment, pk=pk)

    if hasattr(request.user, 'teacher_profile'):
        # Učitel: chceme tabulku odevzdaných
        homeworks = Homework.objects.filter(key__assignment=assignment)
        return render(request, "homework/teacher_detail.html", {
            "assignment": assignment,
            "homeworks": homeworks
        })

    elif hasattr(request.user, 'student_profile'):
        # Student: detail + možnost odevzdání
        already_submitted = False
        submitted_homework = None
        key = Key.objects.filter(student=request.user, assignment=assignment).first()
        if key:
            submitted_homework = Homework.objects.filter(key=key).first()
            already_submitted = submitted_homework is not None

        return render(request, "homework/hw_detail.html", {
            "hwdetail": assignment,
            "already_submitted": already_submitted,
            "submitted_homework": submitted_homework,
        })

    return HttpResponseForbidden("Nemáš přístup.")
    
    
def AssignmentCreateView(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'teacher_profile'):
        return HttpResponseForbidden("Nelze vytvářet úkoly.")

    if request.method=="POST":
        form=AssignmentForm(request.POST)
        if form.is_valid():
            ass=form.save(commit=False)
            if ass.subject not in request.user.teacher_profile.subjects.all():
                return HttpResponseForbidden("Nelze přidávat úkoly do tohoto předmětu!!")
            ass.teacher = request.user
            ass.save() 
            return redirect("hw_detail",pk=ass.id)
    else:
        form=AssignmentForm()
    return render(request,"homework/ass_create.html",{"form":form})

def HwCreateView(request):
    assgn_id=request.GET.get("assgn_id")
    assignment=get_object_or_404(Assignment,pk=assgn_id)
    if not hasattr(request.user, 'student_profile') or assignment.subject not in request.user.student_profile.subjects.all():
        return HttpResponseForbidden("Nemáš přístup k tomuto předmětu.")

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
    