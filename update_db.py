import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

# Add "name" column if it doesn't exist
try:
    c.execute('ALTER TABLE users ADD COLUMN name TEXT')
    print("✅ 'name' column added to users table.")
except sqlite3.OperationalError:
    print("ℹ️ 'name' column already exists, skipping.")

conn.commit()
conn.close()
