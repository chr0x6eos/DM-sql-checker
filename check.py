#!/usr/bin/env python3
import argparse
import csv
import psycopg2

class DB:
    conn = None
    host = ""
    port = 0
    db_name = ""
    username = ""
    password = ""
    verbose = True

    def __init__(self, host: str, port: int, username: str, password: str, db_name: str = '', verbose: bool = True) -> None:
        self.host = host
        self.port = port
        self.db_name = db_name
        self.username = username
        self.password = password
        self.verbose = verbose
        try:
            self.connect()
        except Exception as ex:
            print(
                f'\033[91m[-]\033[39m Could not connect to the DB!\n{ex}')
            exit(1)

    def connect(self):
        """Setup connection using specified params.
        """
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.db_name,
                user=self.username,
                password=self.password
            )
            self.print_debug(
                f"Connected to {self.host}:{self.port} on {self.db_name}!", False)
        except Exception as ex:
            raise ex

    def print_debug(self, message, info=True):
        if self.verbose:
            if info:
                data = "\033[34m[*]\033[39m"
            else:
                data = "\033[92m[+]\033[39m"
            print(f"{data} {message}")

    def exec_sql(self, sql, data):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (data))
                self.conn.commit()
                return cursor.fetchall()
        except Exception as ex:
            print(
                f"\033[91m[-]\033[39m Could not run query: {sql} because of an error.\n{ex}")
            exit(1)

    def csv_to_list(self, csv_name):
        # gets data from the csv file and puts it into a list of lists
        # for accessing the data: data_list[row_number][column_number]
        data_list = []
        with open(csv_name, 'r', encoding='utf-8') as csvfile:
            data_squads = csv.reader(csvfile)
            for row in data_squads:
                # to remove all the ', to have no collisions in the code later on
                new_row = []
                for element in row:
                    if isinstance(element, str):
                        element = element.replace("'", "`")
                    new_row.append(element)

                data_list.append(new_row)
            # deletes the fist row, which contains the table heads
            # optional:uncomment if this makes working with the data easier for you
            #del data_list[0]
        return data_list

    def check(self, file):
        sql_result = []
        #with open(file, 'r') as f:
        sql = "".join(file.readlines())
        sql_result = sorted([[str(y) for y in x]
                            for x in self.exec_sql(sql, [])])
        expected_result = sorted([x for x in self.csv_to_list(
            f'references/{file.name.split(".")[0].upper()}_ref.csv')])

        # Clear empty values
        if [] in sql_result:
            sql_result.remove([])
        if [] in expected_result:
            expected_result.remove([])

        self.print_debug(f'Result of query:\n{sql_result}')
        self.print_debug(f'Expected results:\n{expected_result}')
        if sql_result == expected_result:
            return True
        else:
            print(
                f'\033[93m[!]\033[39m Unexpected results in sql-query:\n{[result if result not in expected_result else None for result in sql_result]}')
            print(f'Expected:\n{expected_result}')
            return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='DM Query comparer by Simon Possegger')
    parser.add_argument(
        '-H', '--host', help='Host the datbase is running on (Default: db)', default='db', type=str)
    parser.add_argument(
        '-P', '--port', help='Port the database is running on (Default: 5432)', default=5432, type=int)
    parser.add_argument(
        '-d', '--db', help='Database to connect to (Default: dm)', default='dm', type=str)
    parser.add_argument(
        '-u', '--user', help='Username for connecting to the database (Default: postgres)', default='postgres', type=str)
    parser.add_argument(
        '-p', '--password', help='Password for connecting to the database (Default: postgres)', default='postgres', type=str)
    parser.add_argument(
        '-v', '--verbose', help='Show verbose', action='store_true'
    )
    parser.add_argument(
        '-s', '--sql', help='Select sql to run', required=True, type=argparse.FileType('r'), nargs='+'
    )

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        exit(1)

    db = DB(args.host, args.port, args.user,
            args.password, args.db, args.verbose)

    if(len(args.sql) > 0):
        for sql in args.sql:
            if db.check(sql):
                print(
                    f'\033[92m[+]\033[39m Query {sql.name} match expected result!')
            else:
                print(f'\033[91m[-]\033[39m Query {sql.name} does not match!')
