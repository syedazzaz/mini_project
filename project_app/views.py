import pdb

from django.contrib.auth import get_user_model, authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json
from .models import User, Project, Task


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'member')

        if not email or not username or not password:
            return Response({'error': 'Email, username, and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(email=email, username=username, password=password, role=role)
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        import pdb; pdb.set_trace()
        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'email': user.email,
                'username': user.username,
                'role': user.role,
            }
        }, status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)


def is_admin(user):
    return user.role == 'admin'

# Create Project (Admins Only)
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    try:
        if not is_admin(request.user):
            return Response({'error': 'Only admins can create projects'}, status=status.HTTP_403_FORBIDDEN)

        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')

        if not title or not description:
            return Response({'error': 'Title and description are required'}, status=status.HTTP_400_BAD_REQUEST)

        project = Project.objects.create(title=title, description=description, user=request.user)

        return Response({'message': 'Project created successfully', 'project_id': project.id}, status=status.HTTP_201_CREATED)

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)


# Get All Projects (Authenticated Users)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_projects(request):
    projects = Project.objects.all().values('id', 'title', 'description', 'user__username')
    return Response(list(projects), status=status.HTTP_200_OK)


# Get Single Project
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project(request):
    project_id = request.GET.get("project_id")  # Get project_id from query params

    if not project_id:
        return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        project = Project.objects.get(id=project_id)
        return Response({
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'user': project.user.username
        }, status=status.HTTP_200_OK)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)



# Update Project (Admins Only)
@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_project(request):
    try:
        project_id = request.data.get("project_id")
        title = request.data.get("project_id", None)
        description = request.data.get("project_id", None)
        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        project = Project.objects.get(id=project_id)

        if not is_admin(request.user) or project.user != request.user:
            return Response({'error': 'Only the project creator (Admin) can update this project'}, status=status.HTTP_403_FORBIDDEN)
        if title:
            project.title = title
        if description:
            project.description = description
        project.save()

        return Response({'message': 'Project updated successfully'}, status=status.HTTP_200_OK)

    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)


# Delete Project (Admins Only)
@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_project(request):
    try:
        project_id = request.data.get("project_id")
        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        project = Project.objects.get(id=project_id)

        if not is_admin(request.user) or project.user != request.user:
            return Response({'error': 'Only the project creator (Admin) can delete this project'}, status=status.HTTP_403_FORBIDDEN)

        project.delete()
        return Response({'message': 'Project deleted successfully'}, status=status.HTTP_200_OK)

    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    try:
        if not is_admin(request.user):
            return Response({'error': 'Only admins can create tasks'}, status=status.HTTP_403_FORBIDDEN)

        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')
        project_id = data.get('project_id')

        if not title or not description or not project_id:
            return Response({'error': 'Title, description, and project_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        task = Task.objects.create(title=title, description=description, project=project)

        return Response({'message': 'Task created successfully', 'task_id': task.id}, status=status.HTTP_201_CREATED)

    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)


# Get All Tasks
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_tasks(request):
    tasks = Task.objects.all().values('id', 'title', 'description', 'status', 'project__title')
    return Response(list(tasks), status=status.HTTP_200_OK)


# Get Single Task
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_task(request):
    try:
        task_id = request.GET.get("task_id")
        if not task_id:
            return Response({'error': 'Task ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        task = Task.objects.get(id=task_id)
        return Response({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'project': task.project.title
        }, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


# Update Task Status (Members Only)
@csrf_exempt
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_task_status(request):
    try:
        task_id = request.GET.get("task_id")
        new_status = request.GET.get("new_status")

        task = Task.objects.get(id=task_id)

        if not request.user.role == 'member':
            return Response({'error': 'Only members can update task statuses'}, status=status.HTTP_403_FORBIDDEN)

        if new_status not in ['To Do', 'In Progress', 'Completed']:
            return Response({'error': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)

        if new_status:
            task.status = new_status
        task.save()

        return Response({'message': 'Task status updated successfully'}, status=status.HTTP_200_OK)

    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)


# Delete Task (Admins Only)
@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request):
    try:
        task_id = request.GET.get("task_id")
        if not task_id:
            return Response({'error': 'Task ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        task = Task.objects.get(id=task_id)

        if not is_admin(request.user):
            return Response({'error': 'Only admins can delete tasks'}, status=status.HTTP_403_FORBIDDEN)

        task.delete()
        return Response({'message': 'Task deleted successfully'}, status=status.HTTP_200_OK)

    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)