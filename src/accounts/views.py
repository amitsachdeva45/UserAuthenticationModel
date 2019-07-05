from django.shortcuts import render
from .forms import UserCreationForm, UserLoginForm, UserAndEmailLoginForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login, get_user_model, logout

User = get_user_model()
# Create your views here.
def home(request):
    data = "NOT LOGIN"
    if request.user.is_authenticated():
        data = request.user.profile.city
    context = {
        "data": data
    }
    return render(request,"base.html",context)
def register(request, *args, **kwargs):
    form = UserCreationForm(request.POST or None)
    context = {
        "form":form
    }
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/login")
    return render(request,"register.html",context)

def user_login(request, *args, **kwargs):
    form = UserLoginForm(request.POST or None)
    context = {
        "form": form,
        "text": "USER LOGIN"
    }
    if form.is_valid():
        print("USER LOGIN")
        username_a = form.cleaned_data.get('username')
        user_obj = User.objects.get(username__iexact = username_a)
        login(request,user_obj)
        return HttpResponseRedirect("/")
    return render(request, "login.html", context)

def user_email_login(request, *args, **kwargs):
    form = UserAndEmailLoginForm(request.POST or None)
    context = {
        "form": form,
        "text": "USER EMAIL LOGIN"
    }
    if form.is_valid():
        print("USER EMAIL LOGIN")
        user_obj = form.cleaned_data.get('user_obj')
        login(request,user_obj)
        return HttpResponseRedirect("/")
    return render(request, "login.html", context)

def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/log1")