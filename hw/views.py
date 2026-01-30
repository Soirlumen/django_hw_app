from .models import Homework, Assignment, Key, ReviewHomework
from accounts.models import SubjectType
from .forms import HomeworkForm, AssignmentForm, EvaluationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import datetime
from accounts.decorators import teacher_required, student_required, own_required
from django.http import HttpResponseForbidden,HttpResponseBadRequest, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.template import loader


@teacher_required
def hw_teacher_list_before_release_view(request):
    now = timezone.now()
    template=loader.get_template("list/before_release.html")
    subjects=request.user.teacher_subjects
    filtered_subjects=Assignment.objects.filter(subject__in=subjects,release__gt=now)
    context={
        "filtered_subjects": filtered_subjects
    }
    return HttpResponse(template.render(context,request))

@login_required
def hw_list_active_view(request):
    assignments_teacher = []
    assignments_student = []
    now = timezone.now()
    template=loader.get_template("list/active.html")
    if request.user.is_teacher:
        subjects = request.user.teacher_subjects
        assignments_teacher = Assignment.objects.filter(subject__in=subjects, release__lte=now, deadline__gt=now)
        
    # student
    if request.user.is_student:
        subjects = request.user.student_subjects
        assignments_student = Assignment.objects.filter(subject__in=subjects, release__lte=now, deadline__gt=now)
    context={
            "assignments_teacher": assignments_teacher,
            "assignments_student": assignments_student,
    }
    return HttpResponse(template.render(context,request))

@login_required
def hw_list_after_deadline_view(request):
    assignments_teacher = []
    assignments_student = []
    now = timezone.now()
    if request.user.is_teacher:
        subjects = request.user.teacher_subjects
        assignments_teacher = Assignment.objects.filter(subject__in=subjects, deadline__lte=now)
        
    # student
    if request.user.is_student:
        subjects = request.user.student_subjects
        assignments_student = Assignment.objects.filter(subject__in=subjects, deadline__lte=now)
    return render(request, "list/after_deadline.html",
        {
            "assignments_teacher": assignments_teacher,
            "assignments_student": assignments_student,
        },
    )    

@teacher_required
def assgn_detail_teacher(request,pk):
    assignm=get_object_or_404(Assignment,pk=pk)
    homeworks = Homework.objects.filter(key__assignment=assignm)
    return render(
            request,
            "homework/teacher_detail.html",
            {"assignment": assignm, "homeworks": homeworks},
        )

@student_required
def assgn_detail_stud(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    key, created = Key.objects.get_or_create(
        student=request.user,
        assignment=assignment
    )
    submitted_homework = Homework.objects.filter(key=key).first()
    already_submitted = submitted_homework is not None

    return render(
        request,
        "homework/student_detail.html",
        {
            "hwdetail": assignment,
            "already_submitted": already_submitted,
            "submitted_homework": submitted_homework,
        },
    )

    
@teacher_required
def assignment_create_view(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST, user=request.user)
        if form.is_valid():
            ass = form.save(commit=False)
            if ass.subject not in request.user.teacher_subjects:
                return HttpResponseForbidden("Nelze přidávat úkoly do tohoto předmětu!!")
            ass.teacher = request.user
            ass.save()
            return redirect("assgn_detail_teacher", pk=ass.pk)
    else:
        form = AssignmentForm(user=request.user)
    return render(request, "homework/ass_create.html", {"form": form})

@student_required
def hw_create_view(request):
    assgn_id = request.GET.get("assgn_id")
    if not assgn_id:
        return HttpResponseBadRequest("Chybí ID úkolu!!")
    assignment = get_object_or_404(Assignment, pk=assgn_id)

    if assignment.subject not in request.user.student_subjects:
        return HttpResponseForbidden("Nemáš přístup k tomuto předmětu.")

    key, created = Key.objects.get_or_create(student=request.user, assignment=assignment)
    hw = Homework.objects.filter(key=key).first()
    if hw:
        messages.warning(request, "Úkol už byl odevzdán, nelze ho odeslat znovu.")
        return redirect("hw_detail", pk=hw.pk)

    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            hw = form.save(commit=False)
            hw.key = key
            hw.submitted = datetime.datetime.now()
            hw.save()
            return redirect("hw_detail", pk=hw.pk)
    else:
        form = HomeworkForm()
    return render(request, "homework/hw_create.html", {"form": form, "hwdetail": assignment})

# @student_required
@own_required(Homework,'key__student')
def hw_update_view(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    if request.method == "POST":
        form = HomeworkForm(request.POST, instance=hw)
        if form.is_valid():
            edit_hw = form.save(commit=False)
            edit_hw.submitted = datetime.datetime.now()
            edit_hw.save()
            return redirect("hw_detail", pk=hw.pk)
    else:
        form = HomeworkForm(instance=hw)
    return render(request, "homework/hw_update.html", {"form": form, "hw": hw})

@own_required(Assignment,'teacher')
def assgn_delete_view(request, pk):
    assgn = get_object_or_404(Assignment, pk=pk)
    if request.method == "POST":
        assgn.delete()
        return redirect("list")
    return render(request, "homework/ass_delete_confirm.html", {"assgn": assgn})

@login_required
def hw_detail_view(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    is_student = request.user == hw.key.student
    is_subject_teacher = request.user.is_teacher and hw.key.assignment.subject in request.user.teacher_subjects

    if not (is_student or is_subject_teacher):
        return HttpResponseForbidden("Nemáš přístup k tomuto domácímu úkolu.")

    return render(request, "homework/hw_detail.html", {"hw": hw})

@own_required(Homework,'key__assignment__teacher')
def create_evaluation_view(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    if request.method == "POST":
        form = EvaluationForm(request.POST, instance=hw)
        if form.is_valid():
            form.save()
            return redirect("hw_detail", pk=hw.pk)
    else:
        form = EvaluationForm(instance=hw)
    return render(request, "homework/hw_evaluate.html", {"form": form, "hw": hw})

@own_required(Homework,'key__assignment__teacher')
def edit_evaluation_view(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    if request.method == "POST":
        form = EvaluationForm(request.POST, instance=hw)
        if form.is_valid():
            edit_hw = form.save(commit=False)
            edit_hw.save()
            return redirect("hw_detail", pk=hw.pk)
    else:
        form = EvaluationForm(instance=hw)
    return render(
        request, "homework/hw_evaluation_update.html", {"form": form, "hw": hw}
    )

@own_required(Homework,'key__assignment__teacher')
def delete_evaluation_view(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    if request.method == "POST":
        hw.score = None
        hw.text_evaluation = None
        hw.save()
        return redirect("hw_detail", pk=hw.pk)
    return render(request, "homework/hw_evaluation_delete_confirm.html", {"hw": hw})


def nevim_pak_prejmenuju(ReviewHomework):
    pass
    #neco=    

