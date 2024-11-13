import aiohttp #untuk mengakses API (pip install aiohttp)
import asyncio #untuk menunggu proses asynchronous (pip install asyncio)
import pandas as pd #untuk membaca file csv (pip install pandas)
import os #untuk membersihkan console (pip install os)

from datetime import datetime #untuk mendapatkan waktu

from crud.user import * #import semua fungsi CRUD user
from crud.pesanan import * #import semua fungsi CRUD pesanan
from crud.layanan import * #import semua fungsi CRUD layanan

from colors import * #import semua variabel colors untuk merubah warna pada terminal
from geolocation import * #import semua fungsi untuk mencari lokasi dan jarak
from invalid_pilihan import * #import fungsi untuk handle invalid pilihan


# fungsi login
def login(username, password):
    # membaca file csv
    df = pd.read_csv('data/table_user.csv', sep=';')

    # perulangan setiap baris pada dataframe untuk memeriksa apakah username dan password cocok
    for index, row in df.iterrows():
        if row['username'] == username and row['password'] == password:
            data = {'id': row['id'], 'role': row['role']}
            return data
    return None

# fungsi register
def register(username, password):
    # membaca file csv
    df = pd.read_csv('data/table_user.csv', sep=';')

    # validasi jika username yang diinput apakah sudah ada di file csv
    if username in df['username'].values:
        data = {'message' : 'Username sudah terdaftar'}
        return data

    # validasi untuk menentukan id user
    if not df['id'].empty:
        # mengambil id terbesar lalu ditambahkan 1 untuk menjadi id data yang baru
        user_id = df['id'].max() + 1
    else:
        # Jika tabel kosong, mulai dengan id 1
        user_id = 1

    # menentukan role user
    role = "user"

    # menyusun dataframe baru
    new_data = pd.DataFrame({
        'id': [user_id],
        'username': [username],
        'password': [password],
        'role': [role]
    })

    # menyimpan dataframe baru
    with open('data/table_user.csv', mode='a', newline='', encoding='utf-8') as f:
        new_data.to_csv(f, header=False, index=False, sep=';')

    # mengembalikan data
    data = {'id': user_id, 'role': role, 'message': 'Pendaftaran berhasil'}
    return data

# Fungsi Untuk Membuat Pesanan
async def pesan(user_id):
    while True:
        os.system('cls')
        print(GREEN+"Pilih Layanan:"+RESET)

        # menampilkan layanan yang tersedia
        df = pd.read_csv('data/table_layanan.csv', sep=';')
        for idx, layanan in enumerate(df['layanan'], start=1):
            print(f"{idx}. {layanan}")
        print("0. Keluar")
        
        # memilih layanan
        while True:
            try:
                pilihan = int(input(YELLOW+"Masukkan nomor pilihan: "+RESET))
                
                # Periksa jika pengguna memilih untuk keluar
                if pilihan == 0:
                    break

                # Memastikan nomor yang dipilih dalam rentang yang valid
                elif 1 <= pilihan <= len(df):
                    layanan_terpilih = df.iloc[pilihan - 1]
                    print(f"Layanan yang dipilih: {layanan_terpilih['layanan']}\n")
                    break
                else:
                    handle_invalid_pilihan()
            except ValueError:
                handle_invalid_pilihan()

        # Periksa jika pengguna memilih untuk keluar
        if pilihan == 0:
            break
        
        async with aiohttp.ClientSession() as session:
            berat = None

            # input berat jika jenis layanan pengiriman
            if layanan_terpilih['jenis'] == 'pengiriman':
                while True:
                    try:
                        berat = int(input(YELLOW + "Masukkan berat barang (kg): " + RESET))
                        if berat > 0:
                            print(f"{MAGENTA}Berat barang: {berat} kg{RESET}\n")
                            break
                        else:
                            print(RED + BOLD + "Berat bnarang tidak boleh negatif" + RESET)
                    except ValueError:
                        print(RED + BOLD + "Berat barang harus berupa angka." + RESET)
            
            # menentukan lokasi penjemputan
            while True:
                lokasi_jemput = input(YELLOW + "Masukkan nama lokasi penjemputan: " + RESET).strip()
                if not lokasi_jemput:
                    print(RED + BOLD + "Lokasi tidak valid." + RESET)
                    continue
                
                koordinat_jemput = await get_koordinat(session, lokasi_jemput)
                if koordinat_jemput:
                    break
                else:
                    print(RED + BOLD + "Lokasi penjemputan tidak ditemukan. Silakan coba lagi." + RESET)

            # menentukan lokasi tujuan
            while True:
                lokasi_tujuan = input(YELLOW + "Masukkan nama lokasi tujuan: " + RESET).strip()
                if not lokasi_tujuan:
                    print(RED + BOLD + "Lokasi tidak valid." + RESET)
                    continue

                koordinat_tujuan = await get_koordinat(session, lokasi_tujuan)
                if koordinat_tujuan:
                    break
                else:
                    print(RED + BOLD + "Lokasi tujuan tidak ditemukan. Silakan coba lagi." + RESET)

            # menentukan jarak dan menghitung total harga jika koordinat ditemukan
            if koordinat_jemput and koordinat_tujuan:
                jarak = await get_jarak(session, koordinat_jemput, koordinat_tujuan)


                # perhitungan total harga jika berat barang ada
                if jarak:
                    jarak = round(jarak)
                    print(f"{MAGENTA}Jarak antara {lokasi_jemput} dan {lokasi_tujuan} adalah {jarak} km.{RESET}")
                    
                # input jarak manual jika jarak tidak ditemukan oleh sistem
                else:
                    print(RED + BOLD + "Gagal menghitung jarak.\n" + RESET)
                    pilih = input(YELLOW + "Apakah ingin memasukkan jarak manual ? (y/n): " + RESET)
                    # jika memilih input jarak manual
                    if pilih.lower() == 'y':
                        while True:
                            try:
                                jarak = float(input(YELLOW + "Masukkan jarak (dalam satuan KM): " + RESET))
                                jarak = round(jarak)
                                
                                if jarak > 1000:
                                    print(RED + BOLD + "Jarak terlalu besar" + RESET)
                                    continue

                                if jarak <= 0:
                                    print(RED + BOLD + "Jarak tidak boleh negatif" + RESET)
                                    continue
                                break
                            except OverflowError:
                                print(RED + BOLD + "Jarak terlalu besar" + RESET)
                            except ValueError:
                                print(RED + BOLD + "Jarak harus berupa angka" + RESET)

                    # jika tidak memilih input jarak manual, mengulang pesanan
                    elif pilih.lower() == 'n':
                        continue
                    else:
                        handle_invalid_pilihan()

                # menghitung total harga jika berat ada   
                if berat:
                    total_harga = layanan_terpilih['harga'] * jarak * berat

                # menghitung total harga jika berat tidak ada
                else:
                    total_harga = layanan_terpilih['harga'] * jarak 
                
                # menampilkan berat barang jika berat ada
                if berat:
                    print(f"{MAGENTA}Berat Barang: {berat} kg.{RESET}")

                print(f"{MAGENTA}Total Harga: {total_harga} Rupiah.{RESET}\n")

            else:
                print("Lokasi tidak ditemukan.")
            
            # membuat pesanan jika jarak dan total_harga diketahui
            if jarak and total_harga:
                while True:
                    confirm = input(YELLOW + "Apakah data yang diinputkan sudah benar? (y/n): " + RESET)
                    if confirm != 'y' and confirm != 'n':
                        handle_invalid_pilihan()
                        continue
                    else:
                        break

                # Menyimpan data pesanan
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
                        'beratBarang': berat,
                        'total_harga': total_harga,
                        'status': 'diproses',
                        'tanggal_pesanan': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }])

                    # Menyimpan DataFrame ke dalam file CSV
                    with open('data/table_pesanan.csv', mode='a', newline='', encoding='utf-8') as f:
                        pesanan_baru.to_csv(f, header=False, index=False, sep=';')

                    print(GREEN+BOLD+"Pesanan telah disimpan.Silahkan menunggu pemrosesan pesanan."+RESET)
                    input("Tekan Enter untuk melanjutkan...")

                elif confirm.lower() == 'n':
                    continue  
                break
    

# menampilkan menu admin
def menu_admin(user_id):
    while True:
        try:
            os.system('cls')
            print(GREEN + BOLD + "Menu Admin" + RESET)
            print("masukkan pilihan :")
            print("1. konfirmasi pesanan")
            print("2. manage user")
            print("3. manage layanan")
            print("4. manage pesanan")
            print("5. logout")
            pilih = input(YELLOW + "masukkan pilihan :" + RESET)
            
            # Konfirmasi Pesanan
            if pilih == "1":
                konfirmasi_pesanan()
            # Manage User
            elif pilih == "2":
                menu_manage_user(user_id)
            # Manage Layanan
            elif pilih == "3":
                menu_manage_layanan()
            # Manage Pesanan
            elif pilih == "4":
                menu_manage_pesanan(user_id)
            #logout / kembali ke menu awal
            elif pilih == "5":
                break
            else:
                handle_invalid_pilihan()
                
        except (KeyboardInterrupt, EOFError):
            pass

# menampilkan menu user
def menu_user(user_id):
    while True:
        try:
            os.system('cls')
            print(GREEN + BOLD + "Menu User" + RESET)
            print("masukkan pilihan :")
            print("1. pesan")
            print("2. history pesanan")
            print("3. logout")
            pilih = input(YELLOW + "masukkan pilihan :"+ RESET)

            # Pesan
            if pilih == "1":
                asyncio.run(pesan(user_id))
            # History pemesanan
            elif pilih == "2":
                history(user_id)
                input("Tekan Enter untuk melanjutkan...")
            # Logout / kembali ke menu awal
            elif pilih == "3":
                break
            else:
                handle_invalid_pilihan()
        except (KeyboardInterrupt, EOFError):
            pass


# menampilkan menu manage user
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
        pilih = input(YELLOW+ "masukkan pilihan :" + RESET)

        # tambah user
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

        # lihat user
        elif pilih == "2":
            read_user()
            input("Tekan Enter untuk melanjutkan...")

        # ubah user
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
        
        # hapus user
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
        
        # kembali ke menu admin
        elif pilih == "5":
            break
        else:
            handle_invalid_pilihan()

# menampilkan menu manage layanan
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
        pilih = input(YELLOW+ "masukkan pilihan :" + RESET)

        # tambah layanan
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

            while True:
                jenis = input("Masukkan jenis (pengiriman/transportasi): ").strip().lower()
                if jenis in ["pengiriman", "transportasi"]:
                    break
                print(RED + "jenis tidak valid. Masukkan 'pengiriman' atau 'transportasi'." + RESET)

            layanan_baru = create_layanan(layanan,harga,jenis)
            if layanan_baru['status'] == "success":
                print(GREEN + layanan_baru['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
            else:
                print(RED + layanan_baru['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
        
        # lihat layanan
        elif pilih == "2":
            read_layanan()
            input("Tekan Enter untuk melanjutkan...")
        
        # ubah layanan
        elif pilih == "3":
            read_layanan()
    
            # Meminta ID layanan yang ingin diubah
            while True:
                try:
                    id = int(input("Masukkan ID layanan: ").strip())
                    break
                except ValueError:
                    print(RED + "ID layanan harus berupa angka" + RESET)
                    
            while True:
                layanan = input("Masukkan layanan (kosongkan untuk mempertahankan nilai lama): ").strip()
                if layanan.isnumeric():
                    print(RED + "layanan tidak boleh berupa angka" + RESET)
                    continue
                else:
                    break

            while True:
                try:
                    harga = int(input("Masukkan harga (masukkan 0 untuk menggunakan harga lama): ").strip())
                    break
                except ValueError:
                    print(RED + "harga harus berupa angka" + RESET)
            
            while True:
                jenis = input("Masukkan jenis (pengiriman/transportasi) (kosongkan untuk mempertahankan nilai lama): ").strip().lower()
                if jenis in ["pengiriman", "transportasi",""]:
                    break
                print(RED + "jenis tidak valid. Masukkan 'pengiriman' atau 'transportasi', atau kosongkan untuk mempertahankan nilai lama." + RESET)

            layanan = update_layanan(id, layanan, harga, jenis)

            if layanan['status'] == "success":
                print(GREEN + layanan['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
            else:
                print(RED + layanan['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
        
        # hapus layanan
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
        
        # kembali ke menu admin
        elif pilih == "5":
            break

# menampilkan menu Manage Pesanan
def menu_manage_pesanan(user_id):
    while True:
        os.system('cls')
        print(GREEN + BOLD + "Manage pesanan" +RESET)
        print("pilihan :")
        print("1. tambah pesanan")
        print("2. lihat pesanan")
        print("3. ubah pesanan")
        print("4. hapus pesanan")
        print("5. kembali")
        pilih = input(YELLOW+ "masukkan pilihan :" + RESET)

        # tambah pesanan
        if pilih == "1":
            asyncio.run(pesan(user_id))

        # lihat pesanan
        elif pilih == "2":
            read_pesanan()
            input("Tekan Enter untuk melanjutkan...")

        # ubah pesanan
        elif pilih == "3":
            read_pesanan()

            while True:
                try:
                    id = int(input("Masukkan ID pesanan: ").strip())
                    break
                except ValueError:
                    print(RED + "ID pesanan harus berupa angka" + RESET)

            pesanan = asyncio.run(update_pesanan(id))

            if pesanan['status'] == "success":
                print(GREEN + pesanan['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
            else:
                print(RED + pesanan['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")

        # hapus pesanan
        elif pilih == "4":
            read_pesanan()

            while True:
                try:
                    id = int(input("Masukkan ID pesanan: ").strip())
                    break
                except ValueError:
                    print(RED + "ID pesanan harus berupa angka" + RESET)

            pesanan = delete_pesanan(id)

            if pesanan['status'] == "success":
                print(GREEN + pesanan['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")
            else:
                print(RED + pesanan['message'] + RESET)
                input("Tekan Enter untuk melanjutkan...")

        # kembali ke menu admin
        elif pilih == "5":
            break

        else:
            handle_invalid_pilihan()

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

            # login
            if pilih == "1":
                
                # Input username dan password untuk login
                while True:
                    username = input(YELLOW + "Masukkan username: "+RESET).strip()
                    if not username:
                        print(RED+BOLD+"Username tidak boleh kosong."+RESET)
                        continue
                    break
                
                while True:
                    password = input(YELLOW + "Masukkan password: "+RESET).strip()
                    if not password :
                        print(RED+BOLD+"Password tidak boleh kosong."+RESET)
                        continue
                    break

                # Memeriksa apakah username dan password valid
                user = login(username, password)
                if user:
                    if user['role'] == "admin":
                        menu_admin(user['id'])
                        os.system('cls')
                    elif user['role'] == "user":
                        menu_user(user['id'])
                        os.system('cls')
                else:
                    print(RED+BOLD+"Username atau password salah."+RESET)
                    input("Tekan Enter untuk melanjutkan...")

            # Register
            elif pilih == "2":
                # Input username dan password untuk login
                while True:
                    username = input(YELLOW + "Masukkan username: "+RESET).strip()
                    if not username:
                        print(RED+BOLD+"Username tidak boleh kosong."+RESET)
                        continue
                    break
                
                while True:
                    password = input(YELLOW + "Masukkan password: "+RESET).strip()
                    if not password :
                        print(RED+BOLD+"Password tidak boleh kosong."+RESET)
                        continue
                    break

                user = register(username, password)

                if user and 'role' in user:
                    print(GREEN+BOLD+user['message']+RESET)
                    input("Tekan Enter untuk melanjutkan...")
                    menu_user(user['id'])

                else:
                    print(RED+BOLD+user['message']+RESET)
                    input("Tekan Enter untuk melanjutkan...")

            # Keluar Program
            elif pilih == "3":
                break
            
            else:
                handle_invalid_pilihan()

        except (KeyboardInterrupt, EOFError) :
            # print(RED + "Terjadi kesalahan: " + str(e) + RESET)
            # input()
            pass

if __name__ == "__main__":
    main()