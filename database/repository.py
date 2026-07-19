from __future__ import annotations

from datetime import datetime
from typing import Any

from database.connection import get_connection
from services.penilaian_service import (
    RekapSiswa,
    hitung_nilai,
    hitung_ranking,
    hitung_rata_total,
    rata_rata,
    tentukan_status,
)


def _row_to_dict(row: Any) -> dict | None:
    return dict(row) if row is not None else None


class Repository:
    BACKUP_TABLES = ["tahun_ajaran", "semester", "kelas", "siswa", "materi", "penilaian", "pengaturan"]

    def get_pengaturan(self, key: str) -> str | None:
        with get_connection() as conn:
            row = conn.execute("SELECT value FROM pengaturan WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else None

    def set_pengaturan(self, key: str, value: str) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO pengaturan(key, value)
                VALUES(?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )

    def backup_json_data(self) -> dict:
        with get_connection() as conn:
            return {
                "version": 1,
                "exported_at": datetime.now().isoformat(timespec="seconds"),
                "tables": {
                    table: [dict(row) for row in conn.execute(f"SELECT * FROM {table}").fetchall()]
                    for table in self.BACKUP_TABLES
                },
            }

    def restore_json_data(self, data: dict) -> None:
        if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("tables"), dict):
            raise ValueError("Format backup tidak valid.")
        with get_connection() as conn:
            conn.execute("PRAGMA foreign_keys = OFF")
            try:
                for table in reversed(self.BACKUP_TABLES):
                    conn.execute(f"DELETE FROM {table}")
                for table in self.BACKUP_TABLES:
                    rows = data["tables"].get(table, [])
                    if not isinstance(rows, list):
                        raise ValueError(f"Data tabel {table} tidak valid.")
                    for row in rows:
                        if not row:
                            continue
                        columns = list(row.keys())
                        placeholders = ",".join("?" for _ in columns)
                        conn.execute(
                            f"INSERT INTO {table}({','.join(columns)}) VALUES({placeholders})",
                            [row[column] for column in columns],
                        )
                conn.execute("PRAGMA foreign_keys = ON")
                violations = conn.execute("PRAGMA foreign_key_check").fetchall()
                if violations:
                    raise ValueError("Backup tidak sesuai relasi database aplikasi.")
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.execute("PRAGMA foreign_keys = ON")

    def list_tahun_ajaran(self) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM tahun_ajaran ORDER BY nama DESC").fetchall()
            return [dict(row) for row in rows]

    def create_tahun_ajaran(self, nama: str) -> int:
        with get_connection() as conn:
            cur = conn.execute("INSERT INTO tahun_ajaran(nama) VALUES(?)", (nama,))
            return int(cur.lastrowid)

    def update_tahun_ajaran(self, id: int, nama: str) -> None:
        with get_connection() as conn:
            conn.execute("UPDATE tahun_ajaran SET nama = ? WHERE id = ?", (nama, id))

    def delete_tahun_ajaran(self, id: int) -> None:
        with get_connection() as conn:
            active = conn.execute("SELECT is_aktif FROM tahun_ajaran WHERE id = ?", (id,)).fetchone()
            if active and active["is_aktif"]:
                raise ValueError("Tahun ajaran aktif tidak bisa dihapus. Aktifkan tahun ajaran lain terlebih dahulu.")
            conn.execute("DELETE FROM tahun_ajaran WHERE id = ?", (id,))

    def set_tahun_ajaran_aktif(self, id: int) -> None:
        with get_connection() as conn:
            conn.execute("UPDATE tahun_ajaran SET is_aktif = 0")
            conn.execute("UPDATE tahun_ajaran SET is_aktif = 1 WHERE id = ?", (id,))

    def get_tahun_ajaran_aktif(self) -> dict | None:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM tahun_ajaran WHERE is_aktif = 1").fetchone()
            return _row_to_dict(row)

    def list_semester(self, tahun_ajaran_id: int) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM semester
                WHERE tahun_ajaran_id = ?
                ORDER BY CASE nama WHEN 'Ganjil' THEN 1 WHEN 'Genap' THEN 2 ELSE 3 END
                """,
                (tahun_ajaran_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def create_semester(self, tahun_ajaran_id: int, nama: str) -> int:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO semester(tahun_ajaran_id, nama) VALUES(?, ?)",
                (tahun_ajaran_id, nama),
            )
            return int(cur.lastrowid)

    def update_semester(self, id: int, nama: str) -> None:
        with get_connection() as conn:
            conn.execute("UPDATE semester SET nama = ? WHERE id = ?", (nama, id))

    def delete_semester(self, id: int) -> None:
        with get_connection() as conn:
            active = conn.execute("SELECT is_aktif FROM semester WHERE id = ?", (id,)).fetchone()
            if active and active["is_aktif"]:
                raise ValueError("Semester aktif tidak bisa dihapus. Aktifkan semester lain terlebih dahulu.")
            conn.execute("DELETE FROM semester WHERE id = ?", (id,))

    def set_semester_aktif(self, id: int) -> None:
        with get_connection() as conn:
            row = conn.execute("SELECT tahun_ajaran_id FROM semester WHERE id = ?", (id,)).fetchone()
            if row is None:
                raise ValueError("Semester tidak ditemukan")
            conn.execute("UPDATE semester SET is_aktif = 0 WHERE tahun_ajaran_id = ?", (row["tahun_ajaran_id"],))
            conn.execute("UPDATE semester SET is_aktif = 1 WHERE id = ?", (id,))

    def get_semester_aktif(self) -> dict | None:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT s.*, ta.nama AS tahun_ajaran
                FROM semester s
                JOIN tahun_ajaran ta ON ta.id = s.tahun_ajaran_id
                WHERE s.is_aktif = 1
                """
            ).fetchone()
            return _row_to_dict(row)

    def list_kelas(self) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute("SELECT * FROM kelas ORDER BY tingkat, nama").fetchall()
            return [dict(row) for row in rows]

    def create_kelas(self, nama: str, tingkat: int) -> int:
        with get_connection() as conn:
            cur = conn.execute("INSERT INTO kelas(nama, tingkat) VALUES(?, ?)", (nama, tingkat))
            return int(cur.lastrowid)

    def update_kelas(self, id: int, nama: str, tingkat: int) -> None:
        with get_connection() as conn:
            conn.execute("UPDATE kelas SET nama = ?, tingkat = ? WHERE id = ?", (nama, tingkat, id))

    def delete_kelas(self, id: int) -> None:
        with get_connection() as conn:
            used = conn.execute("SELECT 1 FROM siswa WHERE kelas_id = ? LIMIT 1", (id,)).fetchone()
            if used:
                raise ValueError("Pindahkan/nonaktifkan siswa dulu")
            conn.execute("DELETE FROM kelas WHERE id = ?", (id,))

    def list_siswa(self, semester_id: int, kelas_id: int | None = None) -> list[dict]:
        params: list[Any] = [semester_id]
        filter_kelas = ""
        if kelas_id is not None:
            filter_kelas = "AND s.kelas_id = ?"
            params.append(kelas_id)
        with get_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT s.*, k.nama AS kelas, k.tingkat
                FROM siswa s
                JOIN kelas k ON k.id = s.kelas_id
                WHERE s.semester_id = ? AND s.is_aktif = 1 {filter_kelas}
                ORDER BY k.tingkat, k.nama, s.nama
                """,
                params,
            ).fetchall()
            return [dict(row) for row in rows]

    def create_siswa(self, data: dict) -> int:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO siswa(nis, nama, kelas_id, semester_id) VALUES(?, ?, ?, ?)",
                (data["nis"], data["nama"], data["kelas_id"], data["semester_id"]),
            )
            return int(cur.lastrowid)

    def update_siswa(self, id: int, data: dict) -> None:
        with get_connection() as conn:
            conn.execute(
                "UPDATE siswa SET nis = ?, nama = ?, kelas_id = ?, semester_id = ? WHERE id = ?",
                (data["nis"], data["nama"], data["kelas_id"], data["semester_id"], id),
            )

    def deactivate_siswa(self, id: int) -> None:
        with get_connection() as conn:
            conn.execute("UPDATE siswa SET is_aktif = 0 WHERE id = ?", (id,))

    def delete_siswa(self, id: int) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM siswa WHERE id = ?", (id,))

    def list_materi(self, semester_id: int, hanya_aktif: bool = True) -> list[dict]:
        filter_aktif = "AND is_aktif = 1" if hanya_aktif else ""
        with get_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM materi
                WHERE semester_id = ? {filter_aktif}
                ORDER BY aspek, urutan, nama
                """,
                (semester_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def list_nama_materi(self, semester_id: int, hanya_aktif: bool = True) -> list[str]:
        filter_aktif = "AND is_aktif = 1" if hanya_aktif else ""
        with get_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT nama, MIN(urutan) AS urutan
                FROM materi
                WHERE semester_id = ? {filter_aktif}
                GROUP BY nama
                ORDER BY urutan, nama
                """,
                (semester_id,),
            ).fetchall()
            return [row["nama"] for row in rows]

    def get_materi_pair_by_nama(self, semester_id: int, nama: str) -> dict[str, dict]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM materi
                WHERE semester_id = ? AND nama = ? AND is_aktif = 1
                ORDER BY aspek
                """,
                (semester_id, nama),
            ).fetchall()
            return {row["aspek"]: dict(row) for row in rows}

    def ensure_materi_pair_by_nama(self, semester_id: int, nama: str) -> dict[str, dict]:
        pair = self.get_materi_pair_by_nama(semester_id, nama)
        if not pair or {"hafalan", "praktik"}.issubset(pair):
            return pair

        source = pair.get("hafalan") or pair.get("praktik")
        missing_aspek = "praktik" if "praktik" not in pair else "hafalan"
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO materi(semester_id, nama, aspek, poin_pengurangan, urutan, is_aktif)
                VALUES(?, ?, ?, ?, ?, 1)
                ON CONFLICT(semester_id, nama, aspek) DO UPDATE SET
                    poin_pengurangan = excluded.poin_pengurangan,
                    urutan = excluded.urutan,
                    is_aktif = 1
                """,
                (
                    semester_id,
                    nama,
                    missing_aspek,
                    source["poin_pengurangan"],
                    source["urutan"],
                ),
            )
        return self.get_materi_pair_by_nama(semester_id, nama)

    def create_materi(self, data: dict) -> int:
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO materi(semester_id, nama, aspek, poin_pengurangan, urutan)
                VALUES(?, ?, ?, ?, ?)
                """,
                (
                    data["semester_id"],
                    data["nama"],
                    data["aspek"],
                    data["poin_pengurangan"],
                    data.get("urutan", 0),
                ),
            )
            return int(cur.lastrowid)

    def create_materi_pair(self, data: dict) -> dict[str, int]:
        created = {}
        with get_connection() as conn:
            for aspek in ("hafalan", "praktik"):
                poin_key = f"poin_{aspek}"
                cur = conn.execute(
                    """
                    INSERT INTO materi(semester_id, nama, aspek, poin_pengurangan, urutan)
                    VALUES(?, ?, ?, ?, ?)
                    ON CONFLICT(semester_id, nama, aspek) DO UPDATE SET
                        poin_pengurangan = excluded.poin_pengurangan,
                        urutan = excluded.urutan,
                        is_aktif = 1
                    """,
                    (
                        data["semester_id"],
                        data["nama"],
                        aspek,
                        data[poin_key],
                        data.get("urutan", 0),
                    ),
                )
                row = conn.execute(
                    """
                    SELECT id FROM materi
                    WHERE semester_id = ? AND nama = ? AND aspek = ?
                    """,
                    (data["semester_id"], data["nama"], aspek),
                ).fetchone()
                created[aspek] = int(row["id"])
        return created

    def update_materi_pair_by_nama(self, semester_id: int, old_nama: str, data: dict) -> None:
        pair = self.ensure_materi_pair_by_nama(semester_id, old_nama)
        with get_connection() as conn:
            for aspek in ("hafalan", "praktik"):
                materi = pair.get(aspek)
                if not materi:
                    continue
                conn.execute(
                    """
                    UPDATE materi
                    SET nama = ?, poin_pengurangan = ?, urutan = ?, is_aktif = 1
                    WHERE id = ?
                    """,
                    (
                        data["nama"],
                        data[f"poin_{aspek}"],
                        data.get("urutan", 0),
                        materi["id"],
                    ),
                )

    def delete_materi_pair_by_nama(self, semester_id: int, nama: str) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM materi WHERE semester_id = ? AND nama = ?", (semester_id, nama))

    def update_materi(self, id: int, data: dict) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE materi
                SET nama = ?, aspek = ?, poin_pengurangan = ?, urutan = ?, is_aktif = ?
                WHERE id = ?
                """,
                (
                    data["nama"],
                    data["aspek"],
                    data["poin_pengurangan"],
                    data.get("urutan", 0),
                    data.get("is_aktif", 1),
                    id,
                ),
            )

    def deactivate_materi(self, id: int) -> None:
        with get_connection() as conn:
            conn.execute("UPDATE materi SET is_aktif = 0 WHERE id = ?", (id,))

    def delete_materi(self, id: int) -> None:
        with get_connection() as conn:
            conn.execute("DELETE FROM materi WHERE id = ?", (id,))

    def salin_materi_ke_semester(self, dari_semester_id: int, ke_semester_id: int) -> int:
        materi = self.list_materi(dari_semester_id, hanya_aktif=True)
        copied = 0
        with get_connection() as conn:
            for item in materi:
                cur = conn.execute(
                    """
                    INSERT OR IGNORE INTO materi(semester_id, nama, aspek, poin_pengurangan, urutan, is_aktif)
                    VALUES(?, ?, ?, ?, ?, 1)
                    """,
                    (ke_semester_id, item["nama"], item["aspek"], item["poin_pengurangan"], item["urutan"]),
                )
                copied += cur.rowcount
        return copied

    def get_penilaian_grid(self, semester_id: int, kelas_id: int) -> dict:
        siswa_list = self.list_siswa(semester_id, kelas_id)
        materi_list = self.list_materi(semester_id, hanya_aktif=True)
        siswa_ids = [s["id"] for s in siswa_list]
        materi_ids = [m["id"] for m in materi_list]
        penilaian_map = {}
        if not siswa_ids or not materi_ids:
            return {"siswa_list": siswa_list, "materi_list": materi_list, "penilaian_map": penilaian_map}

        placeholders_siswa = ",".join("?" for _ in siswa_ids)
        placeholders_materi = ",".join("?" for _ in materi_ids)
        with get_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT siswa_id, materi_id, jumlah_kesalahan, nilai, poin_snapshot, updated_at
                FROM penilaian
                WHERE siswa_id IN ({placeholders_siswa}) AND materi_id IN ({placeholders_materi})
                """,
                [*siswa_ids, *materi_ids],
            ).fetchall()
        for row in rows:
            penilaian_map[(row["siswa_id"], row["materi_id"])] = dict(row)
        return {"siswa_list": siswa_list, "materi_list": materi_list, "penilaian_map": penilaian_map}

    def get_penilaian_materi_kelas(self, semester_id: int, kelas_id: int, nama_materi: str) -> dict:
        siswa_list = self.list_siswa(semester_id, kelas_id)
        materi_pair = self.get_materi_pair_by_nama(semester_id, nama_materi)
        materi_ids = [m["id"] for m in materi_pair.values()]
        penilaian_map = {}
        if siswa_list and materi_ids:
            siswa_ids = [s["id"] for s in siswa_list]
            placeholders_siswa = ",".join("?" for _ in siswa_ids)
            placeholders_materi = ",".join("?" for _ in materi_ids)
            with get_connection() as conn:
                rows = conn.execute(
                    f"""
                    SELECT p.siswa_id, p.materi_id, m.aspek, p.jumlah_kesalahan,
                           p.nilai, p.poin_snapshot, p.updated_at
                    FROM penilaian p
                    JOIN materi m ON m.id = p.materi_id
                    WHERE p.siswa_id IN ({placeholders_siswa})
                      AND p.materi_id IN ({placeholders_materi})
                    """,
                    [*siswa_ids, *materi_ids],
                ).fetchall()
            for row in rows:
                penilaian_map[(row["siswa_id"], row["aspek"])] = dict(row)
        return {
            "siswa_list": siswa_list,
            "materi_pair": materi_pair,
            "penilaian_map": penilaian_map,
        }

    def upsert_penilaian_batch(self, records: list[dict]) -> None:
        if not records:
            return
        with get_connection() as conn:
            conn.executemany(
                """
                INSERT INTO penilaian(
                    siswa_id, materi_id, jumlah_kesalahan, nilai, poin_snapshot, updated_at
                )
                VALUES(:siswa_id, :materi_id, :jumlah_kesalahan, :nilai, :poin_snapshot, :updated_at)
                ON CONFLICT(siswa_id, materi_id) DO UPDATE SET
                    jumlah_kesalahan = excluded.jumlah_kesalahan,
                    nilai = excluded.nilai,
                    poin_snapshot = excluded.poin_snapshot,
                    updated_at = excluded.updated_at
                """,
                records,
            )

    def recalculate_penilaian_by_materi(self, materi_id: int, poin_baru: float) -> int:
        updated_at = datetime.now().isoformat(timespec="seconds")
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT id, jumlah_kesalahan FROM penilaian WHERE materi_id = ?",
                (materi_id,),
            ).fetchall()
            for row in rows:
                conn.execute(
                    """
                    UPDATE penilaian
                    SET nilai = ?, poin_snapshot = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (hitung_nilai(row["jumlah_kesalahan"], poin_baru), poin_baru, updated_at, row["id"]),
                )
            return len(rows)

    def get_rekap_kelas(self, semester_id: int, kelas_id: int) -> list[RekapSiswa]:
        return self._get_rekap(semester_id, kelas_id)

    def get_rekap_semester(self, semester_id: int) -> list[RekapSiswa]:
        return self._get_rekap(semester_id, None)

    def get_statistik_kelas(self, semester_id: int, kelas_id: int) -> dict:
        rekap = self.get_rekap_kelas(semester_id, kelas_id)
        totals = [r.rata_total for r in rekap if r.rata_total is not None]
        materi_count = len(self.list_materi(semester_id, hanya_aktif=True))
        return {
            "jumlah_siswa": len(rekap),
            "jumlah_materi": materi_count,
            "rata_kelas": rata_rata(totals),
            "jumlah_lengkap": sum(1 for r in rekap if r.status == "lengkap"),
            "jumlah_sebagian": sum(1 for r in rekap if r.status == "sebagian"),
            "jumlah_belum": sum(1 for r in rekap if r.status == "belum"),
        }

    def get_laporan_detail(self, semester_id: int, kelas_id: int | None = None) -> dict:
        siswa = self.list_siswa(semester_id, kelas_id)
        materi_names = self.list_nama_materi(semester_id, hanya_aktif=True)
        materi_pair_by_name = {
            name: self.get_materi_pair_by_nama(semester_id, name)
            for name in materi_names
        }
        materi_by_id = {
            item["id"]: item
            for pair in materi_pair_by_name.values()
            for item in pair.values()
        }
        penilaian_map: dict[tuple[int, int], dict] = {}

        if siswa and materi_by_id:
            siswa_ids = [item["id"] for item in siswa]
            placeholders_siswa = ",".join("?" for _ in siswa_ids)
            placeholders_materi = ",".join("?" for _ in materi_by_id)
            with get_connection() as conn:
                rows = conn.execute(
                    f"""
                    SELECT siswa_id, materi_id, nilai
                    FROM penilaian
                    WHERE siswa_id IN ({placeholders_siswa})
                      AND materi_id IN ({placeholders_materi})
                    """,
                    [*siswa_ids, *materi_by_id.keys()],
                ).fetchall()
            for row in rows:
                penilaian_map[(row["siswa_id"], row["materi_id"])] = dict(row)

        detail_rows = []
        current_class = None
        class_no = 0
        for item in siswa:
            if item["kelas"] != current_class:
                current_class = item["kelas"]
                class_no = 0
            class_no += 1

            materi_scores = []
            final_values = []
            for name in materi_names:
                pair = materi_pair_by_name[name]
                h_materi = pair.get("hafalan")
                p_materi = pair.get("praktik")
                h_score = None if not h_materi else penilaian_map.get((item["id"], h_materi["id"]), {}).get("nilai")
                p_score = None if not p_materi else penilaian_map.get((item["id"], p_materi["id"]), {}).get("nilai")
                if h_score is not None:
                    final_values.append(h_score)
                if p_score is not None:
                    final_values.append(p_score)
                materi_scores.append({"nama": name, "hafalan": h_score, "praktik": p_score})

            detail_rows.append(
                {
                    "kelas": item["kelas"],
                    "no": class_no,
                    "nis": item["nis"],
                    "nama": item["nama"],
                    "materi": materi_scores,
                    "rata_akhir": rata_rata(final_values),
                }
            )

        headers = ["Kelas", "No", "Nama"]
        for name in materi_names:
            headers.extend([f"{name} Hafalan", f"{name} Praktik"])
        headers.append("Rata-rata Akhir")
        return {"headers": headers, "materi_names": materi_names, "rows": detail_rows}

    def _get_rekap(self, semester_id: int, kelas_id: int | None) -> list[RekapSiswa]:
        siswa = self.list_siswa(semester_id, kelas_id)
        materi = self.list_materi(semester_id, hanya_aktif=True)
        jumlah_materi_aktif = len(materi)
        materi_by_id = {m["id"]: m for m in materi}
        siswa_ids = [s["id"] for s in siswa]
        nilai_by_siswa: dict[int, dict[str, list[float]]] = {
            s["id"]: {"hafalan": [], "praktik": []} for s in siswa
        }
        dinilai_by_siswa: dict[int, set[int]] = {s["id"]: set() for s in siswa}

        if siswa_ids and materi_by_id:
            placeholders_siswa = ",".join("?" for _ in siswa_ids)
            placeholders_materi = ",".join("?" for _ in materi_by_id)
            with get_connection() as conn:
                rows = conn.execute(
                    f"""
                    SELECT siswa_id, materi_id, nilai
                    FROM penilaian
                    WHERE siswa_id IN ({placeholders_siswa})
                      AND materi_id IN ({placeholders_materi})
                    """,
                    [*siswa_ids, *materi_by_id.keys()],
                ).fetchall()
            for row in rows:
                aspek = materi_by_id[row["materi_id"]]["aspek"]
                nilai_by_siswa[row["siswa_id"]][aspek].append(row["nilai"])
                dinilai_by_siswa[row["siswa_id"]].add(row["materi_id"])

        rekap = []
        for item in siswa:
            nilai_aspek = nilai_by_siswa[item["id"]]
            rata_hafalan = rata_rata(nilai_aspek["hafalan"])
            rata_praktik = rata_rata(nilai_aspek["praktik"])
            rata_total = hitung_rata_total(rata_hafalan, rata_praktik)
            rekap.append(
                RekapSiswa(
                    siswa_id=item["id"],
                    nis=item["nis"],
                    nama=item["nama"],
                    kelas=item["kelas"],
                    rata_hafalan=rata_hafalan,
                    rata_praktik=rata_praktik,
                    rata_total=rata_total,
                    status=tentukan_status(len(dinilai_by_siswa[item["id"]]), jumlah_materi_aktif),
                )
            )
        return hitung_ranking(rekap)
