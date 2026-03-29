from datetime import datetime, timezone

import mariadb
import sys

class TTDatabase:

    create_table_data_sql = """
    CREATE TABLE IF NOT EXISTS `tt_data` (
      `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
      `date` DATE NOT NULL,
      `minutes` INT NOT NULL,
      `category` VARCHAR(100) NOT NULL,
      `activity` VARCHAR(200) NOT NULL,
      `description` TEXT,
      `tag` VARCHAR(100),
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    create_table_deals_sql = """
    CREATE TABLE IF NOT EXISTS `tt_deals` (
      `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
      `name` VARCHAR(100) NOT NULL,
      `description` TEXT,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    create_table_activity_sql = """
    CREATE TABLE IF NOT EXISTS `tt_activity` (
      `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
      `name` VARCHAR(100) NOT NULL,
      `description` TEXT,
      `deal_id` INT UNSIGNED DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    def __init__(self):
        try:
            self.conn = mariadb.connect(
                user="admin",
                password="turbopino",
                host="localhost",    # e.g., "localhost" or IP
                port=3306,
                database="my_time_tracker"
            )
        except mariadb.Error as e:
            print(f"Connection error: {e}")
            sys.exit(1)

        self.cur = self.conn.cursor()
        self.create_tables()
        self.add_dummy()


    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute(self.create_table_data_sql)
        cur.execute(self.create_table_deals_sql)
        cur.execute(self.create_table_activity_sql)

    def insert_deal_entry(self, name, description=None):
        sql = """
              INSERT INTO tt_deals (name, description)
              SELECT ?, ? 
              WHERE NOT EXISTS (
                  SELECT 1 FROM tt_deals  
                  WHERE name = ?);
              """
        cur = self.conn.cursor()
        params = (name, description,
                  name)
        cur.execute(sql, params)
        self.conn.commit()
        last_id = cur.lastrowid
        if last_id:
            cur.close()
            return last_id

        cur.execute("""
                    SELECT id
                    FROM tt_deals
                    WHERE name = ?
                    LIMIT 1
                    """, (name,))
        row = cur.fetchone()
        cur.close()
        return row[0] if row else 0

    def insert_activity_entry(self, name, description=None, deal_id=None):
        sql = """
              INSERT INTO tt_activity (name, description,deal_id)
              SELECT ?, ?, ?
              WHERE NOT EXISTS (
                    SELECT 1 FROM tt_activity  
                    WHERE name = ? AND deal_id = ?);
              """
        cur = self.conn.cursor()
        params = (name, description, deal_id,
                  name, deal_id)
        cur.execute(sql, params)
        self.conn.commit()
        last_id = cur.lastrowid
        if last_id:
            cur.close()
            return last_id
        cur.execute("""
                    SELECT id
                    FROM tt_activity
                    WHERE name = ?
                        AND deal_id = ?
                    LIMIT 1
                    """, (name))
        row = cur.fetchone()
        cur.close()
        return row[0] if row else 0

    def insert_data_entry(self, date, minutes, category, activity, description=None, tag=None):
        sql = """
              INSERT INTO tt_data (date, minutes, category, activity, description, tag)
              SELECT ?, ?, ?, ?, ?, ?
              WHERE NOT EXISTS (
                    SELECT 1 FROM tt_data  
                    WHERE date = ? AND minutes = ? AND category = ? AND activity = ?);
              """
        cur = self.conn.cursor()
        params = (date, minutes, category, activity, description, tag,
                  date, minutes, category, activity)
        cur.execute(sql, params)
        self.conn.commit()
        last_id = cur.lastrowid
        if last_id:
            cur.close()
            return last_id
        cur.execute("""
                    SELECT id
                    FROM tt_data
                    WHERE date = ?
                      AND minutes = ?
                      AND category = ?
                      AND activity = ?
                    LIMIT 1
                    """, (date, minutes, category, activity))
        row = cur.fetchone()
        cur.close()
        return row[0] if row else None

    def add_dummy(self):
        deal_dummy = "test deal"
        act_dummy = "test activity"
        deal_id = self.insert_deal_entry(deal_dummy, description="test deal")
        act_id = self.insert_activity_entry(act_dummy, "test activity",deal_id)
        self.insert_data_entry(datetime.fromtimestamp(0, tz=timezone.utc),
                               1, deal_id, act_id,
                               description="test data", tag=None)

    def query(self):
        # Query
        self.cur.execute("SELECT id, name FROM items")
        for (id, name) in self.cur:
            print(id, name)

    def get_deals(self):
        self.cur = self.conn.cursor(dictionary=True)  # dictionary=True -> rows as dicts
        self.cur.execute("SELECT * FROM tt_data")  # or custom query
        rows = self.cur.fetchall()  # returns list of dicts
        return rows

    def close(self):
        self.cur.close()
        self.conn.close()
