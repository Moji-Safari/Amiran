def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# HELPERS
# ============================================================

def _create_test_with_question(db):
    """
    Insert one test, one question, and two answers.
    Returns a dict with the ids.
    """
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO Test_Task (
                title,
                description,
                max_score
            )
            VALUES (%s, %s, %s)
            RETURNING PK_test_teast_id
            """,
            (
                "Personality Test",
                "A short test",
                10,
            ),
        )

        test = cur.fetchone()
        test_id = test["pk_test_teast_id"]

        cur.execute(
            """
            INSERT INTO Test_Questions (
                question_text,
                FK_test_teast_id,
                question_type
            )
            VALUES (%s, %s, %s)
            RETURNING PK_tst_que_id
            """,
            (
                "Do you like reading?",
                test_id,
                "single_choice",
            ),
        )

        question = cur.fetchone()
        question_id = question["pk_tst_que_id"]

        answer_ids = []

        for text, correct in (
            ("Yes", True),
            ("No", False),
        ):
            cur.execute(
                """
                INSERT INTO Test_Answers (
                    FK_tst_que_id,
                    answer_text,
                    is_correct
                )
                VALUES (%s, %s, %s)
                RETURNING PK_tst_answ_id
                """,
                (
                    question_id,
                    text,
                    correct,
                ),
            )

            answer_ids.append(
                cur.fetchone()["pk_tst_answ_id"]
            )

    db.commit()

    return {
        "test_id": test_id,
        "question_id": question_id,
        "correct_answer_id": answer_ids[0],
        "wrong_answer_id": answer_ids[1],
    }


# ============================================================
# GET TEST
# ============================================================

def test_get_quiz_questions(
    client,
    member_token,
    db,
):
    data = _create_test_with_question(db)

    response = client.get(
        f"/tests/{data['test_id']}",
        headers=_auth(member_token),
    )

    assert response.status_code == 200

    body = response.get_json()

    assert "questions" in body
    assert isinstance(body["questions"], list)
    assert len(body["questions"]) == 1


def test_get_quiz_questions_not_found(
    client,
    member_token,
):
    response = client.get(
        "/tests/999999",
        headers=_auth(member_token),
    )

    assert response.status_code == 404


def test_get_quiz_questions_requires_authentication(
    client,
):
    response = client.get("/tests/1")

    assert response.status_code in (401, 422)


# ============================================================
# SUBMIT QUIZ
# ============================================================

def test_submit_quiz(
    client,
    member_token,
    db,
):
    data = _create_test_with_question(db)

    response = client.post(
        f"/tests/{data['test_id']}/submit",
        json={
            "answers": [
                {
                    "question_id": data["question_id"],
                    "answer_id": data["correct_answer_id"],
                },
            ],
        },
        headers=_auth(member_token),
    )

    assert response.status_code == 201

    body = response.get_json()

    assert body["score"] == 1
    assert "result" in body


def test_submit_quiz_requires_authentication(
    client,
    db,
):
    data = _create_test_with_question(db)

    response = client.post(
        f"/tests/{data['test_id']}/submit",
        json={"answers": []},
    )

    assert response.status_code in (401, 422)


def test_submit_quiz_without_answers(
    client,
    member_token,
    db,
):
    data = _create_test_with_question(db)

    response = client.post(
        f"/tests/{data['test_id']}/submit",
        json={"answers": []},
        headers=_auth(member_token),
    )

    assert response.status_code == 400