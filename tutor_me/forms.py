from django import forms

from .models import TM_User, Review, Time_Range

class EditProfileForm(forms.ModelForm):
    # first_name = forms.CharField(max_length=100,
    #                            required=True,
    #                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    # last_name = forms.CharField(max_length=100,
    #                              required=True,
    #                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    age = forms.IntegerField(required=True, 
                             max_value = 80, 
                             min_value = 16, 
                             widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = TM_User
        fields = ['email', 'age'] #'first_name', 'last_name',


class EditProfileForm_Tutor(forms.ModelForm):
    # first_name = forms.CharField(max_length=100,
    #                              required=True,
    #                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    # last_name = forms.CharField(max_length=100,
    #                             required=True,
    #                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    age = forms.IntegerField(required = True, 
                             max_value = 80, 
                             min_value = 16, 
                             widget=forms.NumberInput(attrs={'class': 'form-control'}))
    hourly_rate = forms.IntegerField(required=True,
                                     widget=forms.NumberInput(attrs={'class': 'form-control'}))
    class Meta:
        model = TM_User
        fields = ['email', 'age', 'hourly_rate'] #'first_name', 'last_name',  

class ReviewForm(forms.ModelForm):
    text = forms.CharField(max_length=250,
                                 required=True,
                                 widget=forms.Textarea(attrs={'class': 'form-control', 'maxlength': '250'}))
    class Meta:
        model = Review
        fields = ['text']

class AvailabilityForm(forms.ModelForm):
    start = forms.DateTimeField(label="Start", input_formats=['%m/%d/%Y %H:%M'], required=True) #input_formats=['%Y/%m/%d %H:%M']    widget=forms.DateTimeInput()
    end = forms.DateTimeField(label="End", input_formats=['%m/%d/%Y %H:%M'], required=True)

    class Meta:
        model = Time_Range
        fields = ['start', 'end']

#class BookingForm(forms.Form):
#    eventTitle = forms.CharField(label="event", max_length=255, required=True)
#    startDateTime = forms.DateTimeField(label="startDateTime", input_formats=['%Y/%m/%d %H:%M'], required=True)
#    endDateTime = forms.DateTimeField(label="endDateTime", input_formats=['%Y/%m/%d %H:%M'], required=True)