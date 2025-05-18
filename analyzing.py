import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import glob
import numpy as np

def analyze_latest_data():
    if not os.path.exists('data/real_estate_kommunarka_latest.csv'):
        print("Файл с последними данными не найден. Сначала запустите скрапер.")
        return False

    print("Загружаем последние данные...")
    df = pd.read_csv('data/real_estate_kommunarka_latest.csv')

    print(f"\nАнализ данных от {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Всего объявлений: {len(df)}")
    print(f"Минимальная цена: {df['price'].min():,} ₽/мес")
    print(f"Максимальная цена: {df['price'].max():,} ₽/мес")
    print(f"Средняя цена: {df['price'].mean():,.2f} ₽/мес")
    print(f"Медианная цена: {df['price'].median():,} ₽/мес")

    os.makedirs('reports', exist_ok=True)

    with open(f'reports/stats_report_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write(f"Анализ данных по аренде квартир возле метро Коммунарка\n")
        f.write(f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Количество объявлений: {len(df)}\n")
        f.write(f"Диапазон цен: от {df['price'].min():,} до {df['price'].max():,} ₽/мес\n")
        f.write(f"Средняя цена: {df['price'].mean():,.2f} ₽/мес\n")
        f.write(f"Медианная цена: {df['price'].median():,} ₽/мес\n")
        f.write(f"Стандартное отклонение: {df['price'].std():,.2f} ₽/мес\n\n")


    print(f"Отчет со статистикой сохранен в reports/stats_report_{timestamp}.txt")

    return True

def analyze_historical_data():
    if not os.path.exists('data/real_estate_kommunarka_history.csv'):
        print("Файл с историческими данными не найден.")
        return False

    print("Загружаем исторические данные...")
    df = pd.read_csv('data/real_estate_kommunarka_history.csv')

    df['scraped_at'] = pd.to_datetime(df['scraped_at'])
    df['date'] = df['scraped_at'].dt.date

    daily_counts = df.groupby('date').size().reset_index(name='count')

    with open(f'reports/historical_report_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write(f"Исторический анализ данных по аренде квартир возле метро Коммунарка\n")
        f.write(f"Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Период данных: с {df['date'].min()} по {df['date'].max()}\n")
        f.write(f"Всего уникальных объявлений за весь период: {df['id'].nunique()}\n\n")

        f.write("Статистика по дням:\n")
        daily_stats = df.groupby('date').agg(
            количество=('id', 'count'),
            средняя_цена=('price', 'mean'),
            медиана_цены=('price', 'median'),
            мин_цена=('price', 'min'),
            макс_цена=('price', 'max')
        ).reset_index()

        for _, row in daily_stats.iterrows():
            f.write(f"\nДата: {row['date']}\n")
            f.write(f"  Количество объявлений: {row['количество']}\n")
            f.write(f"  Средняя цена: {row['средняя_цена']:,.2f} ₽/мес\n")
            f.write(f"  Медианная цена: {row['медиана_цены']:,.2f} ₽/мес\n")
            f.write(f"  Минимальная цена: {row['мин_цена']:,} ₽/мес\n")
            f.write(f"  Максимальная цена: {row['макс_цена']:,} ₽/мес\n")

    print(f"Исторический отчет сохранен в reports/historical_report_{timestamp}.txt")
    return True

def main():
    print("Анализ данных по аренде квартир у метро Коммунарка\n")

    while True:
        print("\nВыберите тип анализа:")
        print("1 - Анализ последних собранных данных")
        print("2 - Анализ исторических данных (если есть)")
        print("3 - Выполнить оба типа анализа")
        print("0 - Выход")

        choice = input("\nВаш выбор: ")

        if choice == '1':
            analyze_latest_data()
        elif choice == '2':
            analyze_historical_data()
        elif choice == '3':
            analyze_latest_data()
            print("\n" + "="*50 + "\n")
            analyze_historical_data()
        elif choice == '0':
            print("До свидания!")
            break
        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    main()
