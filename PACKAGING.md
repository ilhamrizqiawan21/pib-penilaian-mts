# Packaging PIB

## Windows Portable EXE

Jalankan dari root project:

```powershell
.\scripts\build_windows.ps1
```

Output utama ada di:

```text
release\Penilaian PIB\Penilaian PIB.exe
```

Folder hasil build menyertakan:

- `assets\` untuk logo
- `data\` untuk `pib.db`
- `exports\` untuk PDF/Excel

Untuk backup, salin file:

```text
dist\Penilaian PIB\data\pib.db
```

## Android PWA Offline

Masuk folder PWA:

```powershell
cd frontend-pwa
npm install
npm run dev
```

Build produksi:

```powershell
npm run build
```

PWA memakai IndexedDB di browser, bisa diinstall dari Chrome Android saat disajikan lewat server HTTPS atau localhost.

Untuk mencoba dari HP Android di jaringan Wi-Fi yang sama:

1. Jalankan `npm run dev` di laptop.
2. Catat alamat Network yang ditampilkan Vite, biasanya seperti `http://192.168.x.x:5173`.
3. Buka alamat itu dari Chrome Android.
4. Pilih menu Chrome `Tambahkan ke layar utama` atau `Install app`.

Catatan: browser Android biasanya mensyaratkan HTTPS untuk install PWA produksi. Untuk uji lokal, Chrome biasanya mengizinkan `localhost` dan beberapa mode jaringan lokal, tetapi perilaku bisa berbeda antar perangkat.
