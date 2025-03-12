import pyodbc
from datetime import datetime, timedelta


class Database:
    def __init__(self):
        self.server = 'EMRECAN'
        self.database = 'SoftwareProject'
        self.username = 'emrec'
        self.driver = '{ODBC Driver 17 for SQL Server}'
        self.connection_string = f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};Trusted_Connection=yes;'
        self.conn = pyodbc.connect(self.connection_string)

    def save_email(self, email):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Patient_table (email, sentEmail, sentEmail2, Time) VALUES (?, ?, ?, GETDATE())", (email, 0, 0))
        self.conn.commit()

    def get_max_patient_id(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(id) AS max_id FROM Patient_table")
        row = cursor.fetchone()
        max_id = row[0] if row[0] else 0
        return max_id

    def update_sent_email(self, email, field):
        cursor = self.conn.cursor()
        cursor.execute(f'UPDATE Patient_table SET {field} = 1 WHERE email = ?', (email,))
        self.conn.commit()

    def get_emails_to_send(self, field, hours_ago):
        cursor = self.conn.cursor()
        threshold_time = datetime.now() - timedelta(hours=hours_ago)
        cursor.execute(f'SELECT email FROM Patient_table WHERE {field} = 0 AND Time < ?', (threshold_time,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]

db = Database()
