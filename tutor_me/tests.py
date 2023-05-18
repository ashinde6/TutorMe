from django.test import TestCase
from .models import TM_User, Course, FriendRequest, Booking, Course, Dept, Time_Range, Review
from datetime import datetime, timedelta, timezone


# class Review_Tests(TestCase):
#     def setUp(self): 
#         self.commenter = TM_User(name="commenter")
#         self.commenter.save()
#         self.target = TM_User(name='target')
#         self.target.save()
#         self.text = "This is the review for the person I'm trying to review!"

#     def test_Review_str(self):


class Time_Range_Tests(TestCase):
    def setUp(self): 
        self.start = datetime.now()
        self.start = self.start.replace(tzinfo=timezone.utc)
        self.end = self.start + timedelta(hours=7)
        self.time = Time_Range(start = self.start, end =self.end)
        self.time.save()
    
    def test_Time_Range_str(self):
        expected = f'{self.start} {self.end}'
        self.assertEqual(expected, str(self.time))


class Dept(TestCase):

    def test_(self): 
        blue = 0


class Booking_Tests(TestCase):
    def setUp(self): 
        self.tutor = TM_User(name="tutor")
        self.tutor.save()
        self.student = TM_User(name='student')
        self.student.save()
        date_obj = datetime.now()
        date_obj = date_obj.replace(tzinfo=timezone.utc)
        next_date_obj = date_obj + timedelta(hours=7)
        self.time = Time_Range(start = date_obj, end =next_date_obj)
        self.time.save()
        self.course = Course(department="APMA", course_number=3100, course_description="Probability")
        self.course.save()

        self.booking = Booking(tutor=self.tutor, student=self.student, time=self.time, course=self.course)
    
    def test_Booking_params(self):
        self.assertEqual(self.booking.tutor, self.tutor)
        self.assertEqual(self.booking.student, self.student)
        self.assertEqual(self.booking.time, self.time)
        self.assertEqual(self.booking.course, self.course)


class FriendRequest_Tests(TestCase):

    def setUp(self): 
        self.from_user = TM_User(name="U1")
        self.from_user.save()
        self.to_user = TM_User(name="U2")
        self.to_user.save()

        self.friend_request = FriendRequest(from_user=self.from_user, to_user=self.to_user)
        self.friend_request.save()
    
    def test_Friend_Request_from_user(self):
        self.assertEqual(self.friend_request.from_user, self.from_user)
    
    def test_Friend_Request_to_user(self):
        self.assertEqual(self.friend_request.to_user, self.to_user)

    # note to self. do related names later 

        
class Course_Tests(TestCase):

    def setUp(self):

        self.course = Course(department="APMA", course_number=3100, course_description="Probability")
        self.course.save()

    def test_Course_model_str(self): 
        c = Course(department="APMA", course_number=3100)
        self.assertTrue(str(c), "APMA 3100")

    def test_Course_model_blank_tutors_list(self):
        self.assertQuerysetEqual(self.course.tutors.all(), [])
    
    def test_Course_model_1tutor(self):
        tutor = TM_User(name="tutor")
        tutor.save()
        self.course.tutors.add(tutor)
        self.assertIn(tutor, self.course.tutors.all())


class TM_UserTests(TestCase):

    def setUp(self):
        self.t = TM_User(name='t')
        self.t.save()

    def test_TM_is_tutor_default(self):
        t = TM_User(name="t")
        self.assertFalse(t.is_tutor)

    def test_TM_is_student_default(self):
        t = TM_User(name="t")
        self.assertFalse(t.is_student)

    def test_TM_is_active_default(self):
        t = TM_User(name="t")
        self.assertFalse(t.is_active)

    def test_TM_hourly_rate_default(self):
        t = TM_User(name="t")
        self.assertEqual(0, t.hourly_rate)

    def test_TM_adding_multiple_course(self):
        c1 = Course(department="APMA", course_number=3100, course_description="Probability")
        c1.save()
        c2 = Course(department="CS", course_number=3250, course_description="Software Testing")
        c2.save()
        self.t.courses.add(c1)
        self.t.courses.add(c2)
        self.assertEquals(2, len(self.t.courses.all()))

        
        

    # def test_example_failing(self):
    #     x = False
    #     self.assertTrue(x)

