
import sqlite3
from json import load
from unittest import result

TYPES = {
    int: "INTEGER",
    float: "REAL",
    str: "TEXT",
    bytes: "BLOB",
    bool: "BOOLEAN"
}


class Database():

    def __init__(self, path):
        self.connect = sqlite3.connect(path)
        self.cursor = self.connect.cursor()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.connect.commit()
        self.cursor.close()
        self.connect.close()

    def sql_type(self, value):
        return {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            bytes: "BLOB",
            bool: "BOOLEAN"
        }[type(value)]

    def make_head(self, full_row):
        head = ""

        for colname in full_row:
            head += f"{colname} {self.sql_type(full_row[colname])}, "

        return head.strip(", ")

    def make_insertion(self, data):
        colnames = ""
        values = ""

        for (colname, value) in data.items():
            colnames += f"{colname}, "

            if type(value) == str:
                value = "'" + value.replace("'", "''") + "'"

            values += f"{value}, "

        return (colnames.strip(", "), values.strip(", "))

    def make_fetch(self, items):
        fetch_ = ""

        for item in items:
            fetch_ += f"{item}, "

        return fetch_.strip(", ")

    def create_table(self, name, full_row):
        self.cursor.execute(
            f"""CREATE TABLE {name} ({self.make_head(full_row)});""")

    def create_table_from_file(self, name, file):
        with open(file) as ipt:
            items = load(ipt)

        self.create_table(name, items[0])

        for item in items:
            self.insert(name, item)

    def insert(self, table, row):
        colnames, values = self.make_insertion(row)

        self.cursor.execute(
            f"""INSERT INTO {table} ({colnames}) VALUES ({values});""")

    def fetch(self, table, expression, items):
        results = []

        self.cursor.execute(
            f"""SELECT {self.make_fetch(items)} FROM {table} WHERE {expression}""")
        fetch_result = self.cursor.fetchall()

        for values in fetch_result:
            result = {}

            for (item, value) in zip(items, values):
                result[item] = value

            results.append(result)

        return results


class Core():
    def parse_database_expression(self, expression):
        equal_sign_index = expression.find("=")

        colname = expression[0:equal_sign_index-1]
        sign = expression[equal_sign_index-1:equal_sign_index+1]
        value = expression[equal_sign_index+1:len(expression)]

        return (colname, sign, value)

    def adapt_database_expression(self, expression):
        colname, sign, value = self.parse_database_expression(expression)

        if sign == "|=":
            return f"{colname}={value}"
        elif sign == "*=":
            return f"{colname} LIKE '%{value}%'"
