# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Guest area endpoint that returns the 20 most recently added books
- Admin area endpoint that returns the list of librarians

### Changed
- Auth module split into `extensions.py` to break circular imports

### Fixed
- Ruff whitespace warnings across the project

## [1.0.0] - 2026-09-24

### Added

#### Authentication and authorization
- JWT-based signup, login, and refresh endpoints
- Role-based access control with guest, member, and librarian tiers
- `@jwt_required()` and `@role_required()` decorators for route protection
- Rate limiting on `/auth/login` (5 requests per minute per IP)
- `/auth/me`, `/auth/guest-area`, `/auth/member-area`, `/auth/admin-area` endpoints

#### Books
- Full CRUD for books (create, list, get, update, delete)
- Book cover upload with extension and MIME allowlist
- UUID-based filename generation for uploads
- Cover storage under `uploads/book_covers/`

#### Members
- Member creation, lookup by id, list with search and pagination
- Member update and delete (librarian-only)
- Branch association for members

#### Loans
- Loan request creation by members
- Loan approval by librarians with due-date assignment
- Loan borrowing and cancellation by members
- Loan status machine: pending, approved, rejected, borrowed, returned
- Per-member active loan limit (3 concurrent)

#### Quiz
- Personality test retrieval with questions and answers
- Test submission with server-side scoring
- Submission history per member

#### Security
- All SQL queries use psycopg2 parameterized placeholders
- Strict field allowlist on member create/update (no mass assignment)
- Signup hardcodes role to `member` (no self-promotion)
- Generic error messages on 500 responses (no schema leak)
- Session ownership checks on loan and quiz endpoints

#### Infrastructure
- PostgreSQL connection pool with `minconn`/`maxconn` per worker
- Gunicorn production configuration (workers, timeout)
- GitHub Actions CI: lint with ruff, run tests against a Postgres service container
- Performance benchmark suite with `pytest-benchmark`
- HTTP request collection under `http/` for manual testing
- Security audit report covering nine categories

### Changed
- Column names aligned with actual schema:
  - `users.user_id` (was `id`)
  - `members.PK_memb_id` (was `memb_id`)
  - `loan.PK_loan_id`, `loan.FK_memb_id`, `loan.FK_book_id`
  - Role values are strings (`'member'`, `'librarian'`), not integers

### Fixed
- JWT identity stored as a string, matching `get_jwt_identity()` usage in routes
- Test suite independence via `reset_db` and `reset_limiter` autouse fixtures
- Uniqueness constraint handling in quiz answer seed data

[Unreleased]: https://github.com/<your-username>/<your-repo>/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/<your-username>/<your-repo>/releases/tag/v1.0.0