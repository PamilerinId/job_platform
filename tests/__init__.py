from fastapi.testclient import TestClient
from core.settings import app

client = TestClient(app)