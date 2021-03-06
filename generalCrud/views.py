from backendBulletJournal.settings import SECRET_KEY
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .helpers import GetBody
from django.core.serializers import serialize
import json
from .models import User
from .models import Task
from .models import Event
import datetime
from pytz import timezone
import jwt

today = datetime.datetime.today() - datetime.timedelta(hours=7)

# Auth Check
def authCheck (token):
    accessToken = token.split()[1]
    decoded = jwt.decode(accessToken, SECRET_KEY, algorithms="HS256")

def createNewTask(obj, timeInterval):
    return Task(
        name=obj.name,
        taskCycle=obj.taskCycle,
        dueDate=timeInterval.date(),
        userId=obj.userId,
        originalDate=obj.originalDate,
        isComplete=obj.isComplete
    )

# Create your views here.
class UserView(View):
    def get(self, request):
        email = request.GET.get('email', '')
        password = request.GET.get('password', '')
        user = User.objects.filter(email__exact=email)
        if user.exists():
            if user.values_list('password', flat=True)[0] == password:
                userId = user.values('pk')[0]['pk']
                encoded_jwt = jwt.encode({"userId": userId}, SECRET_KEY, algorithm="HS256")
                finalData = {"status": 200, "userId": userId, "token": encoded_jwt}
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
            encoded_jwt = jwt.encode({"userId": user.pk}, SECRET_KEY, algorithm="HS256")
            finalData = {"status": 200, "data": json.loads(serialize("json", [user])), "token": encoded_jwt}
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
        authCheck(request.headers["Authorization"])
        body = GetBody(request)
        task = Task.objects.create(name=body["name"], taskCycle=body["taskCycle"], dueDate=datetime.datetime.strptime(body["dueDate"], '%Y-%m-%d').date(), originalDate=datetime.datetime.strptime(body["dueDate"], '%Y-%m-%d').date(), userId=User.objects.get(id__exact=body["userId"]))
        finalData = json.loads(serialize("json", [task]))
        return JsonResponse(finalData, safe=False)

    def delete(self, request):
        authCheck(request.headers["Authorization"])
        id = request.GET.get('id', '')
        user = request.GET.get('user', '')
        task = Task.objects.get(id=id)
        task.delete()
        newTasks = Task.objects.filter(userId__exact=user)
        finalData = json.loads(serialize("json", newTasks))
        return JsonResponse(finalData, safe=False)

    def put(self, request):
        authCheck(request.headers["Authorization"])
        body = GetBody(request)
        id = request.GET.get('id', '')
        user = request.GET.get('user', '')
        Task.objects.filter(id=id).update(**body)
        newTasks = Task.objects.filter(userId__exact=user)
        finalData = json.loads(serialize("json", newTasks))
        return JsonResponse(finalData, safe=False)

class EventView(View):
    def post(self, request):
        authCheck(request.headers["Authorization"])
        body = GetBody(request)
        startDate = datetime.datetime.strptime(body["startDate"], '%Y-%m-%d %H:%M').date()
        endDate = datetime.datetime.strptime(body["endDate"], '%Y-%m-%d %H:%M').date()
        endTime = datetime.time(23,59,59)
        startTime = datetime.time(0,0,0)
        event = Event.objects.create(name=body["name"], startDate=datetime.datetime.strptime(body["startDate"], '%Y-%m-%d %H:%M'), endDate=datetime.datetime.strptime(body["endDate"], '%Y-%m-%d %H:%M'), userId=User.objects.get(id__exact=body["userId"]), dateClass="month")
        for i in range((endDate - startDate).days + 1):
            if i == 0:
                if (endDate-startDate).days == 0:
                    Event.objects.create(name=body["name"], startDate=datetime.datetime.strptime(body["startDate"], '%Y-%m-%d %H:%M'), endDate=datetime.datetime.strptime(body["endDate"], '%Y-%m-%d %H:%M'), userId=User.objects.get(id__exact=body["userId"]), dateClass="day", master=event)
                else:
                    endOfStartDate = datetime.datetime.combine(startDate, endTime)
                    Event.objects.create(name=body["name"], startDate=datetime.datetime.strptime(body["startDate"], '%Y-%m-%d %H:%M'), endDate=endOfStartDate, userId=User.objects.get(id__exact=body["userId"]), dateClass="day", master=event)
            elif i == (endDate-startDate).days:
                startOfEndDate = datetime.datetime.combine(endDate, startTime)
                Event.objects.create(name=body["name"], startDate=startOfEndDate, endDate=datetime.datetime.strptime(body["endDate"], '%Y-%m-%d %H:%M'), userId=User.objects.get(id__exact=body["userId"]), dateClass="day", master=event)
            else:
                day = startDate + datetime.timedelta(days=i)
                endOfStartDate = datetime.datetime.combine(day, endTime)
                startOfEndDate = datetime.datetime.combine(day, startTime)
                Event.objects.create(name=body["name"], startDate=startOfEndDate, endDate=endOfStartDate, userId=User.objects.get(id__exact=body["userId"]), dateClass="day", master=event)
        
        dayEvents = Event.objects.filter(master=event)
        finalEvent = json.loads(serialize("json", [event]))
        finalEvents = json.loads(serialize("json", dayEvents))
        finalData = {"monthEvent": finalEvent, "dayEvents": finalEvents}
        return JsonResponse(finalData, safe=False)

    def delete(self, request):
        authCheck(request.headers["Authorization"])
        id = request.GET.get('id', '')
        user = request.GET.get('user', '')
        event = Event.objects.get(id=id)
        event.delete()
        newEvents = Event.objects.filter(userId__exact=user)
        finalData = json.loads(serialize("json", newEvents))
        return JsonResponse(finalData, safe=False)

    def put(self, request):
        authCheck(request.headers["Authorization"])
        body = GetBody(request)
        id = request.GET.get('id', '')
        user = request.GET.get('user', '')
        Event.objects.filter(id=id).update(**body)
        newEvents = Event.objects.filter(userId__exact=user)
        finalData = json.loads(serialize("json", newEvents))
        print(finalData)
        return JsonResponse(finalData, safe=False)

class UserViewGet(View):
    def get(self, request, id):
        authCheck(request.headers["Authorization"])
        tasks = Task.objects.filter(userId__exact=id)
        events = Event.objects.filter(userId__exact=id)
        serialTasks = json.loads(serialize("json", tasks))
        serialEvents = json.loads(serialize("json", events))
        data = {"tasks": serialTasks, "events": serialEvents}
        return JsonResponse(data, safe=False)

class SchedulerView(View):
    def get(self, request):
        tomorrow = today + datetime.timedelta(days=1)
        tasks = Task.objects.filter(dueDate=today.strftime('%Y-%m-%d'), isComplete=False, taskCycle__day=True)
        
        newTasks = map(lambda n: createNewTask(n, timeInterval=tomorrow), tasks)
        createTasks = Task.objects.bulk_create(newTasks)
        serialTasks = json.loads(serialize("json", createTasks))
        response = {"status": 200, "tasks": serialTasks}
        return JsonResponse(response, safe=False)

class SchedulerWeekView(View):
    def get(self, request):
        startOfWeek = today - datetime.timedelta(days=today.weekday())
        endOfWeek = startOfWeek + datetime.timedelta(days=6)
        nextWeek = today + datetime.timedelta(days=7)
        tasks = Task.objects.filter(dueDate__gte=startOfWeek, dueDate__lte=endOfWeek, isComplete=False, taskCycle__week=True)
        
        newTasks = map(lambda n: createNewTask(n, timeInterval=nextWeek), tasks)
        createTasks = Task.objects.bulk_create(newTasks)
        serialTasks = json.loads(serialize("json", createTasks))
        response = {"status": 200, "tasks": serialTasks}
        return JsonResponse(response, safe=False)
