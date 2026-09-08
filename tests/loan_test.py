

# ============================================================
# 1. MEMBER CREATES A LOAN REQUEST
# ============================================================

def test_create_loan_request(client, auth_token, test_book):
    token = auth_token("member")

    book_id = test_book["book_id"]

    response = client.post(
        f"/loan/demand?book_id={book_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["message"] == "Loan request created"
    assert "loan_id" in body


# ============================================================
# 2. LOAN REQUEST REQUIRES BOOK_ID
# ============================================================

def test_create_loan_request_without_book_id(
    client,
    auth_token,
):
    token = auth_token("member")

    response = client.post(
        "/loan/demand",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400

    body = response.get_json()

    assert body["error"] == "book_id is required"


# ============================================================
# 3. LIBRARIAN CAN SEE PENDING LOANS
# ============================================================

def test_get_pending_loans(
    client,
    auth_token,
    test_loan,
):
    token = auth_token("librarian")

    response = client.get(
        "/loan/approved/1",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert "loans" in body
    assert isinstance(body["loans"], list)


# ============================================================
# 4. LIBRARIAN APPROVES A LOAN
# ============================================================

def test_approve_loan(
    client,
    auth_token,
    test_loan,
):
    token = auth_token("librarian")

    loan_id = test_loan["loan_id"]

    response = client.post(
        "/loan/approved/2",
        json={
            "loan_id": loan_id,
            "due_date": "2026-10-01",
            "return_date": None,
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["message"] == "Loan approved"
    assert body["loan_id"] == loan_id


# ============================================================
# 5. MEMBER CANCELS A BORROWED LOAN
# ============================================================

def test_cancel_loan(
    client,
    auth_token,
    test_loan,
):
    token = auth_token("member")

    loan_id = test_loan["loan_id"]

    response = client.post(
        "/loan/borrow",
        json={
            "loan_id": loan_id,
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["message"] == "Loan cancelled"
    assert body["loan_id"] == loan_id
