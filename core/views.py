from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic
from .forms import RoomForm

# Create your views here.
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exit')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('core:home')
        else:
            messages.error(request, 'Username OR password does not exit')
        
    return render(request, 'core/login_register.html')

def logoutUser(request):
    logout(request)
    return redirect('core:login')


def home(request):
    q= request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))

    topics = Topic.objects.all()

    room_count = rooms.count()

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}

    return render(request, 'core/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)

    context = {'room': room}   

    return render(request, 'core/room.html', context)

@login_required(login_url='core:login')
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:home')
        
    context={'form': form}

    return render(request, 'core/room_form.html', context)

@login_required(login_url='core:login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)

    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('core:home')
        
    context={'form': form}

    return render(request, 'core/room_form.html', context)

@login_required(login_url='core:login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.method == 'POST':
        room.delete()
        return redirect('core:home')
    
    context={'room': room}

    return render(request, 'core/delete.html', context)