from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import send_mail
from payInt.models import PayrollCenterUsers, PayrollItemsMatched, EmployeesMatched


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Gets the user information from the form and saves the user
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Creates the payroll table for the user
            pint = PayrollCenterUsers(owner=user)
            pint.save()

            for i in settings.PAYROLL_OPTIONS:
                pitem = PayrollItemsMatched(owner=pint, tc_item=i)
                pitem.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate TimeClick payroll integration account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            send_mail(
                mail_subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [to_email],
                fail_silently=False,
            )
            return render(request, 'account_created.html')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('%s?next=%s' % (settings.LOGIN_REDIRECT_URL, request.path))
        return redirect('/upload')
    else:
        return HttpResponse('Activation link is invalid!')
