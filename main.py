from datetime import datetime
from prefect import task, flow, get_run_logger
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import random
import traceback
import os
import hashlib

os.makedirs('data', exist_ok=True)


CHROME_DRIVER_PATH = r'C:\Users\Анастасия\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'

@task(retries=2, retry_delay_seconds=30)
def scrape_data():
    logger = get_run_logger()
    logger.info("Начинаем сбор данных с сайта.")

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')  
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    try:
        service = Service(executable_path=CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        logger.info("Браузер Chrome запущен успешно")

        url_one_room = 'https://realty.yandex.ru/moskva_i_moskovskaya_oblast/snyat/kvartira/odnokomnatnaya/metro-kommunarka/'
        url_studio = 'https://realty.yandex.ru/moskva_i_moskovskaya_oblast/snyat/kvartira/studiya/metro-kommunarka/'
        properties = []

        for url in [url_one_room, url_studio]:
            logger.info(f"Открываем страницу: {url}")
            driver.get(url)

            wait_time = 5 + random.uniform(1, 3)
            logger.info(f"Ждем {wait_time:.2f} секунд для загрузки страницы")
            time.sleep(wait_time)

            page_source = driver.page_source

            soup = BeautifulSoup(page_source, 'html.parser')

            items = soup.select('.OffersSerpItem')
            logger.info(f"Найдено {len(items)} объявлений на странице")

            if not items:
                logger.warning("Селектор .OffersSerpItem не сработал, пробуем альтернативные")

                alternative_selectors = [
                    '.CardComponent', 
                    '.Card', 
                    '.OfferCard', 
                    '[data-test="offer-card"]',
                    '[class*="offer-card"]',
                    '[class*="OfferCard"]'
                ]

                for selector in alternative_selectors:
                    alt_items = soup.select(selector)
                    if alt_items:
                        items = alt_items
                        logger.info(f"Используем другой селектор: {selector}, найдено {len(items)} объявлений")
                        break

            if not items:
                logger.warning("Не удалось найти объявления на странице")
                continue

            for idx, item in enumerate(items):
                try:
                    title_elem = item.select_one('.OffersSerpItemTitle__text') or \
                                item.select_one('[class*="title"]') or \
                                item.select_one('h3') or \
                                item.select_one('h2')

                    price_elem = item.select_one('.OffersSerpItemPrice__price') or \
                                item.select_one('[class*="price"]') or \
                                item.select_one('[data-test="price"]')

                    link_elem = item.select_one('.OffersSerpItem__link') or \
                               item.select_one('a') or \
                               item.select_one('[href]')

                    if title_elem and price_elem and link_elem:
                        title = title_elem.text.strip()

                        price_text = price_elem.text.replace('₽/мес.', '').replace('\xa0', '').replace(' ', '').strip()
                        price_text = ''.join(c for c in price_text if c.isdigit())

                        try:
                            price = int(price_text) if price_text else None
                        except ValueError:
                            price = None
                            logger.warning(f"Не получилось преобразовать цену из текста: '{price_elem.text}'")

                        href = link_elem.get('href', '')
                        link = 'https://realty.yandex.ru' + href if href.startswith('/') else href

                        ad_id = hashlib.md5(link.encode()).hexdigest()

                        properties.append({
                            'id': ad_id,
                            'title': title, 
                            'price': price, 
                            'link': link,
                            'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

                except Exception as e:
                    logger.error(f"Ошибка при обработке объявления {idx+1}: {str(e)}")

        driver.quit()
        logger.info(f"Сбор данных завершен. Собрано {len(properties)} объявлений.")

        if not properties:
            logger.warning("Не удалось собрать данные о недвижимости")
            return pd.DataFrame(columns=['id', 'title', 'price', 'link', 'scraped_at'])

        df = pd.DataFrame(properties)
        return df

    except Exception as e:
        logger.error(f"Произошла ошибка при сборе данных: {str(e)}")
        logger.error(traceback.format_exc())
        return pd.DataFrame(columns=['id', 'title', 'price', 'link', 'scraped_at'])

@task
def save_data(df):
    logger = get_run_logger()
    logger.info("Сохраняем собранные данные.")

    if df.empty:
        logger.warning("Нет данных для сохранения")
        return None

    if 'price' not in df.columns:
        logger.error("В данных отсутствует колонка 'price'")
        df['price'] = None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_file_path = f"data/real_estate_kommunarka_raw_{timestamp}.csv"

    df.to_csv(raw_file_path, index=False)
    logger.info(f"Все собранные данные сохранены в '{raw_file_path}'")

    filtered_df = df.dropna(subset=['price']).copy()
    logger.info(f"После удаления записей без цены осталось {len(filtered_df)} объявлений")

    if filtered_df.empty:
        logger.warning("После фильтрации не осталось объявлений с ценой")
        return raw_file_path

    filtered_df['price'] = filtered_df['price'].astype(int)

    filtered_df = filtered_df.sort_values(by='price').reset_index(drop=True)

    filtered_file_path = f"data/real_estate_kommunarka_{timestamp}.csv"
    filtered_df.to_csv(filtered_file_path, index=False)
    logger.info(f"Данные с ценами сохранены в '{filtered_file_path}'")

    if os.path.exists("data/real_estate_kommunarka_history.csv"):
        history_df = pd.read_csv("data/real_estate_kommunarka_history.csv")
        combined_df = pd.concat([history_df, filtered_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['id', 'price'])
    else:
        combined_df = filtered_df

    combined_df.to_csv("data/real_estate_kommunarka_history.csv", index=False)
    logger.info(f"Данные добавлены в историю. Всего объявлений в истории: {len(combined_df)}")

    filtered_df.to_csv("data/real_estate_kommunarka_latest.csv", index=False)
    logger.info("Обновлен файл с последними данными.")

    return filtered_file_path

@flow(retries=2, retry_delay_seconds=60)
def real_estate_scraper():
    logger = get_run_logger()
    logger.info("Запуск скрапера недвижимости.")

    try:
        data = scrape_data()

        if data.empty:
            logger.warning("Не получено данных, завершаем работу")
            return None

        filepath = save_data(data)
        logger.info("Скрапер завершил работу успешно.")
        return filepath

    except Exception as e:
        logger.error(f"Произошла ошибка в скрапере: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == '__main__':
    real_estate_scraper()
