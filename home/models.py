from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group, Permission
from datetime import date
from django.core.exceptions import ValidationError
from .validators import PasswordValidation

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        
        # Apply password validation
        password_validator = PasswordValidation()
        try:
            # Validate password using the custom password validator
            validated_password = password_validator.validate(password)
        except ValidationError as e:
            raise ValidationError(e.messages)
        
        user = self.model(username=username, **extra_fields)
        user.set_password(validated_password)  # Ensure password is hashed and set properly
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        # Call create_user method to ensure password is validated and set
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.username

class SchoolYear(models.Model):
    year = models.CharField(max_length=9)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.BooleanField(default=False, help_text='Is this the current school year?')

    def __str__(self):
        return f"{self.year} ({self.start_date.year}-{self.end_date.year})"

class GradeLevel(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class ParentGuardian(models.Model):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    address = models.TextField(help_text='Full Address')
    contact_information = models.CharField(max_length=100, null=True)

    def clean(self):
        if self.middle_name is None:
            self.middle_name = ""

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Teacher(models.Model):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]
    teacher_id = models.CharField(max_length=100, unique=True, help_text='Unique Teacher ID', null=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    address = models.TextField(help_text='Full Address')
    contact_information = models.CharField(max_length=500, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)

    def clean(self):
        if self.middle_name is None:
            self.middle_name = ""

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.teacher_id})"

class Section(models.Model):
    name = models.CharField(max_length=100)
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.CASCADE)
    adviser = models.OneToOneField(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Student(models.Model):
    lrn = models.CharField(max_length=20, unique=True, help_text='Learner Reference Number', null=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField()
    place_of_birth = models.TextField(help_text='Birth Address')
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    address = models.TextField(help_text='Full Address')
    parent_guardians = models.ForeignKey(ParentGuardian,  on_delete=models.SET_NULL, null=True, help_text='List of Parents/Guardians')

    def clean(self):
        if self.middle_name is None:
            self.middle_name = ""

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def calculate_age(self, birth_date):
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age

class StudentInfo(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('old', 'Old'),
        ('transferee', 'Transferee'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.SET_NULL, null=True)
    paid_first_quarter = models.BooleanField(default=False)
    paid_second_quarter = models.BooleanField(default=False)
    paid_third_quarter = models.BooleanField(default=False)
    paid_fourth_quarter = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')

    class Meta:
        verbose_name = 'Student Year Information'
        unique_together = ('student', 'school_year')

    def __str__(self):
        return f"{self.student} - {self.school_year}"

class TransferInfo(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='transfer_info')
    previous_school_name = models.CharField(max_length=100)
    previous_school_address = models.TextField(help_text='Full Address of the Previous School')
    transfer_date = models.DateField()

    def __str__(self):
        return f"Transfer Info for {self.student_info.student} ({self.student_info.school_year})"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Principal(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    school_years = models.ManyToManyField(SchoolYear, related_name='principals')

    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.middle_name or ''} {self.teacher.last_name}"

class StudentGrade(models.Model):
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    first_grading = models.IntegerField( null=True, blank=True)
    second_grading = models.IntegerField(null=True, blank=True)
    third_grading = models.IntegerField(null=True, blank=True)
    fourth_grading = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.student} - {self.subject}"

    @property
    def final_grade(self):
        """Calculate and return the final grade based on available gradings."""
        gradings = [
            self.first_grading,
            self.second_grading,
            self.third_grading,
            self.fourth_grading,
        ]
        valid_gradings = [g for g in gradings if g is not None]
        if valid_gradings:
            return sum(valid_gradings) / len(valid_gradings)
        return None

class EventCategory(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Event(models.Model):
    """
    Represents an event organized by the institution.

    Fields:
    - name: The title of the event.
    """
    name = models.CharField(max_length=200)
    note = models.TextField(max_length=500)
    start = models.DateTimeField()
    end = models.DateTimeField()
    color = models.CharField(max_length=7, default="#ff0000")


    def __str__(self):
        return self.name