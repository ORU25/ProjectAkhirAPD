import aiohttp #untuk mengakses API (pip install aiohttp)
import asyncio #untuk menunggu proses asynchronous (pip install asyncio)
import pandas as pd #untuk membaca file csv (pip install pandas)
import os #untuk membersihkan console (pip install os)
from datetime import datetime #untuk mendapatkan waktu

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

# fungsi login
def login(username, password):
    df = pd.read_csv('data/table_user.csv', sep=';')
    for index, row in df.iterrows():
        if row['username'] == username and row['password'] == password:
            data = {'id': row['id'], 'role': row['role']}
            return data
    return None

# fungsi register
def register(username, password):
    df = pd.read_csv('data/table_user.csv', sep=';')
    if df['username'].str.contains(username).any():
        data = {'message' : 'Username sudah terdaftar'}
        return data

    user_id = len(df) + 1
    role = "user"

    new_data = pd.DataFrame({
        'id': [user_id],
        'username': [username],
        'password': [password],
        'role': [role]
    })

    with open('data/table_user.csv', mode='a', newline='', encoding='utf-8') as f:
        new_data.to_csv(f, header=False, index=False, sep=';')



    data = {'id': user_id, 'role': role, 'message': 'Pendaftaran berhasil'}
    return data

# Fungsi untuk mendapatkan koordinat dari nama lokasi menggunakan Nominatim
async def get_koordinat(session, location):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1&countrycodes=ID"

    async with session.get(url) as response:

        # Jika respon berhasil
        if response.status == 200:
            data = await response.json()

            # Jika lokasi ditemukan
            if len(data) > 0:
                print(f'{location} ditemukan.')
                print(f'{data[0]["display_name"]}\n')
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
            print(RED + BOLD +"Gagal mengakses API OSRM."+ RESET)
            return None

# Fungsi Untuk Membuat Pesanan
async def pesan(user_id):
    while True:
        os.system('cls')
        print(GREEN+"Pilih Layanan:"+RESET)
        df = pd.read_csv('data/table_layanan.csv', sep=';')

        for idx, layanan in enumerate(df['layanan'], start=1):
            print(f"{idx}. {layanan}")

        while True:
            try:
                pilihan = int(input(YELLOW+"Masukkan nomor pilihan: "+RESET))
                
                # Memastikan nomor yang dipilih dalam rentang yang valid
                if 1 <= pilihan <= len(df):
                    layanan_terpilih = df.iloc[pilihan - 1]
                    print(f"Layanan yang dipilih: {layanan_terpilih['layanan']}\n")
                    break
                else:
                    print(RED + BOLD +"Nomor yang dimasukkan di luar jangkauan pilihan. Silakan coba lagi." + RESET)
                
            
            except ValueError:
                print(RED + BOLD + "Input tidak valid. Masukkan nomor pilihan dengan benar."+RESET)

        async with aiohttp.ClientSession() as session:
            # while True:
                while True:
                    lokasi_jemput = input(YELLOW + "Masukkan nama lokasi penjemputan: " + RESET)
                    if not lokasi_jemput:
                        print(RED + BOLD + "Lokasi tidak valid." + RESET)
                        continue
                    
                    koordinat_jemput = await get_koordinat(session, lokasi_jemput)
                    if koordinat_jemput:
                        break
                    else:
                        print(RED + BOLD + "Lokasi penjemputan tidak ditemukan. Silakan coba lagi." + RESET)


                while True:
                    lokasi_tujuan = input(YELLOW + "Masukkan nama lokasi tujuan: " + RESET)
                    if not lokasi_tujuan:
                        print(RED + BOLD + "Lokasi tidak valid." + RESET)
                        continue

                    koordinat_tujuan = await get_koordinat(session, lokasi_tujuan)
                    if koordinat_tujuan:
                        break
                    else:
                        print(RED + BOLD + "Lokasi tujuan tidak ditemukan. Silakan coba lagi." + RESET)



                # Jika koordinat ditemukan
                if koordinat_jemput and koordinat_tujuan:
                    jarak = await get_jarak(session, koordinat_jemput, koordinat_tujuan)
                    
                    if jarak:
                        jarak = round(jarak)
                        print(f"{MAGENTA}Jarak antara {lokasi_jemput} dan {lokasi_tujuan} adalah {jarak} km.{RESET}")
                        total_harga = layanan_terpilih['harga'] * jarak

                        print(f"{MAGENTA}Total Harga: {total_harga} Rupiah.{RESET}\n")

                        # Meminta konfirmasi sebelum menyimpan pesanan
                        confirm = input(YELLOW + "Apakah data yang diinputkan sudah benar? (y/n): " + RESET)
                        if confirm.lower() == 'y':
                            # Membuat DataFrame untuk pesanan baru
                            pesanan_baru = pd.DataFrame([{
                                'id': len(pd.read_csv('data/table_pesanan.csv', sep=';')) + 1,
                                'user_id': user_id,
                                'lokasi_jemput': lokasi_jemput,
                                'lokasi_tujuan': lokasi_tujuan,
                                'jarak': jarak,
                                'layanan': layanan_terpilih['layanan'],
                                'total_harga': total_harga,
                                'status': 'Pesanan Diterima',
                                'tanggal_pesanan': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }])

                            with open('data/table_pesanan.csv', mode='a', newline='', encoding='utf-8') as f:
                                pesanan_baru.to_csv(f, header=False, index=False, sep=';')

                            print(GREEN+BOLD+"Pesanan telah disimpan.Silahkan menunggu pemrosesan pesanan."+RESET)
                            input("Tekan Enter untuk melanjutkan...")
                            break

                    else:
                        print(RED + BOLD + "Gagal menghitung jarak." + RESET)
                else:
                    print("Lokasi tidak ditemukan.")


def manu_admin(user_id):
    os.system('cls')
    print(GREEN + BOLD + "Selamat datang, admin!" + RESET)

    while True:
        print("masukkan pilihan :")
        print("1. konfirmasi pesanan")
        print("2. manage user")
        print("3. manage pesanan")
        print("4. manage layanan")
        print("5. logout")
        pilih = input(YELLOW + "masukkan pilihan :" + RESET)

        if pilih == "1":
            pass
        elif pilih == "2":
            pass
        elif pilih == "3":
            pass
        elif pilih == "4":
            pass
        elif pilih == "5":
            break
        else:
            print("pilihan tidak valid")

def menu_user(user_id):
    while True:
        os.system('cls')
        print(GREEN + BOLD + "Selamat datang, user!" + RESET)
        print("masukkan pilihan :")
        print("1. pesan")
        print("2. history pesanan")
        print("3. logout")
        pilih = input(YELLOW + "masukkan pilihan :"+ RESET)

        if pilih == "1":
            asyncio.run(pesan(user_id))
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

            print(CYAN+BOLD+ "Selamat datang di Sistem Pemesanan Transportasi dan Pengiriman" + RESET)
            print("1. login")
            print("2. register")
            print("3. exit")
            pilih = input("Masukkan pilihan: ")

            if pilih == "1":
                
                # Input username dan password untuk login
                username = input(YELLOW + "Masukkan username: "+RESET)
                password = input(YELLOW + "Masukkan password: "+RESET)

                # Memeriksa apakah username dan password valid
                user = login(username, password)
                if user:
                    if user['role'] == "admin":
                        manu_admin(user['id'])
                    elif user['role'] == "user":
                        menu_user(user['id'])
                else:
                    print(RED+BOLD+"Username atau password tidak valid"+RESET)
                    input("Tekan Enter untuk melanjutkan...")


            elif pilih == "2":
                # Input username dan password untuk login
                username = input(YELLOW + "Masukkan username: "+RESET)
                password = input(YELLOW + "Masukkan password: "+RESET)
                user = register(username, password)

                if user and 'role' in user:
                    print(GREEN+BOLD+user['message']+RESET)
                    input("Tekan Enter untuk melanjutkan...")
                    menu_user(user['id'])

                else:
                    print(RED+BOLD+user['message']+RESET)
                    input("Tekan Enter untuk melanjutkan...")
                    
            elif pilih == "3":
                break

            else:
                print(RED+BOLD+"Pilihan tidak valid"+RESET)
                input("Tekan Enter untuk melanjutkan...")

        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()