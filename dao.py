import psycopg2
import logging
import psycopg2.extras

logger = logging.getLogger()

INSERT_FOUR_DIGITS_STATEMENT = """INSERT INTO four_digits (entry, entry_size, multiplier, user_id, bet_type_id, draw_id) 
                                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING four_digits_id, entry, entry_size, multiplier, added_on"""


class DAO:
    def __init__(self, database_url):
        self.database_url = database_url

    def get_connection(self):
        return psycopg2.connect(self.database_url, sslmode='allow', cursor_factory=psycopg2.extras.DictCursor)

    @staticmethod
    def close_connection(conn):
        if conn is not None:
            conn.close()

    def insert_entry(self, entry, entry_size, multiplier, user_id, bet_type_id, draw_id):
        conn = None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(INSERT_FOUR_DIGITS_STATEMENT, (entry, entry_size, multiplier, user_id, bet_type_id, draw_id))
            row = cursor.fetchone()

            if row is None:
                raise ValueError("No data returned from database.")

            cursor.close()
            conn.commit()
            return row
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise error
        finally:
            self.close_connection(conn)
