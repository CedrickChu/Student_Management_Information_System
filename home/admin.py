from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SchoolYear, GradeLevel, Student, Subject, ParentGuardian, Teacher, Section, StudentInfo, StudentGrade, Event, Principal, TransferInfo
from .widgets import PastCustomDatePickerWidget
from django.db import models


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name','last_name', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name')
    ordering = ('username',)

admin.site.unregister(Group)
admin.site.register(Event)

admin.site.register(GradeLevel)
admin.site.register(Subject)
admin.site.register(Section)
admin.site.register(ParentGuardian)
admin.site.register(StudentInfo)
admin.site.register(SchoolYear)
admin.site.register(Principal)
admin.site.register(TransferInfo)
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.DateField: {'widget': PastCustomDatePickerWidget},
    }
    list_display = ['lrn','first_name', 'middle_name', 'last_name', 'birth_date', 'place_of_birth', 'gender','address', ]
    search_fields = ['first_name', 'last_name']

    fieldsets = (
        (None, {
            'fields': ('lrn','first_name','middle_name', 'last_name', 'birth_date', 'place_of_birth', 'gender','address','parent_guardians',)
        }),
    )

@admin.register(StudentGrade)
class StudentGradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'first_grading', 'second_grading', 'third_grading', 'fourth_grading')
    list_filter = ('student', 'subject')
    search_fields = ('student__first_name', 'student__last_name', 'subject__name')
    raw_id_fields = ('student', 'subject')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'middle_name', 'last_name', 'contact_information')
    search_fields = ('first_name', 'middle_name', 'last_name')
    ordering = ('last_name', 'first_name')