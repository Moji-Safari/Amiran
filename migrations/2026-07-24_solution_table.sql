ALTER TABLE Test_Task
RENAME COLUMN test_teast_id TO PK_test_teast_id;


CREATE IF NOT EXISTS TABLE Test_Submissions (
    PK_test_submission_id SERIAL PRIMARY KEY,
    FK_memb_id INT NOT NULL
        REFERENCES Members(PK_memb_id)
        ON DELETE CASCADE,

    FK_test_teast_id INT NOT NULL
        REFERENCES Test_Task(PK_test_teast_id)
        ON DELETE CASCADE,

    score INT NOT NULL,
    result TEXT NOT NULL,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (FK_memb_id, FK_test_teast_id)
);