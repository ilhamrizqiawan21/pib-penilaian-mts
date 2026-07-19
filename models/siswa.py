from pydantic import BaseModel, field_validator


class SiswaCreate(BaseModel):
    nis: str
    nama: str
    kelas_id: int
    semester_id: int

    @field_validator("nis", "nama")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Tidak boleh kosong")
        return v
