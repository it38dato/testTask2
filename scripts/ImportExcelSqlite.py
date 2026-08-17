import pandas as pd
import sqlite3
import os

def import_xlsb_to_sqlite(excel_file, db_file):
    """
    Переносит данные из каждого листа XLSB в новую таблицу SQLite, 
    только если таблица с таким именем еще не существует.
    """
    
    # 1. Подключение к базе данных SQLite
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 2. Чтение всех листов Excel в словарь DataFrame с использованием движка 'pyxlsb'
    try:
        # Указываем engine='pyxlsb' для работы с форматом .xlsb
        dfs = pd.read_excel(excel_file, sheet_name=None, engine='pyxlsb')
    except FileNotFoundError:
        print(f"Ошибка: Файл Excel не найден по пути {excel_file}")
        return
    except Exception as e:
        print(f"Произошла ошибка при чтении файла XLSB: {e}")
        return

    # 3. Итерация по листам и запись в БД
    for sheet_name, df in dfs.items():
        # Очистка имени таблицы (удаление пробелов и спецсимволов для совместимости с SQL)
        table_name = "".join(c for c in sheet_name if c.isalnum() or c in ('_',)).strip('_')
        
        if not table_name:
            print(f"Пропущен лист с пустым или некорректным именем: {sheet_name}")
            continue

        # Проверка существования таблицы в базе данных
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if cursor.fetchone() is None:
            # Таблица не существует, можно импортировать данные
            try:
                # if_exists='fail' гарантирует, что данные не будут перезаписаны
                df.to_sql(name=table_name, con=conn, if_exists='fail', index=False)
                print(f"Таблица '{table_name}' успешно создана и заполнена данными из листа '{sheet_name}'.")
            except Exception as e:
                print(f"Ошибка при создании таблицы '{table_name}': {e}")
        else:
            print(f"Таблица '{table_name}' уже существует в базе данных. Данные не импортированы.")

    # 4. Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()
    print("Процесс импорта завершен.")

# --- Пример использования ---
# Укажите путь к вашему файлу XLSB и имя файла базы данных
excel_file_path = 'N_Data.xlsb' 
database_file_path = 'db.sqlite3'

import_xlsb_to_sqlite(excel_file_path, database_file_path)