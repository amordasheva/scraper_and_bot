# Веб-скрапинг

Проект для сбора и анализа данных о недвижимости с Яндекс.Недвижимость (студии и однокомнатные квартиры у метро Коммунарка).

## Структура проекта

- `main.py` - скрипт для сбора данных
- `api.py` - API для доступа к данным
- `web_interface.py` - веб-интерфейс
- `analyzing.py` - анализ данных
- `data/` - собранные данные
- `requirements.txt` - зависимости
- `run_scraper.bat` - скрипт для быстрого запуска скрапера в Windows

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv scraping_venv
```

2. Активируйте окружение:
- Windows: `scraping_venv\Scripts\activate`
- Mac: `source scraping_venv/bin/activate`

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

### Сбор данных
```bash
python main.py
```
Или просто запустите `run_scraper.bat` двойным кликом (только для Windows)

### Запуск API
```bash
python api.py
```

### Запуск веб-интерфейса
```bash
streamlit run web_interface.py
```

### Анализ данных
```bash
python analyzing.py
```

## Данные

Данные сохраняются в `data/`:
- `real_estate_kommunarka_raw_*.csv` - сырые данные
- `real_estate_kommunarka_*.csv` - обработанные данные
- `real_estate_kommunarka_history.csv` - история
- `real_estate_kommunarka_latest.csv` - последние данные

