# init_db.py - MySQL Version (FIXED)
import pymysql

# Pertama, connect ke MySQL SERVER (bukan database spesifik)
SERVER_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'nain123',  # Ganti dengan password Anda!
    'charset': 'utf8mb4'
}

# Config database
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'nain123',
    'database': 'event_ums',
    'charset': 'utf8mb4'
}

def init_database():
    try:
        # STEP 1: Buat database
        print("🔄 Membuat database 'event_ums'...")
        conn = pymysql.connect(**SERVER_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute('CREATE DATABASE IF NOT EXISTS event_ums CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        conn.commit()
        conn.close()
        print("✅ Database created/already exists")
        
        # STEP 2: Connect ke database spesifik dan buat tabel
        print("\n🔄 Membuat tabel di MySQL...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Baca schema.sql
        with open('schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
        
        # Execute setiap statement (MySQL tidak support executescript)
        statements = schema.split(';')
        for i, statement in enumerate(statements):
            if statement.strip():
                try:
                    cursor.execute(statement)
                    conn.commit()
                    print(f"   ✓ Statement {i+1} executed")
                except pymysql.Error as e:
                    print(f"   ⚠ Warning Statement {i+1}: {e}")
        
        conn.close()
        
        print("\n✅ Database MySQL berhasil dibuat!")
        print("📊 Tabel yang dibuat: peserta, event, pendaftaran, panitia")
        print("\n📌 Konfigurasi database:")
        print(f"   Host     : {DB_CONFIG['host']}")
        print(f"   User     : {DB_CONFIG['user']}")
        print(f"   Database : {DB_CONFIG['database']}")
        print("\n✨ Siap digunakan!\n")

    except pymysql.Error as e:
        print(f"❌ Error MySQL: {e}")
        print("\n💡 Pastikan:")
        print("   1. MySQL Server sudah running")
        print("   2. Username dan password sudah benar")
        print("   3. File schema.sql ada di folder project")
    except FileNotFoundError:
        print("❌ File schema.sql tidak ditemukan!")
        print("   Pastikan schema.sql ada di folder yang sama dengan init_db.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    init_database()