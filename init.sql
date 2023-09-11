
-- DROP TABLE IF EXISTS public.users;

CREATE TABLE IF NOT EXISTS public.users
(
    id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
    fullname character varying(500) COLLATE pg_catalog."default" NOT NULL,
    username character varying(300) COLLATE pg_catalog."default" NOT NULL,
    email character varying(500) COLLATE pg_catalog."default" NOT NULL,
    password character varying(300) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (id)
)

-- DROP TABLE IF EXISTS public.notes;
CREATE TABLE IF NOT EXISTS public.notes
(
    id integer NOT NULL DEFAULT nextval('notes_id_seq'::regclass),
    title character varying(300) COLLATE pg_catalog."default" NOT NULL,
    content text COLLATE pg_catalog."default" NOT NULL,
    user_id integer,
    datetime date,
    CONSTRAINT notes_pkey PRIMARY KEY (id),
    CONSTRAINT fk_users FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

-- DROP TABLE IF EXISTS public.todolist;

CREATE TABLE IF NOT EXISTS public.todolist
(
    id integer NOT NULL DEFAULT nextval('todolist_id_seq'::regclass),
    todo text COLLATE pg_catalog."default" NOT NULL,
    user_id integer,
    CONSTRAINT todolist_pkey PRIMARY KEY (id),
    CONSTRAINT fk_users FOREIGN KEY (user_id)
        REFERENCES public.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)