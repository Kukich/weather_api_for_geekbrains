import sqlite3

class SqliteDB:
    def __init__(self):
        conn = self.connect_to_db("city_weather.db")
        cursor = conn.cursor()
        self.conn = conn
        self.cursor = cursor
        self.create_table("cities")

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def connect_to_db(self,dbname):
        try:
            conn = sqlite3.connect(dbname)
            return conn
        except sqlite3.Error as error:
            print("Failed to connect to db ",error)

    def create_table(self,tablename):
        try:
            sql = """
                    create table if not exists cities
                    (id integer primary key autoincrement,
                    city varchar(255) not null,
                    c_date text,
                    temp varchar(255),
                    weather_id integer not null default 0)
                    """
            self.cursor.execute(sql)
            self.conn.commit()
        except sqlite3.Error as error:
            print("Failed to create table ",tablename,": ",error)

    def add_values(self,values):
        sql_insert = """
        insert into cities (city,c_date,temp,weather_id) values (?,?,?,?)
        """
        self.cursor.executemany(sql_insert, values)
        self.conn.commit()

    def get_value_by_city(self,city):
        sql_select = """
        select * from cities where city=?
        """
        self.cursor.execute(sql_select,[(city)])
        return self.cursor.fetchone()

    def edit_value(self,city,temp,c_date,weather_id):
        print("edit_value " + city)
        sql_update = """
        update cities set temp = ? , c_date = ? ,weather_id = ? 
        where city = ?
        """
        self.cursor.execute(sql_update,[temp,c_date,weather_id,city])
        self.conn.commit()
