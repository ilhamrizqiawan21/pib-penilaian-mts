from services.penilaian_service import (
    NILAI_MAKS,
    RekapSiswa,
    ambil_top_bottom,
    hitung_nilai,
    hitung_ranking,
    hitung_rata_total,
    rata_rata,
    tentukan_status,
)


class TestHitungNilai:
    def test_sempurna(self):
        assert hitung_nilai(0, 2) == NILAI_MAKS

    def test_dengan_kesalahan(self):
        assert hitung_nilai(3, 2) == 84

    def test_floor_nol(self):
        assert hitung_nilai(100, 1) == 0

    def test_poin_desimal(self):
        assert hitung_nilai(2, 2.5) == 85.0


class TestRataRata:
    def test_normal(self):
        assert rata_rata([80, 90, 70]) == 80.0

    def test_kosong(self):
        assert rata_rata([]) is None


class TestRataTotal:
    def test_kedua_aspek(self):
        assert hitung_rata_total(80, 90) == 85.0

    def test_hanya_hafalan(self):
        assert hitung_rata_total(80, None) == 80.0

    def test_keduanya_null(self):
        assert hitung_rata_total(None, None) is None


class TestStatus:
    def test_belum(self):
        assert tentukan_status(0, 5) == "belum"

    def test_sebagian(self):
        assert tentukan_status(2, 5) == "sebagian"

    def test_lengkap(self):
        assert tentukan_status(5, 5) == "lengkap"


class TestRanking:
    def _make(self, nama, total, hafalan=None, praktik=None):
        return RekapSiswa(
            siswa_id=1,
            nis="001",
            nama=nama,
            kelas="7A",
            rata_hafalan=hafalan,
            rata_praktik=praktik,
            rata_total=total,
            status="lengkap",
        )

    def test_urutan_desc(self):
        data = [self._make("Budi", 70), self._make("Ahmad", 90)]
        ranked = hitung_ranking(data)
        assert ranked[0].nama == "Ahmad"
        assert ranked[0].peringkat == 1

    def test_tie_break_nama(self):
        data = [self._make("Budi", 85, 80, 90), self._make("Ahmad", 85, 80, 90)]
        ranked = hitung_ranking(data)
        assert ranked[0].nama == "Ahmad"

    def test_tanpa_nilai_no_rank(self):
        data = [self._make("Ahmad", None)]
        ranked = hitung_ranking(data)
        assert ranked[0].peringkat is None


class TestTopBottom:
    def test_top_5(self):
        ranked = [
            RekapSiswa(i, f"00{i}", f"S{i}", "7A", 90 - i, 90 - i, 90 - i, "lengkap", i)
            for i in range(1, 11)
        ]
        top, bottom = ambil_top_bottom(ranked, 5)
        assert len(top) == 5
        assert top[0].peringkat == 1
        assert bottom[0].peringkat == 10
