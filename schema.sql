--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP TABLE IF EXISTS public.log_targets;
DROP TABLE IF EXISTS public.guilds;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: guilds; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.guilds (
    record_id bigint NOT NULL,
    guild_id bigint,
    selected_language text
);


--
-- Name: guilds_record_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.guilds ALTER COLUMN record_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.guilds_record_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: log_targets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.log_targets (
    record_id bigint NOT NULL,
    guild_id bigint,
    target bigint[],
    act text,
    d_in bigint[],
    name text,
    priority integer,
    output text,
    other text
);


--
-- Name: log_targets_record_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.log_targets ALTER COLUMN record_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.log_targets_record_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- PostgreSQL database dump complete
--

