def test_login_rate_limit(client):
    for _ in range(5):
        client.post(
            "/auth/login",
            json={"identifier": "x@x.com", "password": "wrong"},
        )

    response = client.post(
        "/auth/login",
        json={"identifier": "x@x.com", "password": "wrong"},
    )

    assert response.status_code == 429


def test_rate_limit_is_per_endpoint(client):
    for _ in range(5):
        client.post(
            "/auth/login",
            json={"identifier": "x@x.com", "password": "wrong"},
        )

    # A different endpoint must still work
    response = client.get(
        "/books/",
        headers={"Authorization": "Bearer dummy"},
    )

    # Should be 401 (bad token), not 429
    assert response.status_code in (401, 422)
