from pydantic import BaseModel, field_validator


class PenilaianInput(BaseModel):
    siswa_id: int
    materi_id: int
    jumlah_kesalahan: int

    @field_validator("jumlah_kesalahan")
    @classmethod
    def non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Jumlah kesalahan tidak boleh negatif")
        return v
