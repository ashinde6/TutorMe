from django.contrib import admin
import time

# Register your models here.

from .models import TM_User, Course, Dept, Time_Range, Review, Booking, FriendRequest
import requests, json


from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import AbstractUser, User as auth_user
from django.template import loader


admin.site.register(Course)
admin.site.register(Time_Range)
admin.site.register(Review)
admin.site.register(FriendRequest)


#loads all the courses and depts from sis
@admin.action(description='Update departments db')
def update_dept_db(*_):
    url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearchOptions?institution=UVA01&term=1228"
    r = requests.get(url)
    subject_list = r.json()['subjects']
    dept_set = set()
    for item in subject_list:
        dept_set.add(item['subject'])
        a, _ = Dept.objects.get_or_create(dept=item['subject'])
        a.save()

@admin.action(description='Update courses db')
def update_course_db(modeladmin, request, queryset):
    url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1228"
    for dept in queryset:
        if dept.completed == False:
            # getting rate limited by sis api
            course_data_raw = requests.get(url + '&subject=' + dept.dept + '&page=1') #attempting to fix heroku timeout
            #try:
            #    course_data_raw = requests.get(url + '&subject=' + dept + '&page=1')
            #except requests.ConnectTimeout:
            #    time.sleep(1)
            #    course_data_raw = requests.get(url + '&subject=' + dept + '&page=1')
            course_data = json.dumps(course_data_raw.json())
            courses = json.loads(course_data)
            saved = set()
            for c in courses:
                if c['subject'] + c['catalog_nbr'] in saved:
                    continue
                a, _ = Course.objects.get_or_create(department=c['subject'], course_number=c['catalog_nbr'], course_description=c['descr'])
                a.save()
                b = Dept.objects.get(dept=c['subject'])
                b.courses.add(a)
                b.save()
                saved.add(c['subject'] + c['catalog_nbr'])
            dept.completed = True
            dept.save()

@admin.action(description='Delete all courses')
def del_all_courses(*_):
    for c in Course.objects.all():
        c.delete()

@admin.action(description='Delete all depts')
def del_all_depts(*_):
    for c in Dept.objects.all():
        c.delete()

@admin.action(description='Delete all users')
def del_all_users(*_):
    for c in TM_User.objects.all():
        c.delete()

@admin.action(description='Delete all bookings')
def delete_all_bookings(*_):
    for c in Booking.objects.all():
        c.delete()

@admin.action(description='Clear user\'s courses')
def clear_courses(modeladmin, request, queryset):
    for user in queryset:
        for course in user.courses.all():
            course.tutors.remove(user)
            course.save()
        user.courses.clear()
        user.save()


#should define how the action appears in the panel
class DeptAdmin(admin.ModelAdmin):
    actions = [update_dept_db, update_course_db, del_all_courses, del_all_depts]

class UserAdmin(admin.ModelAdmin):
    actions = [del_all_users, clear_courses]

class BookingAdmin(admin.ModelAdmin):
    actions=[delete_all_bookings]

admin.site.register(TM_User, UserAdmin)
admin.site.register(Dept, DeptAdmin)
admin.site.register(Booking, BookingAdmin)