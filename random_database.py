import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker library for realistic random data
fake = Faker()

# Database connection
def get_db_connection():
    conn = sqlite3.connect("job_applications.db")
    return conn

# Generate random data
def generate_random_data():
    title = fake.job()
    company = fake.company()
    stage = random.choice(['Applied', 'Interview', 'Offer', 'Rejected'])
    salary = random.randint(30000, 120000)
    date_applied = datetime.now().date() - timedelta(days=random.randint(0, 180))
    deadline = date_applied + timedelta(days=random.randint(10, 90))
    role_type = random.choice(['Full-time', 'Part-time', 'Internship', 'Contract'])
    priority = random.choice([0, 1])  # 0 for low priority, 1 for high priority
    user_id = random.randint(1, 1)  # Adjust user IDs as per your app's user base

    return (title, company, stage, salary, date_applied, deadline, role_type, priority, user_id)

# Insert 1000 random records into the database
def insert_random_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for _ in range(1000):
        data = generate_random_data()
        cursor.execute('''
            INSERT INTO applications (title, company, stage, salary, date_applied, deadline, role_type, priority, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
    
    conn.commit()
    conn.close()
    print("Inserted 1000 random job applications into the database.")

def create_table():
    conn = sqlite3.connect("job_applications.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            stage TEXT NOT NULL,
            salary INTEGER NOT NULL,
            date_applied DATE NOT NULL,
            deadline DATE,
            role_type TEXT,
            priority INTEGER,
            user_id INTEGER
        )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    ''')
    conn.commit()
    conn.close()

# Now call this function before inserting data
create_table()

if __name__ == "__main__":
    insert_random_data()