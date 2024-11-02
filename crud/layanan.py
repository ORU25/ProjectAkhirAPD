import pandas as pd

def create_layanan(layanan, harga):
    df = pd.read_csv('data/table_layanan.csv', sep=';')
    if not df['id'].empty:
        layanan_id = df['id'].max() + 1
    else:
        layanan_id = 1
    new_data = pd.DataFrame({
        'id': [layanan_id],
        'layanan': [layanan],
        'harga': [harga]
    })
    with open('data/table_layanan.csv', mode='a', newline='', encoding='utf-8') as f:
        new_data.to_csv(f, header=False, index=False, sep=';')
    return new_data

def read_layanan():
    df = pd.read_csv('data/table_layanan.csv', sep=';')
    return df

def update_layanan(id, layanan, harga):
    df = pd.read_csv('data/table_layanan.csv', sep=';')
    layanan = df.loc[df['id'] == id]
    if layanan.empty:
        return None
    layanan['layanan'] = layanan
    layanan['harga'] = harga
    with open('data/table_layanan.csv', mode='w', newline='', encoding='utf-8') as f:
        df.to_csv(f, index=False, sep=';')
    return layanan

def delete_layanan(id):
    df = pd.read_csv('data/table_layanan.csv', sep=';')
    layanan = df.loc[df['id'] == id]
    if layanan.empty:
        return None
    df = df.drop(layanan.index)
    with open('data/table_layanan.csv', mode='w', newline='', encoding='utf-8') as f:
        df.to_csv(f, index=False, sep=';')
    return layanan