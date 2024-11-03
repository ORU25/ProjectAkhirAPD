import pandas as pd #untuk membaca file csv (pip install pandas)
from tabulate import tabulate #untuk membuat tabel (pip install tabulate)
from datetime import datetime
from colors import *

def read_pesanan():
    try:
        df_pesanan = pd.read_csv('data/table_pesanan.csv', sep=';')
        df_user = pd.read_csv('data/table_user.csv', sep=';')

        df_merged = df_pesanan.merge(df_user[['id','username']], left_on='user_id', right_on='id', suffixes=('', '_user'))

        df = df_merged[['id', 'username', 'lokasi_jemput', 'lokasi_tujuan', 'total_harga', 'status']]
        
        print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return None

def update_pesanan(id, user_id, layanan, lokasi_jemput, lokasi_tujuan, jarak,  status):
    try:
        df = pd.read_csv('data/table_pesanan.csv', sep=';')
        pesanan = df.loc[df['id'] == id]
        
        

        # if pesanan.empty:
        #     return None
        # pesanan['user_id'] = user_id
        # pesanan['layanan'] = layanan
        # pesanan['lokasi_jemput'] = lokasi_jemput
        # pesanan['lokasi_tujuan'] = lokasi_tujuan
        # pesanan['jarak'] = jarak
        # pesanan['status'] = status
        # with open('data/table_pesanan.csv', mode='w', newline='', encoding='utf-8') as f:
        #     df.to_csv(f, index=False, sep=';')
        # return pesanan
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return None

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
        df_merged = df_merged[['id', 'username', 'lokasi_jemput', 'lokasi_tujuan','jarak','total_harga', 'status']]

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
        print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")