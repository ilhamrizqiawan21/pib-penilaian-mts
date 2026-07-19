from pydantic import BaseModel, field_validator


class TahunAjaranCreate(BaseModel):
    nama: str

    @field_validator("nama")
    @classmethod
    def valid_format(cls, v: str) -> str:
        v = v.strip()
        if "/" not in v:
            raise ValueError("Format tahun ajaran: YYYY/YYYY")
        return v


class SemesterCreate(BaseModel):
    tahun_ajaran_id: int
    nama: str

    @field_validator("nama")
    @classmethod
    def valid_nama(cls, v: str) -> str:
        v = v.strip().capitalize()
        if v not in ("Ganjil", "Genap"):
            raise ValueError("Semester harus Ganjil atau Genap")
        return v


class KelasCreate(BaseModel):
    nama: str
    tingkat: int

    @field_validator("nama")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nama kelas tidak boleh kosong")
        return v

    @field_validator("tingkat")
    @classmethod
    def valid_tingkat(cls, v: int) -> int:
        if v not in (7, 8, 9):
            raise ValueError("Tingkat harus 7, 8, atau 9")
        return v
