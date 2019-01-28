create table visits (
    ip varchar(15),
    country varchar(20),
    os varchar(20),
    browser varchar(20),
    ts timestamp
);

create table stats (
    num int,
    timespan int,
    top_country varchar(20),
    top_os varchar(20),
    top_browser varchar(20)
);
