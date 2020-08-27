from django.contrib import messages
from django.template.loader import render_to_string
from .models import Token
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from django.utils.encoding import force_bytes

def send_verification(user,send_to,mode,current_site):
    success = False
    subject = 'Gear Notifier - Activate your '
    if mode == 'P':
        subject += 'phone.'
        carrier_domains = {'AT&T':'mms.att.net','Verizon':'vzwpix.com','Sprint':'pm.sprint.com','T-Mobile':'tmomail.net'}
        send_to = send_to + '@' + carrier_domains[user.carrier]
    else:
        subject += 'account.'
    try:
        new_token = Token(user=user,token_type=mode)
        new_token.save()
        message = render_to_string('users/verify.html', {
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': new_token.token,
                    'mode':mode
                })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [send_to])
        success = True
    except Exception:
        pass
    return success
        
def activation_warnings(user,request):
    if not user.is_active:
        messages.warning(request,"Your email has not been verified - your queries will not be scanned until it is verified. <button class='btn btn-primary' id='E' onclick='clickResendActivation(this.id)'>Resend Email Verification</button>",extra_tags='safe')
    if user.phone and not user.active_phone:
        messages.warning(request,"Your phone number has not been verified - you may not receive any text notifications until it is verified. <button class='btn btn-primary' id='P' onclick='clickResendActivation(this.id)'>Resend Phone Verification</button>",extra_tags='safe')