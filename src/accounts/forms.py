from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db.models import Q
User = get_user_model()
from .models import USERNAME_REGEX

class UserAndEmailLoginForm(forms.Form):
    query = forms.CharField(label='Username/Email', max_length=120)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        query1 = self.cleaned_data.get('query')
        password_a = self.cleaned_data.get('password')
        # Hitting the database twice so we use query loookups
        # user_obj1 = User.objects.filter(email__iexact = query1)
        # user_obj2 = User.objects.filter(username__iexact = query1)
        # user_obj_final = (user_obj1 | user_obj2).distinct()
        user_obj_final = User.objects.filter(
            Q(username__iexact = query1)|
            Q(email__iexact = query1)
        ).distinct()
        if not user_obj_final.exists() and not user_obj_final.count() != 1:
            raise forms.ValidationError("Invalid Credentials")
        user_obj = user_obj_final.first()
        if not user_obj.check_password(password_a):
            # log auth series
            raise forms.ValidationError("Invalid Credentials")
        if not user_obj.is_active:
            raise forms.ValidationError("Inactive User. Please confirm email address")
        self.cleaned_data["user_obj"] = user_obj
        return super(UserAndEmailLoginForm,self).clean(*args,**kwargs)

class UserLoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=120,
                                validators=[
                                    RegexValidator(
                                        regex=USERNAME_REGEX,
                                        message="Username must be alphanumeric or contains:'. + -'",
                                        code='invalid_username'
                                    )]
                                )
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username_a = self.cleaned_data.get('username')
        password_a = self.cleaned_data.get('password')
        user_obj = User.objects.filter(username = username_a).first()
        if not user_obj:
            raise forms.ValidationError("Invalid Credentials")
        else:
            if not user_obj.check_password(password_a):
                raise forms.ValidationError("Invalid Credentials")
            if not user_obj.is_active:
                raise forms.ValidationError("Inactive User. Please confirm email address")
        return super(UserLoginForm,self).clean(*args,**kwargs)

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username','email','zipcode')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username','email', 'password', 'is_staff', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]