import pandas as pd #untuk membaca file csv (pip install pandas)
from tabulate import tabulate #untuk membuat tabel (pip install tabulate)

def create_layanan(layanan, harga, jenis):
    df = pd.read_csv('data/table_layanan.csv', sep=';')
    if not df['id'].empty:
        layanan_id = df['id'].max() + 1
    else:
        layanan_id = 1
    if layanan in df['layanan'].values:
        data = {'status': 'failed','message' : 'Layanan sudah terdaftar'}
        return data
    
    if harga <= 0:
        return {'status': 'failed', 'message': 'Harga layanan harus lebih dari 0'}
    
    new_data = pd.DataFrame({
        'id': [layanan_id],
        'layanan': [layanan],
        'harga': [harga],
        'jenis': [jenis]
    })
    with open('data/table_layanan.csv', mode='a', newline='', encoding='utf-8') as f:
        new_data.to_csv(f, header=False, index=False, sep=';')
    data = {'status': 'success','message' : 'Layanan ditambahkan'}
    return data

def read_layanan():
    try:
        df = pd.read_csv('data/table_layanan.csv', sep=';')
        print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        
def update_layanan(id, layanan_baru, harga, jenis):
    df = pd.read_csv('data/table_layanan.csv', sep=';')
    if layanan_baru in df['layanan'].values:
        data = {'status': 'failed','message' : 'Layanan sudah terdaftar'}
        return data
    
    layanan = df.loc[df['id'] == id]
    if layanan.empty:
        data = {'status': 'failed','message' : 'Layanan tidak ditemukan'}
        return data
    
    if harga < 0:
        return {'status': 'failed', 'message': 'Harga layanan harus lebih dari 0'}

    
    old_layanan = layanan['layanan'].values[0]
    old_harga = layanan['harga'].values[0]
    old_jenis = layanan['jenis'].values[0]

    df.loc[df['id'] == id, 'layanan'] = layanan_baru if layanan_baru else old_layanan
    df.loc[df['id'] == id, 'harga'] = harga if harga != 0 else old_harga
    df.loc[df['id'] == id, 'jenis'] = jenis if jenis else old_jenis

    with open('data/table_layanan.csv', mode='w', newline='', encoding='utf-8') as f:
        df.to_csv(f, index=False, sep=';')
    
    data = {'status': 'success' ,'message': 'Layanan berhasil diperbarui'}
    return data

def delete_layanan(id):
    df = pd.read_csv('data/table_layanan.csv', sep=';')
    layanan = df.loc[df['id'] == id]
    if layanan.empty:
        data = {'status': 'failed','message' : 'Layanan tidak ditemukan'}
        return data
    df = df.drop(layanan.index)
    with open('data/table_layanan.csv', mode='w', newline='', encoding='utf-8') as f:
        df.to_csv(f, index=False, sep=';')
    data = {'status': 'success' ,'message': 'Layanan berhasil dihapus'}
    return data