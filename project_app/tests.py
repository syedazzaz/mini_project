from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Project, Task

User = get_user_model()


class ProjectTaskAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create an admin user
        self.admin_user = User.objects.create_user(
            email="admin@example.com", username="admin", password="adminpass", role="admin"
        )

        # Create a member user
        self.member_user = User.objects.create_user(
            email="member@example.com", username="member", password="memberpass", role="member"
        )

        # Authenticate admin for testing admin APIs
        self.client.login(email="admin@example.com", password="adminpass")

        # Create a project using admin user
        self.project = Project.objects.create(title="Test Project", description="Test Description", user=self.admin_user)

        # Create a task under the project
        self.task = Task.objects.create(title="Test Task", description="Task Desc", status="To Do", project=self.project)

    def test_admin_can_create_project(self):
        """Ensure that only admins can create a project"""
        data = {"title": "New Project", "description": "Project description"}
        response = self.client.post("/api/projects/create/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_member_cannot_create_project(self):
        """Ensure that members cannot create projects"""
        self.client.logout()
        self.client.login(email="member@example.com", password="memberpass")

        data = {"title": "Member Project", "description": "Should fail"}
        response = self.client.post("/api/projects/create/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_get_projects(self):
        """Ensure authenticated users can list all projects"""
        response = self.client.get("/api/projects/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json()) > 0)

    def test_member_can_update_task_status(self):
        """Ensure that members can update task status"""
        self.client.logout()
        self.client.login(email="member@example.com", password="memberpass")

        data = {"task_id": self.task.id, "new_status": "In Progress"}
        response = self.client.patch("/api/tasks/update_status/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_delete_task(self):
        """Ensure that admins can delete tasks"""
        response = self.client.delete(f"/api/tasks/delete/?task_id={self.task.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
