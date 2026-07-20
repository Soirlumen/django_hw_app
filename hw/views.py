from .models import Homework, Assignment, Key, HomeworkStudentComment, CodeFile
from .forms import (CreateHomeworkForm, 
                    HomeworkForm, 
                    AssignmentForm, 
                    EvaluationForm,MakeCommentsForm,
                    HomeworkStudentCommentForm,
                    AssignemntEdit,
                    CommentTeacherMarkForm,
                    )
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import teacher_required, student_required, own_required
from django.http import HttpResponseBadRequest,Http404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import PermissionDenied
from .shuffle import get_the_houmwrk
from .filters import AssignmentTFilter,AssignmentSFilter
from django.utils.translation import gettext as _
from django.db.models import Exists, OuterRef
from django.db.models import Count, Q

@teacher_required
def hw_teacher_list_before_release_view(request):
    now = timezone.now()
    subjects = request.user.teacher_subjects
    filtered_subjects = Assignment.objects.filter(subject__in=subjects, release__gt=now)
    assignemnt_filter_t = AssignmentTFilter(request.GET, queryset=filtered_subjects, user=request.user, prefix="teacher")
    
    context = {
        'filter_t': assignemnt_filter_t,
        'current_status': 'before_release',  # aktivní záložka
        'reset_url_name': 'list_before_release',  # Pro reset tlačítko
    }
    return render(request, "list/assignment_list.html", context)


@login_required
def hw_list_active_view(request):
    assignemnt_filter_s = None
    assignemnt_filter_t = None
    now = timezone.now()
    
    if request.user.is_teacher:
        subjects = request.user.teacher_subjects
        assignments_teacher = Assignment.objects.filter(subject__in=subjects, release__lte=now, deadline__gt=now).order_by("deadline")
        assignemnt_filter_t = AssignmentTFilter(request.GET, queryset=assignments_teacher, user=request.user, prefix="teacher")
        
    if request.user.is_student:
        subjects = request.user.student_subjects
        homework_exists = Homework.objects.filter(key__assignment=OuterRef("pk"), key__student=request.user)
        assignments_student = Assignment.objects.filter(subject__in=subjects, release__lte=now, deadline__gt=now).annotate(is_submitted=Exists(homework_exists)).order_by("deadline")
        assignemnt_filter_s = AssignmentSFilter(request.GET, queryset=assignments_student, user=request.user, prefix="student")
        
    context = {
        'filter_t': assignemnt_filter_t,
        'filter_s': assignemnt_filter_s,
        'current_status': 'active',
        'reset_url_name': 'list_active',
    }
    return render(request, "list/assignment_list.html", context)


@login_required
def hw_list_after_deadline_view(request):
    assignemnt_filter_s = None
    assignemnt_filter_t = None
    now = timezone.now()
    
    if request.user.is_teacher:
        subjects = request.user.teacher_subjects
        assignments_teacher = Assignment.objects.filter(subject__in=subjects, deadline__lte=now).order_by("-deadline")
        assignemnt_filter_t = AssignmentTFilter(request.GET, queryset=assignments_teacher, user=request.user, prefix="teacher")
        
    if request.user.is_student:
        subjects = request.user.student_subjects
        homework_exists = Homework.objects.filter(key__assignment=OuterRef("pk"), key__student=request.user)
        assignments_student = Assignment.objects.filter(subject__in=subjects, deadline__lte=now).annotate(is_submitted=Exists(homework_exists)).order_by("-deadline")
        assignemnt_filter_s = AssignmentSFilter(request.GET, queryset=assignments_student, user=request.user, prefix="student")
        
    context = {
        'filter_t': assignemnt_filter_t,
        'filter_s': assignemnt_filter_s,
        'current_status': 'after_deadline',
        'reset_url_name': 'list_after_deadline',
    }
    return render(request, "list/assignment_list.html", context)


@teacher_required
@own_required(Assignment,"teacher")
def assgn_detail_teacher(request, pk):
    assignment=get_object_or_404(Assignment,pk=pk)
    homeworks = Homework.objects.filter(key__assignment=assignment)
    context={
        "assignment": assignment,
        "homeworks": homeworks,
        "is_after_deadline":assignment.is_after_deadline,
        "is_before_release":assignment.is_before_release,}
    
    return render(request, "homework/teacher_detail.html",context)

@own_required(Assignment,'teacher')
def assgn_edit_view(request,pk):
    assignment=get_object_or_404(Assignment,pk=pk)
    if request.method=="POST":
        form=AssignemntEdit(request.POST,request.FILES,instance=assignment)
        if form.is_valid():
            edit_as=form.save(commit=False)
            files = form.cleaned_data["filesimput"]
            edit_as.save()
            
            remove_files_ids = request.POST.getlist("remove_files")
            if remove_files_ids:
                for file_pk in remove_files_ids:
                    file_obj = assignment.files.filter(pk=file_pk).first()
                    if file_obj:
                        assignment.files.remove(file_obj)
                        delete_file_if_unused(file_obj) # čistící funkce
                        
            for f in files:
                obj_f = CodeFile(file=f)
                obj_f._upload_user = request.user
                obj_f._upload_assignment = assignment
                obj_f.full_clean()
                obj_f.save()
                edit_as.files.add(obj_f)
                messages.success(request, _("Úkol byl úspěšně upraven."))
            return redirect(assignment.get_url())
        messages.warning(request, _("Formulář se nepodařilo odeslat. Zkontroluj prosím vyplněná pole."))
    else:
            form=AssignemntEdit(instance=assignment)
    context={"form": form, "as": assignment,}
    return render(request,"homework/as_update.html",context)
            
    
@student_required
def assgn_detail_stud(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if not request.user.student_subjects.filter(
        pk=assignment.subject_id
    ).exists():
        raise PermissionDenied(
            _("Nemáte přístup k tomuto předmětu.")
        )

    if assignment.is_before_release:
        raise PermissionDenied(
            _("Toto zadání ještě nebylo zveřejněno.")
        )

    key, created = Key.objects.get_or_create(
        student=request.user,
        assignment=assignment,
    )

    submitted_homework = Homework.objects.filter(
        key=key
    ).first()

    comments = None
    if submitted_homework:
        comments = HomeworkStudentComment.objects.filter(
            hw=submitted_homework
        )

    context = {
        "hwdetail": assignment,
        "already_submitted": submitted_homework is not None,
        "submitted_homework": submitted_homework,
        "comments": comments,
    }

    return render(
        request,
        "homework/student_detail.html",
        context,
    )
    
@teacher_required
def assignment_create_view(request):
    if request.method == "POST":
        form = AssignmentForm(
            request.POST,
            request.FILES,
            user=request.user,
        )

        if form.is_valid():
            assignment = form.save(commit=False)

            if assignment.subject not in request.user.teacher_subjects:
                raise PermissionDenied(
                    _("Nelze přidávat úkoly do tohoto předmětu!!")
                )

            assignment.teacher = request.user
            assignment.save()

            files = form.cleaned_data.get("filesimput", [])
            for f in files:
                obj_f = CodeFile(file=f)
                obj_f._upload_user = request.user
                obj_f._upload_assignment = assignment
                obj_f.full_clean()
                obj_f.save()
                assignment.files.add(obj_f)

            messages.success(request, _("Úkol byl úspěšně vytvořen."))
            return redirect("assgn_detail_teacher", pk=assignment.pk)

        messages.warning(request, _("Formulář se nepodařilo odeslat. Zkontroluj prosím vyplněná pole."))

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
        raise PermissionDenied(
            _("Nemáš přístup k tomuto předmětu.")
        )
    if assignment.is_before_release:
        raise PermissionDenied(
            _("Nelze přidat úkol k nezveřejněnému zadání.")
        )

    key, created = Key.objects.get_or_create(student=request.user, assignment=assignment)
    hw = Homework.objects.filter(key=key).first()

    if hw:
        messages.warning(request, _("Úkol už byl odevzdán, nelze ho odeslat znovu."))
        return redirect(hw.get_assgn_student_url())

    if request.method == "POST":
        form = CreateHomeworkForm(request.POST, request.FILES, assignment=assignment, user=request.user)
        if form.is_valid():
            hwform = form.save(commit=False)
            hwform.key = key
            hwform.submitted = timezone.now()
            hwform.full_clean()
            hwform.save()

            files = form.cleaned_data.get("filesimput", [])
            for f in files:
                obj_f = CodeFile(file=f)
                obj_f._upload_user = request.user
                obj_f._upload_assignment = assignment
                obj_f.full_clean()
                obj_f.save()
                hwform.files.add(obj_f)

            return redirect("assgn_detail_student", pk=assignment.pk)
        else:
            messages.warning(request, _("Formulář se nepodařilo odeslat. Zkontroluj prosím vyplněná pole."))
            print(form.errors)
            print(form.non_field_errors())
    else:
        form = CreateHomeworkForm(assignment=assignment, user=request.user)

    is_after_deadline = timezone.now() > assignment.deadline
    context = {
        "form": form,
        "hwdetail": assignment,
        "is_after_deadline": is_after_deadline,
    }
    return render(request, "homework/hw_create.html", context)

# @student_required
@own_required(Homework,'key__student')
def hw_update_view(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    if request.method == "POST":
        form = HomeworkForm(request.POST, request.FILES, instance=hw)
        if form.is_valid():
            edit_hw = form.save(commit=False)
            edit_hw.submitted = timezone.now()
            edit_hw.save()

            remove_files_ids = request.POST.getlist("remove_files")
            if remove_files_ids:
                for file_pk in remove_files_ids:
                    file_obj = hw.files.filter(pk=file_pk).first()
                    if file_obj:
                        hw.files.remove(file_obj)
                        delete_file_if_unused(file_obj) # čistící funkce

            files = form.cleaned_data.get("filesimput", [])
            for f in files:
                obj_f = CodeFile(file=f)
                obj_f._upload_user = request.user
                obj_f._upload_assignment = hw.key.assignment
                obj_f.full_clean()
                obj_f.save()
                edit_hw.files.add(obj_f)

            messages.success(request, _("Změny byly úspěšně uloženy."))
            return redirect(hw.get_assgn_student_url())
    else:
        form = HomeworkForm(instance=hw)
    
    context = {"form": form, "hw": hw}
    return render(request, "homework/hw_update.html", context)

@own_required(Assignment,'teacher')
def assgn_delete_view(request, pk):
    assgn = get_object_or_404(Assignment, pk=pk)
    if request.method == "POST":
        assgn.delete()
        return redirect("list_active")
    context={"assgn": assgn,}
    return render(request,"homework/ass_delete_confirm.html",context)

@login_required
def hw_detail_view(request, pk):
    homework = get_object_or_404(Homework, pk=pk)
    comments=list(HomeworkStudentComment.objects.filter(hw=homework))
    is_student = request.user == homework.key.student
    is_subject_teacher = request.user.is_teacher and homework.key.assignment.subject in request.user.teacher_subjects
    if not (is_student or is_subject_teacher):
        raise PermissionDenied(
            _("Nemáš přístup k tomuto domácímu úkolu.")
        )
    context={"hw": homework,
             "assignment": homework.key.assignment,
             "comments":comments,
             }
    return render(request,"homework/hw_detail.html",context)

def delete_file_if_unused(codefile):
    if not codefile.homework_set.exists() and not codefile.assignment_set.exists():
        codefile.delete()

@own_required(Homework,'key__assignment__teacher')
def edit_evaluation_view(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    if request.method == "POST":
        form = EvaluationForm(request.POST,instance=hw)
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
        messages.warning(request, _("Neplatná hodnota k."))
        return redirect("assgn_detail_teacher", pk=assignment.pk)
    if assignment.is_comments_generated:
        messages.warning(request, _("Komentáře byly již vygenerovány!"))
        return redirect("assgn_detail_teacher", pk=assignment.pk)        

    k = form.cleaned_data["k"]

    if n < 2:
        messages.warning(request, _("Musí existovat alespoň 2 odevzdané domácí úkoly."))
        return redirect("assgn_detail_teacher", pk=assignment.pk)

    if k > n - 1:
        messages.warning(request, _("k je moc velké. Maximum je %(num1)s (odevzdaných je %(num2)s).")%{"num1":n-1,"num2":n})
        return redirect("assgn_detail_teacher", pk=assignment.pk)
    if assignment.deadline > timezone.now():
        messages.warning(request, _("Nemůžete generovat komentáře před deadline!"))
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

    messages.success(request, _("Komentáře byly vygenerovány."))
    return redirect("assgn_detail_teacher", pk=assignment.pk)

@student_required
def reviewer_list_view(request):
    reviews = (
        HomeworkStudentComment.objects
        .filter(reviewer=request.user)
        .select_related("hw__key__assignment")
        .order_by("hw__key__assignment__deadline", "id")
    )
    pending_count = reviews.filter(comment="").count()
    return render(request, "student_comments/reviewer_list.html", {
        "comments": reviews,
        "pending_count": pending_count,
    })


@student_required
@own_required(HomeworkStudentComment, "reviewer")
def reviewer_form_view(request, pk):
    review = get_object_or_404(
        HomeworkStudentComment.objects.select_related(
            "hw__key__assignment"
        ),
        pk=pk,
        reviewer=request.user,
    )

    if request.method == "POST":
        form = HomeworkStudentCommentForm(
            request.POST,
            instance=review,
        )

        if form.is_valid():
            form.instance.submitted = timezone.now()
            form.save()

            messages.success(
                request,
                _("Komentář uložen."),
            )

            return redirect(
                "reviewer_form",
                pk=review.pk,
            )
    else:
        form = HomeworkStudentCommentForm(instance=review)

    return render(
        request,
        "student_comments/reviewer_form.html",
        {
            "comment_obj": review,
            "hw": review.hw,
            "assignment": review.hw.key.assignment,
            "form": form,
        },
    )
    
@login_required
def comment_feedback_detail_view(request, pk):
    review = get_object_or_404(
        HomeworkStudentComment.objects.select_related("hw__key__student", "hw__key__assignment"),
        pk=pk,
    )
    is_student=review.hw.key.student_id==request.user.id
    is_teacher=review.hw.key.assignment.teacher==request.user
    if not (is_student or is_teacher):
        raise Http404()

    return render(request, "student_comments/feedback_detail.html", {
        "comment_obj": review,
        "assignment": review.hw.key.assignment,
        "hw":review.hw,
        "language":review.hw.programming_language,
        "mark": review.mark,
    })
    

@teacher_required
@own_required(
    HomeworkStudentComment,
    "hw__key__assignment__teacher",
)
def teacher_comment_mark_view(request, pk):
    review = get_object_or_404(HomeworkStudentComment, pk=pk)
    if request.method == "POST":
        form = CommentTeacherMarkForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, _("Označení uloženo."))
            return redirect("comment_feedback_detail", pk=review.pk)
        else:
            messages.error(request, _("Formulář obsahuje chyby."))
    return render(request, "student_comments/teacher_mark_form.html", {
        "comment": review,
        "hw":review.hw,
        "form": CommentTeacherMarkForm(instance=review),
    })

@teacher_required
def teacher_comments_list_view(request):
    """Přehled všech peer-review řazený od nejnovějšího deadline."""
    
    # 1. Nejdříve vytáhneme recenzenty s počty pro jednotlivá zadání
    # Chceme vědět: Pro toto assignment_id a tohoto reviewer_id -> kolik je celkem a kolik hotových?
    stats = (
        HomeworkStudentComment.objects
        .filter(hw__key__assignment__teacher=request.user)
        .values('hw__key__assignment_id', 'reviewer_id')
        .annotate(
            total_count=Count('id'),
            filled_count=Count('id', filter=~Q(comment="")) 
        )
    )
    
    stats_dict = {
        (item['hw__key__assignment_id'], item['reviewer_id']): (item['filled_count'], item['total_count'])
        for item in stats
    }
    reviews = (
        HomeworkStudentComment.objects
        .select_related("hw__key__assignment", "hw__key__student", "reviewer")
        .filter(hw__key__assignment__teacher=request.user)
        .order_by(
            "-hw__key__assignment__deadline",
            "hw__key__assignment_id",
            "reviewer_id"
        )
    )
    
    for review in reviews:
        key = (review.hw.key.assignment_id, review.reviewer_id)
        filled, total = stats_dict.get(key, (0, 0))
        review.reviewer_filled_count = filled
        review.reviewer_total_count = total

    pending_count = reviews.filter(comment="").count()
    
    return render(request, "student_comments/teacher_list.html", {
        "comments": reviews,
        "pending_count": pending_count,
    })