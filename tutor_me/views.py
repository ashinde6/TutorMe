from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User as auth_user
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import EditProfileForm, EditProfileForm_Tutor, ReviewForm, AvailabilityForm


from .models import TM_User, Course, Dept, FriendRequest, Review, Booking, Time_Range
from datetime import datetime, timedelta
import pytz


def send_request(request, user_id):
    print(f'request.POST: {request.POST}')
    from_user_ = auth_user.objects.get(id = request.user.id)
    from_user = TM_User.objects.get(auth_user = from_user_)
    start_time = datetime.strptime(request.POST['startDateTime'],"%Y-%m-%dT%H:%M")
    start_time = start_time.replace(tzinfo=pytz.timezone('UTC'))
    hours_dur = int(request.POST['duration'][:2])
    minutes_dur = int(request.POST['duration'][3:])
    # n_hours = hours_dur + start_time.hour
    # n_minutes = minutes_dur + start_time.minute
    # if n_minutes >= 60:
    #     n_hours += 1
    #     n_minutes -= 60
    duration = timedelta(hours=hours_dur, minutes=minutes_dur)
    end_time = start_time + duration
    # end_time = start_time.replace(hour=n_hours, minute=n_minutes)
    # end_time = datetime(end_time.year, end_time.month, end_time.day, end_time.hour, end_time.minute, end_time.second, tzinfo=start_time.tzinfo)
    # time_range = Time_Range.objects.create(start=start_time, end=end_time)
    # to_user = TM_User.objects.get(id=user_id)

    # # check if it falls in the availability of the tutor
    # availabilities = to_user.availability.all()
    # for availability in availabilities:
    #     if time_range.start >= availability.start and time_range.end <= availability.end:
    #         break
    # else:
    #     return HttpResponse('Tutor is not available at that time <a href=' + reverse('tutor_me:edit_profile', args=(to_user.auth_user.id,)) + ">Go Back</a>")

    # # check if the tutor is already booked at that time
    # bookings = Booking.objects.filter(tutor=to_user)
    # for booking in bookings:
    #     if time_range.start < booking.time.start and time_range.start > booking.time.end or time_range.end < booking.time.start and time_range.end > booking.time.end:
    #         return HttpResponse('Tutor is already booked at that time')
    
    # course_l = request.POST['course'].strip().split()
    # course = Course.objects.get(department=course_l[0], course_number=course_l[1])
    # friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
    # booking, created = Booking.objects.get_or_create(tutor=to_user, student=from_user, approved=False, friend_request=friend_request, time=time_range, course=course)
    # friend_request.booking = booking
    # friend_request.save()
    if request.POST['recurring'] == 'False':
        created = create_request_and_booking(start_time, end_time, user_id, from_user, request.POST['course'])
    else:
        for i in range(int(request.POST['count'])):
            created = create_request_and_booking(start_time, end_time, user_id, from_user, request.POST['course'])
            if not created:
                break
            if request.POST['frequency'] == 'weekly':
                start_time = start_time + timedelta(days=7)
                end_time = end_time + timedelta(days=7)
            elif request.POST['frequency'] == 'biweekly':
                start_time = start_time + timedelta(days=14)
                end_time = end_time + timedelta(days=14)
            elif request.POST['frequency'] == 'monthly':
                start_time = start_time + timedelta(days=30)
                end_time = end_time + timedelta(days=30)
    if created: 
        return HttpResponseRedirect(reverse('tutor_me:user_home', args=(request.user.id,)))
    else:
        return HttpResponse('Tutoring Request Was Already Sent')

def create_request_and_booking(start_time, end_time, user_id, from_user, course):
    time_range = Time_Range.objects.create(start=start_time, end=end_time)
    to_user = TM_User.objects.get(id=user_id)

    # check if it falls in the availability of the tutor
    availabilities = to_user.availability.all()
    for availability in availabilities:
        if time_range.start >= availability.start and time_range.end <= availability.end:
            break
    else:
        return HttpResponse('Tutor is not available at that time <a href=' + reverse('tutor_me:edit_profile', args=(to_user.auth_user.id,)) + ">Go Back</a>")

    # check if the tutor is already booked at that time
    bookings = Booking.objects.filter(tutor=to_user)
    for booking in bookings:
        if time_range.start < booking.time.start and time_range.start > booking.time.end or time_range.end < booking.time.start and time_range.end > booking.time.end:
            return HttpResponse('Tutor is already booked at that time')
    
    course_l = course.strip().split()
    course = Course.objects.get(department=course_l[0], course_number=course_l[1])
    friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
    booking, created = Booking.objects.get_or_create(tutor=to_user, student=from_user, approved=False, friend_request=friend_request, time=time_range, course=course)
    friend_request.booking = booking
    friend_request.save()
    return created

def decline_request(request, requestID):
    friend_request = FriendRequest.objects.get(id=requestID)
    if (friend_request.to_user == request.user.tm_user) or (friend_request.from_user == request.user.tm_user):
        friend_request.booking.delete()
        return HttpResponse(f"Tutoring Request {'Declined' if request.user.tm_user.is_tutor else 'Deleted'} for {friend_request.from_user.name} <a href=" + reverse('tutor_me:user_home', args=(request.user.id,)) + ">Go Back</a>")
    else:
        return HttpResponse(f"Tutoring Request NOT {'Declined' if request.user.tm_user.is_tutor else 'Deleted'} <a href=" + reverse('tutor_me:user_home', args=(request.user.id,)) + ">Go Back</a>")

def accept_request(request, requestID):
    friend_request = FriendRequest.objects.get(id=requestID)
    if (friend_request.to_user == request.user.tm_user):
        friend_request.to_user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(friend_request.to_user)
        print(friend_request.booking)
        if friend_request.booking.approved:
            return HttpResponse(f"Tutoring Request Already Accepted for {friend_request.from_user.name} <a href=" + reverse('tutor_me:user_home', args=(request.user.id,)) + ">Go Back</a>")
        for booking in Booking.objects.filter(student=friend_request.from_user, approved=True, cancelled=False):
            if booking.time.start < friend_request.booking.time.start < booking.time.end or booking.time.end > friend_request.booking.time.end > booking.time.start:
                return HttpResponse(f"Tutoring Request Overlaps with {booking.student.name}'s Session with {booking.tutor.name} <a href=" + reverse('tutor_me:user_home', args=(request.user.id,)) + ">Go Back</a>")
        for booking in Booking.objects.filter(tutor=friend_request.from_user, approved=True, cancelled=False):
            if booking.time.start < friend_request.booking.time.start < booking.time.end or booking.time.end > friend_request.booking.time.end > booking.time.start:
                return HttpResponse(f"Tutoring Request Overlaps with {booking.student.name}'s Session with {booking.tutor.name} <a href=" + reverse('tutor_me:user_home', args=(request.user.id,)) + ">Go Back</a>")
        friend_request.booking.approved = True
        friend_request.booking.save()
        friend_request.delete()
        return HttpResponseRedirect(reverse('tutor_me:user_home', args=(request.user.id,))) # HttpResponse(f"Tutoring Request Accepted for {friend_request.from_user.name} <a href=" + reverse('tutor_me:user_home', args=(request.user.id,)) + ">Go Back</a>")
    else:
        return HttpResponse("Tutoring Request Not Accepted <a href=" + reverse('tutor_me:user_home', args=(request.user.id,)) + ">Go Back</a>")

def user_redirect(request):
    print(f'request.user.id: {request.user.id}')
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('tutor_me:user_home', args=(request.user.id,)))
    else:
        return HttpResponseRedirect(reverse('tutor_me:home'))

def remove_course(request, courseID):
    user = request.user.tm_user
    course = Course.objects.get(id=courseID)
    user.courses.remove(course)
    course.tutors.remove(user)
    return HttpResponseRedirect(reverse('tutor_me:profile', args=(request.user.id,)))

class IndexView(generic.DetailView):
    model = TM_User
    template_name = 'tutor_me/index.html'

    def get_context_data(self, **kwargs):
        print(f'self.request: {self.request}')
        context = super().get_context_data(**kwargs)
        obj_requests = FriendRequest.objects.filter(to_user=self.request.user.tm_user)
        requests_formatted = []
        for requesti in obj_requests:
            requests_formatted.append(f'Request from {requesti.from_user.name}')
        context['requests'] = requests_formatted
        if self.request.user.tm_user.is_tutor:
            obj_sessions = Booking.objects.filter(tutor=self.request.user.tm_user)
            context['sessions'] = obj_sessions
        else:
            obj_sessions = Booking.objects.filter(student=self.request.user.tm_user)
            context['sessions'] = obj_sessions
        print(len(obj_sessions))
        return context

def index_view(request, user_id):
    if user_id != request.user.id:
        return HttpResponseRedirect(reverse('tutor_me:user_home', args=(request.user.id,)))
    user = get_object_or_404(auth_user, id=user_id)
    try:
        tm_user = get_object_or_404(TM_User, auth_user=user)
    except:
        tm_user = TM_User(name=f'{user.first_name} {user.last_name}', email=user.email, auth_user=user, is_active=True)
    print(f'request: {request}')
    context = {}
    if tm_user.is_tutor:
        obj_requests = FriendRequest.objects.filter(to_user=tm_user)
    else:
        obj_requests = FriendRequest.objects.filter(from_user=tm_user)
    requests_formatted = []
    # for requesti in obj_requests:
    #     requests_formatted.append(f'Request {f"from {requesti.from_user.name}" if tm_user.is_tutor else f"to {requesti.to_user.name}"}')
    context['requests'] = obj_requests
    if tm_user.is_tutor:
        obj_sessions = Booking.objects.filter(tutor=tm_user, approved=True).order_by('cancelled','time')
        context['sessions'] = obj_sessions
    else:
        obj_sessions = Booking.objects.filter(student=tm_user, approved=True).order_by('cancelled', 'time')
        context['sessions'] = obj_sessions
    print(len(obj_sessions))
    return render(request, 'tutor_me/index.html', context)
    
class CourseView(LoginRequiredMixin, generic.ListView):
    template_name = 'tutor_me/course.html'
    context_object_name = 'course_list'
    model = Course

    def get(self, request, *args, **kwargs):
        def filterString(str):
            remove = [' ', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
            for r in remove:
                str = str.replace(r, '')
            return str

        if 'dept' not in self.kwargs:
            if 'dept' not in self.request.GET:
                depts = list(retrieve_all_depts())
                depts.sort()
                return render(request, 'tutor_me/depts.html', {'dept_list': depts, 'bad_search': False})
            depts = retrieve_all_depts()
            if filterString(self.request.GET['dept'].upper()) not in depts:
                depts = list(depts)
                depts.sort()
                return render(request, 'tutor_me/depts.html', {'dept_list': depts, 'bad_search': True})
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        def filterString(str):
            remove = [' ', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
            for r in remove:
                str = str.replace(r, '')
            return str

        context = super().get_context_data(**kwargs)
        if 'dept' not in self.kwargs:
            if 'dept' not in self.request.GET:
                return {}
            context['dept'] = filterString(self.request.GET['dept'].upper())
        else:
            context['dept'] = filterString(self.kwargs['dept'].upper())

        user = get_object_or_404(auth_user, pk=self.request.user.id)
        tm_user = get_object_or_404(TM_User, auth_user=user)
        context['tm_user'] =  tm_user
        context['tm_user_id'] = tm_user.id


        return context

    def get_queryset(self):
        def filterString(str):
            remove = [' ', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
            for r in remove:
                str = str.replace(r, '')
            return str

        if 'dept' not in self.kwargs:
            if 'dept' not in self.request.GET:
                return {}
            dept = filterString(self.request.GET['dept'].upper())
        else:
            dept = filterString(self.kwargs['dept'].upper())
        course_list = Course.objects.filter(department=dept).order_by('course_number')
        # print(type(course_list))
        print(len(course_list))
        return course_list



class ProfileView(generic.DetailView):
    model = TM_User
    template_name = 'tutor_me/edit_profile.html'

class TutorListView(generic.ListView):
    model = TM_User
    template_name = 'tutor_me/tutors_list.html'

def profile(request, user_id, search):
    user = get_object_or_404(auth_user, pk=user_id)
    tm_user = get_object_or_404(TM_User, auth_user=user)
    print(f'user.id: {user.id}')
    print(f'tm_user.id: {tm_user.id}')

    context = {
        'tm_user': tm_user,
        'courses': tm_user.courses.all().order_by('department', 'course_number'),
    }
    return render(request, 'tutor_me/user_profile.html', context)

def edit_profile_view(request, user_id):
    user = get_object_or_404(auth_user, pk=user_id)
    tm_user = get_object_or_404(TM_User, auth_user=user)
    current_user = TM_User.objects.get(id = request.user.tm_user.id)
    print(f'user.id: {user.id}')
    print(f'tm_user.id: {tm_user.id}')

    #calendar = get_calendar(request, user_id)

    if request.method == 'POST':
        if (tm_user.is_tutor):
            u_form = EditProfileForm_Tutor(request.POST, instance=request.user)
        else:
            u_form = EditProfileForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            tm_user.age = u_form.cleaned_data['age']
            if (tm_user.is_tutor):
                tm_user.hourly_rate = u_form.cleaned_data['hourly_rate']
            tm_user.save()
        r = Review()
        r.target = tm_user
        r.commenter = current_user
        r_form = ReviewForm(request.POST, instance=r)
        if r_form.is_valid():
            r_form.save()
            tm_user.reviews.add(r)
        #e_form = BookingForm(request.POST)
        a = Time_Range()
        a_form = AvailabilityForm(request.POST, instance=a)
        if a_form.is_valid():
            a_form.save()
            tm_user.availability.add(a)

        messages.success(request, f'Your account has been updated!')
        return redirect('tutor_me:profile', user_id=user_id)
    else:
        if (tm_user.is_tutor):
            u_form = EditProfileForm_Tutor(instance=request.user)
        else:
            u_form = EditProfileForm(instance=request.user)
        r = Review()
        r.target = tm_user
        r.commenter = current_user
        r_form = ReviewForm(instance=r)
        #e_form = BookingForm(request.POST)
        a = Time_Range()
        a_form = AvailabilityForm(instance=a)

    context = {
        'availability': tm_user.availability.all().order_by('start'),
        'u_form': u_form,
        'r_form': r_form,
        'a_form': a_form,
        #'e_form': e_form,
        'tm_user': tm_user,
        'courses': tm_user.courses.all().order_by('department', 'course_number'),
        #'calendar': calendar
    }

    # if tm_user.availability.all():
    #     start_avail = tm_user.availability.all()[0].start
    #     end_avail = tm_user.availability.all()[0].end
    #     context['start_avail'] = start_avail
    #     context['end_avail'] = end_avail

    return render(request, 'tutor_me/edit_profile.html', context)

def course_list_view(request, dept):
    courses = list(retrieve_courses_for_dept(request, dept))
    post_courses = []
    for course in courses:
        post_courses.append(course['department'] + ' ' + course['course_number'])
    post_courses.sort()
    return render(request, 'tutor_me/course.html', {'course_list': post_courses, 'dept': dept.upper()})


def dept_list_view(request):
    #if 'dept' not in request.GET:
        #depts = list(retrieve_all_depts())
        #depts.sort()
        #return render(request, 'tutor_me/depts.html', {'dept_list': depts, 'bad_search': False})
    print(request.GET['dept'])

    dept = request.GET['dept']
    courses = list(retrieve_courses_for_dept(request, dept))
    print(f'len(courses): {len(courses)}')
    if len(courses) == 0:
        depts = list(retrieve_all_depts())
        depts.sort()
        return render(request, 'tutor_me/depts.html', {'dept_list': depts, 'bad_search': True})
    post_courses = []
    for course in courses:
        post_courses.append(course['department'] + ' ' + course['course_number'])
    post_courses.sort()
    return render(request, 'tutor_me/course.html', {'course_list': post_courses, 'dept': dept.upper()})


def select_courses(request, user_id):
    user = get_object_or_404(auth_user, pk=user_id)
    tm_user = get_object_or_404(TM_User, auth_user=user)

    if request.method == 'POST':
        print(request.POST)
        for course in request.POST.getlist('courses'):
            tm_user.courses.add(course)
            if tm_user.is_tutor:
                c = Course.objects.get(pk=course)
                c.tutors.add(tm_user)
                c.save()
        tm_user.save()
        return HttpResponseRedirect(reverse('tutor_me:main'))


def select_class(request, user_id):
    # post to user_id to select class

    user = get_object_or_404(auth_user, pk=user_id)

    tm_user, created = TM_User.objects.get_or_create(auth_user=user, name=f'{user.first_name} {user.last_name}',
                                                     email=user.email)

    # print(request.POST)
    # print(request.POST['is_tutor'] if 'is_tutor' in request.POST else 'no tutor')
    # print(request.POST['is_student'] if 'is_student' in request.POST else 'no student')
    # print(tm_user)
    # return HttpResponseRedirect(reverse('tutor_me:home'))
    tm_user.is_tutor = 'is_tutor' in request.POST and request.POST.get("is_tutor") == 'True'
    tm_user.is_student = 'is_tutor' in request.POST and request.POST.get("is_tutor") == 'False'
    tm_user.save()

    return HttpResponseRedirect(reverse('tutor_me:main'))

def clear_class(request):

    user = get_object_or_404(auth_user, pk=request.user.id)

    tm_user = get_object_or_404(TM_User, auth_user=user)

    tm_user.is_tutor = False
    tm_user.is_student = False
    tm_user.save()

    return HttpResponseRedirect(reverse('tutor_me:main'))

def retrieve_all_depts():
    deptList = Dept.objects.all()
    depts = []
    for d in deptList:
        depts.append(d.dept)
    return depts

    # url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearchOptions?institution=UVA01&term=1228"
    # r = requests.get(url)
    # subject_list = r.json()['subjects']
    # dept_set = set()
    # for item in subject_list:
    # dept_set.add(item['subject'])

    # return dept_set
    # print(dept_set)


def retrieve_courses_for_dept(dept):
    remove = [' ', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    for r in remove:
        dept = dept.replace(r, '')
    d = Dept.objects.get(dept=dept)
    classes = []
    for c in d.courses.all():
        course = {'department': c['subject'], 'course_number': c['catalog_nbr'], 'course_description': c['descr']}
        classes.append(course)
    return classes

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.user.tm_user == booking.tutor:
        booking.cancelled = True
        booking.save()
        return HttpResponseRedirect(reverse('tutor_me:main'))
    elif request.user.tm_user == booking.student:
        booking.cancelled = True
        booking.save()
        return HttpResponseRedirect(reverse('tutor_me:main'))
    return HttpResponse("You are not authorized to cancel this booking")

def add_availability(request, user_id):
    # print(request.POST)
    user = get_object_or_404(auth_user, pk=user_id)
    tm_user = get_object_or_404(TM_User, auth_user=user)
    if request.method == 'POST' and 'start' in request.POST and 'end' in request.POST:
        start = datetime.strptime(request.POST['start'], '%Y-%m-%dT%H:%M')
        end = datetime.strptime(request.POST['end'], '%Y-%m-%dT%H:%M')
        if request.POST['recurring'] == 'False':
            create_availability(start, end, tm_user)
        else:
            for i in range(int(request.POST['count'])):
                create_availability(start, end, tm_user)
                if request.POST['frequency'] == 'weekly':
                    start = start + timedelta(days=7)
                    end = end + timedelta(days=7)
                elif request.POST['frequency'] == 'biweekly':
                    start = start + timedelta(days=14)
                    end = end + timedelta(days=14)
                elif request.POST['frequency'] == 'monthly':
                    start = start + timedelta(days=30)
                    end = end + timedelta(days=30)
        return HttpResponseRedirect(reverse('tutor_me:edit_profile', args=(tm_user.auth_user.id,)))
    return HttpResponse('Invalid request')

def create_availability(start, end, tm_user):
    availability = Time_Range.objects.create(start=start, end=end)
    availability.save()
    tm_user.availability.add(availability)
    tm_user.save()

def delete_availability(request, availability_id):
    availability = get_object_or_404(Time_Range, pk=availability_id)
    if availability in request.user.tm_user.availability.all():
        availability.delete()
        return HttpResponseRedirect(reverse('tutor_me:edit_profile', args=(request.user.id,)))
    return HttpResponse("You are not authorized to delete this availability")

#SCOPES = ["https://www.googleapis.com/auth/calendar"]

#service_account_email = "tutorme@tutorme-383702.iam.gserviceaccount.com"
#credentials = service_account.Credentials.from_service_account_file('google-calendar.json')
#scoped_credentials = credentials.with_scopes(SCOPES)
#calendarId = "c_528a5cc804ea55ec62964af339f9034bb80c07a6c7af07181b2ddd6dfe885c70@group.calendar.google.com"


# class CalendarView(FormView):
#     form_class = EventsForm
#     template_name = 'tutor_me/demo.html'
#
#     def post(self, request, *args, **kwargs):
#         form = EventsForm(request.POST)
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_valid(form)
#
#     def form_valid(self, form):
#         eventTitle = form.cleaned_data.get("eventTitle")
#         start_date_data = form.cleaned_data.get("startDateTime")
#         end_date_data = form.cleaned_data.get("endDateTime")
#
#         if start_date_data > end_date_data:
#             messages.add_message(self.request, messages.INFO, 'Please enter the correct period.')
#             return HttpResponseRedirect(reverse("tutor_me:demo"))
#
#         service = build_service(self.request)
#
#         event = (
#             service.events().insert(
#                 calendarId = calendarId,
#                 body={
#                     "summary": eventTitle,
#                     "start": {"dateTime": start_date_data.isoformat()},
#                     "end": {"dateTime": end_date_data.isoformat()},
#                 },
#             ).execute()
#         )
#
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         messages.add_message(self.request, messages.INFO, 'Form submission success!')
#         return reverse('tutor_me:demo')


#def get_credentials(user):
    #token = SocialToken.objects.get(account__user=user, account__provider='google')
#    social_app = SocialApp.objects.get(name='calendar')
#    creds = Credentials.from_authorized_user_info(info=user)

    #creds = Credentials(
    #    #token=token.token,
    #    #refresh_token=token.token_secret,
    #    token_uri='http://oauth2.googleapis.com/token',
    #    client_id=social_app.client_id,
    #    client_secret=social_app.secret,
    #    scopes=SCOPES
    #)

#    if not creds or not creds.valid:
#        if creds and creds.expired and creds.refresh_token:
#            creds.refresh(Request())

#    return creds


#def create_calendar(request, user_id):
#    user = get_object_or_404(auth_user, pk=user_id)
#    tm_user = get_object_or_404(TM_User, auth_user=user)

#    if not tm_user.calendar_exists:
#        creds = get_credentials(user)
#        service = build('calendar', 'v3', credentials=creds)

#        calendar = {
#            'summary': 'calendarSummary',
#            'timeZone': 'America/New_York'
#        }

#        created_calendar = service.calendars().insert(body=calendar).execute()

#        tm_user.calendar_id = created_calendar['id']
#        tm_user.calendar_exists = True
#        tm_user.save()

#        calendar = service.calendars().get(calendarId=created_calendar['id']).execute()
#        return calendar


#def get_calendar(request, user_id):
#    user = get_object_or_404(auth_user, pk=user_id)
#    tm_user = get_object_or_404(TM_User, auth_user=user)

#    if tm_user.calendar_exists:
#        creds = get_credentials(user)
#        service = build('calendar', 'v3', credentials=creds)

#        calendarId = tm_user.calendar_id
#        print(calendarId)
#        print("Cal ID ^^^^")

#        calendar = service.calendars().get(calendarId=calendarId).execute()

#        return calendar
#    else:
#        return create_calendar(request, user_id)

    # def get_context_data(self, **kwargs):
    #     context = super(CalendarView, self).get_context_data(**kwargs)
    #     form = EventsForm()
    #     booking_event = []
    #     service = build_service(self.request)
    #     events = (
    #         service.events().list(
    #             calendarId=calendarId
    #         ).execute()
    #     )
    #
    #     for event in events['items']:
    #         event_title = event['summary']
    #
    #         # Deleted the last 6 characters (deleted UTC time)
    #         start_date_time = event["start"]["dateTime"]
    #         start_date_time = start_date_time[:-6]
    #
    #         # Deleted the last 6 characters (deleted UTC time)
    #         end_date_time = event['end']["dateTime"]
    #         end_date_time = end_date_time[:-6]
    #
    #         booking_event.append([event_title, start_date_time, end_date_time])
    #
    #     context = {
    #         "form": form,
    #         "booking_event": booking_event,
    #     }
    #
    #     return context

    # This code is deprecated as Kaden has added a model for departments, which allows easier searching
    # courseList = Course.objects.all()
    # classes = []
    # for c in courseList:
    # if c.department == dept:
    # course = {'department': c['subject'], 'course_number': c['catalog_nbr'], 'course_description': c['descr']}
    # if course not in classes:
    # classes.append(course)
    # return classes

    # This code is deprecated as it calls sis
    # dept_set = retrieve_all_depts()
    # print(dept)
    # if dept.upper() not in dept_set:
    # Invalid dept mnemonic provided
    # print("Invalid department menomnic")
    # return []

    # url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1228"
    # r = requests.get(url + '&subject=' + dept.upper() + '&page=1')
    # print(r.content)

    # classes = []
    # copied straight from given example
    # for c in r.json():
    # print(c['subject'], c['catalog_nbr'] + '-' + c['class_section'])
    # course = {'department': c['subject'], 'course_number': c['catalog_nbr'], 'course_description': c['descr']}
    # classes.append(c['subject'] + ' ' + c['catalog_nbr'] + '-' + c['class_section'])
    # if course not in classes:
    # classes.append(course)
    # print(c['subject'], c['catalog_nbr'] + '-' + c['class_section'], c['component'], c['descr'], \
    #       c['class_nbr'], c['class_capacity'], c['enrollment_available'])

    # return classes
    # return HttpResponse(f'Classes for {dept.upper()}:'
    # f'{classes}')

# retrieve_courses_for_dept("CS")

