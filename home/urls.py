from django.urls import path
from home import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Pages
    path('logout/', views.logout_view, name='logout'),
    path('test', views.test),
    path('', views.login_view, name='login'),
    path('home/', views.index, name='home'),
    path('dashboard-v2/', views.index2, name='dashboardv2'),
    path('dashboard-v3/', views.index3, name='dashboardv3'),
    path('StudentList/', views.allStudent_list, name='allStudent-list'),
    path('widgets/', views.widgets, name='widgets'),
    path('profile/', views.profile, name='profile'),
    path('student/', views.student_list, name='student-list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student/edit/<int:student_id>/', views.student_update, name='student-update'),
    path('student/add/', views.add_student, name='student-add'),
    path('student/print/', views.PrintStudentListView.as_view(), name='student-print'),
    path('student/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student-delete'),
    path('gradelevel/', views.grade_list, name='grade-level'),
    path('gradelevel/add/', views.add_grade, name='grade-add'),
    path('grade/<int:pk>/update/', views.update_grade, name='grade-update'),
    path('subject/', views.subject_list, name='subject-list'),
    path('subject/add/', views.add_subject, name='subject-add'),
    path('subject/<int:pk>/update/', views.update_subject, name='subject-update'),
    path('report/form137/', views.student_report, name='student_record'),
    path('report/<int:pk>/form137/', views.student_form137, name='student-report-print'),
    path('schoolyear/', views.school_year, name='schoolyear-list'),
    path('schoolyear/add/', views.add_year, name='year-add'),
    path('schoolyear/<int:pk>/update/', views.update_year, name='year-update'),
    path('section/', views.section_list, name='section-list'),
    path('section/add/', views.add_section, name='section-add'),
    path('section/<int:pk>/update/', views.update_section, name='section-update'),
    path('teacher/', views.teacher_list, name='teacher-list'),
    path('teacher/add', views.add_teacher, name='teacher-add'),
    path('teacher/<int:pk>/update/', views.update_teacher, name='teacher-update'),
    path('allStudent/', views.allStudent_list, name='allStudent-list'),
    path('student/generic/add', views.add_generic_student, name='allStudent-add'),
    path('parent/add', views.add_parent, name='parent-add'),
    path('parent/', views.parent_list, name='parent-list'),
    path('parent/update/<int:pk>/', views.update_parent, name='parent-update'),
    path('parentguardian/delete/', views.delete_parent, name='parent-delete'),
    path('teacher/delete/', views.delete_teacher, name='teacher-delete'),
    path('user/', views.user_list, name='user-list'),
    path('user/add/', views.user_add, name='user-add'),
    path('user/update/<int:pk>/', views.user_update, name='user-update'),
    path('invalid/', views.custom_page, name='custom_page'),
    path('student-academic/<int:student_id>/', views.student_academic_record, name='student_academic_record'),
    path('fetch_student_grade/<int:grade_id>/', views.fetch_student_grade, name='fetch_student_grade'),
    path('update_student_grade/<int:grade_id>/', views.update_student_grade, name='update_student_grade'),
    path('delete_student_grade/<int:grade_id>/', views.delete_student_grade, name='delete_student_grade'),
    path('newstudent/', views.student_new, name='student-new'),
    path('student/old/', views.student_old, name='student-old'),
    path('student/transferee/', views.student_transfer, name='student-transfer'),
    path('all_events/', views.all_events, name='all_events'), 
    path('add_event/', views.add_event, name='add_event'), 
    path('update/', views.update_event, name='update'),
    path('remove/', views.delete_event, name='remove'),
    # Examples
    path('examples/calendar/', views.examples_calendar, name='examples_calendar'),
    path('examples/gallery/', views.examples_gallery, name='examples_gallery'),
    path('examples/kanban/', views.examples_kanban, name='examples_kanban'),
    path('examples/invoice/', views.examples_invoice, name='examples_invoice'),
    path('invoice-print/', views.invoice_print, name='invoice_print'),
    path('examples/profile/', views.examples_profile, name='examples_profile'),
    path('examples/e-commerce/', views.examples_e_commerce, name='examples_e_commerce'),
    path('examples/projects/', views.examples_projects, name='examples_projects'),
    path('examples/project-add/', views.examples_project_add, name='examples_project_add'),
    path('examples/project-edit/', views.examples_project_edit, name='examples_project_edit'),
    path('examples/project-detail/', views.examples_project_detail, name='examples_project_detail'),
    path('examples/contacts/', views.examples_contacts, name='examples_contacts'),
    path('examples/faq/', views.examples_faq, name='examples_faq'),
    path('examples/contact-us/', views.examples_contact_us, name='examples_contact_us'),
    # Extra 
    path('lockscreen/', views.lockscreen, name='lockscreen'),
    path('legacy-user-menu/', views.legacy_user_menu, name='legacy_user_menu'),
    path('language-menu/', views.language_menu, name='language_menu'),
    path('error-404/', views.error_404, name='error_404'),
    path('error-500/', views.error_500, name='error_500'),
    path('pace/', views.pace, name='pace'),
    path('blank-page/', views.blank_page, name='blank_page'),
    path('starter-page/', views.starter_page, name='starter_page'),

    # Search
    path('search-simple/', views.search_simple, name='search_simple'),
    path('search-enhanced/', views.search_enhanced, name='search_enhanced'),
    path('simple-result/', views.simple_results, name='simple_results'),
    path('enhanced-result/', views.enhanced_results, name='enhanced_results'),

    path('iframe/', views.iframe, name='iframe'),



    # Mailbox
    path('mailbox/inbox/', views.mailbox_inbox, name='mailbox_inbox'),
    path('mailbox/compose/', views.mailbox_compose, name='mailbox_compose'),
    path('mailbox/read-mail/', views.mailbox_read_mail, name='mailbox_read_mail'),

    # Charts
    path('chartjs/', views.chartjs, name='chartjs'),
    path('flot/', views.flot, name='flot'),
    path('inline/', views.inline, name='inline'),
    path('uplot/', views.uplot, name='uplot'),

    # UI Elements
    path('ui/general/', views.ui_general, name='ui_general'),
    path('ui/icons/', views.ui_icons, name='ui_icons'),
    path('ui/buttons/', views.ui_buttons, name='ui_buttons'),
    path('ui/sliders/', views.ui_sliders, name='ui_sliders'),
    path('ui/modals-alerts/', views.ui_modals_alerts, name='ui_modals_alerts'),
    path('ui/navbar-tabs/', views.ui_navbar_tabs, name='ui_navbar_tabs'),
    path('ui/timeline/', views.ui_timeline, name='ui_timeline'),
    path('ui/ribbons/', views.ui_ribbons, name='ui_ribbons'),

    # Forms
     path('form/general/', views.form_general, name='form_general'),
     path('form/advanced/', views.form_advanced, name='form_advanced'),
     path('form/editors/', views.form_editors, name='form_editors'),
     path('form/validation/', views.form_validation, name='form_validation'),

     # Table
     path('table/simple/', views.table_simple, name='table_simple'),
     path('table/data/', views.table_data, name='table_data'),
     path('table/jsgrid/', views.table_jsgrid, name='table_jsgrid'),

    #Layouts
    path('top-navigation/', views.top_navigation, name='top_navigation'),
    path('top-nav-sidebar/', views.top_nav_sidebar, name='top_nav_sidebar'),
    path('boxed/', views.boxed, name='boxed'),
    path('fixed-sidebar/', views.fixed_sidebar, name='fixed_sidebar'),
    path('fixed-sidebar-custom/', views.fixed_sidebar_custom, name='fixed_sidebar_custom'),
    path('fixed-topnav/', views.fixed_topnav, name='fixed_topnav'),
    path('fixed-footer/', views.fixed_footer, name='fixed_footer'),
    path('collapsed-sidebar/', views.collapsed_sidebar, name='collapsed_sidebar'),

    # Authentication

    path('accounts/logout/', views.user_logout_view, name='logout'),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name="password_change_done" ),
    path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]
