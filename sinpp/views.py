from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from schedule.views import index


@login_required
def user_profile(request):
    return render(request, 'registration/profile.html')


def register_account(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("form valid")
            user = form.save()
            return redirect(index)
    else:
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})
