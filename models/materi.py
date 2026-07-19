from typing import Literal

from pydantic import BaseModel, field_validator


class MateriCreate(BaseModel):
    semester_id: int
    nama: str
    aspek: Literal["hafalan", "praktik"]
    poin_pengurangan: float
    urutan: int = 0

    @field_validator("nama")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nama materi tidak boleh kosong")
        return v

    @field_validator("poin_pengurangan")
    @classmethod
    def positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Poin pengurangan harus > 0")
        return v
