# ReviewPilem API

ReviewPilem adalah API yang dibangun menggunakan **FastAPI** dan **PostgreSQL** untuk memungkinkan pengguna melihat, menulis, dan memberikan reaksi terhadap ulasan film.

## Kenapa FastAPI?
- ✅ Kinerja cepat (asynchronous by default)
- ✅ Auto-generated documentation (Swagger & ReDoc)
- ✅ Developer-friendly dan mudah diintegrasikan

---

## Kenapa PostgreSQL?
- ✅ Permasalahan cocok menggunakan SQL karena saling keterhubungan antar entitas
- ✅ Membutuhkan ACID yang tinggi

---

## Fitur yang Sudah Tersedia

- ✅ **Manajemen Genre**
  - Tambah genre
  - Update genre

- ✅ **Manajemen Film**
  - Tambah film

- ✅ **Autentikasi**
  - Register
  - Login

- ✅ **Profil Pengguna**
  - Lihat dan update profil

- ✅ **Review**
  - Tambah review
  - Update review
  - Hapus review
  - Lihat review berdasarkan film

- ✅ **Reaksi Review**
  - Like review
  - Dislike review
  - Unreact

- ✅ **Daftar Film**
  - Lihat semua film

---

## Fitur yang Belum Selesai

- ❌ Lihat detail film
- ❌ Lihat list film dengan pagination/sorting
- ❌ Pencarian film berdasarkan judul

---

## Dokumentasi API
FastAPI menyediakan dokumentasi secara otomatis di endpoint berikut:

- link: https://drive.google.com/file/d/13yOiS_Y__SyOPWg1pCgnBmgQYRZQ6XBX/view?usp=sharing
- Atau dengan akses /docs
