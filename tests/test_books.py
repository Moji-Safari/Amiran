

# ============================================================
# CREATE
# ============================================================

def test_create_book_success(client, auth_token):
    token = auth_token("librarian")

    response = client.post(
        "/books/create",
        data={
            "title": "The Hobbit",
            "isbn": "9780261102217",
            "publication_year": "1937",
            "genre": "Fantasy",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["message"] == "Book created"
    assert "book_id" in body


def test_create_book_without_title(client, auth_token):
    token = auth_token("librarian")

    response = client.post(
        "/books/create",
        data={
            "isbn": "123",
            "publication_year": "2020",
            "genre": "Fantasy",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["error"] == "title is required"


def test_create_book_empty_title(client, auth_token):
    token = auth_token("librarian")

    response = client.post(
        "/books/create",
        data={
            "title": "",
            "isbn": "123",
            "publication_year": "2020",
            "genre": "Fantasy",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400

    assert response.get_json()["error"] == "title is required"


def test_create_book_title_too_long(client, auth_token):
    token = auth_token("librarian")

    long_title = "A" * 256

    response = client.post(
        "/books/create",
        data={
            "title": long_title,
            "isbn": "123",
            "publication_year": "2020",
            "genre": "Fantasy",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400

    assert (
        response.get_json()["error"]
        == "title must be at most 255 characters"
    )


def test_create_book_requires_authentication(client):
    response = client.post(
        "/books/create",
        data={
            "title": "The Hobbit",
            "isbn": "123",
            "publication_year": "1937",
            "genre": "Fantasy",
        },
    )

    assert response.status_code == 401


def test_create_book_requires_librarian(client, auth_token):
    token = auth_token("member")

    response = client.post(
        "/books/create",
        data={
            "title": "The Hobbit",
            "isbn": "123",
            "publication_year": "1937",
            "genre": "Fantasy",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 403


# ============================================================
# READ ALL
# ============================================================

def test_get_books(client, auth_token):
    token = auth_token("member")

    response = client.get(
        "/books/find/lst",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert "books" in body
    assert isinstance(body["books"], list)


def test_get_books_requires_authentication(client):
    response = client.get("/books/find/lst")

    assert response.status_code == 401


# ============================================================
# READ ONE
# ============================================================

def test_get_book(client, auth_token, test_book):
    token = auth_token("member")

    book_id = test_book["book_id"]

    response = client.get(
        f"/books/find/{book_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["book_id"] == book_id
    assert body["title"] == test_book["title"]


def test_get_book_not_found(client, auth_token):
    token = auth_token("member")

    response = client.get(
        "/books/find/999999",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404

    assert response.get_json()["error"] == "Book not found"


def test_get_book_requires_authentication(client):
    response = client.get("/books/find/1")

    assert response.status_code == 401


# ============================================================
# UPDATE
# ============================================================

def test_update_book_title(client, auth_token, test_book):
    token = auth_token("librarian")

    book_id = test_book["book_id"]

    response = client.patch(
        f"/books/update/{book_id}",
        data={
            "title": "The Hobbit Updated",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["message"] == "Book updated"
    assert body["book_id"] == book_id


def test_update_book_empty_title(client, auth_token, test_book):
    token = auth_token("librarian")

    book_id = test_book["book_id"]

    response = client.patch(
        f"/books/update/{book_id}",
        data={
            "title": "",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400

    assert (
        response.get_json()["error"]
        == "title cannot be empty"
    )


def test_update_book_title_too_long(client, auth_token, test_book):
    token = auth_token("librarian")

    book_id = test_book["book_id"]

    response = client.patch(
        f"/books/update/{book_id}",
        data={
            "title": "A" * 256,
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400

    assert (
        response.get_json()["error"]
        == "title must be at most 255 characters"
    )


def test_update_book_invalid_author_id(client, auth_token, test_book):
    token = auth_token("librarian")

    book_id = test_book["book_id"]

    response = client.patch(
        f"/books/update/{book_id}",
        data={
            "author_id": "-1",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400

    assert (
        response.get_json()["error"]
        == "author_id must be a positive integer"
    )


def test_update_book_not_found(client, auth_token):
    token = auth_token("librarian")

    response = client.patch(
        "/books/update/999999",
        data={
            "title": "Does Not Exist",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404

    assert response.get_json()["error"] == "Book not found"


def test_update_book_requires_librarian(
    client,
    auth_token,
    test_book,
):
    token = auth_token("member")

    book_id = test_book["book_id"]

    response = client.patch(
        f"/books/update/{book_id}",
        data={
            "title": "Unauthorized Update",
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 403


def test_update_book_requires_authentication(client, test_book):
    book_id = test_book["book_id"]

    response = client.patch(
        f"/books/update/{book_id}",
        data={
            "title": "Unauthorized Update",
        },
    )

    assert response.status_code == 401


# ============================================================
# DELETE
# ============================================================

def test_delete_book(client, auth_token, test_book):
    token = auth_token("librarian")

    book_id = test_book["book_id"]

    response = client.delete(
        f"/books/delete/{book_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["message"] == "Book deleted"
    assert body["book_id"] == book_id


def test_delete_book_not_found(client, auth_token):
    token = auth_token("librarian")

    response = client.delete(
        "/books/delete/999999",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404

    assert response.get_json()["error"] == "Book not found"


def test_delete_book_requires_librarian(
    client,
    auth_token,
    test_book,
):
    token = auth_token("member")

    book_id = test_book["book_id"]

    response = client.delete(
        f"/books/delete/{book_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 403


def test_delete_book_requires_authentication(client, test_book):
    book_id = test_book["book_id"]

    response = client.delete(
        f"/books/delete/{book_id}"
    )

    assert response.status_code == 401
