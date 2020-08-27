from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import ReadOnlyPasswordHashField

User = get_user_model()

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email','craigslist_sites','phone','carrier','communication_settings')
        widgets = {
            'craigslist_sites': forms.SelectMultiple()
        }

    def clean_phone(self):
        return self.cleaned_data.get("phone") or None

    def clean_carrier(self):
        phone = self.cleaned_data.get("phone")
        carrier = self.cleaned_data.get("carrier")
        if not phone and carrier:
            raise forms.ValidationError("The Carrier field requires a corresponding phone number unless both fields are left empty.")
        elif phone and not carrier:
            raise forms.ValidationError("If Phone is filled out, Carrier must be as well.")
        return carrier

    def clean_communication_settings(self):
        communication_settings = self.cleaned_data.get("communication_settings")
        phone = self.cleaned_data.get("phone")
        if communication_settings != "E" and not phone:
            raise forms.ValidationError("You must add a phone number in order to receive texts.")
        return communication_settings
    
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserForm, self).save(commit=False)
        if commit:
            user.save()
        return user

class NewUserForm(UserForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput,
                                help_text="""<ul>
                                                <li>Your password can’t be too similar to your other personal information.</li>
                                                <li>Your password must contain at least 8 characters.</li>
                                                <li>Your password can’t be a commonly used password.</li>
                                                <li>Your password can’t be entirely numeric.</li>
                                             <ul>""")
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email','password1','password2','craigslist_sites','phone','carrier','communication_settings')
        widgets = {
            'craigslist_sites': forms.SelectMultiple(attrs={'size': 10})
        }

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        try:
            validate_password(password1, self.instance)
        except forms.ValidationError as error:
            self.add_error('password1', error)
        return password1

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(NewUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserAdminChangeForm(UserForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email','password','craigslist_sites','phone','carrier','communication_settings','is_active','is_staff','is_superuser','active_phone')
        widgets = {
            'craigslist_sites': forms.SelectMultiple(attrs={'size': 10})
        }

    def clean_active_phone(self):
        phone = self.cleaned_data.get("phone")
        active_phone = self.cleaned_data.get("active_phone")
        carrier = self.cleaned_data.get("carrier")
        if (not phone or not carrier) and active_phone:
            raise forms.ValidationError("This field cannot be checked without all phone data provided.")
        return active_phone

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]