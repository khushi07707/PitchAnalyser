-- Initial SQL schema for PostgreSQL (generated from EF Core model intentions)
-- Run this as a starting point if you don't use EF migrations.

CREATE TABLE roles (
    id uuid PRIMARY KEY,
    name varchar(100) NOT NULL UNIQUE,
    description text,
    createdat timestamp without time zone NOT NULL,
    updatedat timestamp without time zone,
    isdeleted boolean NOT NULL DEFAULT false
);

CREATE TABLE users (
    id uuid PRIMARY KEY,
    firstname varchar(200) NOT NULL,
    lastname varchar(200),
    email varchar(256) NOT NULL UNIQUE,
    passwordhash text NOT NULL,
    roleid uuid REFERENCES roles(id),
    createdat timestamp without time zone NOT NULL,
    updatedat timestamp without time zone,
    isdeleted boolean NOT NULL DEFAULT false
);

CREATE TABLE startups (
    id uuid PRIMARY KEY,
    name varchar(200) NOT NULL,
    foundername varchar(200) NOT NULL,
    founderemail varchar(256) NOT NULL,
    industry integer,
    fundingstage integer,
    businessdescription text NOT NULL,
    websiteurl varchar(500),
    createdbyid uuid REFERENCES users(id),
    createdat timestamp without time zone NOT NULL,
    updatedat timestamp without time zone,
    isdeleted boolean NOT NULL DEFAULT false
);

CREATE TABLE financial_data (
    id uuid PRIMARY KEY,
    startupid uuid UNIQUE REFERENCES startups(id) ON DELETE CASCADE,
    annualrevenue numeric,
    annualexpenses numeric,
    netprofit numeric,
    currency varchar(10),
    fiscalyear integer,
    createdat timestamp without time zone NOT NULL,
    updatedat timestamp without time zone,
    isdeleted boolean NOT NULL DEFAULT false
);

CREATE TABLE file_records (
    id uuid PRIMARY KEY,
    filename varchar(500) NOT NULL,
    filepath text NOT NULL,
    contenttype varchar(200),
    size bigint,
    uploadedat timestamp without time zone NOT NULL,
    uploadedbyid uuid REFERENCES users(id),
    pitchid uuid,
    createdat timestamp without time zone NOT NULL,
    updatedat timestamp without time zone,
    isdeleted boolean NOT NULL DEFAULT false
);

CREATE TABLE pitches (
    id uuid PRIMARY KEY,
    startupid uuid REFERENCES startups(id) ON DELETE CASCADE,
    title varchar(300),
    uploadedat timestamp without time zone NOT NULL,
    filerecordid uuid UNIQUE REFERENCES file_records(id),
    extractedtext text,
    createdat timestamp without time zone NOT NULL,
    updatedat timestamp without time zone,
    isdeleted boolean NOT NULL DEFAULT false
);

CREATE TABLE pitch_analyses (
    id uuid PRIMARY KEY,
    pitchid uuid UNIQUE REFERENCES pitches(id) ON DELETE CASCADE,
    analysisjson text NOT NULL,
    summary text,
    score double precision,
    recommendations text,
    completedat timestamp without time zone,
    createdat timestamp without time zone NOT NULL,
    updatedat timestamp without time zone,
    isdeleted boolean NOT NULL DEFAULT false
);
