# File: cek_peserta.py (MYSQL VERSION)
# Script untuk mengecek data peserta yang sudah terdaftar

import pymysql
from pymysql.cursors import DictCursor

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'nain123',  # Ganti dengan password MySQL Anda!
    'database': 'event_ums',
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

def check_peserta():
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        print("\n" + "="*60)
        print("📋 DATA PESERTA TERDAFTAR - MYSQL")
        print("="*60 + "\n")

        # Query untuk mengambil data peserta beserta event yang didaftar
        cursor.execute('''
            SELECT 
                p.nama, 
                p.nim, 
                p.prodi, 
                p.email,
                e.nama_event,
                pd.tanggal_daftar
            FROM peserta p
            JOIN pendaftaran pd ON p.id_peserta = pd.peserta_id
            JOIN event e ON pd.event_id = e.id_event
            ORDER BY pd.tanggal_daftar DESC
        ''')

        results = cursor.fetchall()

        if results:
            for i, row in enumerate(results, 1):
                print(f"🎯 Peserta #{i}")
                print(f"   Nama    : {row['nama']}")
                print(f"   NIM     : {row['nim']}")
                print(f"   Prodi   : {row['prodi']}")
                print(f"   Email   : {row['email']}")
                print(f"   Event   : {row['nama_event']}")
                print(f"   Daftar  : {row['tanggal_daftar']}")
                print()
        else:
            print("❌ Belum ada peserta yang terdaftar.\n")

        # Hitung total
        cursor.execute('SELECT COUNT(*) as total FROM peserta')
        total_peserta = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) as total FROM pendaftaran')
        total_pendaftaran = cursor.fetchone()['total']

        print("="*60)
        print(f"📊 Total Peserta      : {total_peserta}")
        print(f"📊 Total Pendaftaran  : {total_pendaftaran}")
        print("="*60 + "\n")

        conn.close()

    except pymysql.Error as e:
        print(f"❌ Error MySQL: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    check_peserta()