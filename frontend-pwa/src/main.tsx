import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { Repository } from "./db/repository";
import { hitungNilai, ketuntasan, rataTotal } from "./services/penilaian";
import type { Aspek, BackupData, Kelas, Materi, Penilaian, Semester, Siswa, TahunAjaran } from "./types";
import "./styles.css";

const repo = new Repository();
const menus = ["Dashboard", "Periode", "Siswa", "Materi", "Penilaian", "Laporan"] as const;
type Menu = (typeof menus)[number];
const menuMeta: Record<Menu, { short: string; icon: string }> = {
  Dashboard: { short: "Dash", icon: "D" },
  Periode: { short: "Periode", icon: "P" },
  Siswa: { short: "Siswa", icon: "S" },
  Materi: { short: "Materi", icon: "M" },
  Penilaian: { short: "Nilai", icon: "N" },
  Laporan: { short: "Laporan", icon: "L" },
};

function App() {
  const [active, setActive] = useState<Menu>("Dashboard");
  const [ready, setReady] = useState(false);
  const [toast, setToast] = useState("");
  const [tahunAjaran, setTahunAjaran] = useState<TahunAjaran[]>([]);
  const [semester, setSemester] = useState<Semester[]>([]);
  const [kelas, setKelas] = useState<Kelas[]>([]);
  const [siswa, setSiswa] = useState<Siswa[]>([]);
  const [materi, setMateri] = useState<Materi[]>([]);
  const [penilaian, setPenilaian] = useState<Penilaian[]>([]);
  const [namaSekolah, setNamaSekolah] = useState("MTs PIB");

  async function reload() {
    setTahunAjaran(await repo.all<TahunAjaran>("tahunAjaran"));
    setSemester(await repo.all<Semester>("semester"));
    setKelas(await repo.all<Kelas>("kelas"));
    setSiswa(await repo.all<Siswa>("siswa"));
    setMateri(await repo.all<Materi>("materi"));
    setPenilaian(await repo.all<Penilaian>("penilaian"));
    setNamaSekolah((await repo.getSetting("nama_sekolah")) || "MTs PIB");
  }

  async function notify(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(""), 2400);
    await reload();
  }

  useEffect(() => {
    repo.ensureSeed().then(reload).then(() => setReady(true));
    if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js");
  }, []);

  const semesterAktif = semester.find((item) => item.isAktif);
  const tahunAktif = tahunAjaran.find((item) => item.id === semesterAktif?.tahunAjaranId);
  const context = { repo, notify, tahunAjaran, semester, kelas, siswa, materi, penilaian, semesterAktif };

  if (!ready) return <div className="boot">Memuat PIB...</div>;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">PIB</div>
          <div>
            <h1>{namaSekolah}</h1>
            <span>Penilaian Ibadah</span>
          </div>
        </div>
        <nav>
          {menus.map((menu) => (
            <button className={active === menu ? "active" : ""} onClick={() => setActive(menu)} key={menu}>
              <span className="nav-icon">{menuMeta[menu].icon}</span>
              <span>{menuMeta[menu].short}</span>
            </button>
          ))}
        </nav>
        <div className="local-card">Offline aktif<br />Data tersimpan di perangkat ini.</div>
      </aside>
      <main className="content">
        <header className="topbar">
          <div>
            <strong>{active}</strong>
            <span>{semesterAktif ? `${semesterAktif.nama} ${tahunAktif?.nama || ""}` : "Belum ada periode aktif"}</span>
          </div>
          <span className="pill">Offline</span>
        </header>
        {active === "Dashboard" && <Dashboard {...context} setActive={setActive} />}
        {active === "Periode" && <Periode {...context} />}
        {active === "Siswa" && <SiswaView {...context} />}
        {active === "Materi" && <MateriView {...context} />}
        {active === "Penilaian" && <PenilaianView {...context} />}
        {active === "Laporan" && <LaporanView {...context} />}
      </main>
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}

function Dashboard({ siswa, materi, penilaian, setActive }: Ctx & { setActive: (menu: Menu) => void }) {
  const assessed = new Set(penilaian.map((item) => item.siswaId)).size;
  const avg = penilaian.length ? penilaian.reduce((sum, item) => sum + item.nilai, 0) / penilaian.length : null;
  const trend = buildNilaiTrend(materi, penilaian);
  const hardest = trend.filter((item) => item.count > 0).sort((a, b) => a.avg - b.avg).slice(0, 4);
  const studentCompletion = buildStudentCompletion(siswa, penilaian);
  const mostComplete = studentCompletion.filter((item) => item.total > 0).slice(0, 3);
  const leastComplete = [...studentCompletion].filter((item) => item.total > 0).reverse().slice(0, 3);
  return (
    <section>
      <Hero title="Ringkasan Dashboard" subtitle="Pantau data dan progres penilaian offline." />
      <div className="stats">
        <Stat title="Siswa" value={String(siswa.filter((item) => item.isAktif).length)} />
        <Stat title="Materi" value={String(new Set(materi.map((item) => item.nama)).size)} />
        <Stat title="Sudah Dinilai" value={String(assessed)} />
        <Stat title="Rata-rata" value={avg === null ? "-" : avg.toFixed(1)} />
      </div>
      <div className="quick-actions">
        <button onClick={() => setActive("Penilaian")}>Mulai Penilaian</button>
        <button className="soft-button" onClick={() => setActive("Siswa")}>Kelola Siswa</button>
      </div>
      <div className="dashboard-insights">
        <Card title="Tren Nilai">
          <TrendChart data={trend} />
        </Card>
        <Card title="Materi Tersulit">
          <RankList
            empty="Belum ada nilai materi."
            rows={hardest.map((item) => ({
              title: item.nama,
              meta: `${item.count} nilai tersimpan`,
              value: item.avg.toFixed(1),
            }))}
          />
        </Card>
        <Card title="Ketuntasan Terbanyak">
          <RankList
            empty="Belum ada siswa tuntas."
            rows={mostComplete.map((item) => ({
              title: item.nama,
              meta: `${item.tuntas} dari ${item.total} nilai tuntas`,
              value: String(item.tuntas),
            }))}
          />
        </Card>
        <Card title="Ketuntasan Tersedikit">
          <RankList
            empty="Belum ada data ketuntasan."
            rows={leastComplete.map((item) => ({
              title: item.nama,
              meta: `${item.tuntas} dari ${item.total} nilai tuntas`,
              value: String(item.tuntas),
            }))}
          />
        </Card>
      </div>
    </section>
  );
}

function Periode({ repo, notify, tahunAjaran, semester, kelas }: Ctx) {
  async function addPeriod(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const taId = await repo.put("tahunAjaran", { nama: String(form.get("tahun")), isAktif: !tahunAjaran.length });
    await repo.put("semester", { tahunAjaranId: taId, nama: form.get("semester"), isAktif: !semester.length });
    event.currentTarget.reset();
    notify("Periode ditambahkan");
  }
  async function addKelas(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await repo.put("kelas", { nama: String(form.get("nama")).toUpperCase(), tingkat: Number(form.get("tingkat")) });
    event.currentTarget.reset();
    notify("Kelas ditambahkan");
  }
  return (
    <section>
      <Hero title="Periode dan Kelas" subtitle="Atur tahun ajaran, semester, dan kelas." />
      <div className="grid-two">
        <Card title="Tambah Periode">
          <form onSubmit={addPeriod} className="form-stack">
            <input name="tahun" placeholder="2026/2027" required />
            <select name="semester"><option>Ganjil</option><option>Genap</option></select>
            <button>Simpan Periode</button>
          </form>
          <MobileList rows={tahunAjaran.map((item) => ({ title: item.nama, meta: item.isAktif ? "Aktif" : "Tidak aktif" }))} />
        </Card>
        <Card title="Tambah Kelas">
          <form onSubmit={addKelas} className="form-stack">
            <input name="nama" placeholder="8A" required />
            <select name="tingkat"><option>7</option><option>8</option><option>9</option></select>
            <button>Tambah Kelas</button>
          </form>
          <MobileList rows={kelas.map((item) => ({ title: item.nama, meta: `Tingkat ${item.tingkat}` }))} />
        </Card>
      </div>
    </section>
  );
}

function SiswaView({ repo, notify, siswa, kelas, semesterAktif }: Ctx) {
  const [search, setSearch] = useState("");
  const [kelasFilter, setKelasFilter] = useState("semua");
  const [statusFilter, setStatusFilter] = useState("aktif");
  const [editingSiswa, setEditingSiswa] = useState<Siswa | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const kelasName = (kelasId: number) => kelas.find((item) => item.id === kelasId)?.nama || "-";
  const normalizedSearch = search.trim().toLowerCase();
  const filteredSiswa = siswa
    .filter((item) => {
      const matchesSearch = !normalizedSearch || item.nama.toLowerCase().includes(normalizedSearch) || item.nis.toLowerCase().includes(normalizedSearch);
      const matchesKelas = kelasFilter === "semua" || item.kelasId === Number(kelasFilter);
      const matchesStatus = statusFilter === "semua" || (statusFilter === "aktif" ? item.isAktif : !item.isAktif);
      return matchesSearch && matchesKelas && matchesStatus;
    })
    .sort((a, b) => kelasName(a.kelasId).localeCompare(kelasName(b.kelasId)) || a.nama.localeCompare(b.nama));
  const totalPages = Math.max(1, Math.ceil(filteredSiswa.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const paginatedSiswa = filteredSiswa.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  useEffect(() => {
    setPage(1);
  }, [search, kelasFilter, statusFilter, pageSize]);

  async function add(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!semesterAktif) return;
    const form = new FormData(event.currentTarget);
    await repo.put("siswa", {
      nis: String(form.get("nis")),
      nama: String(form.get("nama")),
      kelasId: Number(form.get("kelasId")),
      semesterId: semesterAktif.id,
      isAktif: true,
    });
    event.currentTarget.reset();
    notify("Siswa ditambahkan");
  }

  async function update(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editingSiswa) return;
    const form = new FormData(event.currentTarget);
    await repo.put("siswa", {
      ...editingSiswa,
      nis: String(form.get("nis")),
      nama: String(form.get("nama")),
      kelasId: Number(form.get("kelasId")),
      isAktif: form.get("isAktif") === "true",
    });
    setEditingSiswa(null);
    notify("Siswa diperbarui");
  }

  async function toggleStatus(item: Siswa) {
    await repo.put("siswa", { ...item, isAktif: !item.isAktif });
    notify(item.isAktif ? "Siswa dinonaktifkan" : "Siswa diaktifkan");
  }

  async function deleteSiswa(item: Siswa) {
    const ok = window.confirm(`Hapus permanen ${item.nama}? Data siswa akan hilang dari perangkat ini.`);
    if (!ok) return;
    await repo.delete("siswa", item.id);
    notify("Siswa dihapus permanen");
  }

  return (
    <section>
      <Hero title="Manajemen Siswa" subtitle="Tambah dan pantau data siswa offline." />
      <Card title="Tambah Siswa">
        <form onSubmit={add} className="inline-form">
          <input name="nis" placeholder="NIS" required />
          <input name="nama" placeholder="Nama siswa" required />
          <select name="kelasId">{kelas.map((item) => <option value={item.id} key={item.id}>{item.nama}</option>)}</select>
          <button>Tambah</button>
        </form>
      </Card>
      <Card title="Data Siswa">
        <div className="filter-row">
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Cari NIS atau nama" />
          <select value={kelasFilter} onChange={(event) => setKelasFilter(event.target.value)}>
            <option value="semua">Semua Kelas</option>
            {kelas.map((item) => <option value={item.id} key={item.id}>{item.nama}</option>)}
          </select>
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="aktif">Aktif</option>
            <option value="nonaktif">Nonaktif</option>
            <option value="semua">Semua Status</option>
          </select>
        </div>
        <div className="result-bar">
          <span>{filteredSiswa.length} siswa ditemukan</span>
          <label>
            Per halaman
            <select value={pageSize} onChange={(event) => setPageSize(Number(event.target.value))}>
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
            </select>
          </label>
        </div>
      </Card>
      <ResponsiveRecords
        headers={["NIS", "Nama", "Kelas", "Status", "Aksi"]}
        empty={siswa.length ? "Tidak ada siswa sesuai filter." : "Belum ada siswa terdata."}
        rows={paginatedSiswa.map((item) => ({
          title: item.nama,
          meta: `NIS ${item.nis}`,
          badge: kelasName(item.kelasId),
          status: item.isAktif ? "Aktif" : "Nonaktif",
          cells: [
            item.nis,
            item.nama,
            kelasName(item.kelasId),
            <StatusBadge key="status" status={item.isAktif ? "Aktif" : "Nonaktif"} />,
            <ActionButtons
              key="actions"
              onEdit={() => setEditingSiswa(item)}
              onToggle={() => toggleStatus(item)}
              onDelete={() => deleteSiswa(item)}
              toggleLabel={item.isAktif ? "Nonaktifkan" : "Aktifkan"}
              isActive={item.isAktif}
            />,
          ],
          actions: (
            <ActionButtons
              onEdit={() => setEditingSiswa(item)}
              onToggle={() => toggleStatus(item)}
              onDelete={() => deleteSiswa(item)}
              toggleLabel={item.isAktif ? "Nonaktifkan" : "Aktifkan"}
              isActive={item.isAktif}
            />
          ),
        }))}
      />
      <Pagination currentPage={currentPage} totalPages={totalPages} totalItems={filteredSiswa.length} pageSize={pageSize} onPageChange={setPage} />
      {editingSiswa && (
        <div className="modal-backdrop" role="presentation">
          <div className="modal-card" role="dialog" aria-modal="true" aria-labelledby="edit-siswa-title">
            <h3 id="edit-siswa-title">Edit Siswa</h3>
            <form onSubmit={update} className="form-stack">
              <input name="nis" placeholder="NIS" defaultValue={editingSiswa.nis} required />
              <input name="nama" placeholder="Nama siswa" defaultValue={editingSiswa.nama} required />
              <select name="kelasId" defaultValue={editingSiswa.kelasId}>
                {kelas.map((item) => <option value={item.id} key={item.id}>{item.nama}</option>)}
              </select>
              <select name="isAktif" defaultValue={String(editingSiswa.isAktif)}>
                <option value="true">Aktif</option>
                <option value="false">Nonaktif</option>
              </select>
              <div className="modal-actions">
                <button type="button" className="soft-button" onClick={() => setEditingSiswa(null)}>Batal</button>
                <button>Simpan Perubahan</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}

function MateriView({ repo, notify, materi, semesterAktif }: Ctx) {
  async function add(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!semesterAktif) return;
    const form = new FormData(event.currentTarget);
    const nama = String(form.get("nama"));
    await repo.put("materi", { semesterId: semesterAktif.id, nama, aspek: "hafalan", poinPengurangan: Number(form.get("hafalan")), urutan: Number(form.get("urutan")), isAktif: true });
    await repo.put("materi", { semesterId: semesterAktif.id, nama, aspek: "praktik", poinPengurangan: Number(form.get("praktik")), urutan: Number(form.get("urutan")), isAktif: true });
    event.currentTarget.reset();
    notify("Materi ditambahkan");
  }
  const names = Array.from(new Set(materi.filter((item) => item.isAktif).map((item) => item.nama)));
  return (
    <section>
      <Hero title="Materi Penilaian" subtitle="Buat pasangan Hafalan dan Praktik." />
      <Card title="Tambah Materi">
        <form onSubmit={add} className="labeled-form">
          <Field label="Nama Materi" hint="Contoh: Wudhu, Shalat, Doa Harian">
            <input name="nama" placeholder="Masukkan nama materi" required />
          </Field>
          <Field label="Poin Pengurangan Hafalan" hint="Nilai dikurangi setiap 1 kesalahan Hafalan">
            <input name="hafalan" type="number" min="0" defaultValue="2" />
          </Field>
          <Field label="Poin Pengurangan Praktik" hint="Nilai dikurangi setiap 1 kesalahan Praktik">
            <input name="praktik" type="number" min="0" defaultValue="3" />
          </Field>
          <Field label="Urutan Materi" hint="Dipakai untuk susunan dan tren nilai">
            <input name="urutan" type="number" min="1" defaultValue="1" />
          </Field>
          <button>Tambah</button>
        </form>
      </Card>
      <Card title="Daftar Materi">
        <ResponsiveRecords
          headers={["Materi", "Hafalan", "Praktik", "Urutan"]}
          rows={names.map((name) => {
            const pair = materi.filter((item) => item.nama === name && item.isAktif);
            const hafalan = pair.find((item) => item.aspek === "hafalan")?.poinPengurangan ?? "-";
            const praktik = pair.find((item) => item.aspek === "praktik")?.poinPengurangan ?? "-";
            const urutan = Math.min(...pair.map((item) => item.urutan));
            return {
              title: name,
              meta: `Hafalan -${hafalan} | Praktik -${praktik}`,
              badge: `Urutan ${Number.isFinite(urutan) ? urutan : "-"}`,
              cells: [name, `-${hafalan}`, `-${praktik}`, Number.isFinite(urutan) ? urutan : "-"],
            };
          })}
        />
      </Card>
    </section>
  );
}

function PenilaianView({ repo, notify, kelas, siswa, materi, penilaian }: Ctx) {
  const [kelasId, setKelasId] = useState(0);
  const [namaMateri, setNamaMateri] = useState("");
  const [drafts, setDrafts] = useState<Record<number, { hafalan: number; praktik: number }>>({});
  const names = Array.from(new Set(materi.filter((item) => item.isAktif).map((item) => item.nama)));
  const selectedKelas = kelasId || kelas[0]?.id || 0;
  const selectedNama = namaMateri || names[0] || "";
  const pair = materi.filter((item) => item.nama === selectedNama);
  const siswaKelas = siswa.filter((item) => item.kelasId === selectedKelas && item.isAktif).sort((a, b) => a.nama.localeCompare(b.nama));
  const hMateri = pair.find((m) => m.aspek === "hafalan");
  const pMateri = pair.find((m) => m.aspek === "praktik");
  const rows = siswaKelas.map((student) => {
    const draft = drafts[student.id] || { hafalan: 0, praktik: 0 };
    const nilaiHafalan = hMateri ? hitungNilai(draft.hafalan, hMateri.poinPengurangan) : undefined;
    const nilaiPraktik = pMateri ? hitungNilai(draft.praktik, pMateri.poinPengurangan) : undefined;
    const rata = rataTotal(nilaiHafalan, nilaiPraktik);
    return { student, draft, nilaiHafalan, nilaiPraktik, rata };
  });
  const assessed = rows.filter((row) => row.rata !== null).length;
  const classAverage = assessed ? rows.reduce((sum, row) => sum + (row.rata || 0), 0) / assessed : null;
  const incomplete = rows.filter((row) => row.rata === null || row.rata < 75).length;
  const penilaianSignature = penilaian.map((item) => `${item.id}:${item.siswaId}:${item.materiId}:${item.jumlahKesalahan}`).join("|");

  useEffect(() => {
    resetDrafts();
  }, [selectedKelas, selectedNama, penilaianSignature, siswaKelas.length, hMateri?.id, pMateri?.id]);

  function resetDrafts() {
    const next: Record<number, { hafalan: number; praktik: number }> = {};
    siswaKelas.forEach((student) => {
      const h = penilaian.find((n) => n.siswaId === student.id && n.materiId === hMateri?.id);
      const p = penilaian.find((n) => n.siswaId === student.id && n.materiId === pMateri?.id);
      next[student.id] = { hafalan: h?.jumlahKesalahan || 0, praktik: p?.jumlahKesalahan || 0 };
    });
    setDrafts(next);
  }

  function updateDraft(siswaId: number, aspek: Aspek, value: number) {
    setDrafts((current) => ({
      ...current,
      [siswaId]: {
        hafalan: current[siswaId]?.hafalan || 0,
        praktik: current[siswaId]?.praktik || 0,
        [aspek]: Math.max(0, value),
      },
    }));
  }

  async function saveRecord(siswaId: number, aspek: Aspek, jumlahKesalahan: number) {
    const m = pair.find((item) => item.aspek === aspek);
    if (!m) return;
    const existing = penilaian.find((item) => item.siswaId === siswaId && item.materiId === m.id);
    await repo.put("penilaian", {
      id: existing?.id,
      siswaId,
      materiId: m.id,
      jumlahKesalahan,
      nilai: hitungNilai(jumlahKesalahan, m.poinPengurangan),
      poinSnapshot: m.poinPengurangan,
      updatedAt: new Date().toISOString(),
    });
  }

  async function saveAll() {
    for (const student of siswaKelas) {
      const draft = drafts[student.id] || { hafalan: 0, praktik: 0 };
      if (hMateri) await saveRecord(student.id, "hafalan", draft.hafalan);
      if (pMateri) await saveRecord(student.id, "praktik", draft.praktik);
    }
    notify("Penilaian disimpan");
  }

  return (
    <section>
      <Hero title="Input Penilaian" subtitle="Nilai banyak siswa dalam satu layar." />
      <Card title="Filter">
        <div className="filter-row assessment-filter">
          <Field label="Materi Penilaian" hint="Pilih materi yang akan dinilai">
            <select value={selectedNama} onChange={(e) => setNamaMateri(e.target.value)}>{names.map((item) => <option key={item}>{item}</option>)}</select>
          </Field>
          <Field label="Kelas" hint="Pilih kelas yang sedang dinilai">
            <select value={selectedKelas} onChange={(e) => setKelasId(Number(e.target.value))}>{kelas.map((item) => <option value={item.id} key={item.id}>{item.nama}</option>)}</select>
          </Field>
        </div>
      </Card>
      <AssessmentSummary total={siswaKelas.length} assessed={assessed} average={classAverage} incomplete={incomplete} />
      {!siswaKelas.length ? (
        <Card title="Belum ada siswa">Tambahkan siswa pada kelas ini terlebih dahulu.</Card>
      ) : (
        <AssessmentQuickList
          rows={rows}
          kelasName={kelas.find((item) => item.id === selectedKelas)?.nama || "-"}
          hasHafalan={Boolean(hMateri)}
          hasPraktik={Boolean(pMateri)}
          onChange={updateDraft}
        />
      )}
      <StickySaveBar onReset={resetDrafts} onSave={saveAll} disabled={!siswaKelas.length} />
    </section>
  );
}

function AssessmentSummary({ total, assessed, average, incomplete }: { total: number; assessed: number; average: number | null; incomplete: number }) {
  return (
    <div className="assessment-summary">
      <Stat title="Siswa" value={String(total)} />
      <Stat title="Sudah Dinilai" value={String(assessed)} />
      <Stat title="Rata-rata" value={average === null ? "-" : average.toFixed(1)} />
      <Stat title="Belum Tuntas" value={String(incomplete)} />
    </div>
  );
}

function AssessmentQuickList(props: {
  rows: Array<{ student: Siswa; draft: { hafalan: number; praktik: number }; nilaiHafalan?: number; nilaiPraktik?: number; rata: number | null }>;
  kelasName: string;
  hasHafalan: boolean;
  hasPraktik: boolean;
  onChange: (siswaId: number, aspek: Aspek, value: number) => void;
}) {
  return (
    <div className="assessment-list">
      <div className="assessment-head">
        <span>No</span>
        <span>Nama</span>
        <span>Hafalan</span>
        <span>Praktik</span>
        <span>Rata-rata</span>
        <span>Ketuntasan</span>
      </div>
      {props.rows.map((row, index) => (
        <AssessmentStudentRow
          key={row.student.id}
          number={index + 1}
          row={row}
          kelasName={props.kelasName}
          hasHafalan={props.hasHafalan}
          hasPraktik={props.hasPraktik}
          onChange={props.onChange}
        />
      ))}
    </div>
  );
}

function AssessmentStudentRow(props: {
  number: number;
  row: { student: Siswa; draft: { hafalan: number; praktik: number }; nilaiHafalan?: number; nilaiPraktik?: number; rata: number | null };
  kelasName: string;
  hasHafalan: boolean;
  hasPraktik: boolean;
  onChange: (siswaId: number, aspek: Aspek, value: number) => void;
}) {
  const { student, draft, nilaiHafalan, nilaiPraktik, rata } = props.row;
  return (
    <div className="assessment-row">
      <span className="assessment-no">{props.number}</span>
      <div className="assessment-student">
        <strong>{student.nama}</strong>
        <small>NIS {student.nis} | {props.kelasName}</small>
      </div>
      <CompactStepper
        label="Hafalan"
        value={draft.hafalan}
        score={nilaiHafalan}
        disabled={!props.hasHafalan}
        onChange={(value) => props.onChange(student.id, "hafalan", value)}
      />
      <CompactStepper
        label="Praktik"
        value={draft.praktik}
        score={nilaiPraktik}
        disabled={!props.hasPraktik}
        onChange={(value) => props.onChange(student.id, "praktik", value)}
      />
      <strong className="assessment-average">{rata === null ? "-" : rata.toFixed(1)}</strong>
      <StatusBadge status={ketuntasan(rata)} />
    </div>
  );
}

function CompactStepper({ label, value, score, disabled, onChange }: { label: string; value: number; score?: number; disabled?: boolean; onChange: (value: number) => void }) {
  return (
    <div className="compact-stepper">
      <span>{label}</span>
      <div>
        <button type="button" onClick={() => onChange(Math.max(0, value - 1))} disabled={disabled}>-</button>
        <strong>{disabled ? "-" : value}</strong>
        <button type="button" onClick={() => onChange(value + 1)} disabled={disabled}>+</button>
      </div>
      <small>Nilai {score === undefined ? "-" : score.toFixed(1)}</small>
    </div>
  );
}

function StickySaveBar({ onReset, onSave, disabled }: { onReset: () => void; onSave: () => void; disabled?: boolean }) {
  return (
    <div className="sticky-save">
      <button type="button" className="soft-button" onClick={onReset} disabled={disabled}>Reset</button>
      <button type="button" onClick={onSave} disabled={disabled}>Simpan Semua</button>
    </div>
  );
}

function LaporanView(ctx: Ctx) {
  const [kelasFilter, setKelasFilter] = useState("semua");
  const report = buildReport(ctx.siswa, ctx.kelas, ctx.materi, ctx.penilaian, kelasFilter);
  async function exportBackup() {
    const backup = await ctx.repo.backup();
    const blob = new Blob([JSON.stringify(backup, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `pib-backup-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
    ctx.notify("Backup JSON dibuat");
  }
  async function importBackup(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    await ctx.repo.restore(JSON.parse(await file.text()) as BackupData);
    ctx.notify("Backup JSON dipulihkan");
  }
  function exportExcel() {
    downloadReportExcel(report);
    ctx.notify("Excel laporan dibuat");
  }
  function exportPdf() {
    openReportPdf(report);
    ctx.notify("PDF laporan dibuka");
  }
  return (
    <section>
      <Hero title="Laporan" subtitle="Rekap nilai per kelas, materi, Hafalan, dan Praktik." />
      <Card title="Filter Laporan">
        <div className="report-actions">
          <Field label="Kelas" hint="Pilih kelas yang akan diekspor">
            <select value={kelasFilter} onChange={(event) => setKelasFilter(event.target.value)}>
              <option value="semua">Semua Kelas</option>
              {ctx.kelas.map((item) => <option value={item.id} key={item.id}>{item.nama}</option>)}
            </select>
          </Field>
          <button onClick={exportExcel}>Export Excel</button>
          <button className="soft-button" onClick={exportPdf}>Export PDF</button>
        </div>
      </Card>
      <Card title="Backup Data">
        <div className="inline-form"><button onClick={exportBackup}>Export JSON</button><input type="file" accept="application/json" onChange={importBackup} /></div>
      </Card>
      <Card title="Preview Laporan">
        <DataTable headers={report.headers} rows={report.rows.map((row) => row.cells)} empty="Belum ada data laporan." />
      </Card>
    </section>
  );
}

function Stepper({ value, onSave }: { value: number; onSave: (value: number) => void }) {
  const [current, setCurrent] = useState(value);
  useEffect(() => setCurrent(value), [value]);
  return <div className="stepper"><button onClick={() => setCurrent(Math.max(0, current - 1))}>-</button><strong>{current}</strong><button onClick={() => setCurrent(current + 1)}>+</button><button onClick={() => onSave(current)}>Simpan</button></div>;
}

function InlineStepper({ label, value, onChange, nilai }: { label: string; value: number; onChange: (value: number) => void; nilai?: number }) {
  return (
    <div className="assessment-step">
      <div>
        <strong>{label}</strong>
        <span>Kesalahan: {value} | Nilai: {nilai === undefined ? "-" : nilai.toFixed(1)}</span>
      </div>
      <div className="stepper big">
        <button onClick={() => onChange(Math.max(0, value - 1))}>-</button>
        <strong>{value}</strong>
        <button onClick={() => onChange(value + 1)}>+</button>
      </div>
    </div>
  );
}

function StudentAssessmentPager(props: {
  siswa: Siswa;
  kelas: string;
  index: number;
  total: number;
  draftHafalan: number;
  draftPraktik: number;
  setDraftHafalan: (value: number) => void;
  setDraftPraktik: (value: number) => void;
  nilaiHafalan?: number;
  nilaiPraktik?: number;
  rata: number | null;
  onPrev: () => void;
  onNext: () => void;
  onSave: () => void;
}) {
  return (
    <div className="assessment-card">
      <div className="assessment-progress">
        <span>Siswa {props.index + 1} / {props.total}</span>
        <span className="pill">{ketuntasan(props.rata)}</span>
      </div>
      <div className="student-focus">
        <h3>{props.siswa.nama}</h3>
        <p>NIS {props.siswa.nis} | Kelas {props.kelas}</p>
      </div>
      <InlineStepper label="Hafalan" value={props.draftHafalan} onChange={props.setDraftHafalan} nilai={props.nilaiHafalan} />
      <InlineStepper label="Praktik" value={props.draftPraktik} onChange={props.setDraftPraktik} nilai={props.nilaiPraktik} />
      <div className="score-summary">
        <div><span>Nilai Hafalan</span><strong>{props.nilaiHafalan === undefined ? "-" : props.nilaiHafalan.toFixed(1)}</strong></div>
        <div><span>Nilai Praktik</span><strong>{props.nilaiPraktik === undefined ? "-" : props.nilaiPraktik.toFixed(1)}</strong></div>
        <div><span>Rata-rata</span><strong>{props.rata === null ? "-" : props.rata.toFixed(1)}</strong></div>
      </div>
      <div className="pager-actions">
        <button className="soft-button" onClick={props.onPrev} disabled={props.index === 0}>Sebelumnya</button>
        <button onClick={props.onSave}>Simpan</button>
        <button className="soft-button" onClick={props.onNext} disabled={props.index >= props.total - 1}>Berikutnya</button>
      </div>
    </div>
  );
}

function Hero({ title, subtitle }: { title: string; subtitle: string }) {
  return <div className="hero"><h2>{title}</h2><p>{subtitle}</p></div>;
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return <div className="card"><h3>{title}</h3>{children}</div>;
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
      {hint && <small>{hint}</small>}
    </label>
  );
}

function Stat({ title, value }: { title: string; value: string }) {
  return <div className="stat"><span>{title}</span><strong>{value}</strong></div>;
}

function TrendChart({ data }: { data: Array<{ nama: string; avg: number; count: number }> }) {
  const filled = data.filter((item) => item.count > 0);
  if (!filled.length) return <p className="empty-note">Belum ada nilai untuk membuat tren.</p>;
  const previous = filled.length > 1 ? filled[filled.length - 2].avg : null;
  const latest = filled[filled.length - 1].avg;
  const delta = previous === null ? null : latest - previous;
  return (
    <div className="trend-panel">
      <div className="trend-summary">
        <div>
          <span>Nilai terakhir</span>
          <strong>{latest.toFixed(1)}</strong>
        </div>
        <em className={delta === null ? "" : delta >= 0 ? "up" : "down"}>
          {delta === null ? "Belum ada pembanding" : `${delta >= 0 ? "Naik" : "Turun"} ${Math.abs(delta).toFixed(1)}`}
        </em>
      </div>
      <div className="mini-chart">
        {filled.map((item) => (
          <div className="chart-column" key={item.nama}>
            <span style={{ height: `${Math.max(8, item.avg)}%` }} />
            <small>{item.nama}</small>
          </div>
        ))}
      </div>
    </div>
  );
}

function RankList({ rows, empty }: { rows: Array<{ title: string; meta: string; value: string }>; empty: string }) {
  if (!rows.length) return <p className="empty-note">{empty}</p>;
  return (
    <div className="rank-list">
      {rows.map((row, index) => (
        <div className="rank-item" key={`${row.title}-${index}`}>
          <span>{index + 1}</span>
          <div>
            <strong>{row.title}</strong>
            <small>{row.meta}</small>
          </div>
          <em>{row.value}</em>
        </div>
      ))}
    </div>
  );
}

function buildNilaiTrend(materi: Materi[], penilaian: Penilaian[]) {
  const grouped = new Map<string, { nama: string; urutan: number; values: number[] }>();
  materi.filter((item) => item.isAktif).forEach((item) => {
    if (!grouped.has(item.nama)) grouped.set(item.nama, { nama: item.nama, urutan: item.urutan, values: [] });
    const group = grouped.get(item.nama)!;
    group.urutan = Math.min(group.urutan, item.urutan);
    penilaian.filter((nilai) => nilai.materiId === item.id).forEach((nilai) => group.values.push(nilai.nilai));
  });
  return [...grouped.values()]
    .sort((a, b) => a.urutan - b.urutan || a.nama.localeCompare(b.nama))
    .map((item) => ({
      nama: item.nama,
      count: item.values.length,
      avg: item.values.length ? item.values.reduce((sum, value) => sum + value, 0) / item.values.length : 0,
    }));
}

function buildStudentCompletion(siswa: Siswa[], penilaian: Penilaian[]) {
  return siswa.filter((item) => item.isAktif).map((student) => {
    const nilai = penilaian.filter((item) => item.siswaId === student.id);
    return {
      nama: student.nama,
      total: nilai.length,
      tuntas: nilai.filter((item) => item.nilai >= 75).length,
    };
  }).sort((a, b) => b.tuntas - a.tuntas || b.total - a.total || a.nama.localeCompare(b.nama));
}

function buildReport(siswa: Siswa[], kelas: Kelas[], materi: Materi[], penilaian: Penilaian[], kelasFilter: string) {
  const materiNames = Array.from(new Set(materi.filter((item) => item.isAktif).map((item) => item.nama)))
    .sort((a, b) => {
      const aOrder = Math.min(...materi.filter((item) => item.nama === a).map((item) => item.urutan));
      const bOrder = Math.min(...materi.filter((item) => item.nama === b).map((item) => item.urutan));
      return aOrder - bOrder || a.localeCompare(b);
    });
  const headers = ["Kelas", "No", "Nama", ...materiNames.flatMap((name) => [`${name} Hafalan`, `${name} Praktik`]), "Rata-rata Akhir"];
  const selected = siswa
    .filter((item) => item.isAktif)
    .filter((item) => kelasFilter === "semua" || item.kelasId === Number(kelasFilter))
    .sort((a, b) => (kelas.find((item) => item.id === a.kelasId)?.nama || "").localeCompare(kelas.find((item) => item.id === b.kelasId)?.nama || "") || a.nama.localeCompare(b.nama));
  let currentClass = "";
  let classNo = 0;
  const rows = selected.map((student) => {
    const className = kelas.find((item) => item.id === student.kelasId)?.nama || "-";
    if (className !== currentClass) {
      currentClass = className;
      classNo = 0;
    }
    classNo += 1;
    const scores: string[] = [];
    const finalValues: number[] = [];
    materiNames.forEach((name) => {
      const pair = materi.filter((item) => item.nama === name && item.isAktif);
      const hMateri = pair.find((item) => item.aspek === "hafalan");
      const pMateri = pair.find((item) => item.aspek === "praktik");
      const hScore = penilaian.find((item) => item.siswaId === student.id && item.materiId === hMateri?.id)?.nilai;
      const pScore = penilaian.find((item) => item.siswaId === student.id && item.materiId === pMateri?.id)?.nilai;
      if (hScore !== undefined) finalValues.push(hScore);
      if (pScore !== undefined) finalValues.push(pScore);
      scores.push(hScore === undefined ? "-" : hScore.toFixed(1));
      scores.push(pScore === undefined ? "-" : pScore.toFixed(1));
    });
    const finalAverage = finalValues.length ? finalValues.reduce((sum, value) => sum + value, 0) / finalValues.length : null;
    return {
      title: student.nama,
      cells: [className, String(classNo), student.nama, ...scores, finalAverage === null ? "-" : finalAverage.toFixed(1)],
    };
  });
  return { headers, rows };
}

function reportTableHtml(report: ReturnType<typeof buildReport>) {
  const escape = (value: React.ReactNode) => String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char] || char));
  return `
    <table>
      <thead><tr>${report.headers.map((header) => `<th>${escape(header)}</th>`).join("")}</tr></thead>
      <tbody>${report.rows.map((row) => `<tr>${row.cells.map((cell) => `<td>${escape(cell)}</td>`).join("")}</tr>`).join("")}</tbody>
    </table>
  `;
}

function downloadReportExcel(report: ReturnType<typeof buildReport>) {
  const html = `<!doctype html><html><head><meta charset="utf-8" /></head><body>${reportTableHtml(report)}</body></html>`;
  const blob = new Blob([html], { type: "application/vnd.ms-excel;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `laporan-pib-${new Date().toISOString().slice(0, 10)}.xls`;
  link.click();
  URL.revokeObjectURL(url);
}

function openReportPdf(report: ReturnType<typeof buildReport>) {
  const win = window.open("", "_blank");
  if (!win) return;
  win.document.write(`
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Laporan PIB</title>
        <style>
          body { font-family: Arial, sans-serif; color: #111827; }
          h1 { margin: 0 0 4px; font-size: 20px; }
          p { margin: 0 0 16px; color: #475569; }
          table { width: 100%; border-collapse: collapse; font-size: 10px; }
          th, td { border: 1px solid #94a3b8; padding: 5px; text-align: left; }
          th { background: #eaf2f7; }
          @media print { @page { size: landscape; margin: 10mm; } }
        </style>
      </head>
      <body>
        <h1>Laporan Penilaian Praktik Ibadah</h1>
        <p>Diekspor ${new Date().toLocaleDateString("id-ID")}</p>
        ${reportTableHtml(report)}
        <script>window.onload = () => window.print();</script>
      </body>
    </html>
  `);
  win.document.close();
}

function List({ rows }: { rows: string[] }) {
  return <div className="list">{rows.length ? rows.map((row) => <div key={row}>{row}</div>) : <p>Belum ada data.</p>}</div>;
}

function DataTable({ headers, rows, empty = "Belum ada data." }: { headers: string[]; rows: React.ReactNode[][]; empty?: string }) {
  return (
    <div className="table-card">
      <table>
        <thead><tr>{headers.map((h) => <th key={h}>{h}</th>)}</tr></thead>
        <tbody>
          {rows.length ? rows.map((row, idx) => <tr key={idx}>{row.map((cell, i) => <td key={i}>{cell}</td>)}</tr>) : (
            <tr><td colSpan={headers.length} className="table-empty">{empty}</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function MobileList({ rows }: { rows: Array<{ title: string; meta?: string; badge?: string }> }) {
  return <div className="mobile-list">{rows.length ? rows.map((row) => <MobileListCard key={`${row.title}-${row.meta}`} {...row} />) : <p>Belum ada data.</p>}</div>;
}

function MobileListCard({ title, meta, badge, status, actions }: { title: string; meta?: string; badge?: string; status?: string; actions?: React.ReactNode }) {
  return (
    <div className="mobile-list-card">
      <div>
        <strong>{title}</strong>
        {meta && <span>{meta}</span>}
      </div>
      <div className="mobile-card-side">
        {badge && <em>{badge}</em>}
        {status && <StatusBadge status={status} />}
      </div>
      {actions && <div className="mobile-card-actions">{actions}</div>}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const isInactive = status.toLowerCase().includes("non") || status.toLowerCase().includes("belum");
  return <span className={`status-badge ${isInactive ? "muted" : "ok"}`}>{status}</span>;
}

function ActionButtons({ onEdit, onToggle, onDelete, toggleLabel, isActive }: { onEdit: () => void; onToggle: () => void; onDelete: () => void; toggleLabel: string; isActive: boolean }) {
  return (
    <div className="row-actions">
      <button type="button" className="icon-button soft-button" onClick={onEdit} aria-label="Edit siswa" title="Edit siswa">E</button>
      <button type="button" className="icon-button soft-button" onClick={onToggle} aria-label={toggleLabel} title={toggleLabel}>{isActive ? "Off" : "On"}</button>
      <button type="button" className="icon-button danger-button" onClick={onDelete} aria-label="Hapus permanen siswa" title="Hapus permanen">X</button>
    </div>
  );
}

function Pagination({ currentPage, totalPages, totalItems, pageSize, onPageChange }: { currentPage: number; totalPages: number; totalItems: number; pageSize: number; onPageChange: (page: number) => void }) {
  const start = totalItems ? (currentPage - 1) * pageSize + 1 : 0;
  const end = Math.min(totalItems, currentPage * pageSize);
  return (
    <div className="pagination">
      <span>{start}-{end} dari {totalItems}</span>
      <div>
        <button type="button" className="soft-button" onClick={() => onPageChange(1)} disabled={currentPage === 1}>Awal</button>
        <button type="button" className="soft-button" onClick={() => onPageChange(Math.max(1, currentPage - 1))} disabled={currentPage === 1}>Prev</button>
        <strong>{currentPage} / {totalPages}</strong>
        <button type="button" className="soft-button" onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))} disabled={currentPage === totalPages}>Next</button>
        <button type="button" className="soft-button" onClick={() => onPageChange(totalPages)} disabled={currentPage === totalPages}>Akhir</button>
      </div>
    </div>
  );
}

function ResponsiveRecords({ headers, rows, empty = "Belum ada data." }: { headers: string[]; rows: Array<{ title: string; meta: string; badge?: string; status?: string; actions?: React.ReactNode; cells: React.ReactNode[] }>; empty?: string }) {
  return (
    <>
      <div className="records-mobile">{rows.length ? rows.map((row) => <MobileListCard key={`${row.title}-${row.meta}`} title={row.title} meta={row.meta} badge={row.badge} status={row.status} actions={row.actions} />) : <p>{empty}</p>}</div>
      <DataTable headers={headers} rows={rows.map((row) => row.cells)} empty={empty} />
    </>
  );
}

interface Ctx {
  repo: Repository;
  notify: (message: string) => Promise<void>;
  tahunAjaran: TahunAjaran[];
  semester: Semester[];
  kelas: Kelas[];
  siswa: Siswa[];
  materi: Materi[];
  penilaian: Penilaian[];
  semesterAktif?: Semester;
}

createRoot(document.getElementById("root")!).render(<App />);
