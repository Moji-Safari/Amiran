ALTER TABLE librarian
RENAME COLUMN branch_id TO FK_branch_id;

ALTER TABLE librarian
RENAME COLUMN librarian_id TO PK_librarian_id;

ALTER TABLE Author
RENAME COLUMN author_id TO PK_author_id;

ALTER TABLE Author_book
RENAME COLUMN auth_book_id TO PK_auth_book_id;

ALTER TABLE Author_book
RENAME COLUMN author_id TO FK_author_id;

ALTER TABLE Author_book
RENAME COLUMN book_id TO FK_book_id;

ALTER TABLE Members
RENAME COLUMN memb_id TO PK_memb_id;

ALTER TABLE Members
RENAME COLUMN branch_id TO FK_branch_id;


ALTER TABLE loan_status
RENAME COLUMN loanstatus_id TO PK_loanstatus_id;

ALTER TABLE loan
RENAME COLUMN loan_id TO PK_loan_id;

ALTER TABLE loan
RENAME COLUMN branch_id TO FK_branch_id;

ALTER TABLE loan
RENAME COLUMN book_id TO FK_book_id;

ALTER TABLE loan
RENAME COLUMN memb_id TO FK_memb_id;

-- Notification
ALTER TABLE Notification
RENAME COLUMN notif_id TO PK_notif_id;

ALTER TABLE Notification
RENAME COLUMN memb_id TO FK_memb_id;



ALTER TABLE Test_Questions
RENAME COLUMN tst_que_id TO PK_tst_que_id;

ALTER TABLE Test_Questions
RENAME COLUMN test_teast_id TO FK_test_teast_id;



ALTER TABLE Test_Answers
RENAME COLUMN tst_answ_id TO PK_tst_answ_id;

ALTER TABLE Test_Answers
RENAME COLUMN tst_que_id TO FK_tst_que_id;









