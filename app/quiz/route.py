quiz_bp = Blueprint(
    "quiz",
    __name__,
    url_prefix="/tests"
)

@quiz_bp.get("/<int:test_id>")
@jwt_required()
def get_test(test_id):

    conn = get_db()

    with conn.cursor() as cur:

        # Get test
        cur.execute(
            """
            SELECT
                PK_test_teast_id,
                title,
                description,
                max_score
            FROM Test_Task
            WHERE PK_test_teast_id = %s
            """,
            (test_id,)
        )

        test = cur.fetchone()

        if test is None:
            return {
                "error": "Test not found"
            }, 404

        # Get questions and answers
        cur.execute(
            """
            SELECT
                q.PK_tst_que_id,
                q.question_text,
                q.question_type,
                a.PK_tst_answ_id,
                a.answer_text
            FROM Test_Questions q
            LEFT JOIN Test_Answers a
                ON a.FK_tst_que_id = q.PK_tst_que_id
            WHERE q.FK_test_teast_id = %s
            ORDER BY q.PK_tst_que_id, a.PK_tst_answ_id
            """,
            (test_id,)
        )

        rows = cur.fetchall()

    questions = {}

    for row in rows:

        question_id = row["pk_tst_que_id"]

        if question_id not in questions:
            questions[question_id] = {
                "question_id": question_id,
                "question_text": row["question_text"],
                "question_type": row["question_type"],
                "answers": []
            }

        if row["pk_tst_answ_id"] is not None:
            questions[question_id]["answers"].append({
                "answer_id": row["pk_tst_answ_id"],
                "answer_text": row["answer_text"]
            })

    return {
        "test": {
            "test_id": test["pk_test_teast_id"],
            "title": test["title"],
            "description": test["description"],
            "max_score": test["max_score"]
        },
        "questions": list(questions.values())
    }, 200

@quiz_bp.post("/<int:test_id>/submit")
@jwt_required()
def submit_test(test_id):

    member_id = get_jwt_identity()

    data = request.get_json()

    if not data:
        return {
            "error": "JSON body is required"
        }, 400

    answers = data.get("answers")

    if not isinstance(answers, list) or not answers:
        return {
            "error": "answers must be a non-empty list"
        }, 400

    conn = get_db()

    try:
        with conn.cursor() as cur:

            # -------------------------------------------------
            # 1. Check that the test exists
            # -------------------------------------------------

            cur.execute(
                """
                SELECT
                    PK_test_teast_id,
                    max_score
                FROM Test_Task
                WHERE PK_test_teast_id = %s
                """,
                (test_id,)
            )

            test = cur.fetchone()

            if test is None:
                return {
                    "error": "Test not found"
                }, 404

            # -------------------------------------------------
            # 2. Check whether member already submitted
            # -------------------------------------------------

            cur.execute(
                """
                SELECT
                    PK_test_submission_id,
                    score,
                    result
                FROM Test_Submissions
                WHERE FK_memb_id = %s
                  AND FK_test_teast_id = %s
                """,
                (member_id, test_id)
            )

            existing_submission = cur.fetchone()

            if existing_submission:
                return {
                    "message": "Test has already been submitted",
                    "score": existing_submission["score"],
                    "result": existing_submission["result"]
                }, 200

            # -------------------------------------------------
            # 3. Get all questions belonging to this test
            # -------------------------------------------------

            cur.execute(
                """
                SELECT
                    PK_tst_que_id
                FROM Test_Questions
                WHERE FK_test_teast_id = %s
                """,
                (test_id,)
            )

            questions = cur.fetchall()

            question_ids = {
                row["pk_tst_que_id"]
                for row in questions
            }

            # -------------------------------------------------
            # 4. Validate submitted questions
            # -------------------------------------------------

            submitted_question_ids = set()

            for answer in answers:

                question_id = answer.get("question_id")
                answer_id = answer.get("answer_id")

                if question_id is None or answer_id is None:
                    conn.rollback()

                    return {
                        "error": "Each answer requires question_id and answer_id"
                    }, 400

                if question_id in submitted_question_ids:
                    conn.rollback()

                    return {
                        "error": f"Question {question_id} was answered more than once"
                    }, 400

                if question_id not in question_ids:
                    conn.rollback()

                    return {
                        "error": f"Question {question_id} does not belong to this test"
                    }, 400

                submitted_question_ids.add(question_id)

            # -------------------------------------------------
            # 5. Validate answers and calculate score
            # -------------------------------------------------

            score = 0

            validated_answers = []

            for answer in answers:

                question_id = answer["question_id"]
                answer_id = answer["answer_id"]

                cur.execute(
                    """
                    SELECT
                        PK_tst_answ_id,
                        is_correct
                    FROM Test_Answers
                    WHERE PK_tst_answ_id = %s
                      AND FK_tst_que_id = %s
                    """,
                    (answer_id, question_id)
                )

                selected_answer = cur.fetchone()

                if selected_answer is None:
                    conn.rollback()

                    return {
                        "error": (
                            f"Answer {answer_id} does not belong "
                            f"to question {question_id}"
                        )
                    }, 400

                # SERVER decides whether the answer is correct
                if selected_answer["is_correct"]:
                    score += 1

                validated_answers.append({
                    "question_id": question_id,
                    "answer_id": answer_id
                })

            # -------------------------------------------------
            # 6. Calculate final result SERVER-SIDE
            # -------------------------------------------------

            total_questions = len(question_ids)

            percentage = (
                score / total_questions * 100
                if total_questions > 0
                else 0
            )

            if percentage >= 80:
                result = "Excellent Match"

            elif percentage >= 60:
                result = "Good Match"

            elif percentage >= 40:
                result = "Moderate Match"

            else:
                result = "Low Match"

            # -------------------------------------------------
            # 7. Save submission
            # -------------------------------------------------

            cur.execute(
                """
                INSERT INTO Test_Submissions (
                    FK_memb_id,
                    FK_test_teast_id,
                    score,
                    result
                )
                VALUES (%s, %s, %s, %s)
                RETURNING PK_test_submission_id
                """,
                (
                    member_id,
                    test_id,
                    score,
                    result
                )
            )

            submission = cur.fetchone()

            submission_id = submission["pk_test_submission_id"]

            # -------------------------------------------------
            # 8. Save individual answers
            # -------------------------------------------------

            for answer in validated_answers:

                cur.execute(
                    """
                    INSERT INTO Test_Submission_Answers (
                        FK_test_submission_id,
                        FK_tst_que_id,
                        FK_tst_answ_id
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (
                        submission_id,
                        answer["question_id"],
                        answer["answer_id"]
                    )
                )

            conn.commit()

            return {
                "message": "Test submitted successfully",
                "score": score,
                "result": result
            }, 201

    except Exception:
        conn.rollback()
        raise