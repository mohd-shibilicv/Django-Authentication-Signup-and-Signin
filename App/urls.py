from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('student', views.student_list, name="student"),
    path('signup', views.SignUp, name="signup"),
    path('signin', views.SignIn, name="signin"),
    path('signout/', views.SignOut, name="signout"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
]