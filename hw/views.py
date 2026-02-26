from .models import Homework, Assignment, Key, HomeworkStudentComment
from .forms import CreateHomeworkForm, HomeworkForm, AssignmentForm, EvaluationForm,MakeCommentsForm,HomeworkStudentCommentForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import datetime
from accounts.decorators import teacher_required, student_required, own_required
from django.http import HttpResponseForbidden,HttpResponseBadRequest,Http404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from .shuffle import get_the_houmwrk
from .filters import AssignmentFilter


@teacher_required
def hw_teacher_list_before_release_view(request):
    now = timezone.now()
    subjects=request.user.teacher_subjects
    filtered_subjects=Assignment.objects.filter(subject__in=subjects,release__gt=now)
    context={
        "filtered_subjects": filtered_subjects
    }
    return render(request,"list/before_release.html",context)

@login_required
def hw_list_active_view(request):
    assignments_teacher = []
    assignments_student = []
    now = timezone.now()
    if request.user.is_teacher:
        subjects = request.user.teacher_subjects
        assignments_teacher = Assignment.objects.filter(subject__in=subjects, release__lte=now, deadline__gt=now)
        
    # student
    if request.user.is_student:
        subjects = request.user.student_subjects
        assignments_student = Assignment.objects.filter(subject__in=subjects, release__lte=now, deadline__gt=now)
    f = AssignmentFilter(request.GET, queryset=Assignment.objects.all())
    context={
            "assignments_teacher": assignments_teacher,
            "assignments_student": assignments_student,
            'filter': f,
    }
    return render(request,"list/active.html",context)

# @login_required
# def hw_list_active_view2(request):
#     assignments_teacher = []
#     assignments_student = []
#     now = timezone.now()
#     if request.user.is_teacher:
#         subjects = request.user.teacher_subjects
#         assignments_teacher = Assignment.objects.filter(subject__in=subjects, release__lte=now, deadline__gt=now)
        
#     # student
#     if request.user.is_student:
#         subjects = request.user.student_subjects
#         assignments_student = Assignment.objects.filter(subject__in=subjects, release__lte=now, deadline__gt=now)
#     context={
#             "assignments_teacher": assignments_teacher,
#             "assignments_student": assignments_student,
#     }
#     return render(request,"list/active.html",context)

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
    context={
        "assignments_teacher": assignments_teacher,
        "assignments_student": assignments_student,
            }
    return render(request,"list/after_deadline.html",context)

@teacher_required
def assgn_detail_teacher(request, pk):
    assignment=get_object_or_404(Assignment,pk=pk)
    homeworks = Homework.objects.filter(key__assignment=assignment)
    context={
        "assignment": assignment,"homeworks": homeworks}
    
    return render(request, "homework/teacher_detail.html",context)

@student_required
def assgn_detail_stud(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    key, created = Key.objects.get_or_create(
        student=request.user,
        assignment=assignment
    )
    submitted_homework = Homework.objects.filter(key=key).first()
    already_submitted = submitted_homework is not None
    comments = None
    if submitted_homework:
        comments = HomeworkStudentComment.objects.filter(hw=submitted_homework)

    context={
            "hwdetail": assignment,
            "already_submitted": already_submitted,
            "submitted_homework": submitted_homework,
            "comments":comments,
            }
    return render(request,"homework/student_detail.html",context)

    
@teacher_required
def assignment_create_view(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST, user=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            if assignment.subject not in request.user.teacher_subjects:
                return HttpResponseForbidden("Nelze přidávat úkoly do tohoto předmětu!!")
            assignment.teacher = request.user
            assignment.save()
            return redirect("assgn_detail_teacher", pk=assignment.pk)
    else:
        form = AssignmentForm(user=request.user)
        context={"form": form}
    return render(request,"homework/ass_create.html",context)

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
        return redirect(hw.get_assgn_student_url())

    if request.method == "POST":
        form = CreateHomeworkForm(request.POST)
        if form.is_valid():
            hwform = form.save(commit=False)
            hwform.key = key
            hwform.submitted = timezone.now()
            hwform.full_clean()
            hwform.save()
            return redirect("assgn_detail_student", pk=assignment.pk)

    else:
        form = HomeworkForm()
    is_after_deadline=timezone.now() > assignment.deadline
    context={"form": form, "hwdetail": assignment,"is_after_deadline":is_after_deadline}
    return render(request,"homework/hw_create.html",context)

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
            return redirect(hw.get_assgn_student_url())
    else:
        form = HomeworkForm(instance=hw)
    context={"form": form, "hw": hw}
    return render(request,"homework/hw_update.html",context)

@own_required(Assignment,'teacher')
def assgn_delete_view(request, pk):
    assgn = get_object_or_404(Assignment, pk=pk)
    if request.method == "POST":
        assgn.delete()
        return redirect("assgn_detail_student", pk=assgn.pk)
    context={"assgn": assgn}
    return render(request,"homework/ass_delete_confirm.html",context)

@login_required
def hw_detail_view(request, pk):
    homework = get_object_or_404(Homework, pk=pk)
    comments=list(HomeworkStudentComment.objects.filter(hw=homework))
    is_student = request.user == homework.key.student
    is_subject_teacher = request.user.is_teacher and homework.key.assignment.subject in request.user.teacher_subjects
    if not (is_student or is_subject_teacher):
        return HttpResponseForbidden("Nemáš přístup k tomuto domácímu úkolu.")
    context={"hw": homework,
             "assignment": homework.key.assignment,
             "comments":comments,
             }
    return render(request,"homework/hw_detail.html",context)

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
    context={"form": form, "hw": hw}
    return render(request,"homework/hw_evaluation_update.html",context)

@own_required(Homework,'key__assignment__teacher')
def delete_evaluation_view(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    if request.method == "POST":
        hw.score = None
        hw.text_evaluation = None
        hw.save()
        return redirect("hw_detail", pk=hw.pk)
    context={"hw": hw}
    return render(request,"homework/hw_evaluation_delete_confirm.html",context)

@own_required(Assignment, "teacher")
def assignment_make_comments_view(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if request.method != "POST":
        return redirect("assgn_detail_teacher", pk=assignment.pk)

    submitted_hws = list(Homework.objects.filter(key__assignment=assignment).select_related("key__student")
    )
    n = len(submitted_hws)

    form = MakeCommentsForm(request.POST)
    if not form.is_valid():
        messages.warning(request, "Neplatná hodnota k.")
        return redirect("assgn_detail_teacher", pk=assignment.pk)
    if assignment.is_comments_generated:
        messages.warning(request, "Komentáře byly již vygenerovány!")
        return redirect("assgn_detail_teacher", pk=assignment.pk)        

    k = form.cleaned_data["k"]

    if n < 2:
        messages.warning(request, "Musí existovat alespoň 2 odevzdané domácí úkoly.")
        return redirect("assgn_detail_teacher", pk=assignment.pk)

    if k > n - 1:
        messages.error(request, f"k je moc velké. Maximum je {n-1} (odevzdaných je {n}).")
        return redirect("assgn_detail_teacher", pk=assignment.pk)
    if assignment.deadline > timezone.now():
        messages.warning(request, "Nemůžete generovat komentáře před deadline!")
        return redirect("assgn_detail_teacher", pk=assignment.pk)

    pairs = get_the_houmwrk(submitted_hws, k)

    to_create = []
    for reviewer_hw, hws_to_review in pairs:
        reviewer_id = reviewer_hw.key.student_id
        for hw in hws_to_review:
            to_create.append(
                HomeworkStudentComment(hw=hw, reviewer_id=reviewer_id, comment="")
            )

    with transaction.atomic():
        HomeworkStudentComment.objects.bulk_create(to_create, ignore_conflicts=True)

    messages.success(request, "Komentáře byly vygenerovány.")
    return redirect("assgn_detail_teacher", pk=assignment.pk)

@student_required
def student_comment_list_view(request):
    comments = (
        HomeworkStudentComment.objects
        .filter(reviewer=request.user)
        .select_related("hw__key__assignment")
        .order_by("hw__key__assignment__deadline", "id")
    )
    pending_count = comments.filter(comment="").count()
    return render(request, "student_comments/student_list.html", {
        "comments": comments,
        "pending_count": pending_count,
    })


@student_required
def student_comment_detail_view(request, pk):
    comment_obj = get_object_or_404(
        HomeworkStudentComment.objects.select_related("hw__key__assignment"),
        pk=pk,
        reviewer=request.user,  
    )
    if request.method == "POST":
        form = HomeworkStudentCommentForm(request.POST, instance=comment_obj)
        if form.is_valid():
            form.submitter = timezone.now()
            form.save()
            messages.success(request, "Komentář uložen.")
            return redirect("student_comment_detail", pk=comment_obj.pk)
        else:
            messages.error(request, "Formulář obsahuje chyby.")
    else:
        form = HomeworkStudentCommentForm(instance=comment_obj)

    return render(request, "student_comments/detail.html", {
        "comment_obj": comment_obj,
        "hw": comment_obj.hw,
        "assignment": comment_obj.hw.key.assignment,
        "form": form,
    })

@login_required
def student_received_comment_detail_view(request, pk):
    comment_obj = get_object_or_404(
        HomeworkStudentComment.objects.select_related("hw__key__student", "hw__key__assignment"),
        pk=pk,
    )
    is_student=comment_obj.hw.key.student_id==request.user.id
    is_teacher=comment_obj.hw.key.assignment.teacher==request.user
    if not (is_student or is_teacher):
        raise Http404()

    return render(request, "student_comments/received_detail.html", {
        "comment_obj": comment_obj,
        "assignment": comment_obj.hw.key.assignment,
        "hw":comment_obj.hw.engrossment,
    })
    
def teacher_comments_list_view(request):
    #subjects=request.user.teacher_subjects.all()
    comments=HomeworkStudentComment.objects.select_related(
    "hw__key__assignment","reviewer").order_by(
    "hw__key__assignment","reviewer")
    pending_count = comments.filter(comment="").count()
    return render(request,"student_comments/teacher_list.html",{
        "comments":comments,
        "pending_count":pending_count,
    })
    