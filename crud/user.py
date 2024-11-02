import pandas as pd
from tabulate import tabulate

def create_user(username, password, role):
    df = pd.read_csv('data/table_user.csv', sep=';')
    if not df['id'].empty:
        user_id = df['id'].max() + 1
    else:
        user_id = 1
    if username in df['username'].values:
        data = {'status': 'failed' ,'message': 'Username sudah terdaftar'}
        return data
    new_data = pd.DataFrame({
        'id': [user_id],
        'username': [username],
        'password': [password],
        'role': [role]
    })
    with open('data/table_user.csv', mode='a', newline='', encoding='utf-8') as f:
        new_data.to_csv(f, header=False, index=False, sep=';')
    data = {'status': 'success', 'message': 'Pendaftaran user berhasil'}
    return data

def read_user():
    df = pd.read_csv('data/table_user.csv', sep=';')
    print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=False))

def update_user(id, username, password, role):
    df = pd.read_csv('data/table_user.csv', sep=';')
    if username in df['username'].values:
        data = {'status': 'failed' ,'message': 'Username sudah terdaftar'}
        return data
    
    user = df.loc[df['id'] == id]
    if user.empty:
        data = {'status': 'failed' ,'message': 'User tidak ditemukan'}
        return data
    
    current_username = user['username'].values[0]
    current_password = user['password'].values[0]
    current_role = user['role'].values[0]

    df.loc[df['id'] == id, 'username'] = username if username else current_username
    df.loc[df['id'] == id, 'password'] = password if password else current_password
    df.loc[df['id'] == id, 'role'] = role if role else current_role

    with open('data/table_user.csv', mode='w', newline='', encoding='utf-8') as f:
        df.to_csv(f, index=False, sep=';')
    data = {'status': 'success' ,'message': 'User berhasil diperbarui'}
    return data

def delete_user(id):
    df = pd.read_csv('data/table_user.csv', sep=';')
    user = df.loc[df['id'] == id]
    if user.empty:
        return None
    df = df.drop(user.index)
    with open('data/table_user.csv', mode='w', newline='', encoding='utf-8') as f:
        df.to_csv(f, index=False, sep=';')
    return user


