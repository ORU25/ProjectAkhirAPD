from colors import *

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
                    # print("Lokasi tidak ditemukan.")
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
