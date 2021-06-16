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

class TaskView(View):
    def get(self, request):
        user = request.GET.get("user", "")
        tasks = Task.objects.filter(userId__exact=user)
        finalData = json.loads(serialize("json", tasks))
        return JsonResponse(finalData, safe=False)
        
    def post(self, request):
        body = GetBody(request)
        task = Task.objects.create(name=body["name"], taskCycle=body["taskCycle"], dueDate=datetime.strptime(body["dueDate"], '%Y-%m-%d').date(), userId=User.objects.get(email__exact=body["email"]))
        finalData = json.loads(serialize("json", [task]))
        return JsonResponse(finalData, safe=False)

    def put(self, request, param):
        query = request.GET.get("query", "no query")
        return JsonResponse({"param": param, "query": query})

    def delete(self, request, param):
        query = request.GET.get("query", "no query")
        return JsonResponse({"param": param, "query": query})

class EventView(View):
    def post(self, request):
        body = GetBody(request)
        print(datetime.strptime(body["startDate"], '%Y-%m-%d %H:%M'))
        event = Event.objects.create(name=body["name"], startDate=datetime.strptime(body["startDate"], '%Y-%m-%d %H:%M'), endDate=datetime.strptime(body["endDate"], '%Y-%m-%d %H:%M'), userId=User.objects.get(email__exact=body["email"]), isCalendarHeadline=body["isCalendarHeadline"])
        finalData = json.loads(serialize("json", [event]))
        return JsonResponse(finalData, safe=False)