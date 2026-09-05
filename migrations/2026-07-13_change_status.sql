ALTER TABLE loan_status DROP CONSTRAINT IF EXISTS loan_status_status_name_check;


ALTER TABLE loan_status ADD CONSTRAINT loan_status_status_name_check 
CHECK (status_name IN ('pending', 'approved', 'rejected', 'borrowed', 'returned', 'overdue'));