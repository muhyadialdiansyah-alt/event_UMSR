-- Database Schema untuk MySQL
-- Sistem Pendaftaran Event FEB UMS Rappang

-- Hapus tabel jika sudah ada
DROP TABLE IF EXISTS pendaftaran;
DROP TABLE IF EXISTS peserta;
DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS panitia;

-- Tabel Panitia/Admin
CREATE TABLE panitia (
    panitia_id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel Event
CREATE TABLE event (
    id_event INT AUTO_INCREMENT PRIMARY KEY,
    nama_event VARCHAR(150) NOT NULL,
    tanggal DATE NOT NULL,
    lokasi VARCHAR(200) NOT NULL,
    deskripsi TEXT,
    panitia_id INT,
    FOREIGN KEY (panitia_id) REFERENCES panitia(panitia_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel Peserta/Mahasiswa
CREATE TABLE peserta (
    id_peserta INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    nim VARCHAR(20) UNIQUE NOT NULL,
    prodi VARCHAR(100) NOT NULL,
    no_hp VARCHAR(15) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    alasan TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel Pendaftaran (Junction Table)
CREATE TABLE pendaftaran (
    daftar_id INT AUTO_INCREMENT PRIMARY KEY,
    peserta_id INT NOT NULL,
    event_id INT NOT NULL,
    tanggal_daftar DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (peserta_id) REFERENCES peserta(id_peserta) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES event(id_event) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert data sample
CREATE TABLE panitia (
    panitia_id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL  -- Ini cukup untuk hash
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO panitia VALUES 
(1, 'Admin UMS', 'admin', 
'pbkdf2:sha256:600000$8H9xKjP1mN2oQ3rS$5e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f',
NOW());

INSERT INTO event (nama_event, tanggal, lokasi, deskripsi, panitia_id) VALUES
('Seminar Bisnis Digital', '2025-02-15', 'Gedung FEB Lt.2', 'Seminar tentang transformasi digital dalam bisnis', 1),
('Workshop Python Programming', '2025-02-20', 'Lab Komputer 1', 'Pelatihan dasar pemrograman Python', 1),
('Webinar Kewirausahaan', '2025-03-01', 'Zoom Meeting', 'Webinar memulai bisnis untuk mahasiswa', 1);