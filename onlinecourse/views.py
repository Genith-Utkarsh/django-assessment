from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Choice, Course, Lesson, Question, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, "onlinecourse/course_details_bootstrap.html", {"course": course})


def exam(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    questions = lesson.course.questions.prefetch_related("choices")
    return render(request, "onlinecourse/exam.html", {"exam": lesson, "questions": questions})


@require_POST
def submit(request, lesson_id):
    exam = get_object_or_404(Lesson, pk=lesson_id)
    questions = exam.course.questions.prefetch_related("choices")
    student = request.user if request.user.is_authenticated else User.objects.get_or_create(
        username="demo_student",
        defaults={"first_name": "Demo", "last_name": "Student"},
    )[0]

    selected_choices = []
    score = 0
    total = 0
    for question in questions:
        total += question.grade
        selected_id = request.POST.get(f"question_{question.id}")
        if selected_id:
            choice = question.choices.filter(pk=selected_id).first()
            if choice:
                selected_choices.append(choice)
                if choice.is_correct:
                    score += question.grade

    submission = Submission.objects.create(exam=exam, student=student)
    submission.choices.set(selected_choices)
    request.session["exam_score"] = score
    request.session["exam_total"] = total
    return redirect("show_exam_result", submission_id=submission.id)


def show_exam_result(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.prefetch_related("choices__question"), pk=submission_id
    )
    questions = submission.exam.course.questions.prefetch_related("choices")
    score = request.session.pop("exam_score", sum(
        choice.question.grade for choice in submission.choices.filter(is_correct=True)
    ))
    total = request.session.pop("exam_total", sum(question.grade for question in questions))
    results = [
        {
            "question": question,
            "selected": submission.choices.filter(question=question).first(),
            "correct": question.choices.filter(is_correct=True).first(),
        }
        for question in questions
    ]
    return render(
        request,
        "onlinecourse/exam_result.html",
        {
            "submission": submission,
            "score": score,
            "total": total,
            "percentage": round(score / total * 100) if total else 0,
            "results": results,
        },
    )
