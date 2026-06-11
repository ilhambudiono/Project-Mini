import time
import sys

def main():
    print("=" * 45)
    print("       ⏱️  STOPWATCH DIGITAL ESTETIK  ⏱️       ")
    print("=" * 45)
    print(" Petunjuk: ")
    print(" ▶️  Tekan ENTER untuk MEMULAI")
    print(" 🛑 Tekan Ctrl + C untuk BERHENTI")
    print("-" * 45)
    
    input("👉 Siap? Tekan ENTER sekarang...")
    print("\n⏱️  Stopwatch sedang berjalan...\n")

    # Kombinasi emoji jam bergerak agar terlihat estetik
    animasi_jam = ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"]
    indeks = 0
    waktu_mulai = time.time()

    try:
        while True:
            # Hitung selisih waktu
            waktu_berjalan = time.time() - waktu_mulai
            
            # Ubah detik menjadi format Menit, Detik, dan Milidetik
            menit = int(waktu_berjalan // 60)
            detik = int(waktu_berjalan % 60)
            milidetik = int((waktu_berjalan % 1) * 100) # Mengambil 2 angka di belakang koma
            
            # Ambil emoji jam saat ini
            emoji = animasi_jam[indeks]
            
            # Cetak teks dengan format rapi dan estetik
            # \r untuk menimpa baris yang sama, :02d agar angka selalu 2 digit (misal: 05)
            sys.stdout.write(f"\r  {emoji}  [ {menit:02d}:{detik:02d}:{milidetik:02d} ]")
            sys.stdout.flush()
            
            # Update indeks emoji jam
            indeks = (indeks + 1) % len(animasi_jam)
            
            # Jeda 0.05 detik (lebih cepat dari sebelumnya agar milidetiknya mulus)
            time.sleep(0.05)

    except KeyboardInterrupt:
        waktu_akhir = time.time() - waktu_mulai
        menit = int(waktu_akhir // 60)
        detik = int(waktu_akhir % 60)
        milidetik = int((waktu_akhir % 1) * 100)
        
        # Tampilan waktu berhenti yang rapi
        print("\n\n" + "=" * 45)
        print(" 🛑  STOPWATCH DIHENTIKAN!")
        print(f" 📊  Waktu Akhir: {menit:02d} Menit : {detik:02d} Detik : {milidetik:02d} Milidetik")
        print("=" * 45)

if __name__ == "__main__":
    main()