from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from tournament.utils import indexContext

# Create your views here.
def signup(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserCreationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            newUser = form.save()
            messages.success(request, 'Account created successfully')
            newUser = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, newUser)
            return redirect("/")
    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'useraccounts/signup.html', context)

def logoutView(request):
    logout(request)
    return redirect("/")
    #return render(request, 'tournament/index.html', indexContext(request))