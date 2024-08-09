from django import forms
from .models import AdvUser
class ChangeUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Email')
    postal_code = forms.CharField(required=True, label='Postal code')
    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'postal_code', 'send_messages')

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .apps import user_registered
class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Email')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Password (again)', widget=forms.PasswordInput, help_text='Input same password for validation')
    
    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1
    
    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1!=password2:
            error = {'password2': ValidationError('Passwords do not match', code='password_mismatch')}
            raise ValidationError(error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registered.send(RegisterUserForm, instance=user)
        return user
    
    class Meta:
        model = AdvUser
        fields = {'username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'send_messages', 'postal_code'}


#Categories
from .models import SuperCategory, SubCategory
class SubCategoryForm(forms.ModelForm):
    supercategory = forms.ModelChoiceField(queryset=SuperCategory.objects.all(), empty_label=None, label='Category', required=True)
    class Meta:
        model = SubCategory
        fields = '__all__'

#Ads
class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=100, label='Keyword')

from django.forms import inlineformset_factory
from .models import Ad, AdditionalImage
class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}
AIFormSet = inlineformset_factory(Ad, AdditionalImage, fields='__all__', extra=3)

#Conversion
from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter your message here...'
            }),
        }
