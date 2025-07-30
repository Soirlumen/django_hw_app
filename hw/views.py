from .models import Homework, Assignment, Key
from .forms import HomeworkForm,AssignmentForm,EvaluationForm

from django.shortcuts import render,redirect, get_object_or_404
import datetime
from django.http import HttpResponseForbidden

def hw_list_view(request):
    assignments_teacher = []
    assignments_student = []

    if hasattr(request.user, 'teacher_profile'):
        assignments_teacher = Assignment.objects.filter(teacher=request.user)

    if hasattr(request.user, 'student_profile'):
        subjects = request.user.student_profile.subjects.all()
        assignments_student = Assignment.objects.filter(subject__in=subjects)

    if not assignments_teacher and not assignments_student:
        return render(request, "list.html", {"message": "...nic tu zatím není..."})

    return render(request, "list.html", {
        "assignments_teacher": assignments_teacher,
        "assignments_student": assignments_student,
    })

""" 
def hw_list_view(request):
    assign=Assignment.objects.all()
    if not assign.exists():
        return render(request,"list.html",{"message":"...nic tu zatím není..."})
    return render(request,"list.html",{"assign":assign}) """

def assgn_detail_view(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if hasattr(request.user, 'teacher_profile'):
        homeworks = Homework.objects.filter(key__assignment=assignment)
        return render(request, "homework/teacher_detail.html", {
            "assignment": assignment,
            "homeworks": homeworks,
        })

    elif hasattr(request.user, 'student_profile'):
        already_submitted = False
        submitted_homework = None
        key = Key.objects.filter(student=request.user, assignment=assignment).first() # nebo get, je to divný
        if key:
            submitted_homework = Homework.objects.filter(key=key).first()
            already_submitted = submitted_homework is not None

        return render(request, "homework/student_detail.html", {
            "hwdetail": assignment,
            "already_submitted": already_submitted,
            "submitted_homework": submitted_homework,
        })

    return HttpResponseForbidden("Nemáš přístup.")
    
def assignment_create_view(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'teacher_profile'):
        return HttpResponseForbidden("Nelze vytvářet úkoly.")

    if request.method=="POST":
        form=AssignmentForm(request.POST,user=request.user)
        if form.is_valid():
            ass=form.save(commit=False)
            if ass.subject not in request.user.teacher_profile.subjects.all():
                return HttpResponseForbidden("Nelze přidávat úkoly do tohoto předmětu!!")
            ass.teacher = request.user
            ass.save() 
            return redirect("assgn_detail",pk=ass.pk)
    else:
        form=AssignmentForm(user=request.user)
    return render(request,"homework/ass_create.html",{"form":form})

def hw_create_view(request):
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
            return redirect("hw_detail", pk=hw.pk)
    else:
            form=HomeworkForm()

    return render(request,"homework/hw_create.html",{"form":form,"hwdetail":assignment})
    
def hw_update_view(request,pk):
    hw=get_object_or_404(Homework,pk=pk)
    if hw.key.student!=request.user:
        return HttpResponseForbidden("Nemáte oprávnění upravovat tento úkol.")
    if request.method=="POST":
        form=HomeworkForm(request.POST,instance=hw)
        if form.is_valid():
            edit_hw=form.save(commit=False)
            edit_hw.submitted=datetime.datetime.now()
            edit_hw.save()
            return redirect("hw_detail",pk=hw.pk)
    else:
        form=HomeworkForm(instance=hw)
    return render(request,'homework/hw_update.html',{'form':form,'hw':hw})

def assgn_delete_view(request,pk):
    assgn=get_object_or_404(Assignment,pk=pk)
    if assgn.teacher!=request.user:
        return HttpResponseForbidden("Nemáte oprávnění odstranit tento úkol.")
    if request.method=="POST":
        assgn.delete()
        return redirect("list")
    return render(request,"homework/ass_delete_confirm.html",{"assgn":assgn})

def hw_detail_view(request, pk):
    hw = get_object_or_404(Homework, pk=pk)

    if not (request.user == hw.key.student or request.user == hw.key.assignment.teacher):
        return HttpResponseForbidden("Nemáš přístup k tomuto domácímu úkolu.")

    return render(request, "homework/hw_detail.html", {"hw": hw})


def create_evaluation_view(request, pk):
    hw = get_object_or_404(Homework, pk=pk)

    if hw.key.assignment.teacher != request.user:
        return HttpResponseForbidden("Nemáš oprávnění hodnotit tento úkol.")

    if request.method == "POST":
        form = EvaluationForm(request.POST, instance=hw)
        if form.is_valid():
            form.save()
            return redirect("hw_detail", pk=hw.pk)
    else:
        form = EvaluationForm(instance=hw)
    return render(request, "homework/hw_evaluate.html", {"form": form, "hw": hw})


def edit_evaluation_view(request,pk):
    hw=get_object_or_404(Homework,pk=pk)
    if hw.key.assignment.teacher != request.user:
        return HttpResponseForbidden("Nemáš oprávnění upravit hodnocení tohoto úkolu.")
    if request.method=="POST":
        form=EvaluationForm(request.POST,instance=hw)
        if form.is_valid():
            edit_hw=form.save(commit=False)
            edit_hw.save()
            return redirect("hw_detail",pk=hw.pk)
    else:
        form=EvaluationForm(instance=hw)
    return render(request,'homework/hw_evaluation_update.html',{'form':form,'hw':hw})
    
    
def delete_evaluation_view(request,pk):
    hw=get_object_or_404(Homework, pk = pk)
    if hw.key.assignment.teacher != request.user:
        return HttpResponseForbidden("Nemáš oprávnění upravit hodnocení tohoto úkolu.")
    if request.method=="POST":
        hw.score = None
        hw.text_evaluation = None
        hw.save()
        return redirect("hw_detail",pk=hw.pk)
    return render(request,"homework/hw_evaluation_delete_confirm.html",{"hw":hw})
    
    