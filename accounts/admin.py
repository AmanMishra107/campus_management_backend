from django.contrib import admin
from .models import (
    User,
    Teacher,
    Division,
    Student,
    Subject,
    SubjectAssignment
)


# -------------------------------------------------
# Student Promotion Action (ADMIN SAFE)
# -------------------------------------------------
@admin.action(description="Promote selected students to next semester")
def promote_students(modeladmin, request, queryset):
    success_count = 0

    for student in queryset:

        # Max semester check
        if student.semester >= 4:
            modeladmin.message_user(
                request,
                f"Student {student.roll_number} is already in Semester 4.",
                level="error"
            )
            continue

        next_semester = student.semester + 1

        # Find next semester division (same course & division letter)
        try:
            next_division = Division.objects.get(
                course=student.course,
                semester=next_semester,
                division=student.division.division
            )
        except Division.DoesNotExist:
            modeladmin.message_user(
                request,
                f"Division {student.division.division} for Semester {next_semester} does not exist.",
                level="error"
            )
            continue

        # Promote student
        student.semester = next_semester
        student.division = next_division
        student.save()
        success_count += 1

    if success_count:
        modeladmin.message_user(
            request,
            f"{success_count} student(s) promoted successfully."
        )


# -------------------------------------------------
# Admin Registrations
# -------------------------------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role')
    search_fields = ('username',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'position',
        'is_batch_coordinator',
        'coordinator_semester',
        'coordinator_division',
        'is_hod',
        'hod_course',
    )
    list_filter = ('is_batch_coordinator', 'is_hod', 'department')
    search_fields = ('user__username',)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'division')
    list_filter = ('course', 'semester')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'course', 'semester', 'division')
    list_filter = ('course', 'semester', 'division')
    search_fields = ('roll_number', 'user__username')
    actions = [promote_students]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'semester')
    list_filter = ('course', 'semester')
    search_fields = ('name',)


@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('subject', 'division', 'teacher')
    list_filter = ('division', 'teacher')
