from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import NewUserForm, UserForm
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from .models import Token
from datetime import datetime
from django.urls import reverse_lazy
from .utils import activation_warnings, send_verification
from django.http import JsonResponse
from bootstrap_modal_forms.generic import BSModalDeleteView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
import pytz

class CustomPasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('profile')

    def form_valid(self,form):
        messages.success(self.request,'Your password has been updated.')
        return super().form_valid(form)

class UserDeleteView(BSModalDeleteView):
    model = get_user_model
    template_name = 'users/delete_account.html'
    success_message = 'Your account has been deleted.'
    success_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        auth_logout(self.request)
        return super().form_valid(form)

@login_required
def profile(request):
    user = request.user
    activation_warnings(user,request)
    if request.method == 'POST':
        form = UserForm(request.POST,instance=request.user)
        if form.is_valid():
            user = form.save()
            msg = "Account has been updated."
            current_site = get_current_site(request)
            changed_fields = form.changed_data
            if 'email' in changed_fields:
                user.is_active = False
                user.save()
                msg += " Because you've changed your email, you must re-verify your account (you have been sent a verification email)."
                send_to = user.email
                send_verification(user,send_to,'E',current_site)
            if 'phone' in changed_fields:
                user.active_phone = False
                user.save()
                if user.phone is not None:
                    msg += " Because you've changed your phone number, you must re-verify your phone (you have been sent a verification text)."
                    send_to = user.phone
                    send_verification(user,send_to,'P',current_site)
            messages.success(request,msg)
    else:
        form = UserForm(instance=request.user)
    return render(request, 'users/profile.html',{'title':"Profile",'form':form})

@login_required
def resend_verification(request,mode):
    user = request.user
    response = {}
    if (mode == 'E' and not user.is_active) or (mode == 'P' and not user.active_phone):
        send_to = user.email if mode == 'E' else user.phone
        Token.objects.filter(user=user,token_type=mode).delete() # delete any of the user's existing tokens of the same type (phone, email)
        verify = send_verification(user,send_to,mode,get_current_site(request))
        if verify:
            code = 200
            msg = "verification resent"
        else:
            code = 500
            msg = "error on backend"
    else:
        code = 400
        msg = "bad request"
    response['status'] = 'ok' if code == 200 else 'error'
    response['message'] = msg
    return JsonResponse(response,status=code)

@login_required
def logout(request):
    auth_logout(request)
    return redirect('login')

def login(request):
    if request.user.is_authenticated:
        return redirect('manager')
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request,username=email,password=password)
        if user is not None:
            auth_login(request,user)
            nxt = request.POST.get('next')
            if nxt: 
                return redirect(nxt)
            else:
                return redirect('manager')
        else:
            messages.error(request,'Invalid email/password combination.')
    return render(request,'users/login.html',{'title':'Login'})

def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = user.email
            phone = user.phone
            current_site = get_current_site(request)
            send_verification(user,email,'E',current_site)
            msg = 'Account successfully created - check your email to verify your account'
            if phone:
                msg += ", and check your texts to verify your phone number"
                send_verification(user,phone,'P',current_site)
            msg += ". You may log in, but your entries may not be scanned until you are verified."
            messages.success(request,msg)
            return redirect('login')
    else:
        form = NewUserForm
    return render(request, 'users/register.html',{'title':"Register",'form':form})

def activate(request,uidb64,token,mode):
    if uidb64 is not None and token is not None and mode in ['P','E']:
        try:
            uid = urlsafe_base64_decode(uidb64)
            user_model = get_user_model()
            user = user_model.objects.get(pk=uid)
            if mode == 'E' and user.is_active:
                messages.info(request,"Your account is already activated.")
            elif mode == 'P' and user.active_phone:
                messages.info(request,"Your phone number is already activated.")
            else:
                token = Token.objects.filter(user=user,token=token,token_type=mode).order_by('-pk').first()
                if token is not None:
                    now = datetime.now().replace(tzinfo=pytz.timezone("America/Kentucky/Louisville"))
                    if now < token.expires_at:
                        if mode == 'E':
                            user.is_active = True
                            messages.success(request,"Your account has been activated.")
                        elif mode == 'P':
                            user.active_phone = True
                            messages.success(request,"Your phone number has been activated.")
                        user.save()
                        token.delete()
                    else:
                        messages.error('Your activation token has been expired. Log in and visit your profile page to generate a new one.')
                else:
                    messages.error('Token does not exist.')
        except:
            messages.error(request,"An error occurred during activation.")
    else:
        messages.error(request,"Activation failed.")
    return redirect('login')