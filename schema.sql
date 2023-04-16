CREATE TABLE IF NOT EXISTS categories (
    name varchar(32) primary key
    type varchar(10) not null
);

CREATE TABLE IF NOT EXISTS transactions (
    value decimal not null,
    date date default(DATE('now')),
    category varchar(32) not null,
    note varchar(512),
    FOREIGN KEY (category) REFERENCES categories(name)
);

