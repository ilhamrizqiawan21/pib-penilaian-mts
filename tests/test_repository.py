from database import connection
from database.repository import Repository
from services.penilaian_service import hitung_nilai


def _prepare_repo(tmp_path, monkeypatch):
    db_path = tmp_path / "pib.db"
    monkeypatch.setattr(connection, "DATA_DIR", tmp_path)
    monkeypatch.setattr(connection, "DB_PATH", db_path)
    connection.init_db()
    return Repository()


def test_repository_rekap_statistik_dan_recalculate(tmp_path, monkeypatch):
    repo = _prepare_repo(tmp_path, monkeypatch)

    repo.set_pengaturan("nama_sekolah", "MTs Al-Hikmah")
    assert repo.get_pengaturan("nama_sekolah") == "MTs Al-Hikmah"

    tahun_ajaran_id = repo.create_tahun_ajaran("2026/2027")
    repo.set_tahun_ajaran_aktif(tahun_ajaran_id)
    semester_id = repo.create_semester(tahun_ajaran_id, "Ganjil")
    repo.set_semester_aktif(semester_id)
    kelas_id = repo.create_kelas("7A", 7)

    siswa_id = repo.create_siswa(
        {"nis": "001", "nama": "Ahmad Fauzi", "kelas_id": kelas_id, "semester_id": semester_id}
    )
    hafalan_id = repo.create_materi(
        {
            "semester_id": semester_id,
            "nama": "Doa sebelum makan",
            "aspek": "hafalan",
            "poin_pengurangan": 2,
            "urutan": 1,
        }
    )
    praktik_id = repo.create_materi(
        {
            "semester_id": semester_id,
            "nama": "Wudhu",
            "aspek": "praktik",
            "poin_pengurangan": 3,
            "urutan": 2,
        }
    )

    repo.upsert_penilaian_batch(
        [
            {
                "siswa_id": siswa_id,
                "materi_id": hafalan_id,
                "jumlah_kesalahan": 2,
                "nilai": hitung_nilai(2, 2),
                "poin_snapshot": 2,
                "updated_at": "2026-07-18T18:00:00",
            },
            {
                "siswa_id": siswa_id,
                "materi_id": praktik_id,
                "jumlah_kesalahan": 3,
                "nilai": hitung_nilai(3, 3),
                "poin_snapshot": 3,
                "updated_at": "2026-07-18T18:00:00",
            },
        ]
    )

    grid = repo.get_penilaian_grid(semester_id, kelas_id)
    assert len(grid["siswa_list"]) == 1
    assert len(grid["materi_list"]) == 2
    assert grid["penilaian_map"][(siswa_id, hafalan_id)]["nilai"] == 86

    rekap = repo.get_rekap_kelas(semester_id, kelas_id)
    assert rekap[0].rata_hafalan == 86
    assert rekap[0].rata_praktik == 81
    assert rekap[0].rata_total == 83.5
    assert rekap[0].status == "lengkap"
    assert rekap[0].peringkat == 1

    statistik = repo.get_statistik_kelas(semester_id, kelas_id)
    assert statistik == {
        "jumlah_siswa": 1,
        "jumlah_materi": 2,
        "rata_kelas": 83.5,
        "jumlah_lengkap": 1,
        "jumlah_sebagian": 0,
        "jumlah_belum": 0,
    }

    assert repo.recalculate_penilaian_by_materi(hafalan_id, 4) == 1
    rekap_setelah_recalculate = repo.get_rekap_kelas(semester_id, kelas_id)[0]
    assert rekap_setelah_recalculate.rata_hafalan == 82
    assert rekap_setelah_recalculate.rata_total == 81.5


def test_delete_kelas_ditolak_jika_masih_ada_siswa(tmp_path, monkeypatch):
    repo = _prepare_repo(tmp_path, monkeypatch)
    tahun_ajaran_id = repo.create_tahun_ajaran("2026/2027")
    semester_id = repo.create_semester(tahun_ajaran_id, "Ganjil")
    kelas_id = repo.create_kelas("7A", 7)
    repo.create_siswa({"nis": "001", "nama": "Ahmad", "kelas_id": kelas_id, "semester_id": semester_id})

    try:
        repo.delete_kelas(kelas_id)
    except ValueError as exc:
        assert "Pindahkan/nonaktifkan siswa dulu" in str(exc)
    else:
        raise AssertionError("delete_kelas seharusnya ditolak jika kelas masih punya siswa")


def test_penilaian_per_nama_materi_menyimpan_dua_aspek(tmp_path, monkeypatch):
    repo = _prepare_repo(tmp_path, monkeypatch)
    tahun_ajaran_id = repo.create_tahun_ajaran("2026/2027")
    semester_id = repo.create_semester(tahun_ajaran_id, "Ganjil")
    kelas_id = repo.create_kelas("7A", 7)
    siswa_id = repo.create_siswa({"nis": "001", "nama": "Ahmad", "kelas_id": kelas_id, "semester_id": semester_id})

    materi_ids = repo.create_materi_pair(
        {
            "semester_id": semester_id,
            "nama": "Wudhu",
            "poin_hafalan": 2,
            "poin_praktik": 3,
            "urutan": 1,
        }
    )

    assert set(materi_ids) == {"hafalan", "praktik"}
    assert repo.list_nama_materi(semester_id) == ["Wudhu"]
    assert set(repo.get_materi_pair_by_nama(semester_id, "Wudhu")) == {"hafalan", "praktik"}

    repo.upsert_penilaian_batch(
        [
            {
                "siswa_id": siswa_id,
                "materi_id": materi_ids["hafalan"],
                "jumlah_kesalahan": 2,
                "nilai": hitung_nilai(2, 2),
                "poin_snapshot": 2,
                "updated_at": "2026-07-18T18:00:00",
            },
            {
                "siswa_id": siswa_id,
                "materi_id": materi_ids["praktik"],
                "jumlah_kesalahan": 4,
                "nilai": hitung_nilai(4, 3),
                "poin_snapshot": 3,
                "updated_at": "2026-07-18T18:00:00",
            },
        ]
    )

    data = repo.get_penilaian_materi_kelas(semester_id, kelas_id, "Wudhu")
    assert len(data["siswa_list"]) == 1
    assert data["penilaian_map"][(siswa_id, "hafalan")]["nilai"] == 86
    assert data["penilaian_map"][(siswa_id, "praktik")]["nilai"] == 78


def test_ensure_materi_pair_melengkapi_aspek_lama(tmp_path, monkeypatch):
    repo = _prepare_repo(tmp_path, monkeypatch)
    tahun_ajaran_id = repo.create_tahun_ajaran("2026/2027")
    semester_id = repo.create_semester(tahun_ajaran_id, "Ganjil")
    repo.create_materi(
        {
            "semester_id": semester_id,
            "nama": "Doa Harian",
            "aspek": "praktik",
            "poin_pengurangan": 2.5,
            "urutan": 4,
        }
    )

    pair = repo.ensure_materi_pair_by_nama(semester_id, "Doa Harian")

    assert set(pair) == {"hafalan", "praktik"}
    assert pair["hafalan"]["poin_pengurangan"] == 2.5
    assert pair["hafalan"]["urutan"] == 4


def test_repository_crud_data_master(tmp_path, monkeypatch):
    repo = _prepare_repo(tmp_path, monkeypatch)
    tahun_ajaran_id = repo.create_tahun_ajaran("2026/2027")
    semester_id = repo.create_semester(tahun_ajaran_id, "Ganjil")
    kelas_id = repo.create_kelas("7A", 7)
    siswa_id = repo.create_siswa({"nis": "001", "nama": "Ahmad", "kelas_id": kelas_id, "semester_id": semester_id})

    repo.update_kelas(kelas_id, "7B", 7)
    assert repo.list_kelas()[0]["nama"] == "7B"

    repo.update_siswa(
        siswa_id,
        {"nis": "002", "nama": "Ahmad Fauzi", "kelas_id": kelas_id, "semester_id": semester_id},
    )
    siswa = repo.list_siswa(semester_id, kelas_id)[0]
    assert siswa["nis"] == "002"
    assert siswa["nama"] == "Ahmad Fauzi"

    repo.delete_siswa(siswa_id)
    assert repo.list_siswa(semester_id, kelas_id) == []
    repo.delete_kelas(kelas_id)
    assert repo.list_kelas() == []

    repo.create_materi_pair(
        {
            "semester_id": semester_id,
            "nama": "Wudhu",
            "poin_hafalan": 2,
            "poin_praktik": 3,
            "urutan": 1,
        }
    )
    repo.update_materi_pair_by_nama(
        semester_id,
        "Wudhu",
        {"nama": "Wudhu Lengkap", "poin_hafalan": 1.5, "poin_praktik": 2.5, "urutan": 2},
    )
    pair = repo.get_materi_pair_by_nama(semester_id, "Wudhu Lengkap")
    assert pair["hafalan"]["poin_pengurangan"] == 1.5
    assert pair["praktik"]["poin_pengurangan"] == 2.5
    repo.delete_materi_pair_by_nama(semester_id, "Wudhu Lengkap")
    assert repo.list_nama_materi(semester_id) == []

    repo.update_tahun_ajaran(tahun_ajaran_id, "2027/2028")
    assert repo.list_tahun_ajaran()[0]["nama"] == "2027/2028"
    repo.update_semester(semester_id, "Genap")
    assert repo.list_semester(tahun_ajaran_id)[0]["nama"] == "Genap"
