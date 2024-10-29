import aiohttp #untuk mengakses API (pip install aiohttp)
import asyncio #untuk menunggu proses asynchronous (pip install asyncio)
import pandas as pd #untuk membaca file csv (pip install pandas)
import os #untuk membersihkan console (pip install os)

# Warna untuk mengganti warna teks di terminal
BOLD = '\033[1m'
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m' 
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
LIGHT_GRAY = '\033[37m'
DARK_GRAY = '\033[90m'
BRIGHT_RED = '\033[91m'
BRIGHT_GREEN = '\033[92m'
BRIGHT_YELLOW = '\033[93m'
BRIGHT_BLUE = '\033[94m'
BRIGHT_MAGENTA = '\033[95m'
BRIGHT_CYAN = '\033[96m'
WHITE = '\033[97m'
RESET = '\033[0m'


def login(username, password):
    df = pd.read_csv('data/table_user.csv', sep=';')
    for index, row in df.iterrows():
        if row['username'] == username and row['password'] == password:
            return row['role']
    return None

# Fungsi untuk mendapatkan koordinat dari nama lokasi menggunakan Nominatim
async def get_koordinat(session, location):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"

    async with session.get(url) as response:

        # Jika respon berhasil
        if response.status == 200:
            data = await response.json()

            # Jika lokasi ditemukan
            if len(data) > 0:
                print(f'{location} ditemukan.')
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
            # Jika lokasi tidak ditemukan
            else:
                print("Lokasi tidak ditemukan.")
                return None
            
        # Jika respon gagal
        else:
            print("Gagal mengakses API Nominatim.")
            return None

# Fungsi untuk menghitung jarak antara dua titik menggunakan OSRM
async def get_jarak(session, titik_jemput, titik_tujuan):
    url = f"http://router.project-osrm.org/route/v1/driving/{titik_jemput[1]},{titik_jemput[0]};{titik_tujuan[1]},{titik_tujuan[0]}?overview=false"

    async with session.get(url) as response:

        # Jika respon berhasil
        if response.status == 200:
            data = await response.json()
            jarak = data['routes'][0]['distance'] / 1000
            return jarak
        
        # Jika respon gagal
        else:
            print("Gagal mengakses API OSRM.")
            return None

# Fungsi Untuk Membuat Pesanan
async def pesan():
    while True:
        print("Pilih Layanan:")
        df = pd.read_csv('data/table_layanan.csv', sep=';')
        df = df.drop(columns=['id'])

        for idx, layanan in enumerate(df['layanan'], start=1):
            print(f"{idx}. {layanan}")

        while True:
            try:
                pilihan = int(input("Masukkan nomor pilihan: "))
                
                # Memastikan nomor yang dipilih dalam rentang yang valid
                if 1 <= pilihan <= len(df):
                    layanan_terpilih = df['layanan'].iloc[pilihan - 1]
                    print(f"Layanan yang dipilih: {layanan_terpilih}")
                    break
                else:
                    print("Nomor yang dimasukkan di luar jangkauan pilihan. Silakan coba lagi.")
            
            except ValueError:
                print("Input tidak valid. Masukkan nomor pilihan dengan benar.")

        while True:
            lokasi_jemput = input("Masukkan nama lokasi penjemputan: ")
            lokasi_tujuan = input("Masukkan nama lokasi tujuan: ")
            if lokasi_jemput and lokasi_tujuan:
                break
            else:
                print("Lokasi tidak valid.")

        async with aiohttp.ClientSession() as session:
            # Mendapatkan koordinat dari nama lokasi
            koordinat_jemput = await get_koordinat(session, lokasi_jemput)
            await asyncio.sleep(1) #delay 1 detik antara permintaan
            koordinat_tujuan = await get_koordinat(session, lokasi_tujuan)

            # Jika koordinat ditemukan
            if koordinat_jemput and koordinat_tujuan:
                jarak = await get_jarak(session, koordinat_jemput, koordinat_tujuan)
                if jarak:
                    print(f"Jarak antara {lokasi_jemput} dan {lokasi_tujuan} adalah {jarak:.2f} km.")
                else:
                    print("Gagal menghitung jarak.")
            else:
                print("Lokasi tidak ditemukan.")
        
        

        
        


def manu_admin():
    os.system('cls')
    print(GREEN + BOLD + "Selamat datang, admin!" + RESET)

    while True:
        print("masukkan pilihan :")
        print("1. manage user")
        print("2. manage pesanan")
        print("3. manage layanan")
        print("4. logout")
        pilih = input("masukkan pilihan :")

        if pilih == "1":
            pass
        elif pilih == "2":
            pass
        elif pilih == "3":
            pass
        elif pilih == "4":
            break
        else:
            print("pilihan tidak valid")

def menu_user():
    os.system('cls')
    print(GREEN + BOLD + "Selamat datang, user!" + RESET)
    
    while True:
        print("masukkan pilihan :")
        print("1. pesan")
        print("2. history pesanan")
        print("3. logout")
        pilih = input("masukkan pilihan :")

        if pilih == "1":
            asyncio.run(pesan())
        elif pilih == "2":
            pass
        elif pilih == "3":
            break
        else:
            print("pilihan tidak valid")

# Fungsi utama
def main():
    # membersihkan console
    while True:

        # Try Except Untuk Mencegah Keyboard Interrupt
        try:
            os.system('cls')

            print("Selamat datang di Sistem Pemesanan Transportasi dan Pengiriman")
            print("1. login")
            print("2. exit")
            pilih = input("Masukkan pilihan: ")

            if pilih == "1":
                # Input username dan password untuk login
                username = input("Masukkan username: ")
                password = input("Masukkan password: ")

                # Memeriksa apakah username dan password valid
                role = login(username, password)
                if role == "admin":
                    manu_admin()
                elif role == "user":
                    menu_user()
                else:
                    print("Username atau password tidak valid")
                

            elif pilih == "2":
                break

            else:
                print("Pilihan tidak valid")
                input("Tekan Enter untuk melanjutkan...")

        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()