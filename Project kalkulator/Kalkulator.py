def tambah(a, b):
    return a + b

def kurang(a, b):
    return a - b

def kali(a, b):
    return a * b

def bagi(a, b):
    if b == 0:
        return "Error! Tidak bisa bagi dengan nol."
    return a / b

def pangkat(a, b):
    return a ** b

def modulo(a, b):
    if b == 0:
        return "Error! Tidak bisa modulo dengan nol."
    return a % b

def tampilkan_menu():
    print("\n" + "="*40)
    print("        KALKULATOR PYTHON")
    print("="*40)
    print("  1. Penjumlahan      (+)")
    print("  2. Pengurangan      (-)")
    print("  3. Perkalian        (*)")
    print("  4. Pembagian        (/)")
    print("  5. Pangkat          (**)")
    print("  6. Modulo/Sisa Bagi (%)")
    print("  7. Keluar")
    print("="*40)

def main():
    print("\nSelamat datang di Kalkulator Python!")

    while True:
        tampilkan_menu()

        pilihan = input("\nPilih operasi (1-7): ")

        if pilihan == '7':
            print("\nTerima kasih! Sampai jumpa.")
            break

        if pilihan not in ['1', '2', '3', '4', '5', '6']:
            print("Pilihan tidak valid! Silakan pilih 1-7.")
            continue

        try:
            a = float(input("Masukkan angka pertama  : "))
            b = float(input("Masukkan angka kedua    : "))
        except ValueError:
            print("Input tidak valid! Masukkan angka yang benar.")
            continue

        if pilihan == '1':
            hasil = tambah(a, b)
            simbol = '+'
        elif pilihan == '2':
            hasil = kurang(a, b)
            simbol = '-'
        elif pilihan == '3':
            hasil = kali(a, b)
            simbol = '*'
        elif pilihan == '4':
            hasil = bagi(a, b)
            simbol = '/'
        elif pilihan == '5':
            hasil = pangkat(a, b)
            simbol = '**'
        elif pilihan == '6':
            hasil = modulo(a, b)
            simbol = '%'

        # Tampilkan hasil
        if isinstance(hasil, str):
            print(f"\nHasil: {hasil}")
        else:
            # Tampilkan bilangan bulat jika tidak ada desimal
            if hasil == int(hasil):
                hasil = int(hasil)
            print(f"\nHasil: {a} {simbol} {b} = {hasil}")

        input("\nTekan Enter untuk melanjutkan...")

if __name__ == "__main__":
    main()