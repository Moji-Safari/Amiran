
SET TIME ZONE 'UTC';

CREATE TABLE Branches (
    branch_id SERIAL PRIMARY KEY,
    branch_name VARCHAR(255),
    address TEXT,
    phone VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW() 
);


CREATE TABLE Librarian (
    librarian_id SERIAL PRIMARY KEY,
    branch_id INT REFERENCES Branches(branch_id) ON DELETE SET NULL,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    hire_date TIMESTAMPTZ
);


CREATE TABLE Books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    isbn VARCHAR(20),
    publication_year INT,
    genre VARCHAR(100),
    added_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE Author (
    author_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    birth_date TIMESTAMPTZ
);


CREATE TABLE Author_book (
    auth_book_id SERIAL PRIMARY KEY,
    author_id INT REFERENCES Author(author_id)ON DELETE CASCADE,
    book_id INT REFERENCES Books(book_id) ON DELETE CASCADE
);


CREATE TABLE Members (
    memb_id SERIAL PRIMARY KEY,
    branch_id INT REFERENCES Branches(branch_id) ON DELETE SET NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    membership_type VARCHAR(50),
    join_date TIMESTAMPTZ DEFAULT NOW()
   
);


CREATE TABLE Loan_Status (
    loanstatus_id SERIAL PRIMARY KEY,
    status_name VARCHAR(50) CHECK (
        status_name IN ('pending', 'approved', 'rejected', 'borrowed', 'returned')
    ),
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE Loan (
    loan_id SERIAL PRIMARY KEY,
    branch_id INT REFERENCES Branches(branch_id) ON DELETE SET NULL,
    book_id INT REFERENCES Books(book_id) ON DELETE CASCADE,
    loanstatus_id INT REFERENCES Loan_Status(loanstatus_id) ON DELETE CASCADE,
    memb_id INT REFERENCES Members(memb_id) ON DELETE CASCADE, 
    loan_date TIMESTAMPTZ DEFAULT NOW(),
    due_date TIMESTAMPTZ,
    return_date TIMESTAMPTZ
);


CREATE TABLE Notification (
    notif_id SERIAL PRIMARY KEY,
    memb_id INT REFERENCES Members(memb_id) ON DELETE CASCADE,
    message TEXT,
    sent_date TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE Test_Task (
    PK_test_teast_id SERIAL PRIMARY KEY, 
    title VARCHAR(255),
    description TEXT,
    max_score INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE Test_Questions (
    tst_que_id SERIAL PRIMARY KEY,
    question_text TEXT,
    test_teast_id INT REFERENCES Test_Task(PK_test_teast_id) ON DELETE CASCADE, 
    question_type VARCHAR(50), 
    created_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE Test_Answers (
    tst_answ_id SERIAL PRIMARY KEY,
    tst_que_id INT UNIQUE NOT NULL REFERENCES Test_Questions(tst_que_id),
    answer_text TEXT,
    is_correct BOOLEAN DEFAULT FALSE,
    answered_at TIMESTAMPTZ DEFAULT NOW()
);



CREATE INDEX idx_loan_book_id ON Loan (book_id);



CREATE INDEX idx_loan_member_id ON Loan (memb_id);



CREATE UNIQUE INDEX idx_author_book_unique ON Author_book (author_id, book_id);


CREATE INDEX idx_notification_member_id ON Notification (memb_id);