from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from Authentication import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.db.models import Q

from . models import Student
from django.db import connection

def home(request):
    return render(request, "App/index.html")

def SignUp(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm']

        if User.objects.filter(username=username):
            messages.warning(request, "Username already exists! Try some other username")
            return redirect('signup')

        if User.objects.filter(email=email):
            messages.warning(request, "Email already registered!")
            return redirect('signup')
        
        if len(username) > 10:
            messages.warning(request, "Username must be under 10 characters")
            return redirect('signup')

        if password != confirm_password:
            messages.warning(request, "Passwords didn't match")
            return redirect('signup')

        if not username.isalnum():
            messages.warning(request, "Username must be alphanumeric")
            return redirect('signup')

        my_user = User.objects.create_user(username, email, password)
        my_user.first_name = firstname
        my_user.last_name = lastname
        my_user.is_active = False

        my_user.save()

        messages.success(request, "Account created successfully, We've have sent you a confirmation email in order to activate your account")

        subject = "Welcome to the Homepage"
        message = "Hello" + my_user.first_name + "!! \n" + "Thank you for visiting our website \n We've also sent you a confirmation email address in order to activate your account. \n\n Thank you"
        from_email = settings.EMAIL_HOST_USER
        to_list = [my_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        current_site = get_current_site(request)
        email_subject = "Confirm your email - Django Login"
        message2 = render_to_string('email_confirmation.html', {
            'name': my_user.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(my_user.pk)),
            'token': generate_token.make_token(my_user)
        })

        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [my_user.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('signin')

    return render(request, "App/signup.html")

def SignIn(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            first_name = user.first_name
            messages.success(request, "Successfully Logged In")
            return render(request, "App/index.html", {'firstname': first_name})
        else:
            messages.warning(request, "Wrong Credentials")
            return redirect('signin')

    return render(request, "App/signin.html")

def SignOut(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')


def student_list(request):
    
    posts = Student.objects.filter(name__startswith = 'sha')
    print(posts)
    print(connection.queries)

    return render(request, 'App/output.html', {'posts': posts})
