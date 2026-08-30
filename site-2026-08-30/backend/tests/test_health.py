from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "degraded",
        "service": "AI Intelligence Hub API",
        "version": "0.1.0",
        "environment": "testing",
        "database": "not_configured",
    }


def test_liveness(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_requires_database(client: TestClient) -> None:
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "unhealthy"


def test_request_id_is_returned(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")
    assert response.headers["X-Request-ID"]
