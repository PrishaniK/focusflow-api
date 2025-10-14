from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

class FocusFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass1234")
        response = self.client.post("/auth/jwt/create/", {"username": "testuser", "password": "pass1234"})
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_create_subject(self):
        res = self.client.post("/subjects/", {"name": "Math", "color": "#123456"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_session_stop_computes_minutes(self):
        subj = self.client.post("/subjects/", {"name": "Science", "color": "#FF0000"}).data
        topic = self.client.post("/topics/", {"subject": subj["id"], "title": "Photosynthesis"}).data
        task = self.client.post("/tasks/", {"topic": topic["id"], "title": "Review notes"}).data
        session = self.client.post("/sessions/", {"task": task["id"]}).data
        res = self.client.patch(f"/sessions/{session['id']}/stop/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("minutes", res.data)

