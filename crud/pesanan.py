import pandas as pd #untuk membaca file csv (pip install pandas)
import aiohttp #untuk mengakses API (pip install aiohttp)

from tabulate import tabulate #untuk membuat tabel (pip install tabulate)
from datetime import datetime
from colors import *
from geolocation import *
from invalid_pilihan import *

def read_pesanan():
    try:
        df_pesanan = pd.read_csv('data/table_pesanan.csv', sep=';')
        df_user = pd.read_csv('data/table_user.csv', sep=';')

        df_merged = df_pesanan.merge(df_user[['id','username']], left_on='user_id', right_on='id', suffixes=('', '_user'))

        df = df_merged[['id', 'username','layanan','lokasi_jemput', 'lokasi_tujuan','jarak','beratBarang','total_harga', 'status']]
        df = df.fillna('-')
        
        print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return None

async def update_pesanan(id):
    try:
        df = pd.read_csv('data/table_pesanan.csv', sep=';')
        pesanan = df.loc[df['id'] == id]
        if pesanan.empty:
            data = {'status': 'failed','message' : 'Pesanan tidak ditemukan'}
            return data
        berat = None

        # Ubah layanan ? kalau diubah berarti ngaruh ke total harga dan ada tidaknya berat barang
        while True:
            df_layanan = pd.read_csv('data/table_layanan.csv', sep=';')
            layanan_lama = df_layanan.loc[df_layanan['layanan'] == pesanan['layanan'].values[0]]
            
            pilih_layanan = input(YELLOW+"ubah layanan ? (y/n): "+RESET)
            if pilih_layanan.lower() == 'y':

                for index, row in df_layanan.iterrows():
                    print(f"{index+1}. {row['layanan']}")
                try:
                    pilihan = int(input(YELLOW+"Masukkan nomor pilihan: "+RESET))
                except ValueError:
                    handle_invalid_pilihan()

                if 1 <= pilihan <= len(df_layanan):

                    layanan = df_layanan[df_layanan.index == (pilihan - 1)].iloc[0] 
    
                    print(f"Layanan yang dipilih: {layanan['layanan']}\n")
                    
                    if layanan_lama['jenis'].values[0] == 'pengiriman' and layanan['jenis'] == 'transportasi':
                        berat = None
                    elif layanan_lama['jenis'].values[0] == 'transportasi' and layanan['jenis'] == 'pengiriman':
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
                    break
                else:
                    handle_invalid_pilihan()
                break

            elif pilih_layanan.lower() == 'n':
                layanan = layanan_lama
                berat = pesanan['beratBarang'].values[0]
                break
            else:
                handle_invalid_pilihan()

        # Ubah lokasi ? kalau diubah berarti ngaruh ke jarak dan total harga
        while True:
            pilih_lokasi = input(YELLOW+"ubah lokasi ? (y/n): "+RESET)

            # jika ubah lokasi
            if pilih_lokasi.lower() == 'y':
                async with aiohttp.ClientSession() as session:

                    # mencari lokasi penjemputan
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

                    # mencari lokasi tujuan
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

                    # mencari jarak dari titik koordinat
                    if lokasi_jemput and lokasi_tujuan:
                        jarak = await get_jarak(session, koordinat_jemput, koordinat_tujuan)

                        if jarak:
                            jarak = round(jarak)
                            print(f"{MAGENTA}Jarak antara {lokasi_jemput} dan {lokasi_tujuan} adalah {jarak} km.{RESET}")

                    # input manual jika sistem gagal mendapatkan jarak
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
                        elif pilih.lower() == 'n':
                            continue
                        else:
                            handle_invalid_pilihan()
                    
                    # menghitung total harga  
                    
                    break
            
            # jika tidak ubah lokasi
            elif pilih_lokasi.lower() == 'n':
                lokasi_jemput = pesanan['lokasi_jemput'].values[0]
                lokasi_tujuan = pesanan['lokasi_tujuan'].values[0]
                jarak = pesanan['jarak'].values[0]
                break
            else:
                handle_invalid_pilihan()
        
        # menghitung total harga ketika layanan atau jarak diubah
        if pd.notna(berat) and berat > 0:
            total_harga = layanan['harga'] * jarak * berat
        else:
            total_harga = layanan['harga'] * jarak 

        if pd.notna(berat) and berat > 0:
            print(f"{MAGENTA}Berat Barang: {berat} kg.{RESET}")

        print(f"{MAGENTA}Total Harga: {total_harga} Rupiah.{RESET}\n")

        #  ubah status ?
        while True:
            pilih_status = input(YELLOW+"ubah status ? (y/n): "+RESET)
            if pilih_status.lower() == 'y':
                while True:
                    status = input(YELLOW + "Masukkan status (diproses/dikonfirmasi/ditolak): " + RESET)
                    if status in ['diproses', 'dikonfirmasi', 'ditolak']:
                        break
                    else:
                        handle_invalid_pilihan()
                break
            elif pilih_status.lower() == 'n':
                status = pesanan['status'].values[0]
                break
        
        # menyimpan perubahan
        df.loc[df['id'] == id, 'lokasi_jemput'] = lokasi_jemput
        df.loc[df['id'] == id, 'lokasi_tujuan'] = lokasi_tujuan
        df.loc[df['id'] == id, 'jarak'] = jarak
        df.loc[df['id'] == id, 'layanan'] = layanan['layanan']
        df.loc[df['id'] == id, 'beratBarang'] = berat
        df.loc[df['id'] == id, 'total_harga'] = total_harga
        df.loc[df['id'] == id, 'status'] = status

        df.to_csv('data/table_pesanan.csv', sep=';', index=False)

        data = {'status': 'success' ,'message': 'Layanan berhasil diperbarui'}
        return data
    
    except Exception as e:
        data = {'status': 'failed','message' : f'Terjadi kesalahan: {e}'}
        return data

def delete_pesanan(id):
    try:   
        df = pd.read_csv('data/table_pesanan.csv', sep=';')
        pesanan = df.loc[df['id'] == id]
        if pesanan.empty:
            data = {'status': 'failed','message' : 'Pesanan tidak ditemukan'}
            return data
        df = df.drop(pesanan.index)
        with open('data/table_pesanan.csv', mode='w', newline='', encoding='utf-8') as f:
            df.to_csv(f, index=False, sep=';')
        data = {'status': 'success','message' : 'Pesanan berhasil dihapus'}
        return data
    
    except Exception as e:
        data = {'status': 'failed','message' : f'Terjadi kesalahan: {e}'}
        return data

def konfirmasi_pesanan():
    try:
        # Muat data user dan pesanan
        df_user = pd.read_csv('data/table_user.csv', sep=';')
        df_pesanan = pd.read_csv('data/table_pesanan.csv', sep=';')

        # Gabungkan tabel user dan pesanan berdasarkan user_id
        df_merged = df_pesanan.merge(df_user[['id', 'username']], left_on='user_id', right_on='id', suffixes=('', '_user'))

        # Ubah urutan kolom agar username muncul setelah id pesanan
        df_merged = df_merged[['id', 'username','layanan', 'lokasi_jemput', 'lokasi_tujuan','jarak','beratBarang','total_harga', 'status']]
        df_merged = df_merged.fillna('-')
        # Filter pesanan yang berstatus 'diproses'
        pesanan_diproses = df_merged[df_merged['status'] == 'diproses']
        if pesanan_diproses.empty:
            print("Tidak ada pesanan yang butuh dikonfirmasi")
            input("Tekan Enter untuk melanjutkan...")
            return None

        # Tampilkan daftar pesanan yang berstatus 'diproses'
        print("Daftar Pesanan Yang Butuh Konfirmasi: ")
        print(tabulate(pesanan_diproses, headers='keys', tablefmt='fancy_grid', showindex=False))

        while True:
            try:
                pilih = int(input(YELLOW+"Pilih ID pesanan yang ingin dikonfirmasi: "+RESET))

                if pilih not in pesanan_diproses['id'].values:
                    print(RED+"ID pesanan yang dipilih tidak valid."+RESET)
                    input("Tekan Enter untuk melanjutkan...")
                else:
                    break

            except ValueError:
                print(RED+"Input harus berupa angka."+RESET)
                input("Tekan Enter untuk melanjutkan...")

        id = int(pilih)

        
        # Cari pesanan berdasarkan ID
        if id not in df_pesanan['id'].values:
            message = "Pesanan dengan ID tersebut tidak ditemukan."
            return message
        
        while True:
            print('Konfirmasi atau Tolak?')
            print('1. Konfirmasi')
            print('2. Tolak')
            pilih = input(YELLOW+'Masukkan Pilihan: '+RESET)

            if pilih == '1':
                df_pesanan.loc[df_pesanan['id'] == id, 'status'] = 'dikonfirmasi'
                break
            elif pilih == '2':
                df_pesanan.loc[df_pesanan['id'] == id, 'status'] = 'ditolak'
                break
            else:
                print(RED+'Pilihan tidak valid. Silakan coba lagi.'+RESET)
        

        df_pesanan.to_csv('data/table_pesanan.csv', index=False, sep=';')
        print(GREEN+"Status pesanan berhasil diperbarui."+RESET)
        input("Tekan Enter untuk melanjutkan...")
        pesanan =  df_pesanan.loc[df_pesanan['id'] == id]
        return pesanan

    except Exception as e:
        print(f"{RED}Terjadi kesalahan: {e} {RESET}")
        return None

def history(user_id):
    try:
        df = pd.read_csv('data/table_pesanan.csv', sep=';')
        df = df.loc[df['user_id'] == user_id]

        df = df.drop(columns=['id','user_id'])
        df = df.fillna('-')
        print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")