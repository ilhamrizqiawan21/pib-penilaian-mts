export const KKM_TUNTAS = 75;
export const NILAI_MAKS = 90;

export function hitungNilai(jumlahKesalahan: number, poinPengurangan: number): number {
  return Math.max(0, NILAI_MAKS - jumlahKesalahan * poinPengurangan);
}

export function rataTotal(nilaiHafalan?: number, nilaiPraktik?: number): number | null {
  const values = [nilaiHafalan, nilaiPraktik].filter((value): value is number => value !== undefined);
  if (!values.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

export function ketuntasan(rata: number | null): "Belum Dinilai" | "Tuntas" | "Belum Tuntas" {
  if (rata === null) return "Belum Dinilai";
  return rata >= KKM_TUNTAS ? "Tuntas" : "Belum Tuntas";
}
