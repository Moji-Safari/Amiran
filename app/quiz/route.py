from flask import Blueprint, current_app, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.loan.route import get_member_by_user_id
from db.database import get_db


quiz_bp = Blueprint(
    "quiz",
    __name__,
    url_prefix="/tests",
)


@quiz_bp.get("/<int:test_id>")
@jwt_required()
def get_test(test_id):
    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        PK_test_teast_id AS test_id,
                        title,
                        description,
                        max_score
                    FROM Test_Task
                    WHERE PK_test_teast_id = %s
                    """,
                    (test_id,),
                )

                test = cur.fetchone()

                if test is None:
                    return {
                        "error": "Test not found"
                    }, 404

                cur.execute(
                    """
                    SELECT
                        q.PK_tst_que_id AS question_id,
                        q.question_text,
                        q.question_type,
                        a.PK_tst_answ_id AS answer_id,
                        a.answer_text
                    FROM Test_Questions q
                    LEFT JOIN Test_Answers a
                        ON a.FK_tst_que_id =
                           q.PK_tst_que_id
                    WHERE q.FK_test_teast_id = %s
                    ORDER BY
                        q.PK_tst_que_id,
                        a.PK_tst_answ_id
                    """,
                    (test_id,),
                )

                rows = cur.fetchall()

        questions = {}

        for row in rows:
            question_id = row["question_id"]

            if question_id not in questions:
                questions[question_id] = {
                    "question_id": question_id,
                    "question_text": row["question_text"],
                    "question_type": row["question_type"],
                    "answers": [],
                }

            answer_id = row["answer_id"]

            if answer_id is not None:
                questions[question_id]["answers"].append({
                    "answer_id": answer_id,
                    "answer_text": row["answer_text"],
                })

        return {
            "test": {
                "test_id": test["test_id"],
                "title": test["title"],
                "description": test["description"],
                "max_score": test["max_score"],
            },
            "questions": list(questions.values()),
        }, 200

    except Exception:
        current_app.logger.exception(
            "Failed to retrieve test"
        )

        return {
            "error": "Failed to retrieve test"
        }, 500


@quiz_bp.post("/<int:test_id>/submit")
@jwt_required()
def submit_test(test_id):
    user_id = get_jwt_identity()

    member = get_member_by_user_id(user_id)

    if member is None:
        return {
            "error": "Member not found"
        }, 404

    data = request.get_json(silent=True) or {}

    answers = data.get("answers")

    if not isinstance(answers, list) or not answers:
        return {
            "error": "answers must be a non-empty list"
        }, 400

    member_id = member["memb_id"]

    try:
        with get_db() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        PK_test_teast_id AS test_id,
                        max_score
                    FROM Test_Task
                    WHERE PK_test_teast_id = %s
                    """,
                    (test_id,),
                )

                test = cur.fetchone()

                if test is None:
                    return {
                        "error": "Test not found"
                    }, 404

                cur.execute(
                    """
                    SELECT
                        PK_test_submission_id AS submission_id,
                        score,
                        result
                    FROM Test_Submissions
                    WHERE FK_memb_id = %s
                      AND FK_test_teast_id = %s
                    """,
                    (
                        member_id,
                        test_id,
                    ),
                )

                existing_submission = cur.fetchone()

                if existing_submission:
                    return {
                        "message": (
                            "Test has already been submitted"
                        ),
                        "score": existing_submission["score"],
                        "result": existing_submission["result"],
                    }, 200

                cur.execute(
                    """
                    SELECT
                        PK_tst_que_id AS question_id
                    FROM Test_Questions
                    WHERE FK_test_teast_id = %s
                    """,
                    (test_id,),
                )

                questions = cur.fetchall()

                question_ids = {
                    row["question_id"]
                    for row in questions
                }

                if not question_ids:
                    return {
                        "error": "Test has no questions"
                    }, 400

                submitted_question_ids = set()

                for answer in answers:
                    if not isinstance(answer, dict):
                        return {
                            "error": (
                                "Each answer must be "
                                "a JSON object"
                            )
                        }, 400

                    question_id = answer.get("question_id")
                    answer_id = answer.get("answer_id")

                    if (
                        question_id is None
                        or answer_id is None
                    ):
                        return {
                            "error": (
                                "Each answer requires "
                                "question_id and answer_id"
                            )
                        }, 400

                    if question_id in submitted_question_ids:
                        return {
                            "error": (
                                f"Question {question_id} "
                                "was answered more than once"
                            )
                        }, 400

                    if question_id not in question_ids:
                        return {
                            "error": (
                                f"Question {question_id} "
                                "does not belong to this test"
                            )
                        }, 400

                    submitted_question_ids.add(question_id)

                if submitted_question_ids != question_ids:
                    return {
                        "error": (
                            "All questions must be answered"
                        )
                    }, 400

                score = 0
                validated_answers = []

                for answer in answers:
                    question_id = answer["question_id"]
                    answer_id = answer["answer_id"]

                    cur.execute(
                        """
                        SELECT
                            PK_tst_answ_id AS answer_id,
                            is_correct
                        FROM Test_Answers
                        WHERE PK_tst_answ_id = %s
                          AND FK_tst_que_id = %s
                        """,
                        (
                            answer_id,
                            question_id,
                        ),
                    )

                    selected_answer = cur.fetchone()

                    if selected_answer is None:
                        return {
                            "error": (
                                f"Answer {answer_id} does "
                                f"not belong to question "
                                f"{question_id}"
                            )
                        }, 400

                    if selected_answer["is_correct"]:
                        score += 1

                    validated_answers.append({
                        "question_id": question_id,
                        "answer_id": answer_id,
                    })

                total_questions = len(question_ids)

                percentage = (
                    score / total_questions * 100
                )

                if percentage >= 80:
                    result = "Excellent Match"
                elif percentage >= 60:
                    result = "Good Match"
                elif percentage >= 40:
                    result = "Moderate Match"
                else:
                    result = "Low Match"

                cur.execute(
                    """
                    INSERT INTO Test_Submissions (
                        FK_memb_id,
                        FK_test_teast_id,
                        score,
                        result
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING
                        PK_test_submission_id AS submission_id
                    """,
                    (
                        member_id,
                        test_id,
                        score,
                        result,
                    ),
                )

                submission = cur.fetchone()

                submission_id = submission["submission_id"]

                for answer in validated_answers:
                    cur.execute(
                        """
                        INSERT INTO
                            Test_Submission_Answers (
                                FK_test_submission_id,
                                FK_tst_que_id,
                                FK_tst_answ_id
                            )
                        VALUES (%s, %s, %s)
                        """,
                        (
                            submission_id,
                            answer["question_id"],
                            answer["answer_id"],
                        ),
                    )

            conn.commit()

        return {
            "message": "Test submitted successfully",
            "score": score,
            "result": result,
        }, 201

    except Exception:
        current_app.logger.exception(
            "Failed to submit test"
        )

        return {
            "error": "Failed to submit test"
        }, 500