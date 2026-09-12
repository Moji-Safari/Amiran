--
-- PostgreSQL database dump
--

\restrict Vy5RCvx2cwVgsrjdlyxoqXbG3IIhsRdrkf0pzNGJiBFhgaFiseYQTPoSgPY4qyl

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: author; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.author (
    pk_author_id integer NOT NULL,
    first_name character varying(100),
    last_name character varying(100),
    birth_date timestamp with time zone
);


ALTER TABLE public.author OWNER TO postgres;

--
-- Name: author_book; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.author_book (
    pk_auth_book_id integer NOT NULL,
    fk_author_id integer,
    fk_book_id integer
);


ALTER TABLE public.author_book OWNER TO postgres;

--
-- Name: author_book_pk_auth_book_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.author_book_pk_auth_book_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.author_book_pk_auth_book_id_seq OWNER TO postgres;

--
-- Name: author_book_pk_auth_book_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.author_book_pk_auth_book_id_seq OWNED BY public.author_book.pk_auth_book_id;


--
-- Name: author_pk_author_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.author_pk_author_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.author_pk_author_id_seq OWNER TO postgres;

--
-- Name: author_pk_author_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.author_pk_author_id_seq OWNED BY public.author.pk_author_id;


--
-- Name: books; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.books (
    book_id integer CONSTRAINT books_pk_book_id_not_null NOT NULL,
    title character varying(255) NOT NULL,
    isbn character varying(20),
    publication_year integer,
    genre character varying(100),
    added_at timestamp with time zone DEFAULT now(),
    cover_path character varying(255)
);


ALTER TABLE public.books OWNER TO postgres;

--
-- Name: books_pk_book_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.books_pk_book_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.books_pk_book_id_seq OWNER TO postgres;

--
-- Name: books_pk_book_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.books_pk_book_id_seq OWNED BY public.books.book_id;


--
-- Name: branches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.branches (
    branch_id integer CONSTRAINT branches_pk_branch_id_not_null NOT NULL,
    branch_name character varying(255),
    address text,
    phone character varying(50),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.branches OWNER TO postgres;

--
-- Name: branches_pk_branch_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.branches_pk_branch_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.branches_pk_branch_id_seq OWNER TO postgres;

--
-- Name: branches_pk_branch_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.branches_pk_branch_id_seq OWNED BY public.branches.branch_id;


--
-- Name: librarian; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.librarian (
    pk_librarian_id integer NOT NULL,
    fk_branch_id integer,
    name character varying(255),
    email character varying(255) NOT NULL,
    phone character varying(50),
    hire_date timestamp with time zone,
    user_id integer
);


ALTER TABLE public.librarian OWNER TO postgres;

--
-- Name: librarian_pk_librarian_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.librarian_pk_librarian_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.librarian_pk_librarian_id_seq OWNER TO postgres;

--
-- Name: librarian_pk_librarian_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.librarian_pk_librarian_id_seq OWNED BY public.librarian.pk_librarian_id;


--
-- Name: loan; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.loan (
    pk_loan_id integer NOT NULL,
    fk_branch_id integer,
    fk_book_id integer,
    loanstatus_id integer,
    fk_memb_id integer,
    loan_date timestamp with time zone DEFAULT now(),
    due_date timestamp with time zone,
    return_date timestamp with time zone
);


ALTER TABLE public.loan OWNER TO postgres;

--
-- Name: loan_pk_loan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.loan_pk_loan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.loan_pk_loan_id_seq OWNER TO postgres;

--
-- Name: loan_pk_loan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.loan_pk_loan_id_seq OWNED BY public.loan.pk_loan_id;


--
-- Name: loan_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.loan_status (
    pk_loanstatus_id integer NOT NULL,
    status_name character varying(50),
    description text,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT loan_status_status_name_check CHECK (((status_name)::text = ANY ((ARRAY['pending'::character varying, 'approved'::character varying, 'rejected'::character varying, 'borrowed'::character varying, 'returned'::character varying, 'overdue'::character varying])::text[])))
);


ALTER TABLE public.loan_status OWNER TO postgres;

--
-- Name: loan_status_pk_loanstatus_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.loan_status_pk_loanstatus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.loan_status_pk_loanstatus_id_seq OWNER TO postgres;

--
-- Name: loan_status_pk_loanstatus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.loan_status_pk_loanstatus_id_seq OWNED BY public.loan_status.pk_loanstatus_id;


--
-- Name: members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.members (
    pk_memb_id integer NOT NULL,
    fk_branch_id integer,
    first_name character varying(100),
    last_name character varying(100),
    email character varying(255) NOT NULL,
    phone character varying(50),
    membership_type character varying(50),
    join_date timestamp with time zone DEFAULT now(),
    user_id integer
);


ALTER TABLE public.members OWNER TO postgres;

--
-- Name: members_pk_memb_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.members_pk_memb_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.members_pk_memb_id_seq OWNER TO postgres;

--
-- Name: members_pk_memb_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.members_pk_memb_id_seq OWNED BY public.members.pk_memb_id;


--
-- Name: notification; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification (
    pk_notif_id integer CONSTRAINT notification_notif_id_not_null NOT NULL,
    fk_memb_id integer,
    message text,
    sent_date timestamp with time zone DEFAULT now()
);


ALTER TABLE public.notification OWNER TO postgres;

--
-- Name: notification_notif_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_notif_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notification_notif_id_seq OWNER TO postgres;

--
-- Name: notification_notif_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_notif_id_seq OWNED BY public.notification.pk_notif_id;


--
-- Name: test_answers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test_answers (
    pk_tst_answ_id integer CONSTRAINT test_answers_tst_answ_id_not_null NOT NULL,
    fk_tst_que_id integer CONSTRAINT test_answers_tst_que_id_not_null NOT NULL,
    answer_text text,
    is_correct boolean DEFAULT false,
    answered_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.test_answers OWNER TO postgres;

--
-- Name: test_answers_tst_answ_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.test_answers_tst_answ_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.test_answers_tst_answ_id_seq OWNER TO postgres;

--
-- Name: test_answers_tst_answ_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.test_answers_tst_answ_id_seq OWNED BY public.test_answers.pk_tst_answ_id;


--
-- Name: test_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test_questions (
    pk_tst_que_id integer NOT NULL,
    question_text text,
    fk_test_teast_id integer,
    question_type character varying(50),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.test_questions OWNER TO postgres;

--
-- Name: test_questions_pk_tst_que_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.test_questions_pk_tst_que_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.test_questions_pk_tst_que_id_seq OWNER TO postgres;

--
-- Name: test_questions_pk_tst_que_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.test_questions_pk_tst_que_id_seq OWNED BY public.test_questions.pk_tst_que_id;


--
-- Name: test_submission_answers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test_submission_answers (
    pk_submission_answer_id integer NOT NULL,
    fk_test_submission_id integer NOT NULL,
    fk_tst_que_id integer NOT NULL,
    fk_tst_answ_id integer NOT NULL
);


ALTER TABLE public.test_submission_answers OWNER TO postgres;

--
-- Name: test_submission_answers_pk_submission_answer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.test_submission_answers_pk_submission_answer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.test_submission_answers_pk_submission_answer_id_seq OWNER TO postgres;

--
-- Name: test_submission_answers_pk_submission_answer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.test_submission_answers_pk_submission_answer_id_seq OWNED BY public.test_submission_answers.pk_submission_answer_id;


--
-- Name: test_submissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test_submissions (
    pk_test_submission_id integer NOT NULL,
    fk_memb_id integer NOT NULL,
    fk_test_teast_id integer NOT NULL,
    score integer NOT NULL,
    result text NOT NULL,
    submitted_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.test_submissions OWNER TO postgres;

--
-- Name: test_submissions_pk_test_submission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.test_submissions_pk_test_submission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.test_submissions_pk_test_submission_id_seq OWNER TO postgres;

--
-- Name: test_submissions_pk_test_submission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.test_submissions_pk_test_submission_id_seq OWNED BY public.test_submissions.pk_test_submission_id;


--
-- Name: test_task; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test_task (
    pk_test_teast_id integer NOT NULL,
    title character varying(255),
    description text,
    max_score integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.test_task OWNER TO postgres;

--
-- Name: test_task_pk_test_teast_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.test_task_pk_test_teast_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.test_task_pk_test_teast_id_seq OWNER TO postgres;

--
-- Name: test_task_pk_test_teast_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.test_task_pk_test_teast_id_seq OWNED BY public.test_task.pk_test_teast_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id bigint NOT NULL,
    email character varying(255) NOT NULL,
    password_hash text NOT NULL,
    role character varying(20) DEFAULT 'member'::character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT users_role_check CHECK (((role)::text = ANY ((ARRAY['member'::character varying, 'librarian'::character varying, 'admin'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: author pk_author_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.author ALTER COLUMN pk_author_id SET DEFAULT nextval('public.author_pk_author_id_seq'::regclass);


--
-- Name: author_book pk_auth_book_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.author_book ALTER COLUMN pk_auth_book_id SET DEFAULT nextval('public.author_book_pk_auth_book_id_seq'::regclass);


--
-- Name: books book_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books ALTER COLUMN book_id SET DEFAULT nextval('public.books_pk_book_id_seq'::regclass);


--
-- Name: branches branch_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches ALTER COLUMN branch_id SET DEFAULT nextval('public.branches_pk_branch_id_seq'::regclass);


--
-- Name: librarian pk_librarian_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.librarian ALTER COLUMN pk_librarian_id SET DEFAULT nextval('public.librarian_pk_librarian_id_seq'::regclass);


--
-- Name: loan pk_loan_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loan ALTER COLUMN pk_loan_id SET DEFAULT nextval('public.loan_pk_loan_id_seq'::regclass);


--
-- Name: loan_status pk_loanstatus_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loan_status ALTER COLUMN pk_loanstatus_id SET DEFAULT nextval('public.loan_status_pk_loanstatus_id_seq'::regclass);


--
-- Name: members pk_memb_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.members ALTER COLUMN pk_memb_id SET DEFAULT nextval('public.members_pk_memb_id_seq'::regclass);


--
-- Name: notification pk_notif_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification ALTER COLUMN pk_notif_id SET DEFAULT nextval('public.notification_notif_id_seq'::regclass);


--
-- Name: test_answers pk_tst_answ_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_answers ALTER COLUMN pk_tst_answ_id SET DEFAULT nextval('public.test_answers_tst_answ_id_seq'::regclass);


--
-- Name: test_questions pk_tst_que_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_questions ALTER COLUMN pk_tst_que_id SET DEFAULT nextval('public.test_questions_pk_tst_que_id_seq'::regclass);


--
-- Name: test_submission_answers pk_submission_answer_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_submission_answers ALTER COLUMN pk_submission_answer_id SET DEFAULT nextval('public.test_submission_answers_pk_submission_answer_id_seq'::regclass);


--
-- Name: test_submissions pk_test_submission_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_submissions ALTER COLUMN pk_test_submission_id SET DEFAULT nextval('public.test_submissions_pk_test_submission_id_seq'::regclass);


--
-- Name: test_task pk_test_teast_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_task ALTER COLUMN pk_test_teast_id SET DEFAULT nextval('public.test_task_pk_test_teast_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Name: author_book author_book_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.author_book
    ADD CONSTRAINT author_book_pkey PRIMARY KEY (pk_auth_book_id);


--
-- Name: author author_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.author
    ADD CONSTRAINT author_pkey PRIMARY KEY (pk_author_id);


--
-- Name: books books_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_pkey PRIMARY KEY (book_id);


--
-- Name: branches branches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_pkey PRIMARY KEY (branch_id);


--
-- Name: librarian librarian_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.librarian
    ADD CONSTRAINT librarian_email_key UNIQUE (email);


--
-- Name: librarian librarian_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.librarian
    ADD CONSTRAINT librarian_pkey PRIMARY KEY (pk_librarian_id);


--
-- Name: librarian librarian_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.librarian
    ADD CONSTRAINT librarian_user_id_key UNIQUE (user_id);


--
-- Name: loan loan_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loan
    ADD CONSTRAINT loan_pkey PRIMARY KEY (pk_loan_id);


--
-- Name: loan_status loan_status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loan_status
    ADD CONSTRAINT loan_status_pkey PRIMARY KEY (pk_loanstatus_id);


--
-- Name: members members_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_email_key UNIQUE (email);


--
-- Name: members members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_pkey PRIMARY KEY (pk_memb_id);


--
-- Name: members members_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_user_id_key UNIQUE (user_id);


--
-- Name: notification notification_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (pk_notif_id);


--
-- Name: test_answers test_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_answers
    ADD CONSTRAINT test_answers_pkey PRIMARY KEY (pk_tst_answ_id);


--
-- Name: test_answers test_answers_tst_que_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_answers
    ADD CONSTRAINT test_answers_tst_que_id_key UNIQUE (fk_tst_que_id);


--
-- Name: test_questions test_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_questions
    ADD CONSTRAINT test_questions_pkey PRIMARY KEY (pk_tst_que_id);


--
-- Name: test_submission_answers test_submission_answers_fk_test_submission_id_fk_tst_que_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_submission_answers
    ADD CONSTRAINT test_submission_answers_fk_test_submission_id_fk_tst_que_id_key UNIQUE (fk_test_submission_id, fk_tst_que_id);


--
-- Name: test_submission_answers test_submission_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_submission_answers
    ADD CONSTRAINT test_submission_answers_pkey PRIMARY KEY (pk_submission_answer_id);


--
-- Name: test_submissions test_submissions_fk_memb_id_fk_test_teast_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_submissions
    ADD CONSTRAINT test_submissions_fk_memb_id_fk_test_teast_id_key UNIQUE (fk_memb_id, fk_test_teast_id);


--
-- Name: test_submissions test_submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_submissions
    ADD CONSTRAINT test_submissions_pkey PRIMARY KEY (pk_test_submission_id);


--
-- Name: test_task test_task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_task
    ADD CONSTRAINT test_task_pkey PRIMARY KEY (pk_test_teast_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: idx_author_book_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_author_book_unique ON public.author_book USING btree (fk_author_id, fk_book_id);


--
-- Name: idx_books_genre; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_books_genre ON public.books USING btree (genre);


--
-- Name: idx_loan_book_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_loan_book_id ON public.loan USING btree (fk_book_id);


--
-- Name: idx_loan_member_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_loan_member_id ON public.loan USING btree (fk_memb_id);


--
-- Name: idx_notification_member_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notification_member_id ON public.notification USING btree (fk_memb_id);


--
-- Name: author_book author_book_fk_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.author_book
    ADD CONSTRAINT author_book_fk_author_id_fkey FOREIGN KEY (fk_author_id) REFERENCES public.author(pk_author_id) ON DELETE CASCADE;


--
-- Name: author_book author_book_fk_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.author_book
    ADD CONSTRAINT author_book_fk_book_id_fkey FOREIGN KEY (fk_book_id) REFERENCES public.books(book_id) ON DELETE CASCADE;


--
-- Name: librarian librarian_fk_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.librarian
    ADD CONSTRAINT librarian_fk_branch_id_fkey FOREIGN KEY (fk_branch_id) REFERENCES public.branches(branch_id) ON DELETE SET NULL;


--
-- Name: librarian librarian_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.librarian
    ADD CONSTRAINT librarian_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: loan loan_fk_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loan
    ADD CONSTRAINT loan_fk_book_id_fkey FOREIGN KEY (fk_book_id) REFERENCES public.books(book_id) ON DELETE CASCADE;


--
-- Name: loan loan_fk_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loan
    ADD CONSTRAINT loan_fk_branch_id_fkey FOREIGN KEY (fk_branch_id) REFERENCES public.branches(branch_id) ON DELETE SET NULL;


--
-- Name: loan loan_fk_loanstatus_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loan
    ADD CONSTRAINT loan_fk_loanstatus_id_fkey FOREIGN KEY (loanstatus_id) REFERENCES public.loan_status(pk_loanstatus_id) ON DELETE CASCADE;


--
-- Name: loan loan_memb_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loan
    ADD CONSTRAINT loan_memb_id_fkey FOREIGN KEY (fk_memb_id) REFERENCES public.members(pk_memb_id) ON DELETE CASCADE;


--
-- Name: members members_fk_branch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_fk_branch_id_fkey FOREIGN KEY (fk_branch_id) REFERENCES public.branches(branch_id) ON DELETE SET NULL;


--
-- Name: members members_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.members
    ADD CONSTRAINT members_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: notification notification_memb_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_memb_id_fkey FOREIGN KEY (fk_memb_id) REFERENCES public.members(pk_memb_id) ON DELETE CASCADE;


--
-- Name: test_answers test_answers_tst_que_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_answers
    ADD CONSTRAINT test_answers_tst_que_id_fkey FOREIGN KEY (fk_tst_que_id) REFERENCES public.test_questions(pk_tst_que_id) ON DELETE CASCADE;


--
-- Name: test_questions test_questions_test_teast_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_questions
    ADD CONSTRAINT test_questions_test_teast_id_fkey FOREIGN KEY (fk_test_teast_id) REFERENCES public.test_task(pk_test_teast_id) ON DELETE CASCADE;


--
-- Name: test_submission_answers test_submission_answers_fk_test_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_submission_answers
    ADD CONSTRAINT test_submission_answers_fk_test_submission_id_fkey FOREIGN KEY (fk_test_submission_id) REFERENCES public.test_submissions(pk_test_submission_id) ON DELETE CASCADE;


--
-- Name: test_submission_answers test_submission_answers_fk_tst_answ_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_submission_answers
    ADD CONSTRAINT test_submission_answers_fk_tst_answ_id_fkey FOREIGN KEY (fk_tst_answ_id) REFERENCES public.test_answers(pk_tst_answ_id) ON DELETE CASCADE;


--
-- Name: test_submission_answers test_submission_answers_fk_tst_que_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_submission_answers
    ADD CONSTRAINT test_submission_answers_fk_tst_que_id_fkey FOREIGN KEY (fk_tst_que_id) REFERENCES public.test_questions(pk_tst_que_id) ON DELETE CASCADE;


--
-- Name: test_submissions test_submissions_fk_memb_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_submissions
    ADD CONSTRAINT test_submissions_fk_memb_id_fkey FOREIGN KEY (fk_memb_id) REFERENCES public.members(pk_memb_id) ON DELETE CASCADE;


--
-- Name: test_submissions test_submissions_fk_test_teast_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.test_submissions
    ADD CONSTRAINT test_submissions_fk_test_teast_id_fkey FOREIGN KEY (fk_test_teast_id) REFERENCES public.test_task(pk_test_teast_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict Vy5RCvx2cwVgsrjdlyxoqXbG3IIhsRdrkf0pzNGJiBFhgaFiseYQTPoSgPY4qyl

