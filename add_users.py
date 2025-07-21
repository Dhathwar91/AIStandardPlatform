import sqlite3

# Connect to the existing DB
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Insert dummy users
dummy_users = [
    ('test1@example.com', 'Test@123'),
    ('test2@example.com', 'Password@123'),
    ('hello@example.com', 'Hello@1234')
]

# Insert them into the users table
for email, password in dummy_users:
    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    except sqlite3.IntegrityError:
        print(f"User {email} already exists, skipping...")

# Save changes and close
conn.commit()
conn.close()

print("✅ Dummy users added to users.db")
