# HTTP Client Examples

Runnable request collection for the Library API. Works with:

- **VS Code** — install the "REST Client" extension, open any `.http` file, click "Send Request".
- **JetBrains IDEs** (PyCharm, IntelliJ) — open any `.http` file, click the green run arrow.

## Prerequisites

1. The API is running locally, by default on `http://localhost:5000`.
2. The database is migrated and, ideally, seeded with two dev users:

   - `member@example.com` / `Password123!`
   - `librarian@example.com` / `Password123!`

   If they do not exist yet, create them by running the **Signup** request in `auth.http` twice, changing the email and role each time (the role is set by the database, not by the signup body — to promote a user to librarian, run the SQL in the last section of `auth.http`).

## How authentication works

Protected endpoints expect:

    Authorization: Bearer <access_token>

You get the token by calling `POST /auth/login`. The login request in `auth.http` stores the token into a variable called `memberToken` (or `librarianToken`) that all other files reuse as `{{memberToken}}`.

## Order of operations (first run)

1. Open `auth.http`.
2. Run **Signup (member)** and **Signup (librarian)** if the users don't exist yet.
3. Run **Login (member)** — the response token is saved to `{{memberToken}}`.
4. Run **Login (librarian)** — the response token is saved to `{{librarianToken}}`.
5. Open any other `.http` file and run its requests. Tokens are already populated.

## Note on secrets

Nothing in this folder contains real tokens or passwords. All credentials are dev-only placeholders. If you want per-environment overrides, create `.http-client.env.json` locally — it is already in `.gitignore`.