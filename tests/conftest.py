import pytest

from flask_jwt_extended import create_access_token

from app import create_app
from db.database import get_db


# ============================================================
# APP / CLIENT
# ============================================================

@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "JWT_SECRET_KEY": "test-secret-key",
            "DATABASE_URL": (
                "postgresql://postgres:moj240028@localhost:5432/"
                "library_test_db"
            ),
            "DB_POOL_MIN": 1,
            "DB_POOL_MAX": 5,
        }
    )

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    with app.app_context():
        with get_db() as conn:
            yield conn


# ============================================================
# DB RESET (autouse)
# ============================================================

@pytest.fixture(autouse=True)
def reset_db(app):
    """
    Truncate all tables and re-seed loan_status before each test.
    """
    with app.app_context():
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    TRUNCATE TABLE
                        test_submission_answers,
                        test_submissions,
                        test_answers,
                        test_questions,
                        test_task,
                        notification,
                        loan,
                        loan_status,
                        author_book,
                        author,
                        books,
                        members,
                        librarian,
                        branches,
                        users
                    RESTART IDENTITY CASCADE
                    """
                )

                for name in (
                    "pending",
                    "approved",
                    "rejected",
                    "borrowed",
                    "returned",
                ):
                    cur.execute(
                        """
                        INSERT INTO loan_status (status_name)
                        VALUES (%s)
                        """,
                        (name,),
                    )

            conn.commit()

    yield


# ============================================================
# AUTH TOKENS
# ============================================================

@pytest.fixture
def auth_token(app):
    """
    Returns a function that builds an access token given a user_id.
    Identity is a string, matching get_jwt_identity() in the routes.
    """

    def generate_token(user_id):
        with app.app_context():
            return create_access_token(identity=str(user_id))

    return generate_token


@pytest.fixture
def member_token(auth_token, test_member):
    return auth_token(test_member["user_id"])


@pytest.fixture
def librarian_token(auth_token, test_librarian):
    return auth_token(test_librarian["user_id"])


# ============================================================
# BRANCH
# ============================================================

@pytest.fixture
def test_branch(db):
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO branches (
                branch_name,
                address,
                phone
            )
            VALUES (%s, %s, %s)
            RETURNING branch_id
            """,
            (
                "Main Branch",
                "123 Main St",
                "555-0000",
            ),
        )

        branch = cur.fetchone()

    db.commit()

    return {
        "branch_id": branch["branch_id"],
    }


# ============================================================
# MEMBER
# ============================================================

@pytest.fixture
def test_member(db, test_branch):
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (
                email,
                password_hash,
                role
            )
            VALUES (%s, %s, %s)
            RETURNING user_id
            """,
            (
                "test_member@example.com",
                "TEST_PASSWORD_HASH",
                "member",
            ),
        )

        user = cur.fetchone()

        cur.execute(
            """
            INSERT INTO members (
                user_id,
                FK_branch_id,
                first_name,
                last_name,
                email,
                membership_type
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING PK_memb_id
            """,
            (
                user["user_id"],
                test_branch["branch_id"],
                "Test",
                "Member",
                "test_member@example.com",
                "standard",
            ),
        )

        member = cur.fetchone()

    db.commit()

    return {
        "user_id": user["user_id"],
        "memb_id": member["pk_memb_id"],
        "email": "test_member@example.com",
        "branch_id": test_branch["branch_id"],
    }


# ============================================================
# LIBRARIAN
# ============================================================

@pytest.fixture
def test_librarian(db, test_branch):
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (
                email,
                password_hash,
                role
            )
            VALUES (%s, %s, %s)
            RETURNING user_id
            """,
            (
                "test_librarian@example.com",
                "TEST_PASSWORD_HASH",
                "librarian",
            ),
        )

        user = cur.fetchone()

        cur.execute(
            """
            INSERT INTO librarian (
                user_id,
                FK_branch_id,
                name,
                email
            )
            VALUES (%s, %s, %s, %s)
            RETURNING PK_librarian_id
            """,
            (
                user["user_id"],
                test_branch["branch_id"],
                "Test Librarian",
                "test_librarian@example.com",
            ),
        )

        librarian = cur.fetchone()

    db.commit()

    return {
        "user_id": user["user_id"],
        "librarian_id": librarian["pk_librarian_id"],
        "email": "test_librarian@example.com",
    }


# ============================================================
# BOOK
# ============================================================

@pytest.fixture
def test_book(db):
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO books (
                title,
                isbn,
                publication_year,
                genre
            )
            VALUES (%s, %s, %s, %s)
            RETURNING
                book_id,
                title,
                isbn,
                publication_year,
                genre
            """,
            (
                "Test Book",
                "TEST-ISBN-001",
                2020,
                "Fantasy",
            ),
        )

        book = cur.fetchone()

    db.commit()

    return book


# ============================================================
# LOAN
# ============================================================

@pytest.fixture
def test_loan(db, test_member, test_book):
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT PK_loanstatus_id
            FROM loan_status
            WHERE status_name = 'pending'
            """
        )

        status = cur.fetchone()

        cur.execute(
            """
            INSERT INTO loan (
                FK_branch_id,
                FK_book_id,
                loanstatus_id,
                FK_memb_id
            )
            VALUES (%s, %s, %s, %s)
            RETURNING PK_loan_id
            """,
            (
                test_member["branch_id"],
                test_book["book_id"],
                status["pk_loanstatus_id"],
                test_member["memb_id"],
            ),
        )

        loan = cur.fetchone()

    db.commit()

    return {
        "loan_id": loan["pk_loan_id"],
        "memb_id": test_member["memb_id"],
        "book_id": test_book["book_id"],
    }