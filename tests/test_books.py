import io


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# CREATE
# ============================================================

def test_create_book_success(
    client,
    librarian_token,
):
    response = client.post(
        "/books/",
        data={
            "title": "The Hobbit",
            "isbn": "9780000001",
            "publication_year": "1937",
            "genre": "Fantasy",
        },
        headers=_auth(librarian_token),
    )

    assert response.status_code == 201


def test_create_book_without_title(
    client,
    librarian_token,
):
    response = client.post(
        "/books/",
        data={
            "isbn": "9780000001",
            "publication_year": "1937",
            "genre": "Fantasy",
        },
        headers=_auth(librarian_token),
    )

    assert response.status_code == 400


def test_create_book_member_forbidden(
    client,
    member_token,
):
    response = client.post(
        "/books/",
        data={
            "title": "The Hobbit",
            "isbn": "9780000001",
        },
        headers=_auth(member_token),
    )

    assert response.status_code in (401, 403)


def test_create_book_without_authentication(client):
    response = client.post(
        "/books/",
        data={
            "title": "The Hobbit",
        },
    )

    assert response.status_code in (401, 422)


# ============================================================
# LIST
# ============================================================

def test_list_books_success(
    client,
    member_token,
):
    response = client.get(
        "/books/",
        headers=_auth(member_token),
    )

    assert response.status_code == 200
    assert isinstance(response.get_json(), dict)


def test_list_books_without_authentication(client):
    response = client.get("/books/")

    assert response.status_code in (401, 422)


# ============================================================
# GET ONE
# ============================================================

def test_get_book_success(
    client,
    member_token,
    test_book,
):
    response = client.get(
        f"/books/{test_book['book_id']}",
        headers=_auth(member_token),
    )

    assert response.status_code == 200


def test_get_book_not_found(
    client,
    member_token,
):
    response = client.get(
        "/books/999999",
        headers=_auth(member_token),
    )

    assert response.status_code == 404


def test_get_book_without_authentication(
    client,
    test_book,
):
    response = client.get(
        f"/books/{test_book['book_id']}"
    )

    assert response.status_code in (401, 422)


# ============================================================
# UPDATE
# ============================================================

def test_update_book_success(
    client,
    librarian_token,
    test_book,
):
    response = client.patch(
        f"/books/{test_book['book_id']}",
        data={
            "title": "Updated Book",
        },
        headers=_auth(librarian_token),
    )

    assert response.status_code == 200


def test_update_book_empty_title(
    client,
    librarian_token,
    test_book,
):
    response = client.patch(
        f"/books/{test_book['book_id']}",
        data={
            "title": "",
        },
        headers=_auth(librarian_token),
    )

    assert response.status_code == 400


def test_update_book_member_forbidden(
    client,
    member_token,
    test_book,
):
    response = client.patch(
        f"/books/{test_book['book_id']}",
        data={
            "title": "Unauthorized Update",
        },
        headers=_auth(member_token),
    )

    assert response.status_code in (401, 403)


def test_update_book_not_found(
    client,
    librarian_token,
):
    response = client.patch(
        "/books/999999",
        data={
            "title": "Updated",
        },
        headers=_auth(librarian_token),
    )

    assert response.status_code == 404


# ============================================================
# DELETE
# ============================================================

def test_delete_book_success(
    client,
    librarian_token,
    test_book,
):
    response = client.delete(
        f"/books/{test_book['book_id']}",
        headers=_auth(librarian_token),
    )

    assert response.status_code == 200


def test_delete_book_not_found(
    client,
    librarian_token,
):
    response = client.delete(
        "/books/999999",
        headers=_auth(librarian_token),
    )

    assert response.status_code == 404


def test_delete_book_member_forbidden(
    client,
    member_token,
    test_book,
):
    response = client.delete(
        f"/books/{test_book['book_id']}",
        headers=_auth(member_token),
    )

    assert response.status_code in (401, 403)


def test_delete_book_without_authentication(
    client,
    test_book,
):
    response = client.delete(
        f"/books/{test_book['book_id']}"
    )

    assert response.status_code in (401, 422)


# ============================================================
# COVER
# ============================================================

def test_create_book_with_valid_cover(
    client,
    librarian_token,
):
    response = client.post(
        "/books/",
        data={
            "title": "Book With Cover",
            "cover": (
                io.BytesIO(b"fake image"),
                "cover.jpg",
            ),
        },
        content_type="multipart/form-data",
        headers=_auth(librarian_token),
    )

    assert response.status_code == 201


def test_create_book_with_invalid_cover_extension(
    client,
    librarian_token,
):
    response = client.post(
        "/books/",
        data={
            "title": "Invalid Cover",
            "cover": (
                io.BytesIO(b"fake file"),
                "malware.exe",
            ),
        },
        content_type="multipart/form-data",
        headers=_auth(librarian_token),
    )

    assert response.status_code == 400