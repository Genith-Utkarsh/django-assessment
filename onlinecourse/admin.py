from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User

from .models import Choice, Course, Lesson, Question, Submission


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("content", "course", "grade")
    list_filter = ("course",)
    search_fields = ("content",)
    inlines = [ChoiceInline]


class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    list_filter = ("course",)
    search_fields = ("title",)


class CourseAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "submitted_at")
    list_filter = ("exam", "submitted_at")
    search_fields = ("student__username", "exam__title")


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Submission, SubmissionAdmin)
