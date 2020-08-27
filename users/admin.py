from django.contrib import admin
from django.contrib.auth import get_user_model
from .forms import UserAdminChangeForm, NewUserForm
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Token

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = NewUserForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email','craigslist_sites','phone','carrier','communication_settings','is_active','is_staff','is_superuser','active_phone')
    list_filter = ('is_active','is_staff','is_superuser',)
    fieldsets = (
        (None, {'fields': ('email', 'password','craigslist_sites','phone','carrier','communication_settings')}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser','active_phone')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2','craigslist_sites','phone','carrier','communication_settings')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.register(Token)
admin.site.unregister(Group)