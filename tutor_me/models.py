from django.db import models
from django.contrib.auth.models import User as auth_user


# from django.contrib.postgres.fields import ArrayField

# Create your models here.

class TM_User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    is_tutor = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    auth_user = models.OneToOneField(auth_user, on_delete=models.CASCADE, null=True)
    courses = models.ManyToManyField('Course', blank=True)
    calendar_exists = models.BooleanField(default=False)

    friends = models.ManyToManyField('TM_User', blank=True)

    calendar_id = models.CharField(max_length=200, blank=True, null=True, default='')
    calendar_url = models.CharField(max_length=200, blank=True, null=True, default='')

    # add more fields as needed
    hourly_rate = models.IntegerField(default=0)
    age = models.IntegerField(default=0)

    availability = models.ManyToManyField('Time_Range', blank=True)

    reviews = models.ManyToManyField('Review', blank=True)

    def __str__(self):
        return f'{self.name} ({self.email})'


class FriendRequest(models.Model):
    from_user = models.ForeignKey(TM_User, related_name="from_user", on_delete=models.CASCADE)
    to_user = models.ForeignKey(TM_User, related_name="to_user", on_delete=models.CASCADE)
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, null=True)

class Booking(models.Model):
    tutor = models.ForeignKey(TM_User, on_delete=models.CASCADE, related_name='tutor')
    student = models.ForeignKey(TM_User, on_delete=models.CASCADE, related_name='student')
    time = models.ForeignKey('Time_Range', on_delete=models.CASCADE, related_name='time')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='course')
    approved = models.BooleanField(default=False)
    friend_request = models.ForeignKey('FriendRequest', on_delete=models.SET_NULL, related_name='friend_request', null=True)
    cancelled = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.student.name} booked {self.tutor.name} for {self.course} at {self.time.to_string()}'


class Course(models.Model):
    department = models.CharField(max_length=4)
    course_number = models.CharField(max_length=4)
    course_description = models.CharField(max_length=1000)
    tutors = models.ManyToManyField('TM_User', blank=True)

    def __str__(self):
        return f'{self.department} {self.course_number}'  


class Dept(models.Model):
    dept = models.CharField(max_length=4)
    courses = models.ManyToManyField('Course', blank=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.dept}'

    # add more fields as needed


class Time_Range(models.Model):
    start = models.DateTimeField(blank=True)
    end = models.DateTimeField(blank=True)

    def to_string(self):
        return f'{self.start.strftime("%m/%d/%Y %I:%M %p")} to {self.end.strftime("%m/%d/%Y %I:%M %p")}'

    def __str__(self):
        return f'{self.start} {self.end}'


class Review(models.Model):
    commenter = models.ForeignKey(TM_User, on_delete=models.CASCADE, related_name='commenter')
    target = models.ForeignKey(TM_User, on_delete=models.CASCADE, related_name='target')
    text = models.CharField(blank=True, max_length=500)

    def __str__(self):
        return f'{self.commenter}\'s review of {self.target.name}'
