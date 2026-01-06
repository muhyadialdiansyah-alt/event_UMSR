# setup_admin.py - Setup Admin dengan Password Ter-Hash
import pymysql
from werkzeug.security import generate_password_hash

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'nain123',  # Ganti dengan password MySQL Anda!
    'database': 'event_ums',
    'charset': 'utf8mb4'
}

def setup_admin():
    print("\n" + "="*60)
    print("🔐 SETUP ADMIN PANITIA - PASSWORD AMAN (HASHED)")
    print("="*60 + "\n")
    
    try:
        nama = input("📝 Nama Admin         : ").strip()
        if not nama:
            print("❌ Nama tidak boleh kosong!")
            return
        
        username = input("👤 Username          : ").strip()
        if not username or len(username) < 3:
            print("❌ Username minimal 3 karakter!")
            return
        
        password = input("🔑 Password          : ").strip()
        if not password or len(password) < 6:
            print("❌ Password minimal 6 karakter!")
            return
        
        confirm_password = input("🔑 Konfirmasi Password: ").strip()
        
        if password != confirm_password:
            print("❌ Password tidak cocok!")
            return
        
        print("\n⏳ Membuat admin...\n")
        
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Hash password menggunakan pbkdf2:sha256
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Insert ke database
        cursor.execute('''
            INSERT INTO panitia (nama, username, password)
            VALUES (%s, %s, %s)
        ''', (nama, username, password_hash))
        
        conn.commit()
        conn.close()
        
        print("="*60)
        print("✅ ADMIN BERHASIL DIBUAT!")
        print("="*60)
        print(f"📝 Nama      : {nama}")
        print(f"👤 Username  : {username}")
        print(f"🔐 Password  : (ter-enkripsi) ✓")
        print("="*60)
        print("\n💡 Tips:")
        print("   • Catat username & password Anda")
        print("   • Password tidak bisa di-recover jika lupa")
        print("   • Jangan share password dengan orang lain")
        print("\n✨ Sekarang Anda bisa login ke admin!\n")
        
    except pymysql.IntegrityError as e:
        print(f"❌ Error: Username '{username}' sudah ada di database!")
        print("   Gunakan username yang berbeda.\n")
    except pymysql.Error as e:
        print(f"❌ Error MySQL: {e}")
        print("   Pastikan:")
        print("   1. MySQL Server sudah running")
        print("   2. Password MySQL sudah benar")
        print("   3. Database 'event_ums' sudah ada\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

def list_admin():
    """Tampilkan daftar admin yang sudah ada"""
    print("\n" + "="*60)
    print("📋 DAFTAR ADMIN YANG ADA")
    print("="*60 + "\n")
    
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute('SELECT panitia_id, nama, username FROM panitia')
        admins = cursor.fetchall()
        conn.close()
        
        if admins:
            for i, admin in enumerate(admins, 1):
                print(f"{i}. {admin[1]} (@{admin[2]})")
        else:
            print("❌ Belum ada admin di database")
        
        print()
    except Exception as e:
        print(f"❌ Error: {e}\n")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔐 ADMIN SETUP MENU")
    print("="*60)
    print("\n1. Buat Admin Baru")
    print("2. Lihat Daftar Admin")
    print("3. Keluar")
    print()
    
    choice = input("Pilih menu (1-3): ").strip()
    
    if choice == '1':
        setup_admin()
    elif choice == '2':
        list_admin()
    elif choice == '3':
        print("\n👋 Selesai!\n")
    else:
        print("\n❌ Pilihan tidak valid!\n")