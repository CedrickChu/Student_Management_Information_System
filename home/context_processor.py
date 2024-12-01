from .models import StudentInfo

def student_infos(request):
    student_infos = StudentInfo.objects.select_related('student').all()
    return {'student_infos': student_infos}