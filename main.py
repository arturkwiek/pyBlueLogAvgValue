import pandas as pd
from astral.sun import sun
from astral import LocationInfo
from datetime import datetime, timedelta
import os

def remove_label_convert_int(value):
    """Funkcja do konwersji wartości R, G, B."""
    return int(value.split(': ')[1])

def load_csv_files(directory):
    """Funkcja do wczytywania wszystkich plików CSV z katalogu."""
    files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    data_frames = []
    for file in files:
        file_path = os.path.join(directory, file)
        data = pd.read_csv(
            file_path,
            converters={
                ' R': remove_label_convert_int,
                ' G': remove_label_convert_int,
                ' B': remove_label_convert_int
            }
        )
        data.columns = ['Timestamp', 'R', 'G', 'B']
        data['Timestamp'] = pd.to_datetime(data['Timestamp'])
        data.set_index('Timestamp', inplace=True)
        data_frames.append((file, data))
    return data_frames

def get_sun_times(date, city, delta_minutes=5):
    """Funkcja do pobierania godzin wschodu i zachodu słońca dla danego dnia i lokalizacji."""
    s = sun(city.observer, date=date, tzinfo=city.timezone)
    sunrise = s['sunrise'] - timedelta(minutes=delta_minutes)
    sunset = s['sunset'] + timedelta(minutes=delta_minutes)
    return sunrise, sunset

def calculate_avg_b_values(data, sunrise, sunset):
    """Funkcja do obliczania średniej wartości składowej B w przedziale +-5 minut w chwilach wschodu i zachodu słońca."""
    bw = data.between_time((sunrise - timedelta(minutes=5)).time(), (sunrise + timedelta(minutes=5)).time())['B'].mean()
    bavg = data.between_time(sunrise.time(), sunset.time())['B'].mean()
    bz = data.between_time((sunset - timedelta(minutes=5)).time(), (sunset + timedelta(minutes=5)).time())['B'].mean()
    return bw, bavg, bz

def calculate_b_values(data_frames, city):
    """Funkcja do obliczania średnich wartości składowej B dla wschodu, zachodu słońca oraz całego okresu między nimi."""
    results = []
    for file, data in data_frames:
        log_date = data.index[0].date()
        sunrise, sunset = get_sun_times(log_date, city)

        # Obliczanie wartości średnich dla wschodu, zachodu słońca oraz całego okresu między nimi
        bw, bavg, bz = calculate_avg_b_values(data, sunrise, sunset)

        results.append((file, bw, bavg, bz))

    return results

def main():
    directory = "."  # Bieżący katalog
    city = LocationInfo(name="Tarnów", region="Poland", timezone="Europe/Warsaw", latitude=50.0123, longitude=20.9856)

    data_frames = load_csv_files(directory)
    results = calculate_b_values(data_frames, city)

    min_bw = float('inf')
    max_bw = float('-inf')
    min_bz = float('inf')
    max_bz = float('-inf')
    min_bavg = float('inf')
    max_bavg = float('-inf')

    print("nazwa pliku:\tbw\tbavg\tbz")
    for result in results:
        file, bw, bavg, bz = result
        print(f"{file}:\t{bw:.2f}\t{bavg:.2f}\t{bz:.2f}")
        if not pd.isnull(bw):
            min_bw = min(min_bw, bw)
            max_bw = max(max_bw, bw)
        if not pd.isnull(bz):
            min_bz = min(min_bz, bz)
            max_bz = max(max_bz, bz)
        if not pd.isnull(bavg):
            min_bavg = min(min_bavg, bavg)
            max_bavg = max(max_bavg, bavg)

    print("\nPodsumowanie:")
    print(f"min(bw): {min_bw:.2f}")
    print(f"max(bw): {max_bw:.2f}")
    print(f"min(bz): {min_bz:.2f}")
    print(f"max(bz): {max_bz:.2f}")
    print(f"min(bavg): {min_bavg:.2f}")
    print(f"max(bavg): {max_bavg:.2f}")

if __name__ == "__main__":
    main()
