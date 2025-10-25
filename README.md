# TUGAS KELOMPOK PBP E

# KELOMPOK E10

### ANGGOTA KELOMPOK

  - Prasetya Surya Syahputra
  - Rheina Adinda Morani Sinurat 2406435881
  - Muhammad Fadhlurrohman Pasya 2406411830
  - Angga Ziaurrohchman 2406495943
  - Muhammad Tristan Malik Anbiya 2406409196

## Aplikasi

Aplikasi Lapangin dirancang untuk membantu klub atau panitia pertandingan untuk mencari stadion yang sesuai untuk menggelar pertandingan. Platform ini menyediakan informasi lengkap seputar lokasi, kapasitas,dan pengelola stadion di berbagai daerah, serta memungkinkan pengguna menyewa langsung pada aplikasi.

## Daftar Modul

1.  Review Stadion
    Pada halaman ini, pengguna dapat menambahkan ulasan atau review terhadap Stadion yang telah mereka sewa. Pengguna dan admin memiliki akses untuk mengedit dan menghapus review.

2.  Pencarian Stadion
    Menu ini memungkinkan pengguna untuk menjelajahi daftar Stadion yang tersedia berdasarkan lokasi, kapasitas, dan pengelola stadion. Admin memiliki akses untuk menambahkan, mengedit, dan menghapus data venue agar informasi selalu up to date.

3.  Booking Stadion
    Pengguna dapat melakukan pemesanan Stadion untuk tanggal dan waktu tertentu. Saat melakukan booking, Pengguna dan admin juga dapat mengedit atau membatalkan booking sebelum waktu penyewaan dimulai.

4.  User
    Admin dapat melihat daftar pengguna yang terdaftar dalam aplikasi. Selain itu, admin juga dapat menambahkan pengguna baru, mengedit data pengguna, atau menghapus akun pengguna yang tidak aktif.

5.  FAQ
    Pengguna dapat melihat jawaban dari FAQ, admin dapat menambahkan, menghapus, dan mengedit FAQ

## Sumber Initial Dataset kategori utama produk

- Kaggle:
[https://www.kaggle.com/datasets/antimoni/football-stadiums](https://www.kaggle.com/datasets/antimoni/football-stadiums)
- Dummy Data untuk harga sewa

## Role pengguna beserta deskripsi

daftar role:
1. Pemesan : Pengguna yang mencari dan menyewa stadion,
2. Pengguna (User):
Menggunakan Lapangin untuk menelusuri dan menemukan Stadion yang bisa disewa
Menyewa Stadion untuk keperluan latihan atau pertandingan
Memberikan ulasan setelah menyewa Stadion atau menyewakan stadionnya
3. Administrator (Admin):
Mengelola seluruh aplikasi, termasuk memantau aktivitas pengguna.
Menangani permasalahan teknis dan memberikan bantuan.
Memastikan aplikasi berfungsi dengan baik, selalu diperbarui, dan tetap aman digunakan.

-----

## 🚀 Persiapan Awal (Getting Started)

Berikut adalah langkah-langkah untuk menjalankan proyek ini secara lokal.

1.  **Clone Repositori**
    Gantilah `https://github.com/pbp-kelompok-e10/lapangin` dengan URL repositori Git kelompok Anda.

    ```bash
    git clone https://github.com/pbp-kelompok-e10/lapangin
    cd lapapngin
    ```

2.  **Buat dan Aktifkan *Virtual Environment***
    Disarankan untuk menggunakan *virtual environment* agar dependensi proyek terisolasi.

      * **Windows:**
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
      * **macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install Dependensi**
    Pastikan Anda berada di direktori *root* proyek (tempat `requirements.txt` berada).

    ```bash
    pip install -r requirements.txt
    ```

4.  **Jalankan Migrasi Database**
    Perintah ini akan membuat skema database berdasarkan model Django Anda.

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **(Opsional) Buat Superuser**
    Gunakan perintah ini untuk membuat akun admin.

    ```bash
    python manage.py createsuperuser
    ```

6.  **Jalankan Server Pengembangan**
    Proyek Anda sekarang akan berjalan di `http://127.0.0.1:8000/`.

    ```bash
    python manage.py runserver
    ```

-----

## 🧪 Menjalankan Tes dan Melihat *Coverage*

Proyek ini menggunakan `coverage` untuk mengukur seberapa banyak kode Anda yang diuji.

1.  **Menjalankan Tes Saja**
    Untuk menjalankan semua tes yang ada di aplikasi:

    ```bash
    python manage.py test
    ```

2.  **Menjalankan Tes dengan *Coverage***
    Gunakan perintah `coverage` untuk menjalankan tes sekaligus memantaunya:

    ```bash
    coverage run --source='.' manage.py test
    ```

      * `--source='.'` memberitahu `coverage` untuk memantau semua file di direktori saat ini.

3.  **Melihat Laporan *Coverage* di Terminal**
    Setelah tes selesai, Anda bisa melihat laporan ringkas langsung di terminal:

    ```bash
    coverage report
    ```

-----

## Tautan deplomen PWS dan Link design

PWS : [https://angga-ziaurrohchman-lapangin.pbp.cs.ui.ac.id/](https://angga-ziaurrohchman-lapangin.pbp.cs.ui.ac.id/)
Link Design : [https://www.figma.com/design/RaRxA8STyW3ax1YRha9lYu/PBP?node-id=1-2\&t=6U2el2vgKl0KXWTc-1](https://www.figma.com/design/RaRxA8STyW3ax1YRha9lYu/PBP?node-id=1-2&t=6U2el2vgKl0KXWTc-1)