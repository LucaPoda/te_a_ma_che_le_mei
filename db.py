import sqlite3

connection_obj: sqlite3.Connection


def init():
    global connection_obj
    # Connecting to sqlite
    # connection object
    connection_obj = sqlite3.connect('data.db')

    # cursor object
    cursor_obj = connection_obj.cursor()

    # Creating table

    table = """
        CREATE TABLE IF NOT EXISTS categories (
            name varchar(32) primary key,
            type varchar(10) not null
        );
    """

    cursor_obj.execute(table)

    table = """
        
        CREATE TABLE IF NOT EXISTS transactions (
            value decimal not null,
            date date default(DATE('now')),
            category varchar(32) not null,
            note varchar(512),
            FOREIGN KEY (category) REFERENCES categories(name)
        );"""

    cursor_obj.execute(table)

    """
    insert = ["INSERT INTO transactions (value, date, category, note) VALUES (100, '2023-05-21', 'Food', 'Bought groceries');",
            "INSERT INTO transactions (value, date, category, note) VALUES (200, '2023-05-20', 'Entertainment', 'Bought movie tickets');",
            "INSERT INTO transactions (value, date, category, note) VALUES (300, '2023-05-19', 'Bills', 'Paid electricity bill');",
            "INSERT INTO transactions (value, date, category, note) VALUES (400, '2023-05-18', 'Food', 'Bought lunch');",
            "INSERT INTO transactions (value, date, category, note) VALUES (500, '2023-03-17', 'Entertainment', 'Bought concert tickets');",
            "INSERT INTO transactions (value, date, category, note) VALUES (600, '2023-03-16', 'Bills', 'Paid water bill');",
            "INSERT INTO transactions (value, date, category, note) VALUES (700, '2023-03-15', 'Food', 'Bought dinner');",
            "INSERT INTO transactions (value, date, category, note) VALUES (800, '2023-06-14', 'Entertainment', 'Bought game tickets');",
            "INSERT INTO transactions (value, date, category, note) VALUES (900, '2023-06-13', 'Bills', 'Paid internet bill');",
            "INSERT INTO transactions (value, date, category, note) VALUES (1000, '2023-06-12', 'Food', 'Bought breakfast');"]
    
    for cmd in insert:
        cursor_obj.execute(cmd)
        connection_obj.commit()
    
    """
    print("Database is Ready")


def get_categories_with_type(type):
    cursor = connection_obj.cursor()
    sql = "SELECT * from categories where type = '{0}' or type = 'both'"
    args = type
    cursor.execute(sql.format(args))
    categories = cursor.fetchall()

    result = []
    for cat in categories:
        result.append(cat[0])

    return result

def get_all_transactions():
    cursor = connection_obj.cursor()
    sql = "SELECT strftime('%Y', date) as year, strftime('%m', date) as month, value, category, note, date " \
          "from transactions " \
          "order by year, month, category, date"
    cursor.execute(sql)
    result = cursor.fetchall()

    return result

def get_all_categories():
    cursor = connection_obj.cursor()
    sql = "SELECT * from categories"
    args = type
    cursor.execute(sql.format(args))
    categories = cursor.fetchall()

    return categories


def insert_transaction(data):
    cursor = connection_obj.cursor()
    cursor.execute("INSERT INTO transactions (value, category, note, date) VALUES {0}".format(data))
    connection_obj.commit()


def insert_category(data):
    cursor = connection_obj.cursor()
    cursor.execute("INSERT INTO categories (name, type) VALUES {0}".format(data))
    connection_obj.commit()


def disconnect():
    global connection_obj
    # Close the connection
    connection_obj.close()