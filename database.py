import sqlite3

class Database:
    def _init_(self):
        self.conn = sqlite3.connect("student.db")
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS student(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                roll TEXT,
                sem TEXT,
                section TEXT,
                branch TEXT
            )
        """)
        self.conn.commit()

    def save_student(self, name, roll, sem, section, branch):
        self.cursor.execute(
            "INSERT INTO student(name, roll, sem, section, branch) VALUES (?, ?, ?, ?, ?)",
            (name, roll, sem, section, branch)
        )
        self.conn.commit()

    def get_student(self):
        self.cursor.execute("SELECT name, roll, sem, section, branch FROM student ORDER BY id DESC LIMIT 1")
        return self.cursor.fetchone()