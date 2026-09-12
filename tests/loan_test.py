def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# CREATE LOAN
# ============================================================

def test_create_loan_success(
    client,
    member_token,
    test_book,
):
    response = client.post(
        "/loan/demand",
        json={"book_id": test_book["book_id"]},
        headers=_auth(member_token),
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["message"] == "Loan request created"
    assert "loan_id" in body


def test_create_loan_without_book_id(
    client,
    member_token,
):
    response = client.post(
        "/loan/demand",
        json={},
        headers=_auth(member_token),
    )

    assert response.status_code == 400


def test_create_loan_without_authentication(
    client,
    test_book,
):
    response = client.post(
        "/loan/demand",
        json={"book_id": test_book["book_id"]},
    )

    assert response.status_code in (401, 422)


def test_librarian_cannot_create_member_loan(
    client,
    librarian_token,
    test_book,
):
    response = client.post(
        "/loan/demand",
        json={"book_id": test_book["book_id"]},
        headers=_auth(librarian_token),
    )

    # Librarian is authenticated but has no member record.
    assert response.status_code == 404


# ============================================================
# PENDING LOANS
# ============================================================

def test_get_pending_loans_success(
    client,
    librarian_token,
    test_loan,
):
    response = client.get(
        "/loan/approved/1",
        headers=_auth(librarian_token),
    )

    assert response.status_code == 200

    body = response.get_json()

    assert "loans" in body
    assert isinstance(body["loans"], list)


def test_get_pending_loans_member_forbidden(
    client,
    member_token,
):
    response = client.get(
        "/loan/approved/1",
        headers=_auth(member_token),
    )

    assert response.status_code in (401, 403)


def test_get_pending_loans_without_authentication(client):
    response = client.get(
        "/loan/approved/1"
    )

    assert response.status_code in (401, 422)


# ============================================================
# APPROVE
# ============================================================

def test_approve_loan_success(
    client,
    librarian_token,
    test_loan,
):
    response = client.post(
        "/loan/approved/1",
        json={
            "loan_id": test_loan["loan_id"],
            "due_date": "2026-10-01",
            "return_date": None,
        },
        headers=_auth(librarian_token),
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["message"] == "Loan approved"
    assert body["loan_id"] == test_loan["loan_id"]


def test_approve_loan_invalid_id(
    client,
    librarian_token,
):
    response = client.post(
        "/loan/approved/2",
        json={
            "loan_id": 999999,
            "due_date": "2026-10-01",
        },
        headers=_auth(librarian_token),
    )

    assert response.status_code == 400


def test_member_cannot_approve_loan(
    client,
    member_token,
    test_loan,
):
    response = client.post(
        "/loan/approved/2",
        json={
            "loan_id": test_loan["loan_id"],
            "due_date": "2026-10-01",
        },
        headers=_auth(member_token),
    )

    assert response.status_code in (401, 403)


# ============================================================
# INVALID STATE TRANSITIONS
# ============================================================

def test_returned_loan_cannot_be_borrowed(
    client,
    member_token,
    test_loan,
    db,
):
    # Move the loan to 'returned' (status id 5) first.
    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE loan
            SET loanstatus_id = 5
            WHERE PK_loan_id = %s
            """,
            (test_loan["loan_id"],),
        )

    db.commit()

    response = client.post(
        "/loan/borrow",
        json={
            "loan_id": test_loan["loan_id"],
        },
        headers=_auth(member_token),
    )

    assert response.status_code == 400


def test_cancelled_loan_cannot_be_borrowed(
    client,
    member_token,
    test_loan,
    db,
):
    # Move the loan to 'rejected' (status id 3) first.
    with db.cursor() as cur:
        cur.execute(
            """
            UPDATE loan
            SET loanstatus_id = 3
            WHERE PK_loan_id = %s
            """,
            (test_loan["loan_id"],),
        )

    db.commit()

    response = client.post(
        "/loan/borrow",
        json={
            "loan_id": test_loan["loan_id"],
        },
        headers=_auth(member_token),
    )

    assert response.status_code == 400


def test_invalid_loan_id_cannot_change_state(
    client,
    member_token,
):
    response = client.post(
        "/loan/borrow",
        json={
            "loan_id": 999999,
        },
        headers=_auth(member_token),
    )

    assert response.status_code == 400