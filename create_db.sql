CREATE TABLE public.dom
(
    id "char"[] NOT NULL,
    dom "char"[] NOT NULL,
    website "char"[],
    "time" timestamp(6) without time zone[],
    project "char"[],
    next_dom "char"[],
    previous_dom "char"[],
    url "char"[],
    PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.dom
    OWNER to postgres;