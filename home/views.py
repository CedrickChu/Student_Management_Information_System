from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Prefetch
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponse
from django.conf import settings
from django.dispatch import receiver
# from allauth.account.signals import user_signed_up
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.http import Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import SchoolYear, GradeLevel, Student, Subject, ParentGuardian, Section, Teacher, StudentInfo, User, StudentGrade, Event, Principal
from django.urls import reverse_lazy
from .forms import StudentForm, ParentGuardianForm, GradeLevelForm, SubjectForm, SchoolYearForm, SectionForm, TeacherForm, StudentInfoForm, ParentGuardianForm, UserRegistrationForm, StudentGradeForm, TransferInfoForm
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from datetime import date
from django.views.decorators.http import require_http_methods
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION, DELETION
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
import json
from django.contrib.contenttypes.models import ContentType

def test(request):
    return render(request, 'test.html')

def log_admin_action(request, obj, action_flag, change_message):
    """
    Logs an action performed by the user in the admin logs.
    """
    user = request.user
    content_type = ContentType.objects.get_for_model(obj)

    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=content_type.pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=action_flag,
        change_message=change_message
    )
    
def is_superuser(user):
    return user.is_superuser

def custom_page(request):
    return render(request, 'custom_page.html')

def user_logout_view(request):
  logout(request)
  return redirect('/accounts/login/')

def index(request):
    current_school_year = SchoolYear.objects.filter(status=True).first()
    school_years = SchoolYear.objects.all()
    total_grade_levels = GradeLevel.objects.count()
    user_count = User.objects.count()
    
    school_level_filter = current_school_year  # Default to the current school year
    school_year_id = request.GET.get('school_year')
    
    if school_year_id and school_year_id.isdigit():
        school_level_filter = SchoolYear.objects.filter(id=int(school_year_id)).first()

    # Initialize the chart data variables in case no school year is selected
    pie_chart_data_json = json.dumps({'labels': [], 'data': [], 'backgroundColor': []})
    bar_chart_data_json = json.dumps({'labels': [], 'data': [], 'backgroundColor': []})

    if school_level_filter:
        total_enrollees = StudentInfo.objects.filter(school_year=school_level_filter).count()
        male_students_count = StudentInfo.objects.filter(school_year=school_level_filter, student__gender='M').count()
        female_students_count = StudentInfo.objects.filter(school_year=school_level_filter, student__gender='F').count()
        students = StudentInfo.objects.filter(school_year=school_level_filter)
        age_brackets = ['6-7', '8-9', '10-11', '12-13', '14-15', '16+']
        age_distribution = {bracket: 0 for bracket in age_brackets}
        for student_info in students:
            student = student_info.student
            age = student.calculate_age(student.birth_date)

            # Group students into age brackets
            if 6 <= age <= 7:
                age_distribution['6-7'] += 1
            elif 8 <= age <= 9:
                age_distribution['8-9'] += 1
            elif 10 <= age <= 11:
                age_distribution['10-11'] += 1
            elif 12 <= age <= 13:
                age_distribution['12-13'] += 1
            elif 14 <= age <= 15:
                age_distribution['14-15'] += 1
            elif age >= 16:
                age_distribution['16+'] += 1
        
        # Prepare data for the chart
        age_labels = list(age_distribution.keys())
        age_counts = list(age_distribution.values())

        age_chart_data = {
            'labels': age_labels,
            'data': age_counts,
            'backgroundColor': 'rgba(75, 192, 192, 0.7)',
        }

        age_chart_data_json = json.dumps(age_chart_data)

        # Prepare data for the pie chart (Gender Distribution)
        pie_chart_data = {
            'labels': ['Male', 'Female'],
            'data': [male_students_count, female_students_count],
            'backgroundColor': [
                'rgba(54, 162, 235, 0.7)',  # Male
                'rgba(255, 99, 132, 0.7)'   # Female
            ]
        }
        pie_chart_data_json = json.dumps(pie_chart_data)

        # Prepare data for the bar chart (Grade Level Distribution)
        grade_levels = GradeLevel.objects.all()
        grade_labels = [grade.name for grade in grade_levels]
        student_counts = [StudentInfo.objects.filter(school_year=school_level_filter, grade_level=grade).count() for grade in grade_levels]

        # To handle the color dynamically and avoid repetition
        colors = [
            'rgba(75, 192, 192, 0.7)', 'rgba(153, 102, 255, 0.7)', 'rgba(255, 159, 64, 0.7)',
            'rgba(255, 206, 86, 0.7)', 'rgba(54, 162, 235, 0.7)', 'rgba(255, 99, 132, 0.7)'
        ]
        bar_chart_data = {
            'labels': grade_labels,
            'data': student_counts,
            'backgroundColor': colors * (len(grade_levels) // len(colors) + 1)  # Repeat colors if necessary
        }
        bar_chart_data_json = json.dumps(bar_chart_data)

    else:
        total_enrollees = 0 

    active_teachers_count = Teacher.objects.filter(status=Teacher.ACTIVE).count()
    
    admin_activity_last_30_days = LogEntry.objects.filter(action_time__gte=timezone.now() - timedelta(days=30)).count()

    add_actions_count = LogEntry.objects.filter(action_flag=ADDITION).count()
    change_actions_count = LogEntry.objects.filter(action_flag=CHANGE).count()
    delete_actions_count = LogEntry.objects.filter(action_flag=DELETION).count()

    log_count = request.GET.get('log_count', '5')
    try:
        log_count = int(log_count)
    except ValueError:
        log_count = 5

    recent_admin_logs = LogEntry.objects.all().order_by('-action_time')[:log_count]

    context = {
        'parent': 'dashboard',
        'segment': 'dashboardv1',
        'total_enrollees': total_enrollees,
        'school_years': school_years,
        'selected_year': school_level_filter,
        'active_teachers_count': active_teachers_count,
        'total_grade_levels': total_grade_levels,
        'user_count': user_count,
        'admin_activity_last_30_days': admin_activity_last_30_days,
        'add_actions_count': add_actions_count,
        'change_actions_count': change_actions_count,
        'delete_actions_count': delete_actions_count,
        'recent_admin_logs': recent_admin_logs,
        'pie_chart_data_json': pie_chart_data_json,
        'bar_chart_data_json': bar_chart_data_json,
        'age_chart_data_json': age_chart_data_json,
    }

    return render(request, 'index.html', context)

def index2(request):
  context = {
    'parent': 'dashboard',
    'segment': 'dashboardv2'
  }
  return render(request, 'pages/index2.html', context)

def index3(request):
  context = {
    'parent': 'dashboard',
    'segment': 'dashboardv3'
  }
  return render(request, 'pages/index3.html', context)

def allStudent_list(request):
    student_infos = StudentInfo.objects.all()
    parent_guardians = ParentGuardian.objects.all()
    grade_level_filter = request.GET.get('grade_level')
    school_level_filter = request.GET.get('school_year')

    if grade_level_filter:
        student_infos = student_infos.filter(grade_level_id=grade_level_filter)
    if school_level_filter:
        student_infos = student_infos.filter(school_year_id=school_level_filter)

    paginator = Paginator(student_infos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    grade_levels = GradeLevel.objects.all()
    school_years = SchoolYear.objects.all()
    students = [info.student for info in student_infos]
    allStudents = Student.objects.all()
    sections = Section.objects.all()

    # Handle student year info form
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, pk=student_id)
        student_year_info_form = StudentInfoForm(request.POST, student=student)
        if student_year_info_form.is_valid():
            student_year_info_form.save()
            return redirect('success_page')
    else:
        student_year_info_form = StudentInfoForm()

    context = {
        'student_infos': page_obj,
        'grade_levels': grade_levels,
        'students': students,
        'school_years': school_years,
        'allStudents': allStudents,
        'sections': sections,
        'parent_guardians': parent_guardians,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'student_year_info_form': student_year_info_form,
        'parent': 'masterlist',
        'segment': 'allStudent-list'
    }
    return render(request, 'student/all_student_list.html', context)


def all_events(request):                                                                                                 
    all_events = Event.objects.all()                                                                                    
    out = []                                                                                                             
    for event in all_events:                                                                                             
        out.append({                                                                                                     
            'title': event.name,  
            'id': event.pk,
            'note': event.note,                                                                                   
            'start': event.start.strftime("%Y-%m-%dT%H:%M:%S"), 
            'end': event.end.strftime("%Y-%m-%dT%H:%M:%S"),
            'color': event.color,                                                         
        })                                                                                                               
    return JsonResponse(out, safe=False) 
 
def add_event(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    name = request.GET.get("name", None)
    note = request.GET.get("note", None)
    color = request.GET.get("color", None)
    event = Event(name=str(name),note=note, start=start, end=end, color=color)
    event.save()
    log_admin_action(request, event, ADDITION, "Event Added through custom page.")

    data = {}
    return JsonResponse(data)
 
def update_event(request):
    if request.method == 'GET':  
        event_id = request.GET.get('id')
        title = request.GET.get('name')
        start = request.GET.get('start')
        note = request.GET.get("note")
        end = request.GET.get('end')
        color = request.GET.get('color')

        try:
            event = Event.objects.get(id=event_id)
            event.name = title
            event.start = start
            event.note = note
            event.end = end
            event.color = color
            event.save()

            return JsonResponse({'status': 'success', 'message': 'Event updated successfully.'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
 
def delete_event(request):
    if request.method == 'GET': 
        event_id = request.GET.get('id')
        try:
            event = Event.objects.get(id=event_id)
            event.delete()
            return JsonResponse({'status': 'success', 'message': 'Event deleted successfully.'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def login_view(request):
    if request.user.is_authenticated:
         return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})




def logout_view(request):
    logout(request)
    return redirect('/')


@user_passes_test(is_superuser)
@login_required
def user_list(request):
    users = User.objects.all()
    user_form = UserRegistrationForm()
    context = {
        'users': users,
        'user_form': user_form,
        'form_title': 'New User',
        'submit_label': 'Save'
    }
    return render(request, 'user/user_list.html', context)

@user_passes_test(is_superuser)
@login_required
def user_add(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user_instance = form.save()
            log_admin_action(request, user_instance, ADDITION, "User Added through custom page.")
            return redirect(reverse('user-list'))
        else:
            users = User.objects.all()
            context = {
                'users': users,
                'user_form': form,
                'form_title': 'New User',
                'submit_label': 'Save'
            }
            return render(request, 'user/user_list.html', context)
    return redirect(reverse('user-list'))

@user_passes_test(is_superuser)
@login_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, instance=user)
        if form.is_valid():
            user_instance = form.save()
            log_admin_action(request, user_instance, CHANGE, "User Updated through custom page.")
            return redirect(reverse('user-list'))
        else:
            users = User.objects.all()
            context = {
                'users': users,
                'user_form': form,
                'form_title': 'Edit User',
                'submit_label': 'Update'
            }
            return render(request, 'user/user_list.html', context)
    return redirect(reverse('user-list'))

@login_required
def student_list(request):
    students = Student.objects.all()
    parent_guardians = ParentGuardian.objects.all()
    school_years = SchoolYear.objects.all()
    grade_levels = GradeLevel.objects.all()


    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'students': page_obj,
        'parent_guardians': parent_guardians,
        'school_years': school_years,
        'grade_levels': grade_levels,
        'paginator': paginator,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'parent': 'reports',
        'segment': 'student-list',
    }
    return render(request, 'student/student_list.html', context)

@user_passes_test(is_superuser)
@login_required
def add_generic_student(request):
    # Initialize the form and fetch all students for the modal
    students = Student.objects.all()
    
    if request.method == 'POST':
        student_form = StudentInfoForm(request.POST)
        if student_form.is_valid():
            # Save the form and get the instance
            student_info = student_form.save()
            log_admin_action(request, student_info, ADDITION, "Student Added through custom page.")  # Log the action
            return JsonResponse({'success': True})  # Respond with success if the form is valid
        else:
            # Respond with errors if the form is invalid
            return JsonResponse({'errors': student_form.errors}, status=400)
    
    # For GET requests, initialize the form and pass students to the context
    student_form = StudentInfoForm()
    return render(request, 'student/studentinfo_add_modal.html', {
        'student_form': student_form,
        'students': students
    })


class PrintStudentListView(ListView):
    model = Student
    template_name = 'student/print_student.html'
    context_object_name = 'students'
    paginate_by = 16

    def get_queryset(self):
        queryset = Student.objects.all()

        # Filter by school year
        school_year_id = self.request.GET.get('school_year')
        if school_year_id:
            student_infos = StudentInfo.objects.filter(school_year__id=school_year_id).values_list('student_id', flat=True)
            queryset = queryset.filter(id__in=student_infos)

        # Filter by grade level
        grade_level_id = self.request.GET.get('grade_level')
        if grade_level_id:
            queryset = queryset.filter(studentinfo__grade_level__id=grade_level_id)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = self.get_queryset()

        # Calculate age for each student and store it in a dictionary
        student_ages = []
        for student in students:
            birth_date = student.birth_date
            age_years = self.calculate_age(birth_date)

            if age_years == 0:
                today = date.today()
                age_delta = today - birth_date
                age_months = age_delta.days // 30
                age_days = age_delta.days % 30
            else:
                age_months = None
                age_days = None

            student_ages.append({
                'student': student,
                'age_years': age_years,
                'age_months': age_months,
                'age_days': age_days
            })

        # Fetch selected school year and grade level for display in context
        school_year_id = self.request.GET.get('school_year')
        if school_year_id:
            school_year = get_object_or_404(SchoolYear, id=school_year_id)
        else:
            school_year = None

        grade_level_id = self.request.GET.get('grade_level')
        if grade_level_id:
            grade_level = get_object_or_404(GradeLevel, id=grade_level_id)
        else:
            grade_level = None

        context['student_ages'] = student_ages
        context['school'] = { 'address': 'Km.5 Tiniguiban Hi-Way, Puerto Princesa City', 'contact_number': 'Tel. # (048) 434 - 0041'}
        context['school_year'] = school_year
        context['grade_level_selected'] = grade_level
        context['school_years'] = SchoolYear.objects.all()
        context['grade_levels'] = GradeLevel.objects.all()
        context['principal'] = Principal.objects.filter(school_years=school_year, is_active=True).first()

        return context

    def calculate_age(self, birth_date):
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@user_passes_test(is_superuser)
@login_required
def student_update(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        if request.user.is_superuser:
            form = StudentForm(request.POST, instance=student)
            if form.is_valid():
                # Save the updated student and log the change
                student_instance = form.save()
                log_admin_action(request, student_instance, CHANGE, "Student record updated through custom page.")
                messages.success(request, 'Student edited successfully!')
                return redirect('student-list')
        else:
            messages.error(request, 'You do not have permission to edit student records.')
            form = StudentForm(instance=student)  # Show the form with existing data, but not editable
    else:
        form = StudentForm(instance=student)
        # Make fields readonly for non-superusers
        if not request.user.is_superuser:
            for field in form.fields.values():
                field.widget.attrs['readonly'] = True

    return render(request, 'student/student_update.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
@login_required
def add_student(request):
    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        
        if student_form.is_valid():
            # Save the student data
            student = student_form.save()

            # Log the action in the admin log
            log_admin_action(request, student, ADDITION, "Student added through custom page.")

            # Prepare the response data
            student_year_info_url = reverse('student-year-info', kwargs={'student_id': student.id})
            response = {
                'success': True,
                'student_id': student.id,
                'student_name': f"{student.first_name} {student.middle_name} {student.last_name}",
                'student_year_info_url': student_year_info_url,
            }
            return JsonResponse(response)

        # If form is not valid, return the form errors
        errors = {'errors': student_form.errors}
        return JsonResponse(errors, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'student/student_confirm_delete.html'
    context_object_name = 'student'

    def get_success_url(self):
        return reverse('student-list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return response


@login_required
def subject_list(request):
    grade_levels = GradeLevel.objects.all()
    selected_grade_level_id = request.GET.get('grade_level')

    # If no grade level is selected, use the first grade level as the default
    if not selected_grade_level_id and grade_levels.exists():
        selected_grade_level_id = grade_levels.first().id

    # Filter subjects by the selected grade level
    if selected_grade_level_id:
        subjects = Subject.objects.filter(grade_level_id=selected_grade_level_id)
    else:
        subjects = Subject.objects.all()

    context = {
        'subjects': subjects,
        'grade_levels': grade_levels,
        'selected_grade_level_id': selected_grade_level_id,
        'form_title': 'Add Subject',
        'submit_label': 'Add Subject'
    }
    return render(request, 'maintenance/subject_list.html', context)

@user_passes_test(is_superuser)
@login_required
def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject_instance = form.save()
            log_admin_action(request, subject_instance, ADDITION, "Subject added through custom page.")
            search = request.POST.get('search', '')
            grade_level = request.POST.get('grade_level', '')
            return redirect(f'/subject/?search={search}&grade_level={grade_level}')
    else:
        form = SubjectForm()
    submit_label = 'Add Subject'
    return render(request, 'maintenance/subject_list.html', {
        'subject_form': form,
        'submit_label': submit_label,
        'form_title': 'Add Subject'
    })


@user_passes_test(is_superuser)
@login_required
def update_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            subject_instance = form.save()
            log_admin_action(request, subject_instance, CHANGE, "Subject updated through custom page.")
            search = request.POST.get('search', '')
            grade_level = request.POST.get('grade_level', '')
            return redirect(f'/subject/?search={search}&grade_level={grade_level}')
    else:
        form = SubjectForm(instance=subject)
    submit_label = 'Update subject'
    return render(request, 'maintenance/subject_list.html', {
        'subject_form': form,
        'submit_label': submit_label,
        'form_title': 'Edit subject'
    })

# class SchoolYearListView(ListView):
#     model = SchoolYear
#     template_name = 'grades/schoolyear_list.html'
#     context_object_name = 'schoolyears'

@login_required
def grade_list(request):
    grades = GradeLevel.objects.order_by('id')
    grade_form = GradeLevelForm()
    submit_label = 'Add Grade'
    return render(request, 'maintenance/gradelevel_list.html', {
        'grades': grades,
        'grade_form': grade_form,
        'submit_label': submit_label,
        'form_title': 'Add Grade'
    })


@user_passes_test(is_superuser)
@login_required
def add_grade(request):
    if request.method == 'POST':
        form = GradeLevelForm(request.POST)
        if form.is_valid():
            grade_instance = form.save()
            log_admin_action(request, grade_instance, ADDITION, "Grade added through custom page.")
            return redirect('grade-level')
    else:
        form = GradeLevelForm()
    submit_label = 'Add Grade'
    return render(request, 'maintenance/gradelevel_list.html', {
        'grade_form': form,
        'submit_label': submit_label,
        'form_title': 'Add Grade'
    })

@user_passes_test(is_superuser)
@login_required
def update_grade(request, pk):
    grade = get_object_or_404(GradeLevel, pk=pk)
    if request.method == 'POST':
        form = GradeLevelForm(request.POST, instance=grade)
        if form.is_valid():
            grade_instance = form.save()
            log_admin_action(request, grade_instance, CHANGE, "Grade Updated through custom page.")
            return redirect('grade-level')
    else:
        form = GradeLevelForm(instance=grade)
    submit_label = 'Update Grade'
    return render(request, 'maintenance/gradelevel_list.html', {
        'grade_form': form,
        'submit_label': submit_label,
        'form_title': 'Edit Grade'
    })

@login_required
def student_report(request):
    students = Student.objects.all()
    grade_levels = GradeLevel.objects.all()
    search_query = request.GET.get('search')

    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(lrn__icontains=search_query)
        )
    context = {
        'students': students,
        'grade_levels': grade_levels,
    }
    return render(request, 'report/student_record.html', context)

@login_required
def student_form137(request, pk):
    student = get_object_or_404(Student, pk=pk)
    context = {
        'student': student,
    }
    return render(request, 'report/form137.html', context)

@login_required
def school_year(request):
    school_years = SchoolYear.objects.all()
    school_year_form = SchoolYearForm()
    submit_label = 'Add School Year'
    return render(request, 'maintenance/school_year.html', {
        'school_years': school_years,
        'school_year_form': school_year_form,
        'submit_label': submit_label,
        'form_title': 'Add School Year',
    })


@user_passes_test(is_superuser)
@login_required
def add_year(request):
    if request.method == 'POST':
        form = SchoolYearForm(request.POST)
        if form.is_valid():
            year_instance = form.save()
            log_admin_action(request, year_instance, ADDITION, "School Year added through custom page.")
            return redirect('schoolyear-list')
    else:
        form = SchoolYearForm()
    submit_label = 'Add Year'
    return render(request, 'maintenance/school_year.html', {
        'school_year_form': form,
        'submit_label': submit_label,
        'form_title': 'Add School Year',
        'school_years': SchoolYear.objects.all()
    })

@user_passes_test(is_superuser)
@login_required
def update_year(request, pk):
    year = get_object_or_404(SchoolYear, pk=pk)
    if request.method == 'POST':
        form = SchoolYearForm(request.POST, instance=year)
        if form.is_valid():
            year_instance = form.save()
            log_admin_action(request, year_instance, CHANGE, "School Year Updated through custom page.")
            return redirect('schoolyear-list')
    else:
        form = SchoolYearForm(instance=year)
    submit_label = 'Update Grade'
    return render(request, 'maintenance/school_year.html', {
        'grade_form': form,
        'submit_label': submit_label,
        'form_title': 'Edit School Year'
    })

@login_required
def section_list(request):
    sections = Section.objects.all()
    grade_levels = GradeLevel.objects.all()
    advisers = Teacher.objects.all()
    grade_level_filter = request.GET.get('grade_level')
    default_grade_level_id = 1

    if grade_level_filter:
        sections = sections.filter(grade_level_id=grade_level_filter)
    else:
        sections = sections.filter(grade_level_id=default_grade_level_id)

    section_form = SectionForm()
    submit_label = 'Add Section'
    return render(request, 'maintenance/section_list.html', {
        'sections': sections,
        'advisers': advisers,
        'section_form': section_form,
        'submit_label': submit_label,
        'form_title': 'Add Section',
        'grade_levels': grade_levels,
        'default_grade_level_id': default_grade_level_id,
    })

@user_passes_test(is_superuser)
@login_required
def add_section(request):
    if request.method == 'POST':
        section_form = SectionForm(request.POST)
        if section_form.is_valid():
            # Check if adviser is already assigned to a section
            adviser_id = section_form.cleaned_data['adviser'].id
            if Section.objects.filter(adviser_id=adviser_id).exists():
                messages.error(request, 'This teacher is already assigned to a section.')
            else:
                section_instance = section_form.save()
                log_admin_action(request, section_instance, ADDITION, "Section added through custom page.")
                return redirect('section-list')
    else:
        initial_grade_level = request.GET.get('grade_level')
        section_form = SectionForm(initial={'grade_level': initial_grade_level})
        # If no filter is applied, set default grade level
        if not initial_grade_level:
            section_form.fields['grade_level'].initial = 1  # Set your default grade level ID here

    submit_label = 'Add Section'
    return render(request, 'maintenance/section_list.html', {
        'section_form': section_form,
        'submit_label': submit_label,
        'form_title': 'Add Section',
    })

@user_passes_test(is_superuser)
@login_required
def update_section(request, pk):
    section = get_object_or_404(Section, pk=pk)
    if request.method == 'POST':
        section_form = SectionForm(request.POST, instance=section)
        if section_form.is_valid():
            section_instance = section_form.save()
            log_admin_action(request, section_instance, CHANGE, "Section Updated through custom page.")
            return redirect('section-list')
    else:
        section_form = SubjectForm(instance=section)
    submit_label = 'Update section'
    return render(request, 'maintenance/section_list.html', {
        'section_form': section_form,
        'submit_label': submit_label,
        'form_title': 'Edit Section'
    })

@login_required
def teacher_list(request):
    teachers = Teacher.objects.all()
    paginator = Paginator(teachers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'teachers': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'parent': 'masterlist',
        'segment': 'teacher-list'
    }
    return render(request, 'maintenance/teacher_list.html', context)

@user_passes_test(is_superuser)
@login_required
def add_teacher(request):
    if request.method == 'POST':
        teacher_form = TeacherForm(request.POST)
        if teacher_form.is_valid():
            teacher_instance = teacher_form.save()
            log_admin_action(request, teacher_instance, ADDITION, "Teacher Added through custom page.")
            return JsonResponse({'success': True})
        else:
            errors = {
                'errors': teacher_form.errors,
            }
            return JsonResponse(errors, status=400)

    teacher_form = TeacherForm()
    return render(request, 'maintenance/teacher_add_modal.html', {
        'teacher_form': teacher_form,
    })

@user_passes_test(is_superuser)
@login_required
def update_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher_form = TeacherForm(request.POST, instance=teacher)
        if teacher_form.is_valid():
            teacher_instance = teacher_form.save()
            log_admin_action(request, teacher_instance, CHANGE, "Teacher Updated through custom page.")
            return JsonResponse({'status': 1})
        else:
            errors = teacher_form.errors.as_json()
            return JsonResponse({'status': 0, 'errors': errors})
    else:
        teacher_data = {
            'teacher_id': teacher.teacher_id,
            'first_name': teacher.first_name,
            'middle_name': teacher.middle_name,
            'last_name': teacher.last_name,
            'address': teacher.address,
            'contact_information': teacher.contact_information
        }
        return JsonResponse(teacher_data)


@user_passes_test(is_superuser)
@login_required
def add_parent(request):
    if request.method == 'POST':
        form = ParentGuardianForm(request.POST)
        if form.is_valid():
            parent_instance = parent = form.save()
            log_admin_action(request, parent_instance, ADDITION, "Parent Added through custom page.")
            response = {
                'success': True,
                'parent_id': parent.id,
                'parent_name': f"{parent.first_name} {parent.middle_name} {parent.last_name}"
            }
            return JsonResponse(response)

        errors = {'errors': form.errors}
        return JsonResponse(errors, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def parent_list(request):
    parents = ParentGuardian.objects.all()
    search_query = request.GET.get('search')
    if search_query:
        parents = parents.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    paginator = Paginator(parents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'parents' : page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'parent': 'masterlist',
        'segment': 'parent-list',

        }
    return render(request, 'maintenance/parent_list.html', context)

@user_passes_test(is_superuser)
@login_required
def update_parent(request, pk):
    parent = get_object_or_404(ParentGuardian, pk=pk)
    if request.method == 'POST':
        form = ParentGuardianForm(request.POST, instance=parent)
        if form.is_valid():
            parent_instance = form.save()
            log_admin_action(request, parent_instance, CHANGE, "Parent Updated through custom page.")
            return JsonResponse({'status': 1})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'status': 0, 'errors': errors})
    else:
        parent_data = {
            'first_name': parent.first_name,
            'middle_name': parent.middle_name,
            'last_name': parent.last_name,
            'address': parent.address,
            'contact_information': parent.contact_information
        }
        return JsonResponse(parent_data)

@user_passes_test(is_superuser)
@login_required
@csrf_exempt
def delete_parent(request):
    if request.method == 'POST' and request.user.is_superuser:
        parent_id = request.POST.get('id')
        parent = get_object_or_404(ParentGuardian, id=parent_id)
        parent_instance = parent.delete()
        log_admin_action(request, parent_instance, DELETION, "Parent Deleted through custom page.")
        return JsonResponse(1, safe=False)
    return JsonResponse(0, safe=False)

@user_passes_test(is_superuser)
@login_required
@csrf_exempt
def delete_teacher(request):
    if request.method == 'POST' and request.user.is_superuser:
        teacher_id = request.POST.get('id')
        teacher = get_object_or_404(Teacher, id=teacher_id)
        teacher_instance = teacher.delete()
        log_admin_action(request, teacher_instance, DELETION, "Teacher Deleted through custom page.")
        return JsonResponse(1, safe=False)
    return JsonResponse(0, safe=False)

@login_required
def student_academic_record(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student_infos = StudentInfo.objects.filter(student=student)
    subjects = Subject.objects.all()
    default_student_info = student_infos.first()
    if not default_student_info:
        default_student_info = None

    student_grades = StudentGrade.objects.filter(student=default_student_info) if default_student_info else None
    grade_levels = set(info.grade_level for info in student_infos)

    grade_level_id = None

    # Handle filtering by grade level if form is submitted
    if 'grade_level' in request.GET:
        grade_level_id = request.GET.get('grade_level')
        if grade_level_id:
            student_info = StudentInfo.objects.filter(student=student, grade_level=grade_level_id).first()
            if student_info:
                student_grades = StudentGrade.objects.filter(student=student_info)
                default_student_info = student_info

    # Get subjects that already have grades for this student and grade level
    if default_student_info:
        graded_subject_ids = StudentGrade.objects.filter(student=default_student_info).values_list('subject_id', flat=True)
        subjects = subjects.exclude(id__in=graded_subject_ids)
        # Filter subjects by the student's grade level
        subjects = subjects.filter(grade_level=default_student_info.grade_level)

    # Handle form submission to add StudentGrade
    if request.method == 'POST':
        form = StudentGradeForm(request.POST)
        if form.is_valid():
            grade_level_id = request.POST.get('grade_level')
            if grade_level_id:
                default_student_info = StudentInfo.objects.filter(student=student, grade_level=grade_level_id).first()

            student_grade = form.save(commit=False)
            student_grade.student = default_student_info
            student_grade.save()

            url = reverse('student_academic_record', args=[student_id])
            if grade_level_id:
                url += f'?grade_level={grade_level_id}#{grade_level_id}'
            return redirect(url)
    else:
        form = StudentGradeForm()

    context = {
        'student': student,
        'student_infos': student_infos,
        'default_student_info': default_student_info,
        'student_grades': student_grades,
        'grade_levels': grade_levels,
        'subjects': subjects,
        'form': form,
        'grade_level_id': grade_level_id,
        'parent': 'reports',
        'segment': 'student_academic_record',
    }

    return render(request, 'student/student_academic_record.html', context)


@require_POST
def fetch_student_grade(request, grade_id):
    grade = get_object_or_404(StudentGrade, id=grade_id)
    data = {
        'id': grade.id,
        'first_grading': grade.first_grading,
        'second_grading': grade.second_grading,
        'third_grading': grade.third_grading,
        'fourth_grading': grade.fourth_grading,
    }
    return JsonResponse(data)

@require_POST
def update_student_grade(request, grade_id):
    grade = get_object_or_404(StudentGrade, id=grade_id)
    grade.first_grading = request.POST.get('first_grading')
    grade.second_grading = request.POST.get('second_grading')
    grade.third_grading = request.POST.get('third_grading')
    grade.fourth_grading = request.POST.get('fourth_grading')
    log_admin_action(request, grade, CHANGE, "Grade Updated through custom page.")
    grade.save()
    return JsonResponse({'success': True, 'message': 'Grade updated successfully.'})

@require_POST
def delete_student_grade(request, grade_id):
    grade = get_object_or_404(StudentGrade, id=grade_id)
    log_admin_action(request, grade, DELETION, "Grade Deleted through custom page.")
    grade.delete()
    return JsonResponse({'success': True, 'message': 'Grade deleted successfully.'})

@login_required
def student_new(request):
    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        student_info_form = StudentInfoForm(request.POST)
        if student_form.is_valid():
            student = student_form.save()
            log_admin_action(request, student, ADDITION, "Student Added through custom page.")
            student_info_data = request.POST.copy()
            student_info_data['student'] = student.id
            student_info_data['status'] = 'new'
            student_info_form = StudentInfoForm(student_info_data)

            if student_info_form.is_valid():
                student_info_instance = student_info_form.save()
                log_admin_action(request, student_info_instance, ADDITION, "Student Year Info Added through custom page.")
                return JsonResponse({
                    'success': True,
                    'student_id': student.id,
                    'student_name': f"{student.lrn} - {student.first_name} {student.middle_name} {student.last_name}"
                })
            else:
                return JsonResponse({'errors': student_info_form.errors}, status=400)
        else:
            return JsonResponse({'errors': student_form.errors}, status=400)

    student_form = StudentForm()
    student_info_form = StudentInfoForm()
    return render(request, 'student/student_new.html', {
        'student_form': student_form,
        'student_info_form': student_info_form,
    })

@login_required
def student_old(request):
    if request.method == 'POST':
        student_form = StudentInfoForm(request.POST)
        if student_form.is_valid():
            student_info = student_form.save(commit=False)
            student_info.status = 'old'
            log_admin_action(request, student_info, ADDITION, "Student Year Info Added through custom page.")
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': student_form.errors}, status=400)

    # For GET requests
    student_form = StudentInfoForm()
    students = Student.objects.all()
    grade_levels = GradeLevel.objects.all()
    sections = Section.objects.all()
    school_years = SchoolYear.objects.all()
    parent_guardians = ParentGuardian.objects.all()

    return render(request, 'student/student_old.html', {
        'student_form': student_form,
        'students': students,
        'grade_levels': grade_levels,
        'sections': sections,
        'school_years': school_years,
        'parent_guardians': parent_guardians
    })

@login_required
def student_transfer(request):
    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        student_info_form = StudentInfoForm(request.POST)
        student_transfer_form = TransferInfoForm(request.POST)
        if student_form.is_valid():
            student = student_form.save()
            student_info_data = request.POST.copy()
            student_info_data['student'] = student.id
            student_info_data['status'] = 'Transferee'
            student_info_form = StudentInfoForm(student_info_data)

            if student_info_form.is_valid() and student_transfer_form.is_valid():
                student_info_instance = student_info_form.save()
                log_admin_action(request, student_info_instance, ADDITION, "Student Year Info Added through custom page.")
                student_transfer_instance = student_transfer_form.save()
                log_admin_action(request, student_transfer_instance, ADDITION, "Student Added through custom page.")
                return JsonResponse({
                    'success': True,
                    'student_id': student.id,
                    'student_name': f"{student.lrn} - {student.first_name} {student.middle_name} {student.last_name}"
                })
            else:
                errors = {
                    'student_info_form': student_info_form.errors,
                    'student_transfer_form': student_transfer_form.errors
                }
                return JsonResponse({'success': False, 'errors': errors}, status=400)
        else:
            return JsonResponse({'success': False, 'errors': {'student_form': student_form.errors}}, status=400)

    student_form = StudentForm()
    student_info_form = StudentInfoForm()
    student_transfer_form = TransferInfoForm()

    return render(request, 'student/student_transferee.html', {
        'student_form': student_form,
        'student_info_form': student_info_form,
        'student_transfer_form': student_transfer_form,
    })



def widgets(request):
  context = {
    'parent': '',
    'segment': 'widgets'
  }
  return render(request, 'pages/widgets.html', context)

# EXAMPLES




def examples_calendar(request):
  context = {
    'parent': '',
    'segment': 'calendar'
  }
  return render(request, 'pages/calendar.html', context)

def examples_gallery(request):
  context = {
    'parent': '',
    'segment': 'gallery'
  }
  return render(request, 'pages/gallery.html', context)

def examples_kanban(request):
  context = {
    'parent': '',
    'segment': 'kanban_board'
  }
  return render(request, 'pages/kanban.html', context)

# Mailbox

def mailbox_inbox(request):
  context = {
    'parent': 'mailbox',
    'segment': 'inbox'
  }
  return render(request, 'pages/mailbox/mailbox.html', context)

def mailbox_compose(request):
  context = {
    'parent': 'mailbox',
    'segment': 'compose'
  }
  return render(request, 'pages/mailbox/compose.html', context)

def mailbox_read_mail(request):
  context = {
    'parent': 'mailbox',
    'segment': 'read_mail'
  }
  return render(request, 'pages/mailbox/read-mail.html', context)

# Pages -- Examples

def examples_invoice(request):
  context = {
    'parent': 'pages',
    'segment': 'invoice'
  }
  return render(request, 'pages/examples/invoice.html', context)

def invoice_print(request):
  context = {
    'parent': 'pages',
    'segment': 'invoice_print'
  }
  return render(request, 'pages/examples/invoice-print.html', context)

def examples_profile(request):
  context = {
    'parent': 'pages',
    'segment': 'profile'
  }
  return render(request, 'pages/examples/profile.html', context)

def examples_e_commerce(request):
  context = {
    'parent': 'pages',
    'segment': 'ecommerce'
  }
  return render(request, 'pages/examples/e-commerce.html', context)

def examples_projects(request):
  context = {
    'parent': 'pages',
    'segment': 'projects'
  }
  return render(request, 'pages/examples/projects.html', context)

def examples_project_add(request):
  context = {
    'parent': 'pages',
    'segment': 'project_add'
  }
  return render(request, 'pages/examples/project-add.html', context)

def examples_project_edit(request):
  context = {
    'parent': 'pages',
    'segment': 'project_edit'
  }
  return render(request, 'pages/examples/project-edit.html', context)

def examples_project_detail(request):
  context = {
    'parent': 'pages',
    'segment': 'project_detail'
  }
  return render(request, 'pages/examples/project-detail.html', context)

def examples_contacts(request):
  context = {
    'parent': 'pages',
    'segment': 'contacts'
  }
  return render(request, 'pages/examples/contacts.html', context)

def examples_faq(request):
  context = {
    'parent': 'pages',
    'segment': 'faq'
  }
  return render(request, 'pages/examples/faq.html', context)

def examples_contact_us(request):
  context = {
    'parent': 'pages',
    'segment': 'contact_us'
  }
  return render(request, 'pages/examples/contact-us.html', context)

# Extra -- login & Registration v1
# def login_v1(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/login.html', context)

# def login_v2(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/login-v2.html', context)

# def registration_v1(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/register.html', context)

# def registration_v2(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/register-v2.html', context)

# def forgot_password_v1(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/forgot-password.html', context)

# def forgot_password_v2(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/forgot-password-v2.html', context)

# def recover_password_v1(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/recover-password.html', context)

# def recover_password_v2(request):
#   context = {
#     'parent': '',
#     'segment': ''
#   }
#   return render(request, 'pages/examples/recover-password-v2.html', context)

def lockscreen(request):
  context = {
    'parent': '',
    'segment': ''
  }
  return render(request, 'pages/examples/lockscreen.html', context)

def legacy_user_menu(request):
  context = {
    'parent': 'extra',
    'segment': 'legacy_user'
  }
  return render(request, 'pages/examples/legacy-user-menu.html', context)

def language_menu(request):
  context = {
    'parent': 'extra',
    'segment': 'legacy_menu'
  }
  return render(request, 'pages/examples/language-menu.html', context)

def error_404(request):
  context = {
    'parent': 'extra',
    'segment': 'error_404'
  }
  return render(request, 'pages/examples/404.html', context)

def error_500(request):
  context = {
    'parent': 'extra',
    'segment': 'error_500'
  }
  return render(request, 'pages/examples/500.html', context)

def pace(request):
  context = {
    'parent': 'extra',
    'segment': 'pace'
  }
  return render(request, 'pages/examples/pace.html', context)

def blank_page(request):
  context = {
    'parent': 'extra',
    'segment': 'blank_page'
  }
  return render(request, 'pages/examples/blank.html', context)

def starter_page(request):
  context = {
    'parent': 'extra',
    'segment': 'starter_page'
  }
  return render(request, 'pages/examples/starter.html', context)

# Search

def search_simple(request):
  context = {
    'parent': 'search',
    'segment': 'search_simple'
  }
  return render(request, 'pages/search/simple.html', context)

def search_enhanced(request):
  context = {
    'parent': 'search',
    'segment': 'search_enhanced'
  }
  return render(request, 'pages/search/enhanced.html', context)

def simple_results(request):
  context = {
    'parent': '',
    'segment': ''
  }
  return render(request, 'pages/search/simple-results.html', context)

def enhanced_results(request):
  context = {
    'parent': '',
    'segment': ''
  }
  return render(request, 'pages/search/enhanced-results.html', context)

# MISCELLANEOUS

def iframe(request):
  context = {
    'parent': '',
    'segment': ''
  }
  return render(request, 'pages/search/iframe.html', context)

# Charts

def chartjs(request):
  context = {
    'parent': 'charts',
    'segment': 'chartjs'
  }
  return render(request, 'pages/charts/chartjs.html', context)

def flot(request):
  context = {
    'parent': 'charts',
    'segment': 'flot'
  }
  return render(request, 'pages/charts/flot.html', context)

def inline(request):
  context = {
    'parent': 'charts',
    'segment': 'inline'
  }
  return render(request, 'pages/charts/inline.html', context)

def uplot(request):
  context = {
    'parent': 'charts',
    'segment': 'uplot'
  }
  return render(request, 'pages/charts/uplot.html', context)

def profile(request):
  context = {
    'parent': 'pages',
    'segment': 'profile'
  }
  return render(request, 'pages/examples/profile.html', context)

# Layout
def top_navigation(request):
  context = {
    'parent': 'layout',
    'segment': 'top_navigation'
  }
  return render(request, 'pages/layout/top-nav.html', context)

def top_nav_sidebar(request):
  context = {
    'parent': 'layout',
    'segment': 'top navigation with sidebar'
  }
  return render(request, 'pages/layout/top-nav-sidebar.html', context)

def boxed(request):
  context = {
    'parent': 'layout',
    'segment': 'boxed_layout'
  }
  return render(request, 'pages/layout/boxed.html', context)

def fixed_sidebar(request):
  context = {
    'parent': 'layout',
    'segment': 'fixed_layout'
  }
  return render(request, 'pages/layout/fixed-sidebar.html', context)

def fixed_sidebar_custom(request):
  context = {
    'parent': 'layout',
    'segment': 'layout_cuastom'
  }
  return render(request, 'pages/layout/fixed-sidebar-custom.html', context)

def fixed_topnav(request):
  context = {
    'parent': 'layout',
    'segment': 'fixed_topNav'
  }
  return render(request, 'pages/layout/fixed-topnav.html', context)

def fixed_footer(request):
  context = {
    'parent': 'layout',
    'segment': 'fixed_footer'
  }
  return render(request, 'pages/layout/fixed-footer.html', context)

def collapsed_sidebar(request):
  context = {
    'parent': 'layout',
    'segment': 'collapsed_sidebar'
  }
  return render(request, 'pages/layout/collapsed-sidebar.html', context)

# UI Elements

def ui_general(request):
  context = {
    'parent': 'ui',
    'segment': 'general'
  }
  return render(request, 'pages/UI/general.html', context)

def ui_icons(request):
  context = {
    'parent': 'ui',
    'segment': 'icons'
  }
  return render(request, 'pages/UI/icons.html', context)

def ui_buttons(request):
  context = {
    'parent': 'ui',
    'segment': 'buttons'
  }
  return render(request, 'pages/UI/buttons.html', context)

def ui_sliders(request):
  context = {
    'parent': 'ui',
    'segment': 'sliders'
  }
  return render(request, 'pages/UI/sliders.html', context)

def ui_modals_alerts(request):
  context = {
    'parent': 'ui',
    'segment': 'modals_alerts'
  }
  return render(request, 'pages/UI/modals.html', context)

def ui_navbar_tabs(request):
  context = {
    'parent': 'ui',
    'segment': 'navbar_tabs'
  }
  return render(request, 'pages/UI/navbar.html', context)

def ui_timeline(request):
  context = {
    'parent': 'ui',
    'segment': 'timeline'
  }
  return render(request, 'pages/UI/timeline.html', context)

def ui_ribbons(request):
  context = {
    'parent': 'ui',
    'segment': 'ribbons'
  }
  return render(request, 'pages/UI/ribbons.html', context)

# Forms

def form_general(request):
  context = {
    'parent': 'forms',
    'segment': 'form_general'
  }
  return render(request, 'pages/forms/general.html', context)

def form_advanced(request):
  context = {
    'parent': 'forms',
    'segment': 'advanced_form'
  }
  return render(request, 'pages/forms/advanced.html', context)

def form_editors(request):
  context = {
    'parent': 'forms',
    'segment': 'text_editors'
  }
  return render(request, 'pages/forms/editors.html', context)

def form_validation(request):
  context = {
    'parent': 'forms',
    'segment': 'validation'
  }
  return render(request, 'pages/forms/validation.html', context)

# Table

def table_simple(request):
  context = {
    'parent': 'tables',
    'segment': 'simple_table'
  }
  return render(request, 'pages/tables/simple.html', context)

def table_data(request):
  context = {
    'parent': 'tables',
    'segment': 'data_table'
  }
  return render(request, 'pages/tables/data.html', context)

def table_jsgrid(request):
  context = {
    'parent': 'tables',
    'segment': 'jsGrid'
  }
  return render(request, 'pages/tables/jsgrid.html', context)
