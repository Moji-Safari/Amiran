def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# AUTH
# ============================================================

def test_perf_login(client, test_member, benchmark):
    from app.extensions import limiter

    was_enabled = limiter.enabled
    limiter.enabled = False

    try:
        def call():
            client.post(
                "/auth/login",
                json={
                    "identifier": "test_member@example.com",
                    "password": "wrong",
                },
            )

        benchmark(call)
    finally:
        limiter.enabled = was_enabled


# ============================================================
# BOOKS
# ============================================================

def test_perf_list_books(client, member_token, benchmark):
    def call():
        client.get("/books/", headers=_auth(member_token))

    benchmark(call)


def test_perf_get_book(client, member_token, test_book, benchmark):
    def call():
        client.get(
            f"/books/{test_book['book_id']}",
            headers=_auth(member_token),
        )

    benchmark(call)


# ============================================================
# MEMBERS
# ============================================================

def test_perf_list_members(client, member_token, benchmark):
    def call():
        client.get(
            "/members/lst?search=&page=1&limit=10",
            headers=_auth(member_token),
        )

    benchmark(call)


def test_perf_find_member(
    client, member_token, test_member, benchmark
):
    def call():
        client.get(
            f"/members/find/{test_member['memb_id']}",
            headers=_auth(member_token),
        )

    benchmark(call)


# ============================================================
# LOANS
# ============================================================

def test_perf_list_pending_loans(
    client, librarian_token, test_loan, benchmark
):
    def call():
        client.get(
            "/loan/approved/1",
            headers=_auth(librarian_token),
        )

    benchmark(call)


def test_perf_create_loan_request(
    client, member_token, test_book, benchmark
):
    def call():
        client.post(
            "/loan/demand",
            json={"book_id": test_book["book_id"]},
            headers=_auth(member_token),
        )

    benchmark(call)


# ============================================================
# QUIZ
# ============================================================

def test_perf_get_quiz(
    client, member_token, perf_quiz_seed, benchmark
):
    test_id = perf_quiz_seed["test_id"]

    def call():
        client.get(
            f"/tests/{test_id}",
            headers=_auth(member_token),
        )

    benchmark(call)
