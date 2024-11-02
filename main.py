import aiohttp #untuk mengakses API (pip install aiohttp)
import asyncio #untuk menunggu proses asynchronous (pip install asyncio)
import pandas as pd #untuk membaca file csv (pip install pandas)
import os #untuk membersihkan console (pip install os)

from datetime import datetime #untuk mendapatkan waktu

from crud.user import create_user, read_user, update_user, delete_user
from crud.pesanan import create_pesanan, read_pesanan, update_pesanan, delete_pesanan, konfirmasi_pesanan
from crud.layanan import create_layanan, read_layanan, update_layanan, delete_layanan

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

    if not df['id'].empty:
        user_id = df['id'].max() + 1
    else:

        user_id = 1  # Jika tabel kosong, mulai dengan ID 1
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

    try:
        async with session.get(url) as response:

            if response.status == 200:
                data = await response.json()

                if data:
                    print(f'{location} ditemukan.')
                    print(f'{data[0]["display_name"]}\n')
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    return lat, lon
                else:
                    print("Lokasi tidak ditemukan.")
                    return None            
            else:
                print("Gagal mengakses API Nominatim.")
                return None

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return None

# Fungsi untuk menghitung jarak antara dua titik menggunakan OSRM
async def get_jarak(session, titik_jemput, titik_tujuan):
    url = f"http://router.project-osrm.org/route/v1/driving/{titik_jemput[1]},{titik_jemput[0]};{titik_tujuan[1]},{titik_tujuan[0]}?overview=false"

    try:
        async with session.get(url) as response:

            if response.status == 200:
                data = await response.json()
                jarak = data['routes'][0]['distance'] / 1000
                return jarak
            
            else:
                print(RED + BOLD +"Gagal mengakses API OSRM."+ RESET)
                return None

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

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
                    handle_invalid_pilihan()
                
            
            except ValueError:
                handle_invalid_pilihan()

        async with aiohttp.ClientSession() as session:
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
                        

                    else:
                        print(RED + BOLD + "Gagal menghitung jarak.\n" + RESET)
                        pilih = input(YELLOW + "Apakah ingin memasukkan jarak manual ? (y/n): " + RESET)
                        if pilih.lower() == 'y':
                            while True:
                                try:
                                    jarak = float(input(YELLOW + "Masukkan jarak (dalam satuan KM): " + RESET))
                                    jarak = round(jarak)
                                    break
                                except ValueError:
                                    print(RED + BOLD + "Jarak harus berupa angka." + RESET)

                            total_harga = layanan_terpilih['harga'] * jarak
                            
                            print(f"{MAGENTA}Total Harga: {total_harga} Rupiah.{RESET}\n")

                        elif pilih.lower() == 'n':
                            continue
                        else:
                            handle_invalid_pilihan()
                            
                else:
                        print("Lokasi tidak ditemukan.")

                if jarak and total_harga:
                    # Meminta konfirmasi sebelum menyimpan pesanan
                    confirm = input(YELLOW + "Apakah data yang diinputkan sudah benar? (y/n): " + RESET)
                    if confirm.lower() == 'y':
                        df_pesanan = pd.read_csv('data/table_pesanan.csv', sep=';')
                        if not df_pesanan['id'].empty:
                            id = df_pesanan['id'].max() + 1
                        else:
                            id = 1
                        # Membuat DataFrame untuk pesanan baru
                        pesanan_baru = pd.DataFrame([{
                            'id': id,
                            'user_id': user_id,
                            'lokasi_jemput': lokasi_jemput,
                            'lokasi_tujuan': lokasi_tujuan,
                            'jarak': jarak,
                            'layanan': layanan_terpilih['layanan'],
                            'total_harga': total_harga,
                            'status': 'diproses',
                            'tanggal_pesanan': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }])

                        with open('data/table_pesanan.csv', mode='a', newline='', encoding='utf-8') as f:
                            pesanan_baru.to_csv(f, header=False, index=False, sep=';')

                        print(GREEN+BOLD+"Pesanan telah disimpan.Silahkan menunggu pemrosesan pesanan."+RESET)
                        input("Tekan Enter untuk melanjutkan...")
                    break


def manu_admin(user_id):
    while True:
        os.system('cls')
        print(GREEN + BOLD + "Menu Admin" + RESET)
        print("masukkan pilihan :")
        print("1. konfirmasi pesanan")
        print("2. manage user")
        print("3. manage layanan")
        print("4. manage pesanan")
        print("5. logout")
        pilih = input(YELLOW + "masukkan pilihan :" + RESET)

        if pilih == "1":
            konfirmasi_pesanan()
        elif pilih == "2":
            menu_manage_user(user_id)
        elif pilih == "3":
            menu_manage_layanan()
        elif pilih == "4":
            menu_manage_pesanan(user_id)
        elif pilih == "5":
            break
        else:
            handle_invalid_pilihan()

def menu_user(user_id):
    while True:
        os.system('cls')
        print(GREEN + BOLD + "Menu User" + RESET)
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
            handle_invalid_pilihan()

def menu_manage_user(user_id):
    while True:
        os.system('cls')
        print(GREEN + BOLD + "Manage User" +RESET)
        print("pilihan :")
        print("1. tambah user")
        print("2. lihat user")
        print("3. ubah user")
        print("4. hapus user")
        print("5. kembali")
        pilih = input("masukkan pilihan :")

        if pilih == "1":
            while True:
                username = input("Masukkan username: ").strip()
                if username:
                    break
                print(RED + "Username tidak boleh kosong" + RESET)
            while True:
                password = input("Masukkan password: ").strip()
                if password:
                    break
                print(RED + "Password tidak boleh kosong" + RESET)
            while True:
                role = input("Masukkan role (admin/user): ").strip().lower()
                if role in ["admin", "user"]:
                    break
                print(RED + "Role tidak valid. Masukkan 'admin' atau 'user'." + RESET)

            user = create_user(username, password, role)
            if user['status'] == "success":
                print(GREEN + user['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
            else:
                print(RED + user['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")

        elif pilih == "2":
            read_user()
            input("Tekan Enter untuk melanjutkan...")

        elif pilih == "3":
            read_user()
    
            # Meminta ID user yang ingin diubah
            while True:
                try:
                    id = int(input("Masukkan ID user: ").strip())
                    if id == user_id:
                        print(RED + "ID user tidak boleh sama dengan ID yang login saat ini" + RESET)
                        continue
                    break
                except ValueError:
                    print(RED + "ID user harus berupa angka" + RESET)

            username = input("Masukkan username (kosongkan untuk mempertahankan nilai lama): ").strip()            
            password = input("Masukkan password (kosongkan untuk mempertahankan nilai lama): ").strip()
            
            while True:
                role = input("Masukkan role (admin/user) atau kosongkan untuk mempertahankan nilai lama: ").strip().lower()
                if role in ["admin", "user", ""]:
                    break
                print(RED + "Role tidak valid. Masukkan 'admin' atau 'user', atau kosongkan untuk mempertahankan nilai lama." + RESET)

            user = update_user(id, username, password, role)

            if user['status'] == "success":
                print(GREEN + user['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
            else:
                print(RED + user['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
        
        elif pilih == "4":
            read_user()
    
            # Meminta ID user yang ingin dihapus
            while True:
                try:
                    id = int(input("Masukkan ID user: ").strip())
                    if id == user_id:
                        print(RED + "ID user tidak boleh sama dengan ID yang login saat ini" + RESET)
                        continue
                    
                    break
                except ValueError:
                    print(RED + "ID user harus berupa angka" + RESET)

            user = delete_user(id)

            if user['status'] == "success":
                print(GREEN + user['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
            else:
                print(RED + user['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
        
        elif pilih == "5":
            break
        else:
            handle_invalid_pilihan()

def menu_manage_layanan():
    while True:
        os.system('cls')
        print(GREEN + BOLD + "Manage Layanan" +RESET)
        print("pilihan :")
        print("1. tambah layanan")
        print("2. lihat layanan")
        print("3. ubah layanan")
        print("4. hapus layanan")
        print("5. kembali")
        pilih = input("masukkan pilihan :")

        if pilih == "1":
            while True:
                layanan = input("Masukkan layanan: ").strip()
                if layanan:
                    break
                print(RED + "layanan tidak boleh kosong" + RESET)
            while True:
                try:
                    harga = int(input("Masukkan harga: "))
                    if harga:
                        break
                    print(RED + "harga tidak boleh kosong" + RESET)
                except ValueError:
                    print(RED + "harga harus berupa angka" + RESET)

            layanan_baru = create_layanan(layanan,harga)
            if layanan_baru['status'] == "success":
                print(GREEN + layanan_baru['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
            else:
                print(RED + layanan_baru['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
        
        elif pilih == "2":
            read_layanan()
            input("Tekan Enter untuk melanjutkan...")
        
        elif pilih == "3":
            read_layanan()
    
            # Meminta ID layanan yang ingin diubah
            while True:
                try:
                    id = int(input("Masukkan ID layanan: ").strip())
                    break
                except ValueError:
                    print(RED + "ID layanan harus berupa angka" + RESET)

            layanan = input("Masukkan layanan (kosongkan untuk mempertahankan nilai lama): ").strip()            
            while True:
                try:
                    harga = int(input("Masukkan harga (masukkan 0 untuk menggunakan harga lama): ").strip())
                    break
                except ValueError:
                    print(RED + "harga harus berupa angka" + RESET)

            layanan = update_layanan(id, layanan, harga)

            if layanan['status'] == "success":
                print(GREEN + layanan['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
            else:
                print(RED + layanan['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
        
        elif pilih == "4":
            read_layanan()

            while True:
                try:
                    id = int(input("Masukkan ID layanan: ").strip())
                    break
                except ValueError:
                    print(RED + "ID layanan harus berupa angka" + RESET)

            layanan = delete_layanan(id)

            if layanan['status'] == "success":
                print(GREEN + layanan['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
            else:
                print(RED + layanan['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
        
        elif pilih == "5":
            break

def menu_manage_pesanan(user_id):
    pass

def handle_invalid_pilihan():
    print(RED + BOLD + "Pilihan tidak valid" + RESET)
    input("Tekan Enter untuk melanjutkan...")

# Fungsi utama
def main():
    while True:
        # Try Except Untuk Mencegah Keyboard Interrupt
        try:
            # membersihkan console
            os.system('cls')
            
            print(CYAN + BOLD + "Selamat datang di Sistem Pemesanan Transportasi dan Pengiriman" + RESET)
            print("1. Login")
            print("2. Register")
            print("3. Exit")
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
                        os.system('cls')
                    elif user['role'] == "user":
                        menu_user(user['id'])
                        os.system('cls')
                else:
                    print(RED+BOLD+"Username atau password salah."+RESET)
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
                handle_invalid_pilihan()

        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()