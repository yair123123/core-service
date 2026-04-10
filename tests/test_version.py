def test_version_without_app_version(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {
        "service_version": "1.0.0",
        "min_supported_app_version": "1.0.0",
        "latest_app_version": "1.0.0",
        "app_version": None,
        "must_update": None,
        "update_url": None,
        "update_message": "A newer app version is available.",
    }


def test_version_marks_update_required(client):
    response = client.get("/version", params={"app_version": "0.9.9"})
    assert response.status_code == 200
    assert response.json()["must_update"] is True


def test_version_marks_update_not_required(client):
    response = client.get("/version", params={"app_version": "1.0.0"})
    assert response.status_code == 200
    assert response.json()["must_update"] is False


def test_version_rejects_invalid_semver(client):
    response = client.get("/version", params={"app_version": "1.0.beta"})
    assert response.status_code == 400
    assert "numeric and dot-separated" in response.json()["detail"]
