"""gear_notifier URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('manager/',include('gn_manager.urls')),
    path('',user_views.login,name='login'),
    path('logout/',user_views.logout,name='logout'),
    path('register/',user_views.register, name='register'),
    path('profile/',login_required(user_views.profile),name='profile'),
    path('delete_account/',login_required(user_views.UserDeleteView.as_view()),name='delete_account'),
    path('activate/<uidb64>/<token>/<mode>/',user_views.activate, name='activate'),
    path('resend_verification/<mode>/',user_views.resend_verification,name='resend_verification'),
    path('change_password/',login_required(user_views.CustomPasswordChangeView.as_view()),name='change_password'),
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name="users/reset_password.html",
                                                                email_template_name='users/password_reset_email.html',
                                                                subject_template_name='users/password_reset_subject.txt'),name='reset_password'),
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),name='password_reset_confirm'),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),name='password_reset_complete')
]