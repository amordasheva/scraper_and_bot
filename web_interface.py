import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Настройки API
API_BASE_URL = "http://localhost:8000/api"

def main():
    st.title("📊 Real Estate Data Explorer")
    st.write("Интерфейс для просмотра данных о недвижимости")

    # Получаем список файлов
    try:
        response = requests.get(f"{API_BASE_URL}/files")
        if response.status_code == 200:
            files = response.json()
            
            # Создаем боковую панель с фильтрами
            st.sidebar.title("Фильтры")
            
            # Выбор файла
            selected_file = st.sidebar.selectbox(
                "Выберите файл",
                [f["filename"] for f in files],
                index=0
            )

            # Фильтры цены
            st.sidebar.subheader("Фильтр по цене")
            min_price = st.sidebar.number_input("Минимальная цена", value=0)
            max_price = st.sidebar.number_input("Максимальная цена", value=1000000)

            # Сортировка
            st.sidebar.subheader("Сортировка")
            sort_by = st.sidebar.selectbox(
                "Сортировать по",
                ["price", "title", "scraped_at"],
                index=0
            )
            sort_order = st.sidebar.radio(
                "Порядок сортировки",
                ["asc", "desc"],
                index=0
            )

            # Пагинация
            st.sidebar.subheader("Пагинация")
            limit = st.sidebar.slider("Количество записей", 1, 100, 10)
            offset = st.sidebar.number_input("Смещение", 0, 1000, 0)

            # Получаем данные с учетом фильтров
            params = {
                "filename": selected_file,
                "limit": limit,
                "offset": offset,
                "min_price": min_price if min_price > 0 else None,
                "max_price": max_price if max_price < 1000000 else None,
                "sort_by": sort_by,
                "sort_order": sort_order
            }

            response = requests.get(f"{API_BASE_URL}/data", params=params)
            if response.status_code == 200:
                data = response.json()
                
                # Отображаем статистику
                st.subheader("📈 Статистика")
                stats_response = requests.get(f"{API_BASE_URL}/stats", params={"filename": selected_file})
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Всего записей", stats["total_records"])
                    with col2:
                        st.metric("Мин. цена", f"{stats['price_stats']['min']:,.0f} ₽")
                    with col3:
                        st.metric("Макс. цена", f"{stats['price_stats']['max']:,.0f} ₽")
                    with col4:
                        st.metric("Средняя цена", f"{stats['price_stats']['mean']:,.0f} ₽")
                
                # Отображаем данные
                st.subheader("📋 Данные")
                if data["data"]:
                    df = pd.DataFrame(data["data"])
                    st.dataframe(df)
                    
                    # Добавляем информацию о пагинации
                    st.write(f"Показано {len(df)} из {data['total']} записей")
                else:
                    st.warning("Нет данных, соответствующих выбранным фильтрам")
            else:
                st.error(f"Ошибка при получении данных: {response.status_code}")
        else:
            st.error("Не удалось получить список файлов")
    except Exception as e:
        st.error(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main() 