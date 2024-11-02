import pandas as pd #untuk membaca file csv (pip install pandas)
from tabulate import tabulate #untuk membuat tabel (pip install tabulate)
from datetime import datetime


def create_pesanan(user_id, layanan, lokasi_jemput, lokasi_tujuan):
    try:
        df = pd.read_csv('data/table_pesanan.csv', sep=';')
        if not df['id'].empty:
            pesanan_id = df['id'].max() + 1
        else:
            pesanan_id = 1
        new_data = pd.DataFrame({
            'id': [pesanan_id],
            'user_id': [user_id],
            'layanan': [layanan],
            'lokasi_jemput': [lokasi_jemput],
            'lokasi_tujuan': [lokasi_tujuan],
            'tanggal_pesanan' : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'dipesan'
        })    
        with open('data/table_pesanan.csv', mode='a', newline='', encoding='utf-8') as f:
            new_data.to_csv(f, header=False, index=False, sep=';')
        return new_data
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return None

def read_pesanan():
    try:
        df = pd.read_csv('data/table_pesanan.csv', sep=';')
        return df
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return None

def update_pesanan(id, user_id, layanan, lokasi_jemput, lokasi_tujuan, tanggal, waktu, status):
    try:
        df = pd.read_csv('data/table_pesanan.csv', sep=';')
        pesanan = df.loc[df['id'] == id]
        if pesanan.empty:
            return None
        pesanan['user_id'] = user_id
        pesanan['layanan'] = layanan
        pesanan['lokasi_jemput'] = lokasi_jemput
        pesanan['lokasi_tujuan'] = lokasi_tujuan
        pesanan['tanggal'] = tanggal
        pesanan['status'] = status
        with open('data/table_pesanan.csv', mode='w', newline='', encoding='utf-8') as f:
            df.to_csv(f, index=False, sep=';')
        return pesanan
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return None

def delete_pesanan(id):
    try:   
        df = pd.read_csv('data/table_pesanan.csv', sep=';')
        pesanan = df.loc[df['id'] == id]
        if pesanan.empty:
            return None
        df = df.drop(pesanan.index)
        with open('data/table_pesanan.csv', mode='w', newline='', encoding='utf-8') as f:
            df.to_csv(f, index=False, sep=';')
        return pesanan
    
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return None

def konfirmasi_pesanan():
    try:
        # Muat data user dan pesanan
        df_user = pd.read_csv('data/table_user.csv', sep=';')
        df_pesanan = pd.read_csv('data/table_pesanan.csv', sep=';')

        # Gabungkan tabel user dan pesanan berdasarkan user_id
        df_merged = df_pesanan.merge(df_user[['id', 'username']], left_on='user_id', right_on='id', suffixes=('', '_user'))
        
        # Hapus kolom id dari tabel user agar tidak redundan
        df_merged = df_merged.drop(columns=['user_id', 'id_user'])

        # Ubah urutan kolom agar username muncul setelah id pesanan
        df_merged = df_merged[['id', 'username', 'lokasi_jemput', 'lokasi_tujuan', 'status']]

        # Filter pesanan yang berstatus 'diproses'
        pesanan_diproses = df_merged[df_merged['status'] == 'diproses']
        if pesanan_diproses.empty:
            print("Tidak ada pesanan yang butuh dikonfirmasi")
            input("Tekan Enter untuk melanjutkan...")
            return None

        # Tampilkan daftar pesanan yang berstatus 'diproses'
        print("Daftar Pesanan Yang Butuh Konfirmasi':")
        print(tabulate(pesanan_diproses, headers='keys', tablefmt='fancy_grid', showindex=False))
        while True:
            try:
                pilih = int(input("Pilih ID pesanan yang ingin dikonfirmasi: "))

                if pilih not in pesanan_diproses['id'].values:
                    print("ID pesanan yang dipilih tidak valid.")
                    input("Tekan Enter untuk melanjutkan...")
                else:
                    break

            except ValueError:
                print("Input harus berupa angka.")
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
            pilih = input('Masukkan Pilihan: ')

            if pilih == '1':
                df_pesanan.loc[df_pesanan['id'] == id, 'status'] = 'dikonfirmasi'
                break
            elif pilih == '2':
                df_pesanan.loc[df_pesanan['id'] == id, 'status'] = 'ditolak'
                break
            else:
                print('Pilihan tidak valid. Silakan coba lagi.')
        

        df_pesanan.to_csv('data/table_pesanan.csv', index=False, sep=';')
        print("Status pesanan berhasil diperbarui.")
        input("Tekan Enter untuk melanjutkan...")
        pesanan =  df_pesanan.loc[df_pesanan['id'] == id]
        return pesanan

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return None
