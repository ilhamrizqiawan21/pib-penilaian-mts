import type { BackupData, Kelas, Materi, Penilaian, Semester, Siswa, TahunAjaran } from "../types";

type StoreName = "tahunAjaran" | "semester" | "kelas" | "siswa" | "materi" | "penilaian" | "pengaturan";
const DB_NAME = "pib-penilaian-pwa";
const DB_VERSION = 1;

function requestToPromise<T>(request: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export class Repository {
  private dbPromise: Promise<IDBDatabase>;

  constructor() {
    this.dbPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = () => {
        const db = request.result;
        for (const name of ["tahunAjaran", "semester", "kelas", "siswa", "materi", "penilaian"]) {
          if (!db.objectStoreNames.contains(name)) db.createObjectStore(name, { keyPath: "id", autoIncrement: true });
        }
        if (!db.objectStoreNames.contains("pengaturan")) db.createObjectStore("pengaturan", { keyPath: "key" });
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  private async store(name: StoreName, mode: IDBTransactionMode = "readonly") {
    const db = await this.dbPromise;
    return db.transaction(name, mode).objectStore(name);
  }

  async all<T>(name: StoreName): Promise<T[]> {
    return requestToPromise((await this.store(name)).getAll()) as Promise<T[]>;
  }

  async put(name: StoreName, value: any): Promise<number> {
    const result = await requestToPromise((await this.store(name, "readwrite")).put(value));
    return Number(result);
  }

  async delete(name: StoreName, id: number): Promise<void> {
    await requestToPromise((await this.store(name, "readwrite")).delete(id));
  }

  async clear(name: StoreName): Promise<void> {
    await requestToPromise((await this.store(name, "readwrite")).clear());
  }

  async getSetting(key: string): Promise<string | undefined> {
    const row = await requestToPromise((await this.store("pengaturan")).get(key)) as { key: string; value: string } | undefined;
    return row?.value;
  }

  async setSetting(key: string, value: string): Promise<void> {
    await requestToPromise((await this.store("pengaturan", "readwrite")).put({ key, value }));
  }

  async ensureSeed(): Promise<void> {
    if ((await this.all<TahunAjaran>("tahunAjaran")).length) return;
    const taId = await this.put("tahunAjaran", { nama: "2026/2027", isAktif: true });
    const semesterId = await this.put("semester", { tahunAjaranId: taId, nama: "Ganjil", isAktif: true });
    const kelasId = await this.put("kelas", { nama: "8A", tingkat: 8 });
    await this.put("siswa", { nis: "001", nama: "Ahmad Fauzi", kelasId, semesterId, isAktif: true });
    await this.put("materi", { semesterId, nama: "Wudhu", aspek: "hafalan", poinPengurangan: 2, urutan: 1, isAktif: true });
    await this.put("materi", { semesterId, nama: "Wudhu", aspek: "praktik", poinPengurangan: 3, urutan: 1, isAktif: true });
    await this.setSetting("nama_sekolah", "MTs PIB");
  }

  async backup(): Promise<BackupData> {
    const settingsRows = await this.all<{ key: string; value: string }>("pengaturan");
    return {
      version: 1,
      exportedAt: new Date().toISOString(),
      tahunAjaran: await this.all<TahunAjaran>("tahunAjaran"),
      semester: await this.all<Semester>("semester"),
      kelas: await this.all<Kelas>("kelas"),
      siswa: await this.all<Siswa>("siswa"),
      materi: await this.all<Materi>("materi"),
      penilaian: await this.all<Penilaian>("penilaian"),
      pengaturan: Object.fromEntries(settingsRows.map((row) => [row.key, row.value])),
    };
  }

  async restore(data: BackupData): Promise<void> {
    for (const store of ["tahunAjaran", "semester", "kelas", "siswa", "materi", "penilaian", "pengaturan"] as StoreName[]) {
      await this.clear(store);
    }
    for (const row of data.tahunAjaran) await this.put("tahunAjaran", row);
    for (const row of data.semester) await this.put("semester", row);
    for (const row of data.kelas) await this.put("kelas", row);
    for (const row of data.siswa) await this.put("siswa", row);
    for (const row of data.materi) await this.put("materi", row);
    for (const row of data.penilaian) await this.put("penilaian", row);
    for (const [key, value] of Object.entries(data.pengaturan || {})) await this.setSetting(key, value);
  }
}
