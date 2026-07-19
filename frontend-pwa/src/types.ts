export type SemesterName = "Ganjil" | "Genap";
export type Aspek = "hafalan" | "praktik";

export interface TahunAjaran {
  id: number;
  nama: string;
  isAktif: boolean;
}

export interface Semester {
  id: number;
  tahunAjaranId: number;
  nama: SemesterName;
  isAktif: boolean;
}

export interface Kelas {
  id: number;
  nama: string;
  tingkat: number;
}

export interface Siswa {
  id: number;
  nis: string;
  nama: string;
  kelasId: number;
  semesterId: number;
  isAktif: boolean;
}

export interface Materi {
  id: number;
  semesterId: number;
  nama: string;
  aspek: Aspek;
  poinPengurangan: number;
  urutan: number;
  isAktif: boolean;
}

export interface Penilaian {
  id: number;
  siswaId: number;
  materiId: number;
  jumlahKesalahan: number;
  nilai: number;
  poinSnapshot: number;
  updatedAt: string;
}

export interface BackupData {
  version: 1;
  exportedAt: string;
  tahunAjaran: TahunAjaran[];
  semester: Semester[];
  kelas: Kelas[];
  siswa: Siswa[];
  materi: Materi[];
  penilaian: Penilaian[];
  pengaturan: Record<string, string>;
}
