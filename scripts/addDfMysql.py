import pandas as pd
#from sqlalchemy import create_engine, text
import re
import mysql.connector
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from pathlib import Path
import json

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE_PATH = os.path.join(BASE_DIR, 'config.json')
# Функция для загрузки конфигурации
def load_config(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл конфигурации '{file_path}' не найден.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Ошибка: Не удалось декодировать JSON из файла '{file_path}'. Проверьте синтаксис.")
        exit(1)
# Загружаем все данные из файла
CONFIG_DATA = load_config(CONFIG_FILE_PATH)

def funcBtnFindBtnClick(dictDirDownloads, exeYa, exeYaDriver, url, tegXPath, tegCssSelector, tegClassName, strStatus):
    options = Options()
    options.binary_location = exeYa
    options.add_experimental_option("prefs", dictDirDownloads)
    # options.add_experimental_option("detach", True)
    # СТРОКА ДЛЯ ФОНОВОГО РЕЖИМА
    options.add_argument("--headless=new")
    # Дополнительные флаги для стабильности в фоновом режиме
    options.add_argument("--disable-gpu")  # Отключает использование графического процессора
    options.add_argument("--window-size=1920,1080")  # Задает виртуальный размер экрана (важно для кликов)
    service = Service(executable_path=exeYaDriver)
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        # Ждем максимум 20 секунд, пока элемент появится в DOM
        wait = WebDriverWait(driver, 20)
        # Нажимаем "закрыть" один раз
        btnXPath = wait.until(EC.presence_of_element_located((By.XPATH, tegXPath)))
        driver.execute_script("arguments[0].click();", btnXPath)
        print("Кнопка нажата!")
        # Небольшая пауза, чтобы DOM обновился после закрытия модалки
        time.sleep(2)
        # Ожидание кликабельности
        clickCssSelector = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, tegCssSelector)))
        clickCssSelector.click()
        time.sleep(20)
        print("Файл excel скачан из сайта Барс!")
        strStatus = "OK"
    except Exception as e:
        print(f"Ошибка: {e}")
        strStatus = "Error" # Возможно стоит добавить переменную e в strStatus
    finally:
        driver.quit()
    return dictDirDownloads, exeYa, exeYaDriver, url, tegXPath, tegCssSelector, tegClassName, strStatus
# Функция парсит сайт и скачивает из сайта файл сохраняя формат и расширение csv. в dictDirDownloads мы указываем путь
# где будут храниться файлы. также необходимо указать теги,
# тег tegXPath закрывает всплывающее окно в момент запуска сайта, tegCssSelector тег парсит кнопки и нажимает на кнопку
# tegClassName тег находит необходимую кнопку по икнокам, который нужно нажать
#Функция удаляет старое имя файла и меняет название файла на новое:
def funcRenameFiles(dirDownload, strNewNameFile, strAddNewFile):
    # Получаем список файлов в папке, сортируем по времени создания
    listFiles = [os.path.join(dirDownload, file) for file in os.listdir(dirDownload)]
    #print("listFiles:")
    #print(listFiles)
    if listFiles:
        strNeedDelFile = max(listFiles, key=os.path.getctime)
        #print("strNeedDelFile:")
        #print(strNeedDelFile)
        # Сохраняем расширение (например, .xlsx или .csv)
        strExtensionFile = os.path.splitext(strNeedDelFile)[1]
        #print("strExtensionFile:")
        #print(strExtensionFile)
        # Формируем путь для целевого файла exp1
        #print("strNewNameFile:")
        #print(strNewNameFile)
        strAddNewFile = f"{strNewNameFile}{strExtensionFile}"
        #print("strAddNewFile:")
        #print(strAddNewFile)
        strAddNewFile = os.path.join(dirDownload, strAddNewFile)
        # print(strAddNewFile)
        # Проверяем, существует ли уже файл с таким именем. Если да — удаляем его.
        if os.path.exists(strAddNewFile):
            os.remove(strAddNewFile)
            print(f"Старый файл {strNeedDelFile} удален.")
        # Переименовываем
        os.rename(strNeedDelFile, strAddNewFile)
        print(f"Файл сохранен как: {strAddNewFile}")
    return dirDownload, strNewNameFile, strAddNewFile
#Функция считывает файл *.csv и переводит в Dataframe:
def funcCsvDf(file, dfFile, strStatus):
    try:
        dfFile = pd.read_csv(file, encoding='utf-8', sep=';')
        print("Файл успешно прочитан в UTF-8")
        strStatus = "OK"
    except UnicodeDecodeError:
        dfFile = pd.read_csv(file, encoding='cp1251', sep=';')
        strStatus = "OK"
    except FileNotFoundError:
        print(f"Ошибка: Файл '{file}' не найден. Проверьте путь.")
        strStatus = "Error"
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
        strStatus = "Error"
    return file, dfFile, strStatus
#Функция сортирует по дате и объединяет 2 готовые таблицы dataframe в 1:
def funcSortDataLastMerge2df(dfResult, df1, df2, listdf1, listdf2, colDf1, colDf2, colDateDf1, colDateDf2):
    df1 = df1[listdf1]
    df2 = df2[listdf2]
    # print(df1)
    # print(df2)
    # dfTestRow = df1[df1[colDf1] == 'IR002663']
    # print(dfTestRow)
    # dfTestRow = df2[df2[colDf2] == 'IR002663']
    # print(dfTestRow)
    #df1[colDateDf1] = pd.to_datetime(df1[colDateDf1], dayfirst=True)
    #df2[colDateDf2] = pd.to_datetime(df2[colDateDf2], dayfirst=True)
    df1.loc[:, colDateDf1] = pd.to_datetime(df1[colDateDf1], dayfirst=True)
    df2.loc[:, colDateDf2] = pd.to_datetime(df2[colDateDf2], dayfirst=True)
    df1 = df1.sort_values(colDateDf1).drop_duplicates(colDf1, keep='last')
    df2 = df2.sort_values(colDateDf2).drop_duplicates(colDf2, keep='last')
    dfResult = pd.merge(
        df1,
        df2,
        left_on=colDf1,
        right_on=colDf2,
        how='inner',
        suffixes=('_Left', '_Right')
    )
    return dfResult, df1, df2, listdf1, listdf2, colDf1, colDf2, colDateDf1, colDateDf2
#Функция сравнения двух таблиц и запись в отчет:
def funcLogDf(df1, df2, strSheets, dir, listStatusData, strCurrentDate):
    # Текущая дата для имени файла
    #strCurrentDate = datetime.now().strftime("%Y-%m-%d")
    #log_filename = f"log_{strSheets}_{strCurrentDate}.xlsx"
    strFileName = os.path.join(dir, f"log_{strSheets}_{strCurrentDate}.xlsx")
    print("strFileName:")
    print(strFileName)
    #1. Готовим данные для сравнения размеров
    dictStatusData = {
        "Параметр": ["Кол-во строк", "Кол-во столбцов"],
        "Таблица 1 (Исходная)": [df1.shape[0], df1.shape[1]],
        "Таблица 2 (После БД)": [df2.shape[0], df2.shape[1]]
    }
    dfStatusData = pd.DataFrame(dictStatusData)
    #print("dfStatusData:")
    #print(dfStatusData)
    #2. Сравнение содержимого (если размеры совпадают)
    # Сбрасываем названия колонок у обоих DF в 0, 1, 2..., чтобы сравнить только значения
    dfTemp1 = df1.copy()
    dfTemp2 = df2.copy()
    dfTemp1.columns = range(df1.shape[1])
    dfTemp2.columns = range(df2.shape[1])
    #print("dfTemp1, dfTemp2:")
    #print(dfTemp1)
    #print(dfTemp2)
    # Используем .values, чтобы сравнивать чистые массивы данных, игнорируя индексы
    #if df1.shape == df2.shape:
    if dfTemp1.shape == dfTemp2.shape:
        # Создаем маску различий
        #coutValues = (dfTemp1 != dfTemp2).sum().sum()
        intCoutValues = (dfTemp1.values != dfTemp2.values).sum()
        print("coutValues:", intCoutValues)
        strStatusText = f"Найдено {intCoutValues} несовпадающих ячеек" if intCoutValues > 0 else "Данные идентичны"
    else:
        strStatusText = "Размеры таблиц отличаются, детальное сравнение значений не проводилось"
    print("strStatusText:", strStatusText)
    dfStatusData.loc[len(dfStatusData)] = ["Результат сравнения", strStatusText, strStatusText]
    #print("dfStatusData:")
    #print(dfStatusData)
    #listStatusData = dfStatusData.to_dict(orient="records")
    listStatusData = dfStatusData.values.tolist()
    #print("listStatusData:")
    #print(listStatusData)
    #3. Запись в Excel
    #with pd.ExcelWriter(strFileName, engine='xlsxwriter') as writer:
    with pd.ExcelWriter(strFileName, engine='openpyxl') as writer:
        dfStatusData.to_excel(writer, index=False, sheet_name='Summary')
        # Опционально: записываем сами таблицы на другие листы для контроля
        #df1.head(100).to_excel(writer, sheet_name='Table1_Sample')
        #df2.head(100).to_excel(writer, sheet_name='Table2_Sample')
    print(f"Отчет сохранен в файл: {strFileName}")
    return df1, df2, strSheets, dir, listStatusData, strCurrentDate
#Функция удаляет талицу из БД. необоходимо указать таблицу, которую нужно удалить:
def funcDropMysqlTable(dbHost, dbUser, dbPasswd, dbName, df, strStatus):
    try:
        conn = mysql.connector.connect(
            host=dbHost,
            user=dbUser,
            password=dbPasswd,
            database=dbName
        )
        if conn.is_connected():
            cursor = conn.cursor()
            #print(df)
            #print(type(df))
            querryDropTables = f"DROP TABLE IF EXISTS {df};"
            print(querryDropTables)
            cursor.execute(querryDropTables)
            print(f"Таблица '{df}' была удалена.")
            conn.commit() # Подтверждение изменений
            strStatus = "Ok"

    except mysql.connector.Error as e:
        print(f"Ошибка при подключении к MySQL: {e}")
        strStatus = "Error"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("Соединение с MySQL закрыто.")
    return dbHost, dbUser, dbPasswd, dbName, df, strStatus
#Функция загружает таблицу Dataframe в БД Mysql, зная префикс и имя листа. В нашем случае имя листа это таблица
def funcDfMysql(df, userDb, passwdDb, hostDb, nameDb, strPrefixTech, strSheetsName, strStatus):
    '''
    engine = None
    try:
        conn = f"mysql+mysqlconnector://{userDb}:{passwdDb}@{hostDb}/{nameDb}"
        engine = create_engine(conn)
        df.columns = df.columns.str.replace(' ', '_', regex=False).str.replace(r'[^a-zA-Z0-9_]', '', regex=True)
        #df.columns = pd.factorize(df.columns)[0].astype(str) + '_' + df.columns
        df.columns = [f"{i}_{col}" for i, col in enumerate(df.columns)]
        #df = df.loc[:, ~df.columns.duplicated()]
        strSheetsSafeName = re.sub(r'[^a-zA-Z0-9_]', '', strSheetsName.replace(' ', '_'))
        strSheetsNamePrefix = f"{strPrefixTech}_{strSheetsSafeName}"
        if strSheetsNamePrefix and strSheetsSafeName:
            print(f"Импорт данных из листа '{strSheetsName}' в таблицу '{strSheetsNamePrefix}'...")
            # При использовании if_exists='replace', старая таблица удаляется полностью перед созданием новой схемы.
            df.to_sql(name=strSheetsNamePrefix, con=engine, index=False, if_exists='replace')
            print(f"Таблица '{strSheetsNamePrefix}' успешно обновлена.")
            strStatus = "OK"
        else:
            print(f"Пропущен лист с пустым или недопустимым именем: '{strSheetsName}'")
    except ImportError:
        print("Ошибка: Не установлена библиотека 'pyxlsb'. Пожалуйста, выполните: pip install pyxlsb")
        strStatus = "Error"
    except mysql.connector.Error as err:
        print(f"Ошибка подключения к MySQL: {err}")
        strStatus = "Error"
    except Exception as e:
        print(f"Ошибка при запросе: {e}")
        strStatus = "Error"
    finally:
        if engine:
            # if 'engine' in locals() and engine:
            engine.dispose()
    '''
    conn = None
    cursor = None
    try:
        # 1. Подключение к БД через mysql-connector
        conn = mysql.connector.connect(
            user=userDb,
            password=passwdDb,
            host=hostDb,
            database=nameDb
        )
        cursor = conn.cursor()
        # 2. Обработка имён колонок (ваш оригинальный код)
        df.columns = df.columns.str.replace(' ', '_', regex=False).str.replace(r'[^a-zA-Z0-9_]', '', regex=True)
        df.columns = [f"{i}_{col}" for i, col in enumerate(df.columns)]
        # Очистка имени таблицы
        strSheetsSafeName = re.sub(r'[^a-zA-Z0-9_]', '', strSheetsName.replace(' ', '_'))
        strSheetsNamePrefix = f"{strPrefixTech}_{strSheetsSafeName}"
        if strSheetsNamePrefix and strSheetsSafeName:
            print(f"Импорт данных из листа '{strSheetsName}' в таблицу '{strSheetsNamePrefix}'...")
            # 3. Эмуляция if_exists='replace' (удаляем старую таблицу, если она есть)
            cursor.execute(f"DROP TABLE IF EXISTS `{strSheetsNamePrefix}`")
            # 4. Динамическое создание таблицы на основе типов данных DataFrame
            columns_schema = []
            for col in df.columns:
                # Определяем тип колонки (упрощенно: числа или текст)
                if 'int' in str(df[col].dtype):
                    col_type = "INT"
                elif 'float' in str(df[col].dtype):
                    col_type = "DOUBLE"
                else:
                    col_type = "TEXT"  # TEXT заменяет VARCHAR для избежания проблем с длиной
                columns_schema.append(f"`{col}` {col_type}")
            create_table_query = f"CREATE TABLE `{strSheetsNamePrefix}` ({', '.join(columns_schema)})"
            cursor.execute(create_table_query)
            # 5. Подготовка и вставка данных (замена df.to_sql)
            # Заменяем NaN на None, чтобы в MySQL записались NULL
            df_clean = df.astype(object).where(df.notnull(), None)
            # Формируем запрос INSERT INTO table VALUES (%s, %s, ...)
            placeholders = ", ".join(["%s"] * len(df.columns))
            columns_escaped = ", ".join([f"`{col}`" for col in df.columns])
            insert_query = f"INSERT INTO `{strSheetsNamePrefix}` ({columns_escaped}) VALUES ({placeholders})"
            # Превращаем DataFrame в список кортежей и заливаем пачкой
            data_tuples = [tuple(x) for x in df_clean.to_numpy()]
            cursor.executemany(insert_query, data_tuples)
            # Фиксируем изменения в базе
            conn.commit()
            print(f"Таблица '{strSheetsNamePrefix}' успешно обновлена.")
        else:
            print(f"Пропущен лист с пустым или недопустимым именем: '{strSheetsName}'")
        strStatus = "OK"
    except mysql.connector.Error as err:
        print(f"Ошибка подключения к MySQL: {err}")
        strStatus = "Error"
    except Exception as e:
        print(f"Ошибка при запросе: {e}")
        strStatus = "Error"
    finally:
        # Закрываем ресурсы
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
    return df, userDb, passwdDb, hostDb, nameDb, strPrefixTech, strSheetsName, strStatus
#Функция, которая сохраняет в файл новые таблицы Dataframe:
def funcBackupDf(dir, df, strSheets, strStatus, strFileName, strCurrentDate):
    #strCurrentDate = datetime.now().strftime("%Y-%m-%d")
    #filename = f"{dir}\backup_{strSheets}_{strCurrentDate}.xlsx"
    strFileName = os.path.join(dir, f"backup_{strSheets}_{strCurrentDate}.xlsx")
    #print(strFileName)
    try:
        df.to_excel(strFileName, index=False)
        print(f"Файл '{strFileName}' успешно сохранен!")
        strStatus = 'OK'
    except Exception as e:
        print(f"Ошибка при сохранении: {e}")
        strStatus = 'Error'
    return dir, df, strSheets, strStatus, strFileName, strCurrentDate

def funcRunBuntton():
    listStatus = []
    #1 Копирование таблицы из сайта BARS в Excel формат:
    #dirDownload = r'L:\OESS\BSS\Nokia\Backup\Portal'
    dirDownload = CONFIG_DATA.get("DIRL")
    strCurrentDate = datetime.now().strftime("%Y-%m-%d")

    print("Parsing Site BARS for get Files...")
    # Настройка пути и параметров
    if not os.path.exists(dirDownload):
        os.makedirs(dirDownload)
    dictDirDownloads = {
        "download.default_directory": dirDownload,  # Путь сохранения
        "download.prompt_for_download": False,  # Не спрашивать куда сохранять
        "directory_upgrade": True
    }
    #print("dictDirDownloads:")
    #print(dictDirDownloads)
    dictDirDownloads, exeYa, exeYaDriver, urlSites, tegSitesXPath, tegSitesCssSelector, tegSitesClassName, strStatus = funcBtnFindBtnClick(
        dictDirDownloads,
        #r'C:\Program Files\Yandex\YandexBrowser\Application\browser.exe',
        #r'L:\OESS\BSS\Nokia\Backup\Portal\yandexdriver.exe',
        CONFIG_DATA.get("BROWSER"),
        CONFIG_DATA.get("DIRL")+f'\yandexdriver.exe',
        f'https://{CONFIG_DATA.get("HOSTBARS")}/web/main/sites',
        "//p[contains(text(), 'закрыть')]",
        '[data-testid="DownloadIcon"]',
        'MuiSvgIcon-root',
        ''
    )
    dirDownload, fileName, fileSiltes  = funcRenameFiles(
        dirDownload, 'exportSites', ''
    )
    print("fileSiltes:")
    print(fileSiltes)
    strStatus = "Parsing page Sites - " + strStatus
    print(strStatus)
    subList = []
    subList.append(strStatus)
    dictDirDownloads, exeYa, exeYaDriver, urlCandidates, tegCandidatesXPath, tegCandidatesCssSelector, tegCandidatesClassName, strStatus = funcBtnFindBtnClick(
        dictDirDownloads,
        #r'C:\Program Files\Yandex\YandexBrowser\Application\browser.exe',
        #r'L:\OESS\BSS\Nokia\Backup\Portal\yandexdriver.exe',
        CONFIG_DATA.get("BROWSER"),
        CONFIG_DATA.get("DIRL")+f'\yandexdriver.exe',
        f'https://{CONFIG_DATA.get("HOSTBARS")}/web/main/candidates',
        "//p[contains(text(), 'закрыть')]",
        '[data-testid="DownloadIcon"]',
        'MuiSvgIcon-root',
        ''
    )
    dirDownload, fileName, fileCandidates = funcRenameFiles(
        dirDownload, 'exportCandidates', ''
    )
    print("fileCandidates:")
    print(fileCandidates)
    strStatus = "Parsing page Candidates - " + strStatus
    print(strStatus)
    subList.append(strStatus)

    #2 Сортировка таблицы из сайта BARS:
    print("Sorting tables dfSites and dfCandidates from files...")
    fileSites, dfSites, strStatus = funcCsvDf(fileSiltes, pd.DataFrame(), '')
    print("dfSites:")
    #print(dfSites)
    strStatus = "Sorting table Sites - " + strStatus
    print(strStatus)
    subList.append(strStatus)
    fileCandidates, dfCandidates, strStatus = funcCsvDf(fileCandidates, pd.DataFrame(), '')
    print("dfCandidates:")
    #print(dfCandidates)
    strStatus = "Sorting table Candidates - " + strStatus
    print(strStatus)
    subList.append(strStatus)
    listStatus.append(subList)
    # Получить таблицу Site Nokia (Наименование - A, Статус - D, Тип плана - F, Когда создан - J, Сайт - A, Конструктивный тип сайта - C, Адрес - G, Когда создан - J):
    dfSiteNew, dfSites, dfCandidates, listSites, listCandidate, colSites, colCandidate, colDateSites, colDateCandidate = funcSortDataLastMerge2df(
        pd.DataFrame(), dfSites, dfCandidates,
        ['Наименование', 'Статус', 'Тип плана', 'Когда создан'],
        ['Сайт', 'Конструктивный тип сайта', 'Адрес', 'Когда создан'],
        'Наименование', 'Сайт', 'Когда создан', 'Когда создан'
    )
    #print("dfSiteNew:")
    #print(dfSiteNew)
    # Изменить порядок колонок так, чтобы соответсвовал в таблице БД:
    dfSiteNew = dfSiteNew[dfSiteNew['Наименование'].str[2:4] == '00']
    dfSiteNew['Наименование'] = dfSiteNew['Наименование'].str[:2] + dfSiteNew['Наименование'].str[4:]
    dfSiteNew = dfSiteNew.reindex(columns=['Наименование','Конструктивный тип сайта','Адрес','Статус','Тип плана'])
    #print(dfSiteNew)
    #dfTestRow = dfSiteNew[dfSiteNew['Наименование'] == 'IR2663']
    #print(dfTestRow)

    #3 Сравнение полученой таблицы из сайта BARS с свежей таблицой из БД:
    # Находим все файлы, подходящие под маску backup_site_*
    print("Checking new files with backup files...")
    strFiles = Path(dirDownload).glob('backup_site_*')
    try:
        # Выбираем файл с максимальным временем последней модификации
        strLatestBackupFile = max(strFiles, key=os.path.getmtime)
        print(f"Самый свежий файл: {strLatestBackupFile}")

    except ValueError:
        print("Файлы, соответствующие маске, не найдены.")
    try:
        # Читаем файл. Параметр header=0 (по умолчанию) сохраняет имена столбцов
        dfSiteOld = pd.read_excel(strLatestBackupFile)
        #print("dfSiteOld:")
        #print(dfSiteOld)
        # Выводим список всех имен столбцов для проверки
        #print("\nИмена столбцов:")
        #print(dfSiteOld.columns.tolist())
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
    dfSiteOld, dfSiteNew, strSheets, dirDownload, subList, strCurrentDate = funcLogDf(dfSiteOld, dfSiteNew, 'site', dirDownload, [], strCurrentDate)
    print("subList:")
    print(subList)
    listStatus.append(subList)

    #4 Удаление таблицы Info из БД:
    print("Dropping old table from DB...")
    HOST, USER, PASSWORD, DB_NAME, DB_TABLE, strStatus = funcDropMysqlTable(
        #'10.57.182.34', 'DjangoUser', 'q1w2e3r4t5y6', 'DjangoTemplate',
        CONFIG_DATA.get("IPDBDJANGO"), CONFIG_DATA.get("USERDBDJANGO"),
        CONFIG_DATA.get("PASSWORDDBDJANGO"), CONFIG_DATA.get("NAMEDBDJANGO"),
        #input("Введите названия таблиц через запятую (например: users, orders): ")
        'FromDBTEST__'+'site', ''
    )
    strStatus = "Dropping old table Info from DB - " + strStatus
    print(strStatus)
    subList = []
    subList.append(strStatus)

    #5 Загрузка таблицы Info в БД:
    print("Loading new table in DB...")
    dfSiteNew, USER, PASSWORD, HOST, DB_NAME, strPrefix, strSheets, strStatus = funcDfMysql(
        dfSiteNew,
        #'DjangoUser', 'q1w2e3r4t5y6', '10.57.182.34', 'DjangoTemplate',
        CONFIG_DATA.get("USERDBDJANGO"), CONFIG_DATA.get("PASSWORDDBDJANGO"),
        CONFIG_DATA.get("IPDBDJANGO"),CONFIG_DATA.get("NAMEDBDJANGO"),
        'FromDBTEST_', 'site', ''
    )
    print("dfSiteNew:")
    #print(dfSiteNew)
    strStatus = "Loading new table in DB - " + strStatus
    print(strStatus)
    subList.append(strStatus)
    #dfTestRow = dfSite[dfSite.iloc[:, 0] == 'IR2663']
    #print(dfTestRow)

    #6 Сохранить новую таблицу в эксель файл
    print("Saving backup file...")
    dirDownload, dfSiteNew, strDfNameSheet, strStatus, strFileBackup, strCurrentDate = funcBackupDf(
        dirDownload, dfSiteNew,'site', '', '', strCurrentDate
    )
    print("strFileBackup:")
    #print(strFileBackup)
    strStatus = "Saving backup file - " + strStatus
    print(strStatus)
    subList.append(strStatus)
    print("strCurrentDate:")
    print(strCurrentDate)
    subList.append(strCurrentDate)
    listStatus.append(subList)
    print("listStatus:")
    print(listStatus)
    return listStatus
funcRunBuntton()