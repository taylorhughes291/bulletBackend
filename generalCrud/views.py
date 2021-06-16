from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .helpers import GetBody
from django.core.serializers import serialize
import json
from .models import User
from .models import Task
from .models import Event
from datetime import datetime


# Create your views here.
class UserView(View):
    def get(self, request):
        email = request.GET.get('email', '')
        password = request.GET.get('password', '')
        user = User.objects.filter(email__exact=email)
        if user.exists():
            if user.values_list('password', flat=True)[0] == password:
                finalData = {"status": 200, "email": email}
            else:
                finalData = {"status": 403, "msg": "You have entered an incorrect password."} 
        else:
            finalData = {"status": 409, "msg": "This user does not exist."} 
        return JsonResponse(finalData, safe=False)
        
    def post(self, request):
        body = GetBody(request)
        email = body["email"]
        data = User.objects.filter(email__exact=email)
        if data.exists():
            finalData = {"status": 403, "msg": "This user already exists"}
        else:
            user = User.objects.create(name=body["name"], email=body["email"], phone=body["phone"], password=body["password"])
            finalData = json.loads(serialize("json", [user]))
        return JsonResponse(finalData, safe=False)
    
    def delete(self, request):
        id = request.GET.get('id', '')
        tasks = Task.objects.filter(userId__exact=id)
        print(tasks)
        events = Event.objects.filter(userId__exact=id)
        tasks.delete()
        events.delete()
        user = User.objects.get(id=id)
        print(user)
        user.delete()
        return JsonResponse({"status": 200, "msg": "user and tasks deleted"})

class TaskView(View):
    def post(self, request):
        body = GetBody(request)
        task = Task.objects.create(name=body["name"], taskCycle=body["taskCycle"], dueDate=datetime.strptime(body["dueDate"], '%Y-%m-%d').date(), userId=User.objects.get(email__exact=body["email"]))
        finalData = json.loads(serialize("json", [task]))
        return JsonResponse(finalData, safe=False)

    def delete(self, request):
        id = request.GET.get('id', '')
        task = Task.objects.get(id=id)
        task.delete()
        return JsonResponse({"status": 200, "msg": "task deleted"})

class EventView(View):
    def post(self, request):
        body = GetBody(request)
        print(datetime.strptime(body["startDate"], '%Y-%m-%d %H:%M'))
        event = Event.objects.create(name=body["name"], startDate=datetime.strptime(body["startDate"], '%Y-%m-%d %H:%M'), endDate=datetime.strptime(body["endDate"], '%Y-%m-%d %H:%M'), userId=User.objects.get(email__exact=body["email"]), isCalendarHeadline=body["isCalendarHeadline"])
        finalData = json.loads(serialize("json", [event]))
        return JsonResponse(finalData, safe=False)

    def delete(self, request, id):
        event = Event.objects.get(id=id)
        event.delete()
        return JsonResponse({"status": 200, "msg": "event deleted"})

class UserViewGet(View):
    def get(self, request):
        tasks = Task.objects.filter(userId__exact=id)
        events = Event.objects.filter(userId__exact=id)
        serialTasks = json.loads(serialize("json", tasks))
        serialEvents = json.loads(serialize("json", events))
        data = {"tasks": serialTasks, "events": serialEvents}
        return JsonResponse(data, safe=False)
