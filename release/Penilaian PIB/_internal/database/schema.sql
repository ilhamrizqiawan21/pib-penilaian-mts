PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pengaturan (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tahun_ajaran (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nama      TEXT NOT NULL UNIQUE,
    is_aktif  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS semester (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tahun_ajaran_id INTEGER NOT NULL REFERENCES tahun_ajaran(id) ON DELETE CASCADE,
    nama            TEXT NOT NULL,
    is_aktif        INTEGER NOT NULL DEFAULT 0,
    UNIQUE(tahun_ajaran_id, nama)
);

CREATE TABLE IF NOT EXISTS kelas (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nama    TEXT NOT NULL UNIQUE,
    tingkat INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS siswa (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nis         TEXT NOT NULL,
    nama        TEXT NOT NULL,
    kelas_id    INTEGER NOT NULL REFERENCES kelas(id),
    semester_id INTEGER NOT NULL REFERENCES semester(id) ON DELETE CASCADE,
    is_aktif    INTEGER NOT NULL DEFAULT 1,
    UNIQUE(nis, semester_id)
);

CREATE TABLE IF NOT EXISTS materi (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_id      INTEGER NOT NULL REFERENCES semester(id) ON DELETE CASCADE,
    nama             TEXT NOT NULL,
    aspek            TEXT NOT NULL CHECK(aspek IN ('hafalan', 'praktik')),
    poin_pengurangan REAL NOT NULL CHECK(poin_pengurangan > 0),
    urutan           INTEGER NOT NULL DEFAULT 0,
    is_aktif         INTEGER NOT NULL DEFAULT 1,
    UNIQUE(semester_id, nama, aspek)
);

CREATE TABLE IF NOT EXISTS penilaian (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    siswa_id         INTEGER NOT NULL REFERENCES siswa(id) ON DELETE CASCADE,
    materi_id        INTEGER NOT NULL REFERENCES materi(id) ON DELETE CASCADE,
    jumlah_kesalahan INTEGER NOT NULL CHECK(jumlah_kesalahan >= 0),
    nilai            REAL NOT NULL CHECK(nilai >= 0 AND nilai <= 90),
    poin_snapshot    REAL NOT NULL,
    updated_at       TEXT NOT NULL,
    UNIQUE(siswa_id, materi_id)
);

CREATE INDEX IF NOT EXISTS idx_siswa_semester_kelas
    ON siswa(semester_id, kelas_id);
CREATE INDEX IF NOT EXISTS idx_materi_semester
    ON materi(semester_id, is_aktif);
CREATE INDEX IF NOT EXISTS idx_penilaian_siswa
    ON penilaian(siswa_id);
CREATE INDEX IF NOT EXISTS idx_penilaian_materi
    ON penilaian(materi_id);
