from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from typing import Optional, List
from datetime import datetime

app = FastAPI(title="Real Estate Data API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Путь к файлам с данными
DATA_DIR = "data"

def get_latest_data_file():
    """Получает путь к последнему файлу с данными"""
    files = [f for f in os.listdir(DATA_DIR) if f.startswith("real_estate_kommunarka_") and not f.endswith("_raw_")]
    if not files:
        raise HTTPException(status_code=404, detail="No data files found")
    return os.path.join(DATA_DIR, sorted(files)[-1])

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "Real Estate Data API"}

@app.get("/files")
async def list_files():
    """Получение списка доступных файлов с данными"""
    files = []
    for filename in os.listdir(DATA_DIR):
        if filename.startswith("real_estate_kommunarka_") and not filename.endswith("_raw_"):
            file_path = os.path.join(DATA_DIR, filename)
            df = pd.read_csv(file_path)
            files.append({
                "filename": filename,
                "rows": len(df),
                "columns": df.columns.tolist()
            })
    return files

@app.get("/data")
async def get_data(
    filename: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc"
):
    """
    Получение данных с возможностью фильтрации и сортировки
    
    Параметры:
    - filename: имя файла (если не указано, используется последний)
    - limit: количество записей (1-100)
    - offset: смещение
    - min_price: минимальная цена
    - max_price: максимальная цена
    - sort_by: поле для сортировки
    - sort_order: порядок сортировки (asc/desc)
    """
    try:
        # Определяем файл для чтения
        if filename:
            file_path = os.path.join(DATA_DIR, filename)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
        else:
            file_path = get_latest_data_file()

        # Читаем данные
        df = pd.read_csv(file_path)

        # Применяем фильтры
        if min_price is not None:
            df = df[df['price'] >= min_price]
        if max_price is not None:
            df = df[df['price'] <= max_price]

        # Применяем сортировку
        if sort_by:
            if sort_by not in df.columns:
                raise HTTPException(status_code=400, detail=f"Invalid sort column: {sort_by}")
            df = df.sort_values(by=sort_by, ascending=(sort_order == "asc"))

        # Применяем пагинацию
        total = len(df)
        df = df.iloc[offset:offset + limit]

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "data": df.to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats(filename: Optional[str] = None):
    """Получение статистики по данным"""
    try:
        # Определяем файл для чтения
        if filename:
            file_path = os.path.join(DATA_DIR, filename)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
        else:
            file_path = get_latest_data_file()

        # Читаем данные
        df = pd.read_csv(file_path)

        # Рассчитываем статистику
        stats = {
            "total_records": len(df),
            "price_stats": {
                "min": df['price'].min(),
                "max": df['price'].max(),
                "mean": df['price'].mean(),
                "median": df['price'].median()
            },
            "last_update": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
        }

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 