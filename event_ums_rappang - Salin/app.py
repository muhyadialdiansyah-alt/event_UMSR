# File: app.py (IMPROVED VERSION)
# Aplikasi utama Flask untuk Sistem Pendaftaran Event FEB UMS Rappang

from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
from pymysql.cursors import DictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import os
from contextlib import contextmanager

# Inisialisasi aplikasi Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ums_rappang_2025_secret_key_change_in_production')

# ============================================
# KONFIGURASI MYSQL - IMPROVED SECURITY
# ============================================

def get_mysql_config():
    """Get MySQL configuration from environment variables"""
    if 'PYTHONANYWHERE_DOMAIN' in os.environ:
        # Production (PythonAnywhere)
        return {
            'host': os.environ.get('MYSQL_HOST', 'mahasiswaumsfeb.mysql.pythonanywhere-services.com'),
            'user': os.environ.get('MYSQL_USER', 'mahasiswaumsfeb'),
            'password': os.environ.get('MYSQL_PASSWORD'),  # Dari environment variable
            'database': os.environ.get('MYSQL_DATABASE', 'mahasiswaumsfeb$event_ums'),
            'charset': 'utf8mb4',
            'cursorclass': DictCursor
        }
    else:
        # Development (Local)
        return {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', 'nain123'),
            'database': os.environ.get('MYSQL_DATABASE', 'event_ums'),
            'charset': 'utf8mb4',
            'cursorclass': DictCursor
        }

@contextmanager
def get_db_connection():
    """Context manager untuk koneksi database yang aman"""
    conn = None
    try:
        conn = pymysql.connect(**get_mysql_config())
        yield conn
    except pymysql.Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

# ============================================
# DECORATOR UNTUK LOGIN CHECK
# ============================================

def login_required(f):
    """Decorator untuk route yang memerlukan login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Silakan login terlebih dahulu!', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# ROUTE UNTUK HALAMAN PESERTA
# ============================================

@app.route('/')
def index():
    """Halaman utama - Landing page"""
    return render_template('index.html')


@app.route('/events')
def events():
    """Tampilkan semua event"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT e.*, p.nama as nama_panitia
                FROM event e
                LEFT JOIN panitia p ON e.panitia_id = p.panitia_id
                ORDER BY e.tanggal ASC
            ''')
            
            events = cursor.fetchall()
        
        return render_template('events.html', events=events)
    except Exception as e:
        flash(f'Error mengambil data event: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
def register(event_id):
    """Halaman pendaftaran event"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if request.method == 'POST':
                # Validasi input
                nama = request.form.get('nama', '').strip()
                nim = request.form.get('nim', '').strip()
                prodi = request.form.get('prodi', '').strip()
                no_hp = request.form.get('no_hp', '').strip()
                email = request.form.get('email', '').strip()
                alasan = request.form.get('alasan', '').strip()
                
                # Cek apakah semua field diisi
                if not all([nama, nim, prodi, no_hp, email]):
                    flash('Semua field wajib diisi!', 'error')
                    return redirect(url_for('register', event_id=event_id))
                
                try:
                    # Cek apakah NIM atau email sudah terdaftar untuk event ini
                    cursor.execute('''
                        SELECT p.id_peserta 
                        FROM peserta p
                        JOIN pendaftaran pd ON p.id_peserta = pd.peserta_id
                        WHERE (p.nim = %s OR p.email = %s) AND pd.event_id = %s
                    ''', (nim, email, event_id))
                    
                    if cursor.fetchone():
                        flash('Anda sudah terdaftar untuk event ini!', 'error')
                        return redirect(url_for('register', event_id=event_id))
                    
                    # Insert peserta (atau ambil yang sudah ada)
                    cursor.execute('''
                        INSERT INTO peserta (nama, nim, prodi, no_hp, email, alasan)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            nama = VALUES(nama),
                            prodi = VALUES(prodi),
                            no_hp = VALUES(no_hp),
                            alasan = VALUES(alasan)
                    ''', (nama, nim, prodi, no_hp, email, alasan))
                    
                    peserta_id = conn.insert_id()
                    
                    # Jika ON DUPLICATE KEY UPDATE triggered, ambil id yang sudah ada
                    if peserta_id == 0:
                        cursor.execute('SELECT id_peserta FROM peserta WHERE nim = %s', (nim,))
                        peserta_id = cursor.fetchone()['id_peserta']
                    
                    # Insert pendaftaran
                    cursor.execute('''
                        INSERT INTO pendaftaran (peserta_id, event_id)
                        VALUES (%s, %s)
                    ''', (peserta_id, event_id))
                    
                    conn.commit()
                    
                    flash('Pendaftaran berhasil! Terima kasih telah mendaftar.', 'success')
                    return redirect(url_for('success'))
                    
                except pymysql.IntegrityError as e:
                    flash('Error: Data sudah terdaftar atau tidak valid!', 'error')
                    return redirect(url_for('register', event_id=event_id))
            
            # GET request - tampilkan form
            cursor.execute('SELECT * FROM event WHERE id_event = %s', (event_id,))
            event = cursor.fetchone()
            
            if event is None:
                flash('Event tidak ditemukan!', 'error')
                return redirect(url_for('events'))
            
            return render_template('register.html', event=event)
            
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('events'))


@app.route('/success')
def success():
    """Halaman sukses setelah pendaftaran"""
    return render_template('success.html')

# ============================================
# ROUTE UNTUK ADMIN/PANITIA
# ============================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Halaman login admin"""
    # Jika sudah login, redirect ke dashboard
    if 'logged_in' in session:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Username dan password harus diisi!', 'error')
            return redirect(url_for('admin_login'))
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM panitia WHERE username = %s', (username,))
                user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['logged_in'] = True
                session['admin_id'] = user['panitia_id']
                session['admin_name'] = user['nama']
                
                flash(f'Login berhasil! Selamat datang, {user["nama"]}', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Username atau password salah!', 'error')
                return redirect(url_for('admin_login'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('admin_login'))
    
    return render_template('admin_login.html')


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Dashboard admin"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as count FROM event')
            total_events = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM peserta')
            total_peserta = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM pendaftaran')
            total_pendaftaran = cursor.fetchone()['count']
            
            cursor.execute('SELECT * FROM event ORDER BY tanggal DESC LIMIT 5')
            recent_events = cursor.fetchall()
        
        return render_template('admin_dashboard.html',
                             total_events=total_events,
                             total_peserta=total_peserta,
                             total_pendaftaran=total_pendaftaran,
                             recent_events=recent_events)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_login'))


@app.route('/admin/events')
@login_required
def admin_events():
    """Halaman kelola event"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT e.*, p.nama as nama_panitia,
                       COUNT(pd.daftar_id) as jumlah_peserta
                FROM event e
                LEFT JOIN panitia p ON e.panitia_id = p.panitia_id
                LEFT JOIN pendaftaran pd ON e.id_event = pd.event_id
                GROUP BY e.id_event
                ORDER BY e.tanggal DESC
            ''')
            events = cursor.fetchall()
        
        return render_template('admin_events.html', events=events)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Route untuk admin mengubah passwordnya sendiri"""
    if request.method == 'POST':
        old_password = request.form.get('old_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validasi input
        if not all([old_password, new_password, confirm_password]):
            flash('Semua field harus diisi!', 'error')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash('Password baru tidak cocok!', 'error')
            return redirect(url_for('change_password'))
        
        if len(new_password) < 6:
            flash('Password minimal 6 karakter!', 'error')
            return redirect(url_for('change_password'))
        
        if old_password == new_password:
            flash('Password baru harus berbeda dengan password lama!', 'error')
            return redirect(url_for('change_password'))
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                admin_id = session['admin_id']
                cursor.execute('SELECT password FROM panitia WHERE panitia_id = %s', (admin_id,))
                user = cursor.fetchone()
                
                if not user or not check_password_hash(user['password'], old_password):
                    flash('Password lama tidak sesuai!', 'error')
                    return redirect(url_for('change_password'))
                
                new_password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
                
                cursor.execute(
                    'UPDATE panitia SET password = %s WHERE panitia_id = %s',
                    (new_password_hash, admin_id)
                )
                conn.commit()
            
            flash('Password berhasil diubah! Silakan login kembali dengan password baru.', 'success')
            return redirect(url_for('admin_logout'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('change_password'))
    
    return render_template('admin_change_password.html')


@app.route('/admin/event/add', methods=['GET', 'POST'])
@login_required
def admin_event_add():
    """Tambah event baru"""
    if request.method == 'POST':
        nama_event = request.form.get('nama_event', '').strip()
        tanggal = request.form.get('tanggal', '').strip()
        lokasi = request.form.get('lokasi', '').strip()
        deskripsi = request.form.get('deskripsi', '').strip()
        panitia_id = session['admin_id']
        
        if not all([nama_event, tanggal, lokasi]):
            flash('Field nama event, tanggal, dan lokasi wajib diisi!', 'error')
            return redirect(url_for('admin_event_add'))
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO event (nama_event, tanggal, lokasi, deskripsi, panitia_id)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (nama_event, tanggal, lokasi, deskripsi, panitia_id))
                
                conn.commit()
            
            flash('Event berhasil ditambahkan!', 'success')
            return redirect(url_for('admin_events'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('admin_event_add'))
    
    return render_template('admin_event_add.html')


@app.route('/admin/event/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def admin_event_edit(event_id):
    """Edit event"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if request.method == 'POST':
                nama_event = request.form.get('nama_event', '').strip()
                tanggal = request.form.get('tanggal', '').strip()
                lokasi = request.form.get('lokasi', '').strip()
                deskripsi = request.form.get('deskripsi', '').strip()
                
                if not all([nama_event, tanggal, lokasi]):
                    flash('Field nama event, tanggal, dan lokasi wajib diisi!', 'error')
                    return redirect(url_for('admin_event_edit', event_id=event_id))
                
                cursor.execute('''
                    UPDATE event
                    SET nama_event = %s, tanggal = %s, lokasi = %s, deskripsi = %s
                    WHERE id_event = %s
                ''', (nama_event, tanggal, lokasi, deskripsi, event_id))
                
                conn.commit()
                
                flash('Event berhasil diupdate!', 'success')
                return redirect(url_for('admin_events'))
            
            cursor.execute('SELECT * FROM event WHERE id_event = %s', (event_id,))
            event = cursor.fetchone()
            
            if not event:
                flash('Event tidak ditemukan!', 'error')
                return redirect(url_for('admin_events'))
        
        return render_template('admin_event_edit.html', event=event)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_events'))


@app.route('/admin/event/delete/<int:event_id>', methods=['POST'])
@login_required
def admin_event_delete(event_id):
    """Hapus event"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Cek apakah event ada
            cursor.execute('SELECT nama_event FROM event WHERE id_event = %s', (event_id,))
            event = cursor.fetchone()
            
            if not event:
                flash('Event tidak ditemukan!', 'error')
                return redirect(url_for('admin_events'))
            
            cursor.execute('DELETE FROM event WHERE id_event = %s', (event_id,))
            conn.commit()
        
        flash(f'Event "{event["nama_event"]}" berhasil dihapus!', 'success')
        return redirect(url_for('admin_events'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_events'))


@app.route('/admin/peserta')
@login_required
def admin_peserta():
    """Halaman data peserta"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    p.*,
                    e.nama_event,
                    e.tanggal as tanggal_event,
                    pd.tanggal_daftar
                FROM peserta p
                JOIN pendaftaran pd ON p.id_peserta = pd.peserta_id
                JOIN event e ON pd.event_id = e.id_event
                ORDER BY pd.tanggal_daftar DESC
            ''')
            peserta = cursor.fetchall()
        
        return render_template('admin_peserta.html', peserta=peserta)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/logout')
def admin_logout():
    """Logout admin"""
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('admin_login'))

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ============================================
# JALANKAN APLIKASI
# ============================================

if __name__ == '__main__':
    # Cek apakah environment variables sudah di-set
    if not os.environ.get('MYSQL_PASSWORD'):
        print("⚠️  WARNING: MYSQL_PASSWORD tidak di-set di environment variables!")
        print("   Gunakan password default untuk development.")
    
    app.run(debug=True)