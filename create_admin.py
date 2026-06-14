import mysql.connector
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    "host": "gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com",
    "port": 4000,
    "user": "3p4oDGx2vdiHDMg.root",
    "password": "Wi65W1a6rIl8q5qL",
    "database": "volunteer_db",
    "autocommit": True,
    "use_pure": True,
    "ssl_verify_cert": True,
    "ssl_verify_identity": True,
    "ssl_ca": r"C:\Users\ASUS\Downloads\isrgrootx1.pem"
}

username = "admin"
password = "admin123"

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

hashed_password = generate_password_hash(password)

try:
    cursor.execute(
        "INSERT INTO admins (username, password) VALUES (%s, %s)",
        (username, hashed_password)
    )
    conn.commit()
    print("Admin created successfully!")
    print("Username:", username)
    print("Password:", password)
except mysql.connector.IntegrityError:
    print("Admin already exists.")

cursor.close()
conn.close()
