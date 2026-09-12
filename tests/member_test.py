# ============================================================
# GET MEMBER
# ============================================================

def test_get_member(
    client,
    member_token,
    test_member,
):
    memb_id = test_member["memb_id"]

    response = client.get(
        f"/members/find/{memb_id}",
        headers={
            "Authorization": f"Bearer {member_token}",
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["member"]["memb_id"] == memb_id


def test_get_member_not_found(
    client,
    member_token,
):
    response = client.get(
        "/members/find/999999",
        headers={
            "Authorization": f"Bearer {member_token}",
        },
    )

    assert response.status_code == 404


def test_get_member_requires_authentication(
    client,
):
    response = client.get("/members/find/1")

    assert response.status_code in (401, 422)


# ============================================================
# MEMBER SEARCH
# ============================================================

def test_search_members(
    client,
    librarian_token,
):
    response = client.get(
        "/members/lst?search=Test",
        headers={
            "Authorization": f"Bearer {librarian_token}",
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert "members" in body
    assert isinstance(body["members"], list)


def test_search_members_pagination(
    client,
    librarian_token,
):
    response = client.get(
        "/members/lst?search=Test&page=1&limit=10",
        headers={
            "Authorization": f"Bearer {librarian_token}",
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert "members" in body
    assert "total" in body
    assert isinstance(body["members"], list)
    assert isinstance(body["total"], int)


def test_search_members_requires_authentication(
    client,
):
    response = client.get(
        "/members/lst?search=Test",
    )

    assert response.status_code in (401, 422)