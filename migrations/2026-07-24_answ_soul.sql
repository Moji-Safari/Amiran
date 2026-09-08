CREATE TABLE Test_Submission_Answers (
    PK_submission_answer_id SERIAL PRIMARY KEY,

    FK_test_submission_id INT NOT NULL
        REFERENCES Test_Submissions(PK_test_submission_id)
        ON DELETE CASCADE,

    FK_tst_que_id INT NOT NULL
        REFERENCES Test_Questions(PK_tst_que_id)
        ON DELETE CASCADE,

    FK_tst_answ_id INT NOT NULL
        REFERENCES Test_Answers(PK_tst_answ_id)
        ON DELETE CASCADE,

    UNIQUE (FK_test_submission_id, FK_tst_que_id)
);