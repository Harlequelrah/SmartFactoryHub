from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from auth_app.form import CustomUserCreationForm
from django.shortcuts import render , redirect
from django.contrib.auth import login , authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')    
    else:
        form = CustomUserCreationForm()
    return render(request, 'inscription.html', {'form': form})


def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username , password= password)
        if user is not None:
            login(request, user)
            return redirect('sensor:sensor_dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return  render(request, 'connexion.html')      
@login_required
def accueil(request):
    return render(request, 'accueil.html')

def deconnexion(request):
    logout(request)
    return redirect('connexion')