from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (register_user, login_user, list_projects, create_project, get_project, update_project,
                    delete_project, list_tasks, create_task, get_task, update_task_status, delete_task)

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('projects/', list_projects, name='list_projects'),
    path('projects/create/', create_project, name='create_project'),
    path('get_project/', get_project, name='get_project'),
    path('projects/update/', update_project, name='update_project'),
    path('projects/delete/', delete_project, name='delete_project'),
    path('tasks/', list_tasks, name='list_tasks'),
    path('tasks/create/', create_task, name='create_task'),
    path('get_task/', get_task, name='get_task'),
    path('tasks/update-status/', update_task_status, name='update_task_status'),
    path('tasks/delete/', delete_task, name='delete_task'),

]
