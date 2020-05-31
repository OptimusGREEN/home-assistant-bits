from mysql.connector import MySQLConnection, Error
from mysql.connector import errorcode
import logging

from globals.modules.strings_lib import list_from_string


class DataBase():
    def __init__(self, user, password, db="ha_retained_data", host="127.0.0.1", port="3306", auto_create=True):
        """[summary]

        Arguments:
            user {str} -- [mysql username]
            password {str} -- [mysql password]

        Keyword Arguments:
            db {str} -- [database to use] (default: {"ha_retained_data"})
            host {str} -- [hostname or ip of mysql server] (default: {"127.0.0.1"})
            port {str} -- [port used for mysql server] (default: {"3306"})
            auto_create {bool} -- [True: automatically create the database if it doesn't exist] (default: {True})
        """
        self.user = user
        self.password = password
        self.db = db
        self.host = host
        self.port = port
        self.cnx = None
        self.cursor = None
        self.auto_create = auto_create

    def read(self, table="", known_col="", row_id="", target_col="", operation=None, auto_dc=True, *args, **kwargs):

        self.__connect()
        if operation:
            self.cursor.execute(operation)
        else:
            operation = "SELECT {} from {} WHERE {}='{}'".format(target_col, table, known_col, row_id)
            self.cursor.execute(operation)
        result = self.cursor.fetchone()[0]
        if auto_dc:
            self.__disconnect()
        return result

    def write(self, table, headings, data, row2check=None, auto_dc=True, *args, **kwargs):

        self.__connect()
        if not row2check:
            if isinstance(data, (list, tuple)):
                row2check = data[0]
            elif isinstance(data, str):
                row2check = list_from_string(data)[0]
        head2check = headings[0]
        if isinstance(headings, str):
            head2check = list_from_string(headings)[0]
        if not self.__check_table_exists(table):
            logging.info("No table called '{}'".format(table))
            self.__create_table(table, headings)
        if not self.__check_row_exists(table, head2check, row2check):
            stmt = self.__build_insert_str(table, headings)
        else:
            stmt = self.__build_update_str(table, headings, data)
            data = None
        self.cursor.execute(stmt, params=data)
        self.cnx.commit()
        if auto_dc:
            self.__disconnect()

    def __connect(self):
        try:
            self.cnx = MySQLConnection(user=self.user, password=self.password, host=self.host, port=self.port)
            self.cursor = self.cnx.cursor(buffered=True)
            logging.info(self.cnx.get_server_info())
            self.__check_db_exists()
        except Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.info("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.info("Database does not exist")
            else:
                logging.error(str(err))

    def __disconnect(self):
        logging.debug("disconnecting")
        try:
            self.cursor.close()
            self.cnx.close()
            self.cnx = None
            self.cursor = None
        except Error as err:
            logging.error("Problem Disconnecting: {}".format(err))
            exit(1)

    def __create_database(self):
        try:
            self.cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.db))
        except Error as err:
            logging.warning("Failed creating database: {}".format(err))
            exit(1)

    def __create_table(self, table, headings):
        h_list = []
        if isinstance(headings, (list, tuple)):
            for h in headings:
                h_list.append(str(h))
        else:
            h2_list = headings.split(",")
            for h in h2_list:
                new_h = h.strip()
                h_list.append(new_h)
        print(h_list)
        TABLES = {}
        t = "`{}` varchar(80) NOT NULL, "
        headings_list = []
        for h in h_list:
            nstr = t.format(h)
            headings_list.append(nstr)
        headings_insert = ""
        for h in headings_list:
            headings_insert += h
        pk = h_list[0]
        TABLES[table] = ("CREATE TABLE `{}` ({}PRIMARY KEY (`{}`)) ENGINE=InnoDB".format(table, headings_insert, pk))
        table_description = TABLES[table]
        try:
            print("Creating table {}: ".format(table), end='')
            self.cursor.execute(table_description)
        except Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                logging.error("{}: table already exists.".format(table))
            else:
                logging.error(err.msg)
        else:
            logging.info("Table created")

    def __check_db_exists(self):
        try:
            self.cursor.execute("USE {}".format(self.db))
        except Error as err:
            logging.info("Database {} does not __exists.".format(self.db))
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                if self.auto_create:
                    self.__create_database()
                    logging.info("Database {} created successfully.".format(self.db))
            else:
                logging.error(str(err))
                exit(1)

    def __check_table_exists(self, tablename):
        self.__connect()
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))
        if self.cursor.fetchone()[0] == 1:
            return True
        return False

    def __check_row_exists(self, table, heading, row2check):
        self.__connect()
        stmt = "SELECT EXISTS(SELECT * from {} WHERE {}='{}')".format(table, heading, row2check)
        self.cursor.execute(stmt)
        if self.cursor.fetchone()[0]:
            return True
        return False

    def __build_insert_str(self, table, headings):
        if isinstance(headings, str):
            # ("INSERT INTO employees (emp_no, first_name, last_name, hire_date) " "VALUES (%s, %s, %s, %s)")
            num = headings.split(",")
            vals = ""
            for x in range(len(num)):
                vals += "{}".format("%s, ")
        elif isinstance(headings, (list, tuple)):
            vals = ""
            for x in range(len(headings)):
                vals += "{}".format("%s, ")
            h = ""
            for x in headings:
                h += "{}, ".format(x)
            headings = h.rsplit(',', 1)[0]
        else:
            logging.error("Not suitable types provided")
            return
        vals = vals.rsplit(',', 1)[0]
        output1 = "INSERT INTO {} ({}) ".format(table, headings)
        output2 = "VALUES({})".format(vals)
        output = output1 + output2
        logging.debug(output)
        print(output)
        return output

    def __build_update_str(self, table, headings, values):
        if isinstance(headings, str):
            headings = list_from_string(headings)
        if isinstance(values, str):
            values = list_from_string(values)
        pairs_count = len(headings)
        if pairs_count > 1:
            s = ""
            for k,v in zip(headings, values):
                s += '{}="{}", '.format(k,v)
            s = s.rsplit(',', 1)[0]
        else:
            s = "{}={}".format(headings[0], values[0])
        output1 = "UPDATE {} SET {} ".format(table, s)
        output2 = 'WHERE {}="{}"'.format(headings[0], values[0])
        output = output1 + output2
        logging.debug(output)
        print(output)
        return output

