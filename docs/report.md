# UTS COMP6991031 — LAPORAN UJIAN TENGAH SEMESTER

> **Catatan sebelum export ke PDF:** isi [ISI] di bawah, sisipkan screenshot di tempat bertanda [SS], hapus blok catatan ini.

---

## Identitas

- **NIM:** [ISI NIM]
- **Nama:** [ISI NAMA]
- **Kelas:** [ISI KELAS]

## Judul Projek

**Aquarium Parameter Log (aqualog)** — Aplikasi Web Pencatat Parameter Air Akuarium Multi-Tier dengan Docker Compose

## Tautan

- **GitHub:** https://github.com/saintbobi/aqualog
- **Artikel:** [ISI URL artikel dev.to/Medium]
- **YouTube:** [ISI URL video demo]

---

# SOAL 1 — ANALISIS PROJEK & PEMILIHAN MODEL LAYANAN CLOUD

## 1a. Profil dan Alasan Pemilihan Projek

**Nama & kategori.** Aquarium Parameter Log (aqualog) — aplikasi **web** multi-tier (frontend + backend + database). Repository: `saintbobi/aqualog`, image Docker Hub: `saintbobi705/aqualog:1.0.0`.

**Masalah yang diselesaikan.** Penghobi akuarium wajib memantau kimia air (pH, suhu, NH3, NO2, NO3) secara rutin. Ammonia bisa naik dalam semalam dan pergeseran pH terjadi perlahan berminggu-minggu — saat ikan menunjukkan stres, sering sudah terlambat. Tank udang (shrimp) lebih sensitif lagi: selisih 0,05 ppm ammonia bisa jadi batas antara koloni sehat dan kosong. Praktik umum saat ini: mencatat hasil tes di notes app yang tersebar — tanpa tren, tanpa riwayat terstruktur, tanpa indikator aman/tidak aman.

**Target pengguna.** Penghobi akuarium air tawar, aquascaper, dan pemelihara udang (Neocaridina) yang tes air rutin tapi tidak punya tempat terstruktur menyimpan datanya.

**Fitur inti (MVP).** Mencatat (log) hasil pengukuran air per tank dan melihat trennya: form input parameter → tersimpan ke database → tampil sebagai tabel + grafik garis (Chart.js), plus verdict otomatis **safe/warning/danger** berbasis aturan ambang per jenis tank (shrimp lebih ketat daripada freshwater).

**Motivasi dan kaitan karier.** Saya menargetkan peran **Backend / Cloud Engineer**. Projek ini melatih inti pekerjaan tersebut: containerization (multi-stage Dockerfile), orkestrasi (Docker Compose: network, volume, healthcheck, depends_on), komunikasi antar-service lewat DNS nama service, dan pengelolaan stateful service (database). Saya sengaja memilih domain yang saya pahami (aquarium) agar fokus penuh ke sisi infrastruktur, bukan ke riset domain.

**Requirement.**

| Aspek | Requirement |
|---|---|
| Teknis | FastAPI + Jinja2 (satu container), PostgreSQL 16 + Redis (container terpisah), Docker Compose, jalan di localhost via `docker compose up -d --build` |
| Biaya | **Rp0 / free tier** — seluruh komponen open source; jalan di komputer pribadi; repo GitHub Public gratis; Docker Hub Public gratis. Bila kelak naik ke cloud: pakai free tier penyedia (lihat 1c) |
| Kepatuhan | Aplikasi **tidak menyimpan data pribadi by design** — hanya nama tank (bebas dummy) dan angka hasil pengukuran air; tanpa akun user, tanpa password. Sehubungan **UU No. 27 Tahun 2022 (PDP)**: karena tidak ada data pribadi yang dikumpulkan, tidak ada kewajiban pengendalian berbasis persetujuan/permintaan hapus yang melekat; keputusan desain ini tetap saya ambil sadar sebagai bentuk *privacy by design* — mencegah lebih murah daripada mengelola. Kredensial database hanya di `.env` yang di-ignore Git; repo memuat `.env.example` dengan nilai dummy |

**Karakteristik cloud esensial (NIST).** ***Measured service*** — layanan cloud mengukur pemakaian resource secara transparan (storage database, request API, memory cache) dan itu yang paling projek ini butuhkan saat naik ke cloud: pemakaian volume data readings tumbuh per pencatatan, dan penagihan/limit free tier berbasis pengukuran pemakaian itulah yang menentukan biaya Rp0 saya.

## 1b. Perbandingan Lima Model Layanan

| Model | Tingkat abstraksi | Saya kelola | Penyedia kelola | Contoh nyata | Cocok untuk projek ini? |
|---|---|---|---|---|---|
| **IaaS** | Rendah — VM, network, storage mentah | OS, runtime, middleware, aplikasi, data, patching | Infrastruktur fisik, virtualisasi, jaringan dasar | AWS EC2, GCP Compute Engine | Tidak — harus setup & rawat sendiri VM untuk app sekecil ini; boros waktu, biaya tetap walau idle |
| **PaaS** | Sedang — platform runtime siap pakai | Aplikasi + data | OS, runtime, scaling, patching, middleware | Heroku, Railway, AWS Elastic Beanstalk | **Ya — pilihan utama**; cukup deploy container/app, DB managed, cocok skala kecil dengan free tier |
| **SaaS** | Tinggi — aplikasi jadi, tinggal pakai | Hanya data & konfigurasi pengguna | Semua (aplikasi, infra, update) | Google Sheets, Notion | Tidak — projek ini membangun aplikasi, bukan mengonsumsinya |
| **BaaS** | Tinggi — backend komponen siap pakai (auth, DB, storage) | Logika aplikasi frontend + data | Auth, database API, storage, realtime | Firebase, **Supabase** | Cukup cocok sebagai komponen — mis. ganti Postgres self-hosted dengan Supabase (Postgres + Auth + RLS); tapi fleksibilitas logic dibatasi SDK penyedia |
| **FaaS** | Sangat tinggi — fungsi per-event | Kode fungsi + data | Semua di luar fungsi, scaling per-invocation | AWS Lambda, Cloudflare Workers | Kurang cocok sebagai satu-satunya model — app saya stateful (DB relasional + cache) dan long-running; FaaS cocok jadi pelengkap (mis. webhook notifikasi bahaya) |

## 1c. Model Deployment dan Rekomendasi

**Perbedaan model deployment:**

- **Public cloud** — infrastruktur dibagikan publik via internet, dimiliki penyedia (AWS, GCP, Azure). Murah untuk mulai, elastic, tanpa CAPEX.
- **Private cloud** — infrastruktur eksklusif satu organisasi (on-prem atau colocation). Kontrol & kepatuhan maksimal, biaya CAPEX tinggi.
- **Hybrid** — kombinasi private + public, beban/data sensitif di private, beban elastis di public. Kompleksitas integrasi menengah.
- **Multi-cloud** — beberapa penyedia public sekaligus, menghindari vendor lock-in dan memilih layanan terbaik tiap penyedia; kompleksitas operasi tertinggi.

**Rekomendasi bila aqualog dipindah dari localhost ke cloud: PaaS di public cloud** (mis. Railway/Render/Fly.io untuk app + Supabase untuk database, atau AWS App Runner + RDS).

**Justifikasi:**

- **Teknis** — app sudah dibungkus container; PaaS container-based tinggal menerima image Docker (`saintbobi705/aqualog:1.0.0`) tanpa ubah kode. Database managed menyediakan backup & HA yang tidak saya punya di localhost.
- **Biaya** — target Rp0: **free tier** PaaS (contoh: Railway trial, Render free web service, Supabase free tier 500 MB). Model harga: **pay-as-you-go** setelah free tier habis — cocok beban kecil bervariasi; **reserved** tidak perlu (beban kecil, komitmen justru mahal); **spot instance** tidak cocok (dibidik beban interruptible batch, bukan web service 24/7 kecil).
- **Kepatuhan** — data tetap tanpa PII; negara penyimpanan data (region) dapat dipilih dekat pengguna (mis. Singapore) — relevan bila kelak ada data pribadi, sejalan prinsip pelindungan UU 27/2022.

**Dua trade-off:**

1. **Vendor lock-in** — fitur PaaS spesifik (mis. autoscaling internal, secrets format, VPC internal) membuat pindah penyedia mahal; mitigasi: tetap standar (container OCI, Postgres standar) dan hindari SDK proprietary untuk logic inti.
2. **Batas free tier & cold start** — instance free tier sering "sleep" saat idle → request pertama lambat puluhan detik; dan batas resource free tier (bandwidth/rows) bisa tiba-tiba terlampaui → mitigasi: cache Redis di depan DB (sudah ada di projek), monitoring pemakaian, upgrade ke pay-as-you-go saat trafik nyata.

**Peran Docker dalam perpindahan:** image container adalah artefak yang identik di laptop dan di cloud. Karena aplikasi, dependensi, dan konfigurasi sudah terkunci dalam image multi-stage (`python:3.12-slim` + venv), memindahkan localhost → PaaS hanyalah `docker push` + daftarkan image, tanpa instalasi runtime di server tujuan. Config yang berbeda antar lingkungan (host DB, kredensial) hanya lewat environment variables dari `.env` — jadi perpindahan tidak menyentuh kode sama sekali.

---

# SOAL 2 — BUKTI APLIKASI BERJALAN

Kode, Dockerfile, docker-compose.yml, README, dan 11 commit bertahap: https://github.com/saintbobi/aqualog

## 2a. Desain Arsitektur

```
browser ──► app (FastAPI + Jinja2, port 8000)
              │  GET/POST
              ├──► db (PostgreSQL 16, named volume, healthcheck)
              └──► redis (cache, healthcheck, 30s TTL)
           [profile tools: adminer di port 8080]
```

- **Network:** user-defined `aquarium-net` (bridge) — app menemukan db & redis lewat **nama service**, bukan IP.
- **Volume:** named volume `aquarium-data` (Postgres) dan `redis-data` — data bertahan lintas `docker compose down`.
- **Alur request:** browser → `localhost:8000` (port mapping) → container `app` → cek cache Redis (`readings:tank:N`) → cache miss: query SQL ke `db` → response JSON/HTML → browser render tabel + chart.

**Mengapa container, bukan VM:** container berbagi kernel host lewat **namespaces** (isolasi network/mount/PID) dan dibatasi resource via **cgroups** — tanpa boot OS tamu. Ukuran image app saya **272 MB** (VM ringan saja GB-an) dan startup hitungan **detik** (`docker compose up -d` ± 5–8 detik sampai healthy), sedangkan VM butuh menit untuk boot. Untuk 4 service kecil di laptop, VM boros memory dan waktu.

## 2b. Dockerfile

`Dockerfile` di repo — ringkasan pemenuhan 6 ketentuan:

1. **Multi-stage:** `builder` (pip + toolchain) → `runtime` (hanya venv jadi). 
2. **Tag versi spesifik:** `python:3.12-slim` (bukan `latest`).
3. **Dependency sebelum source:** `COPY requirements.txt` + `pip install` di layer awal → saat kode berubah, layer pip **CACHED** (terbukti di screenshot rebuild, build < 1 detik).
4. **WORKDIR, ENV, EXPOSE, CMD exec form:** `WORKDIR /app`; `ENV PYTHONDONTWRITEBYTECODE=1`; `EXPOSE 8000`; `CMD ["uvicorn", ...]` — exec form menjadikan uvicorn PID 1 sehingga `SIGTERM` diterima dan container berhenti bersih.
5. **COPY alih-alih ADD:** hanya `COPY` dipakai. Perbedaan: `ADD` punya fitur magic — auto-extract tar lokal dan fetch URL — yang tak deterministik dan jarang dibutuhkan; `COPY` murni menyalin file → perilaku jelas dan layer lebih cacheable. `ADD` hanya tepat bila butuh auto-extract (tidak pernah di projek ini).
6. **.dockerignore** ada: mengecualikan `.git`, `.env`, `docs`, `__pycache__` → context build kecil dan secret tak pernah masuk image.

**Ukuran image hasil build:**

[SS: `docker images aquarium-log-app` → 272 MB]

**Multi-stage menjaga image kecil** karena layer builder (pip, wheel, toolchain gcc) tidak ikut ter-copy ke runtime — runtime hanya menerima `/opt/venv` final. Tanpa multi-stage, toolchain build Python ikut terbawa → image bisa 2–3× lebih besar dan permukaan serangan lebih luas.

## 2c. Docker Compose

`docker-compose.yml` di repo — ringkasan pemenuhan 6 ketentuan:

1. **4 service:** `app`, `db`, `redis`, `adminer`.
2. **User-defined network** `aquarium-net`; app konek ke database via nama service `db` (`POSTGRES_HOST=db`), bukan IP/localhost.
3. **Named volume** `aquarium-data` untuk Postgres (+ `redis-data`).
4. **Healthcheck DB** (`pg_isready`) + `depends_on: condition: service_healthy` — app menunggu db benar-benar siap; juga healthcheck redis.
5. **Konfigurasi dari `.env`** — Compose membaca env vars; yang di-commit hanya `.env.example` dengan nilai dummy.
6. **Profile `tools`** — Adminer hanya jalan dengan `docker compose --profile tools up -d`.

Jalankan satu perintah: `docker compose up -d --build` → buka http://localhost:8000.

## 2d. Bukti Berjalan di Localhost

1. **Semua service berjalan & DB healthy:**

   [SS: `docker compose ps` — app Up, db (healthy), redis (healthy), adminer (tools)]

2. **Uji endpoint (status code):**

   [SS: `curl -i http://localhost:8000/health` → **HTTP/1.1 200 OK**]
   [SS: `curl -i -X POST .../tanks` → **201 Created**]
   [SS: `curl -i -X POST .../readings` → **201 Created** + assessment safe]
   [SS: `curl -i "…/readings?tank_id=3"` → **200 OK** + data dari DB]

3. **Uji persistensi:**

   [SS: GET readings sebelum down — data ada]
   [SS: `docker compose down` — container removed]
   [SS: `docker compose up -d` — service nyala lagi, db healthy]
   [SS: GET readings setelah up — **data masih ada**]

   `docker compose down` menghapus container & network tetapi **tidak** menyentuh named volume, sehingga data Postgres bertahan. `docker compose down -v` juga menghapus named volume → data hilang permanen; hanya dipakai bila ingin reset total.

4. **Tampilan aplikasi di browser:**

   [SS: http://localhost:8000 — daftar tank, form, banner SAFE/WARNING/DANGER, tabel, grafik Chart.js]

5. **Bonus (bukti tambahan):**

   [SS: Redis — `redis-cli KEYS "readings*"` + TTL → cache benar-benar dipakai]
   [SS: Docker Hub — repo `saintbobi705/aqualog` tag `1.0.0` + `latest`]
   [SS: log build dengan layer `CACHED`]
   [SS: Adminer — tabel `readings` di database]

## 2e. Push ke GitHub

https://github.com/saintbobi/aqualog — Public, **11 commit bertahap** dengan pesan bermakna (`git log`), README lengkap (deskripsi, cara jalankan, endpoint, AI Usage Declaration, screenshot), `.env` di `.gitignore`, `.env.example` tersedia. Orang lain bisa menjalankan: `git clone` → `cp .env.example .env` → `docker compose up -d --build`.

## 2f. Video Demo

[ISI URL YouTube] — 3–5 menit, Public, narasi suara sendiri: perkenalan & alasan, penjelasan Dockerfile & docker-compose.yml dengan bahasa sendiri, demo aplikasi termasuk uji persistensi. Tautan GitHub & artikel di deskripsi video.

## 2g. Artikel

[ISI URL artikel] — 500–800 kata, memuat masalah & alasan, arsitektur, potongan penting Dockerfile & docker-compose.yml beserta penjelasan, cara menjalankan, screenshot, pelajaran, tautan repo & video.

---

# AI USAGE DECLARATION

**Tipe penggunaan: Partial (≤50%).**

| Alat | Bagian yang dibantu | Perkiraan porsi |
|---|---|---|
| Claude Code (Anthropic, model GLM via z.ai) | Brainstorming pemilihan ide projek; scaffold kode FastAPI (endpoint, skema DB); boilerplate Dockerfile & docker-compose.yml; debugging; kerangka draft artikel & laporan ini | ±40% dari proses pengerjaan |

**Contoh prompt utama:**

- "buat outline terlebih dahulu apa saja yang harus dikerjakan" (brainstorming struktur pengerjaan UTS)
- "build FastAPI app: tanks + readings, GET /health, POST/readings 201, Postgres with named volume, Redis cache"
- "write multi-stage Dockerfile with pinned tags, exec-form CMD, dependency layer first"

**Yang dikerjakan sendiri tanpa AI:** pemilihan & finalisasi ide projek, keputusan arsitektur (memilih satu container app + managed-style DB service, tanpa user account demi PDP), seluruh pengujian & pengambilan screenshot, pengeditan & finalisasi README/artikel dengan bahasa sendiri, perekaman video dengan suara sendiri, penyusunan akhir jawaban.

---

# PERNYATAAN ORISINALITAS

Saya menyatakan bahwa projek ini adalah hasil pekerjaan saya sendiri. Penggunaan AI dilakukan terbatas sebagai alat bantu sesuai deklarasi di atas (Partial, maksimal 50%), tidak menggantikan pemahaman saya atas materi. Saya memahami seluruh kode, Dockerfile, docker-compose.yml, dan konsep yang dipakai (multi-stage build, healthcheck, named volume, user-defined network, shared responsibility model) serta mampu menjelaskannya kembali. Repo dibuat sendiri selama periode ujian dengan riwayat commit bertahap, tidak berisi secret maupun data pribadi, dan tidak menyalin utuh projek orang lain.

Kota, [tanggal]

[Nama, NIM]
