from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.encoding import force_bytes,  force_str
from django.template.loader import render_to_string
from account.forms import RegistrationForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from email.mime.image import MIMEImage
from django.http import HttpResponse
from django.conf import settings
import os

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            domain = request.get_host()

            send_email_activation(user, domain, uid, token)

            # send activation email
            subject = 'Activate Your Student Portal Account'
            html_content = render_to_string('account/activate_account.html', {
                'user': user,
                'uid': uid,
                'token': token,
                'domain': domain,
            })
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject,
                text_content,
                "Student Services Portal <juvenpinoy@gmail.com>",
                [user.email],
            )

            email.attach_alternative(html_content, "text/html")
            email.send()

            role_msg = user.role

            messages.success(request, "Account created successfully, please check your email to activate your account.")
            return redirect('login')
    else:
        form = RegistrationForm()

    return render(request, 'account/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, "Account has been successfully activated! You are now able to log in.")
        else:
            messages.error(request, "Your account is already active. Please log in again.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid. Please check your email and try again.")
        return redirect('login')

def send_email_activation(user, domain, uid, token):
    subject = 'Activate Your Student Portal Account'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    html_content = render_to_string('account/activate_account.html', {
        "user": user,
        "domain": domain,
        "uid": uid,
        "token": token,
    })

    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(subject, text_content, from_email, to)
    email.attach_alternative(html_content, "text/html")

    logo_path = os.path.join(settings.MEDIA_ROOT, "img", "student_logo.png")

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<student_logo>')
            logo.add_header('Content-Disposition', 'inline', filename="student_logo.png")
            email.attach(logo)

    email.send()

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.success(request, "If the email exists, a reset link has been sent.")
            return redirect("forgot_password")

        domain = request.get_host()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        send_email_password_reset(user, domain, uid, token)

        messages.success(request, "Password reset email has been sent successfully.")
        return redirect("login")

    return render(request, "account/forgot_password.html")

def send_email_password_reset(user, domain, uid, token):
    subject = 'Reset Your SSP Password'
    from_email = settings.DEFAULT_FROM_EMAIL

    html_content = render_to_string("account/password_reset_email.html", {
        "user": user,
        "domain": domain,
        "uid": uid,
        "token": token,
    })

    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        [user.email],
    )

    email.attach_alternative(html_content, "text/html")

    logo_path = os.path.join(settings.MEDIA_ROOT, "img", "student_logo.png")

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<student_logo>')
            logo.add_header('Content-Disposition', 'inline', filename="student_logo.png")
            email.attach(logo)
    email.send()

def password_reset(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):

        if request.method == "POST":
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, "Password has been reset successfully. You can now login.")
                return redirect("login")
            else:
                messages.error(request, "Passwords do not match. Please try again.")

        return render(request, "account/password_reset.html")

    else:
        return HttpResponse("Reset link is invalid or expired.")

@login_required
def dashboard(request):
    user = request.user

    if user.role == "admin":
        return render(request, "admin_dashboard.html")


    elif user.role == "staff":
        return redirect("staff_dashboard")

    elif user.role == "student":
        return redirect('student_dashboard')

    else:
        messages.error(request, "Invalid role or not registered account.")
        return redirect("login")


def logout_view(request):
    logout(request)
    messages.info(request, "You have logout successfully")
    return redirect('login')
