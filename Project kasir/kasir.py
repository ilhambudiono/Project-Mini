"""
================================================
  SISTEM KASIR MINIMARKET
  Dibuat dengan Python (tanpa library tambahan)
================================================
"""

import sqlite3
import datetime
import os

DB = "minimarket.db"


# ══════════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════════

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS produk (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                kode     TEXT    NOT NULL UNIQUE,
                nama     TEXT    NOT NULL,
                harga    INTEGER NOT NULL,
                stok     INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS transaksi (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                no_struk     TEXT    NOT NULL,
                tanggal      TEXT    NOT NULL,
                total        INTEGER NOT NULL,
                bayar        INTEGER NOT NULL,
                kembalian    INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS detail_transaksi (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                no_struk      TEXT    NOT NULL,
                kode_produk   TEXT    NOT NULL,
                nama_produk   TEXT    NOT NULL,
                harga         INTEGER NOT NULL,
                qty           INTEGER NOT NULL,
                subtotal      INTEGER NOT NULL
            );
        """)
    isi_produk_contoh()


def isi_produk_contoh():
    """Isi data produk awal kalau tabel masih kosong."""
    with get_db() as conn:
        if conn.execute("SELECT COUNT(*) FROM produk").fetchone()[0] == 0:
            produk = [
                ("A001", "Aqua 600ml",         3000,  50),
                ("A002", "Aqua 1500ml",         5000,  30),
                ("B001", "Indomie Goreng",       3500, 100),
                ("B002", "Indomie Kuah",         3500, 100),
                ("C001", "Chitato Original",     8000,  40),
                ("C002", "Pringles Original",   25000,  20),
                ("D001", "Teh Botol Sosro",      5000,  60),
                ("D002", "Coca Cola 250ml",      6000,  45),
                ("E001", "Roti Tawar Sari Roti", 12000,  25),
                ("E002", "Susu Ultra 200ml",     5500,  35),
            ]
            conn.executemany(
                "INSERT INTO produk (kode, nama, harga, stok) VALUES (?,?,?,?)",
                produk
            )


# ══════════════════════════════════════════════
#  TAMPILAN HELPER
# ══════════════════════════════════════════════

def bersihkan_layar():
    os.system("cls" if os.name == "nt" else "clear")


def garis(karakter="─", panjang=50):
    print(karakter * panjang)


def header(judul):
    bersihkan_layar()
    garis("═")
    print(f"  🛒  {judul}")
    garis("═")
    print()


def rupiah(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")


def input_angka(pesan, minimal=0):
    """Minta input angka bulat, ulangi kalau salah."""
    while True:
        try:
            nilai = int(input(pesan))
            if nilai < minimal:
                print(f"  ⚠  Masukkan angka minimal {minimal}.")
            else:
                return nilai
        except ValueError:
            print("  ⚠  Harus berupa angka!")


def tekan_enter():
    input("\n  Tekan Enter untuk lanjut...")


# ══════════════════════════════════════════════
#  FITUR: TRANSAKSI PENJUALAN
# ══════════════════════════════════════════════

def buat_no_struk():
    sekarang = datetime.datetime.now()
    return sekarang.strftime("TRX%Y%m%d%H%M%S")


def tampilkan_keranjang(keranjang):
    if not keranjang:
        print("  (keranjang kosong)\n")
        return
    print(f"  {'No':<4} {'Nama Produk':<22} {'Harga':>10} {'Qty':>5} {'Subtotal':>12}")
    garis("-")
    for i, item in enumerate(keranjang, 1):
        print(f"  {i:<4} {item['nama']:<22} {rupiah(item['harga']):>10} {item['qty']:>5} {rupiah(item['subtotal']):>12}")
    garis("-")
    total = sum(i["subtotal"] for i in keranjang)
    print(f"  {'TOTAL':>43} {rupiah(total):>12}")
    print()


def cari_produk(kode):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM produk WHERE kode=?", (kode.upper(),)
        ).fetchone()


def transaksi_baru():
    header("TRANSAKSI PENJUALAN")
    keranjang = []

    while True:
        tampilkan_keranjang(keranjang)
        print("  [kode]  Scan/ketik kode produk")
        print("  [L]     Lihat daftar produk")
        print("  [H]     Hapus item dari keranjang")
        print("  [B]     Bayar & selesaikan transaksi")
        print("  [X]     Batal & kembali ke menu")
        print()
        pilihan = input("  > ").strip().upper()

        if pilihan == "X":
            return
        elif pilihan == "L":
            lihat_produk(pause=True)
            header("TRANSAKSI PENJUALAN")
        elif pilihan == "H":
            hapus_item_keranjang(keranjang)
            header("TRANSAKSI PENJUALAN")
        elif pilihan == "B":
            if not keranjang:
                print("\n  ⚠  Keranjang masih kosong!")
                tekan_enter()
                header("TRANSAKSI PENJUALAN")
            else:
                proses_pembayaran(keranjang)
                return
        else:
            # anggap input sebagai kode produk
            produk = cari_produk(pilihan)
            if not produk:
                print(f"\n  ⚠  Produk dengan kode '{pilihan}' tidak ditemukan.")
                tekan_enter()
                header("TRANSAKSI PENJUALAN")
                continue

            if produk["stok"] == 0:
                print(f"\n  ⚠  Stok {produk['nama']} habis!")
                tekan_enter()
                header("TRANSAKSI PENJUALAN")
                continue

            print(f"\n  Produk : {produk['nama']}")
            print(f"  Harga  : {rupiah(produk['harga'])}")
            print(f"  Stok   : {produk['stok']}")
            qty = input_angka("  Jumlah : ", minimal=1)

            if qty > produk["stok"]:
                print(f"\n  ⚠  Stok tidak cukup! Stok tersedia: {produk['stok']}")
                tekan_enter()
                header("TRANSAKSI PENJUALAN")
                continue

            # cek kalau produk sudah ada di keranjang → tambah qty
            for item in keranjang:
                if item["kode"] == produk["kode"]:
                    item["qty"] += qty
                    item["subtotal"] = item["harga"] * item["qty"]
                    break
            else:
                keranjang.append({
                    "kode":     produk["kode"],
                    "nama":     produk["nama"],
                    "harga":    produk["harga"],
                    "qty":      qty,
                    "subtotal": produk["harga"] * qty,
                })

            header("TRANSAKSI PENJUALAN")


def hapus_item_keranjang(keranjang):
    if not keranjang:
        print("\n  ⚠  Keranjang kosong.")
        tekan_enter()
        return
    tampilkan_keranjang(keranjang)
    no = input_angka(f"  Nomor item yang dihapus (1-{len(keranjang)}): ", minimal=1)
    if no > len(keranjang):
        print("  ⚠  Nomor tidak valid.")
    else:
        dihapus = keranjang.pop(no - 1)
        print(f"  ✓ '{dihapus['nama']}' dihapus dari keranjang.")
    tekan_enter()


def proses_pembayaran(keranjang):
    header("PEMBAYARAN")
    tampilkan_keranjang(keranjang)
    total = sum(i["subtotal"] for i in keranjang)

    print(f"  Total yang harus dibayar: {rupiah(total)}")
    while True:
        bayar = input_angka("  Uang bayar              : Rp ", minimal=1)
        if bayar < total:
            print(f"  ⚠  Uang kurang {rupiah(total - bayar)}. Coba lagi.")
        else:
            break

    kembalian = bayar - total
    no_struk = buat_no_struk()
    tanggal = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # simpan ke database
    with get_db() as conn:
        conn.execute(
            "INSERT INTO transaksi (no_struk,tanggal,total,bayar,kembalian) VALUES (?,?,?,?,?)",
            (no_struk, tanggal, total, bayar, kembalian)
        )
        for item in keranjang:
            conn.execute(
                """INSERT INTO detail_transaksi
                   (no_struk,kode_produk,nama_produk,harga,qty,subtotal)
                   VALUES (?,?,?,?,?,?)""",
                (no_struk, item["kode"], item["nama"],
                 item["harga"], item["qty"], item["subtotal"])
            )
            # kurangi stok
            conn.execute(
                "UPDATE produk SET stok = stok - ? WHERE kode = ?",
                (item["qty"], item["kode"])
            )

    cetak_struk(no_struk, tanggal, keranjang, total, bayar, kembalian)


def cetak_struk(no_struk, tanggal, keranjang, total, bayar, kembalian):
    print()
    garis("═")
    print("         MINIMARKET SEJAHTERA")
    print("      Jl. Contoh No. 1, Surabaya")
    print("         Telp: 031-1234567")
    garis("─")
    print(f"  No. Struk : {no_struk}")
    print(f"  Tanggal   : {tanggal}")
    garis("─")
    for item in keranjang:
        print(f"  {item['nama']}")
        print(f"    {item['qty']} x {rupiah(item['harga']):<15} {rupiah(item['subtotal']):>10}")
    garis("─")
    print(f"  {'TOTAL':<30} {rupiah(total):>10}")
    print(f"  {'Bayar':<30} {rupiah(bayar):>10}")
    print(f"  {'Kembalian':<30} {rupiah(kembalian):>10}")
    garis("─")
    print("      Terima kasih sudah belanja!")
    print("         Selamat datang kembali")
    garis("═")
    tekan_enter()


# ══════════════════════════════════════════════
#  FITUR: MANAJEMEN PRODUK
# ══════════════════════════════════════════════

def lihat_produk(pause=False):
    header("DAFTAR PRODUK")
    with get_db() as conn:
        produk_list = conn.execute(
            "SELECT * FROM produk ORDER BY kode"
        ).fetchall()

    if not produk_list:
        print("  Belum ada produk.")
    else:
        print(f"  {'Kode':<8} {'Nama Produk':<25} {'Harga':>12} {'Stok':>6}")
        garis("-")
        for p in produk_list:
            stok_info = str(p["stok"])
            if p["stok"] == 0:
                stok_info = "HABIS"
            elif p["stok"] <= 5:
                stok_info = f"{p['stok']} ⚠"
            print(f"  {p['kode']:<8} {p['nama']:<25} {rupiah(p['harga']):>12} {stok_info:>6}")

    if pause:
        tekan_enter()


def tambah_produk():
    header("TAMBAH PRODUK BARU")
    kode = input("  Kode produk  : ").strip().upper()
    if not kode:
        print("  ⚠  Kode tidak boleh kosong.")
        tekan_enter()
        return

    # cek kode sudah ada
    if cari_produk(kode):
        print(f"  ⚠  Kode '{kode}' sudah digunakan.")
        tekan_enter()
        return

    nama = input("  Nama produk  : ").strip()
    if not nama:
        print("  ⚠  Nama tidak boleh kosong.")
        tekan_enter()
        return

    harga = input_angka("  Harga (Rp)   : ", minimal=1)
    stok  = input_angka("  Stok awal    : ", minimal=0)

    with get_db() as conn:
        conn.execute(
            "INSERT INTO produk (kode, nama, harga, stok) VALUES (?,?,?,?)",
            (kode, nama, harga, stok)
        )
    print(f"\n  ✓ Produk '{nama}' berhasil ditambahkan!")
    tekan_enter()


def edit_produk():
    header("EDIT PRODUK")
    lihat_produk()
    print()
    kode = input("  Masukkan kode produk yang akan diedit: ").strip().upper()
    produk = cari_produk(kode)
    if not produk:
        print(f"  ⚠  Produk '{kode}' tidak ditemukan.")
        tekan_enter()
        return

    print(f"\n  Produk saat ini:")
    print(f"    Nama  : {produk['nama']}")
    print(f"    Harga : {rupiah(produk['harga'])}")
    print(f"    Stok  : {produk['stok']}")
    print(f"\n  (Kosongkan untuk tidak mengubah)\n")

    nama_baru  = input(f"  Nama baru  [{produk['nama']}]: ").strip() or produk["nama"]
    harga_input = input(f"  Harga baru [{rupiah(produk['harga'])}]: Rp ").strip()
    stok_input  = input(f"  Stok baru  [{produk['stok']}]: ").strip()

    harga_baru = int(harga_input) if harga_input.isdigit() else produk["harga"]
    stok_baru  = int(stok_input)  if stok_input.isdigit()  else produk["stok"]

    with get_db() as conn:
        conn.execute(
            "UPDATE produk SET nama=?, harga=?, stok=? WHERE kode=?",
            (nama_baru, harga_baru, stok_baru, kode)
        )
    print(f"\n  ✓ Produk '{kode}' berhasil diperbarui!")
    tekan_enter()


def hapus_produk():
    header("HAPUS PRODUK")
    lihat_produk()
    print()
    kode = input("  Masukkan kode produk yang akan dihapus: ").strip().upper()
    produk = cari_produk(kode)
    if not produk:
        print(f"  ⚠  Produk '{kode}' tidak ditemukan.")
        tekan_enter()
        return

    konfirmasi = input(f"\n  Hapus '{produk['nama']}'? (y/n): ").strip().lower()
    if konfirmasi == "y":
        with get_db() as conn:
            conn.execute("DELETE FROM produk WHERE kode=?", (kode,))
        print(f"  ✓ Produk '{produk['nama']}' berhasil dihapus.")
    else:
        print("  Dibatalkan.")
    tekan_enter()


# ══════════════════════════════════════════════
#  FITUR: LAPORAN
# ══════════════════════════════════════════════

def laporan_penjualan():
    header("LAPORAN PENJUALAN")
    print("  [1] Hari ini")
    print("  [2] Semua transaksi")
    print()
    pilihan = input("  Pilih: ").strip()

    with get_db() as conn:
        if pilihan == "1":
            hari_ini = datetime.date.today().strftime("%d-%m-%Y")
            rows = conn.execute(
                "SELECT * FROM transaksi WHERE tanggal LIKE ? ORDER BY tanggal DESC",
                (f"{hari_ini}%",)
            ).fetchall()
            judul = f"Laporan Hari Ini ({hari_ini})"
        else:
            rows = conn.execute(
                "SELECT * FROM transaksi ORDER BY tanggal DESC"
            ).fetchall()
            judul = "Semua Transaksi"

    header(f"LAPORAN — {judul.upper()}")
    if not rows:
        print("  Belum ada transaksi.")
    else:
        print(f"  {'No. Struk':<22} {'Tanggal':<22} {'Total':>12} {'Bayar':>12} {'Kembalian':>12}")
        garis("-")
        for r in rows:
            print(f"  {r['no_struk']:<22} {r['tanggal']:<22} {rupiah(r['total']):>12} {rupiah(r['bayar']):>12} {rupiah(r['kembalian']):>12}")
        garis("-")
        grand_total = sum(r["total"] for r in rows)
        print(f"  {'TOTAL PENDAPATAN':<58} {rupiah(grand_total):>12}")
        print(f"  Jumlah transaksi: {len(rows)}")
    tekan_enter()


def laporan_stok_menipis():
    header("LAPORAN STOK MENIPIS")
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM produk WHERE stok <= 10 ORDER BY stok ASC"
        ).fetchall()

    if not rows:
        print("  Semua stok aman (> 10).")
    else:
        print(f"  {'Kode':<8} {'Nama Produk':<25} {'Stok':>6}  Status")
        garis("-")
        for p in rows:
            status = "HABIS ❌" if p["stok"] == 0 else "MENIPIS ⚠"
            print(f"  {p['kode']:<8} {p['nama']:<25} {p['stok']:>6}  {status}")
    tekan_enter()


# ══════════════════════════════════════════════
#  MENU UTAMA
# ══════════════════════════════════════════════

def menu_produk():
    while True:
        header("MANAJEMEN PRODUK")
        print("  [1] Lihat semua produk")
        print("  [2] Tambah produk baru")
        print("  [3] Edit produk")
        print("  [4] Hapus produk")
        print("  [0] Kembali ke menu utama")
        print()
        pilihan = input("  Pilih: ").strip()

        if pilihan == "1":   lihat_produk(pause=True)
        elif pilihan == "2": tambah_produk()
        elif pilihan == "3": edit_produk()
        elif pilihan == "4": hapus_produk()
        elif pilihan == "0": return
        else: print("  ⚠  Pilihan tidak valid."); tekan_enter()


def menu_laporan():
    while True:
        header("LAPORAN")
        print("  [1] Laporan penjualan")
        print("  [2] Laporan stok menipis")
        print("  [0] Kembali ke menu utama")
        print()
        pilihan = input("  Pilih: ").strip()

        if pilihan == "1":   laporan_penjualan()
        elif pilihan == "2": laporan_stok_menipis()
        elif pilihan == "0": return
        else: print("  ⚠  Pilihan tidak valid."); tekan_enter()


def menu_utama():
    init_db()
    while True:
        header("SISTEM KASIR MINIMARKET")
        print("  [1] Transaksi Penjualan")
        print("  [2] Manajemen Produk")
        print("  [3] Laporan")
        print("  [0] Keluar")
        print()
        pilihan = input("  Pilih menu: ").strip()

        if pilihan == "1":   transaksi_baru()
        elif pilihan == "2": menu_produk()
        elif pilihan == "3": menu_laporan()
        elif pilihan == "0":
            bersihkan_layar()
            print("  Terima kasih! Sampai jumpa. 👋\n")
            break
        else:
            print("  ⚠  Pilihan tidak valid.")
            tekan_enter()


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════

if __name__ == "__main__":
    menu_utama()
