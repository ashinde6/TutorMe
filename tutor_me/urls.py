from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView

app_name = 'tutor_me'
urlpatterns = [
    path('home', TemplateView.as_view(template_name="tutor_me/index.html"), name='home'),
    path('', views.user_redirect , name='main'),
    path('clear_class', views.clear_class, name='clear_class'),
    path('<int:user_id>/', views.index_view, name='user_home'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('<int:user_id>/select_class/', views.select_class, name='select_class'),
    path('retrieve_course_for_dept/<str:dept>/', views.retrieve_courses_for_dept, name='retrieve_courses_for_dept'),
    path('courses/<str:dept>/', views.CourseView.as_view(), name='courses'),
    path('<int:user_id>/select_courses/', views.select_courses, name='select_courses'),
    path('courses/', views.CourseView.as_view(), name='courses'),
    path('tutor_list/', views.TutorListView.as_view(), name='tutors'),
    path('tutor_list/<str:course>/', views.TutorListView.as_view(), name='tutors'),
    path('<int:user_id>/profile/', views.edit_profile_view, name='edit_profile'),
    path('<int:user_id>/profile/', views.profile, name='profile'), 
    path('<int:user_id>/profile/send_request/', views.send_request, name='send_request'), 
    path('remove_course/<int:courseID>', views.remove_course, name='remove_course'),
    path('<int:user_id>/profile/add_availability/', views.add_availability, name='add_availability'),
    path('accept_request/<int:requestID>', views.accept_request, name='accept_request'),
    path('decline_request/<int:requestID>', views.decline_request, name='decline_request'),
    path('cancel_booking/<int:booking_id>', views.cancel_booking, name='cancel_booking'),
    path('delete_availability/<int:availability_id>', views.delete_availability, name='delete_availability'),
]