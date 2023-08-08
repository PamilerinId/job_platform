from .  import client



def test_root():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    # assert response.json() == {"message": "The API is LIVE!!"}
