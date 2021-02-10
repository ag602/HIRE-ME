from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import *
from django.forms import ClearableFileInput

class SignUpFormone(forms.ModelForm):
    email = forms.RegexField(label=_("Email"), max_length=30, regex=r'^[\w.@+-]+$',
                                help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
                                )
    class Meta:
        model = User
        fields = ('email',)

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    # account_type = forms.CharField(max_length=30, choices=account_type_choices, null=True, default='employer')
    # is_employee = forms.RadioSelect()
    # email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    # username = forms.RegexField(label=_("Email"), max_length=30, regex=r'^[\w.@+-]+$',
    #                             help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
    #                             error_messages={'invalid': _(
    #                                 "This value may contain only letters, numbers and @/./+/-/_ characters.")})

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password1', 'password2','role')
        # labels = {
        #     'username': _('Set Username'),
        # }
        error_messages = {
            'password_mismatch': _("Error : The two password fields didn't match."),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    skills = forms.CharField(required=False, widget=forms.TextInput
                           (attrs={'data-role': 'tagsinput', 'id': 'skills', 'max-tags': 10}))
    pic = forms.FileField(required=False, widget=forms.FileInput
                           (attrs={"class": "file-upload"}))
    class Meta:
        model = Profile
        fields = ('user', 'skills', 'tagline', 'intro', 'pic')


# For multi file upload refer - https://stackoverflow.com/questions/38257231/how-can-i-upload-multiple-files-to-a-model-field
class ProfileFile(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']
        widgets = {
            'file': ClearableFileInput(attrs={'multiple': True}),
        }
        # widget is important to upload multiple files

class Postjob(forms.ModelForm):
    # file_two = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    is_approved = forms.BooleanField(required=False)
    class Meta:
        model = Post
        fields = ['user', 'title', 'type', 'category', 'location', 'min_salary', 'max_salary', 'tags', 'description',
                  'file_one', 'company','deadline', 'is_approved']

class Applyjob(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ('user', 'email', 'job' , 'applied_at', 'cv')

class Contactform(forms.ModelForm):
    # file_two = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    class Meta:
        model = Contact
        fields = ['name','email','subject','message']




# Customizing default paypal button to html based button
from paypal.standard.forms import PayPalPaymentsForm
from django.utils.html import format_html
class ExtPayPalPaymentsForm(PayPalPaymentsForm):
    def render(self):
        form_open  = u'''<form action="%s" id="PayPalForm" method="post">''' % (self.get_endpoint())
        form_close = u'</form>'
        # format html as you need
        submit_elm = u'''<input type="submit"  class="button big ripple-effect margin-top-20 margin-bottom-65" value="Pay Now">'''
        return format_html(form_open+self.as_p()+submit_elm+form_close)

