from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.
def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('core:home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
        
    return render(request, 'core/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('core:login')

def registerPage(request):
    page = 'register'

    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('core:home')
        else:
            messages.error(request, 'An error has occured during registration')

    context = {'page': page, 'form': form}
    return render(request, 'core/login_register.html', context)


def home(request):
    q= request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))

    topics = Topic.objects.all()[0:5]

    room_count = rooms.count()

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:5]

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}

    return render(request, 'core/home.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'core/profile.html', context)

def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('core:user-profile', pk=user.id)

    return render(request, 'core/update-user.html', {'form': form})

def room(request, pk):
    room = Room.objects.get(id=pk)

    room_messages = room.message_set.all().order_by('-created')

    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(user=request.user, room=room, body=request.POST.get('body'))
        room.participants.add(request.user)
        return redirect('core:room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}   

    return render(request, 'core/room.html', context)

@login_required(login_url='core:login')
def createRoom(request):
    form = RoomForm()

    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('core:home')
        
    context={'form': form, 'topics': topics}

    return render(request, 'core/room_form.html', context)

@login_required(login_url='core:login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)

    form = RoomForm(instance=room)

    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}

    return render(request, 'core/room_form.html', context)

@login_required(login_url='core:login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.method == 'POST':
        room.delete()
        return redirect('core:home')

    return render(request, 'core/delete.html', {'obj': room})

@login_required(login_url='core:login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    # if user not the owner of the message = ALERT
    if request.user != message.user:
        return HttpResponse('You are not allowed here!')

    # step 2 - delete the message and redirect to the room
    if request.method == 'POST':
        message.delete()
        return redirect('core:room', pk=message.room.id)
    
    # step 1 - approve deleting of the message
    return render(request, 'core/delete.html' , {'obj': message})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'core/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'core/activity.html', {'room_messages': room_messages})