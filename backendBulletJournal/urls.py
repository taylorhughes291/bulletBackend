"""backendBulletJournal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from generalCrud.views import UserView, TaskView, EventView, UserViewGet, SchedulerView, SchedulerWeekView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', UserView.as_view()),
    path('task/', TaskView.as_view()),
    path('event/', EventView.as_view()),
    path('user/<id>/', UserViewGet.as_view()),
    path('scheduler/day/', SchedulerView.as_view()),
    path('scheduler/week/', SchedulerWeekView.as_view()),
]
