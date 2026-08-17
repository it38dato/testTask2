from django.shortcuts import render
from .models import Content
from rest_framework import viewsets
from .serializers import ContentSerializer
import pandas as pd
import mysql.connector
from mysql.connector import Error
from django.conf import settings
import numpy as np
import re
from django.db import connection
#from scripts import addDfMysql
# Create your views here.
class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer

# Компилируем регулярные выражения ОДИН раз при запуске сервера, а не в цикле
RE_REGION = re.compile(r"(автономный округ|автономная область|область|край|округ|республика)", re.IGNORECASE)
RE_RAYON = re.compile(r"(район)", re.IGNORECASE)
RE_CITY = re.compile(r"(город)", re.IGNORECASE)
RE_VILLAGE = re.compile(r"(деревня|поселок|посёлок|село)", re.IGNORECASE)
RE_STREET = re.compile(r"(улица)", re.IGNORECASE)
RE_TOWER = re.compile(r"(вышка|амс)", re.IGNORECASE)
RE_HOUSE = re.compile(r"(дом)", re.IGNORECASE)
RE_SPACES = re.compile(r"\s+")

def checkTable(check):
    return check.empty
def funcCorrectNumbBS(numb, numbFull):
    if len(numb) == 1:
        numbFull = "000" + numb
    elif len(numb) == 2:
        numbFull = "00" + numb
    elif len(numb) == 3:
        numbFull = "0" + numb
    elif len(numb) == 4:
        numbFull = numb
    else:
        print("- Enter the BS number correctly")
    return numb, numbFull
def funcCorrectRegBS(reg, numbReg, lnhoif, utc, msw, plan, arfcnMin, arfcnMax, eNodeB, satell, eArfcn, ruRegion, ipS1):
    hostEricsson = settings.CONFIG_DATA.get("IPERICSSON")
    pathIpPlan = settings.CONFIG_DATA.get("PATHIPPLAN")
    if reg == "AN":
        numbReg = "87"
        lnhoif = ["1875", "3400", "", "", "", ""]
        utc = "UTC+12"
        msw = "МСК+9"
        plan = f"http://{hostEricsson}/CreateSite_web/CES/table_ip_plan_AND"
        satell = "SATELL"
        eArfcn = "3400"
        ruRegion = "Чукотский автономный округ"
        ipS1 = "10.222.1.12"
    elif reg == "BI":
        numbReg="79"
        lnhoif = ["1750", "1875", "1892", "6175", "6200", "3400"]
        utc = "UTC+10"
        msw = "МСК+7"
        plan = f"http://{hostEricsson}/CreateSite_web/CES/table_ip_plan_BIR/"
        satell = "SATELL"
        eArfcn = "1750"
        ruRegion = "Еврейская автономная область"
        ipS1 = "10.222.1.12"
    elif reg == "HB":
        numbReg="27"
        lnhoif = ["1892", "6175", "6200", "3400", "50", "75"]
        utc = "UTC+10"
        msw = "МСК+7"
        plan = f"http://{hostEricsson}/CreateSite_web/CES/table_ip_plan_HAB/"
        satell = "SATELL"
        eArfcn = "1892"
        ruRegion = "Хабаровский край"
        ipS1 = "7.17.60.1"
    elif reg == "KM":
        numbReg="41"
        lnhoif = ["1275", "1875", "3400", "6175", "75", ""]
        utc = "UTC+12"
        msw = "МСК+9"
        plan = f"http://{hostEricsson}/CreateSite_web/CES/table_ip_plan_KAM/"
        satell = "SATELL"
        eArfcn = "1875"
        ruRegion = "Камчатский край"
        ipS1 = "10.222.1.12"
    elif reg == "IR":
        numbReg="38"
        lnhoif = ["1875", "1425", "1400", "6175", "6200", "1250"]
        utc = "UTC+8"
        msw = "МСК+5"
        plan = f"http://{hostEricsson}/CreateSite_web/CES/table_ip_plan_IRK/"
        satell = "SATELL"
        eArfcn = "1875"
        ruRegion = "Иркутская область"
        ipS1 = "7.17.60.1"
    elif reg == "MD":
        numbReg="49"
        lnhoif = ["1875", "1425", "6175", "3400", "75", ""]
        utc = "UTC+11"
        msw = "МСК+8"
        plan = f"http://{hostEricsson}/CreateSite_web/CES/table_ip_plan_MGD/"
        satell = "SATELL"
        eArfcn = "1425"
        ruRegion = "Магаданская область"
        ipS1 = "10.222.1.12"
    elif reg == "SA":
        numbReg="65"
        lnhoif = ["1750", "6175", "6200", "3400", "75", "100"]
        utc = "UTC+11"
        msw = "МСК+8"
        plan = f"http://{hostEricsson}/CreateSite_web/CES/table_ip_plan_SAH/"
        satell = "SATELL"
        eArfcn = "1750"
        ruRegion = "Сахалинская область"
        ipS1 = "10.222.1.12"
    elif reg == "YA":
        numbReg="14"
        lnhoif = ["1875", "6175", "3400", "", "", ""]
        utc = "UTC+9"
        msw = "МСК+6"
        plan = f"http://{hostEricsson}/CreateSite_web/CES/table_ip_plan_YAK/"
        satell = "SATELL"
        eArfcn = "1875"
        ruRegion = "Республика Саха (Якутия)"
        ipS1 = "10.222.1.12"
    elif reg == "IO":
        numbReg="88"
        lnhoif = ["1875", "", "", "", "", ""]
        utc = "UTC+8"
        msw = "МСК+5"
        plan = f"http://{hostEricsson}/CreateSite_web/CES/table_ip_plan_IRK/"
        satell = "SATELL"
        eArfcn = "1875"
        ruRegion = "Иркутская область"
        ipS1 = "10.222.1.12"
    elif reg == "AM":
        numbReg="28"
        lnhoif = ["125", "1875", "", "", "", "", "", "", "", "", "", ""]
        utc = "Etc/GMT-9"
        msw = "МСК+6"
        plan = pathIpPlan
        arfcnMin = 812
        arfcnMax = 885
        eNodeB = "eNodeB_BLG"
        eArfcn = ""
        ruRegion = "Амурская область"
        ipS1 = ""
    elif reg == "BU":
        numbReg="3"
        lnhoif = ["1425", "1427", "1875", "1923", "3400", "6175", "6200", "38750", "38950", "39550", "39100", "39150"]
        utc = "Etc/GMT-8"
        msw = "МСК+5"
        plan = f"http://{hostEricsson}/CreateSite_web/CES/table_ip_plan_BRT/"
        arfcnMin = 1
        arfcnMax = 100
        eNodeB = "eNodeB_BRT"
        eArfcn = ""
        ruRegion = "Республика Бурятия"
        ipS1 = ""
    elif reg == "VV":
        numbReg="25"
        lnhoif = ["100", "125", "1875", "3400", "6175", "6200", "38700", "38750", "38900", "38950", "", ""]
        utc = "Etc/GMT-10"
        msw = "МСК+7"
        plan = f"http://{hostEricsson}/CreateSite_web/CES/table_ip_plan_VLD/"
        arfcnMin = 812
        arfcnMax = 885
        eNodeB = "eNodeB_VLD"
        eArfcn = ""
        ruRegion = "Приморский край"
        ipS1 = ""
    elif reg == "ZB":
        numbReg="75"
        lnhoif = ["1598", "1900", "75", "", "", "", "", "", "", "", "", ""]
        utc = "Etc/GMT-9"
        msw = "МСК+6"
        plan = pathIpPlan
        arfcnMin = 756
        arfcnMax = 772
        eNodeB = "eNodeB_CHI"
        eArfcn = ""
        ruRegion = "Забайкальский край"
        ipS1 = ""
    else:
        print("- Enter region correctly")
        numbReg=""
        lnhoif = ["", "", "", "", "", ""]
        utc = ""
        msw = ""
        plan = "http://"
        satell = ""
        arfcnMin = 0
        arfcnMax = 0
        eNodeB = ""
        eArfcn = ""
        ruRegion = ""
        ipS1 = ""
    return reg, numbReg, lnhoif, utc, msw, plan, arfcnMin, arfcnMax, eNodeB, satell, eArfcn, ruRegion, ipS1
def funcNokiaAddSublistSite(reg, numb, sublist):
    numbFull = ""
    numbReg = "" 
    timeUtc = ""
    timeMsw = ""
    ipPlan = ""
    subnetWork = ""
    listLnhoif = []
    arfcnMin = 0
    arfcnMax = 0
    satell = ""
    eArfcn = ""
    ruRegion = ""
    ipS1 = ""

    hostRdb = settings.CONFIG_DATA.get("HOSTRDB")    
    sublist.append(reg)
    sublist.append(numb)

    numb, numbFull = funcCorrectNumbBS(numb, numbFull)
    reg, numbReg, listLnhoif, timeUtc, timeMsw, ipPlan, arfcnMin, arfcnMax, subnetWork, satell, eArfcn, ruRegion, ipS1 = funcCorrectRegBS(reg, numbReg, listLnhoif, timeUtc, timeMsw, ipPlan, arfcnMin, arfcnMax, subnetWork, satell, eArfcn, ruRegion, ipS1)

    sublist.append(numbFull)
    sublist.append(numbReg)
    sublist.append(numbReg+numbFull)
    sublist.append(reg+numbFull)
    sublist.append(reg+"00"+numbFull)
    sublist.append("https://"+hostRdb+"/p/list.aspx?op=list&k=c3a5t1r&v=c3a5ts5c1cs9r133&q="+reg+"00"+numbFull)

    sublist.append(str(int(numbFull)+3000))
    sublist.append(reg+str(int(numbFull)+3000))
    sublist.append(numbReg+str(int(numbFull)+3000))
    sublist.append(str(int(numbFull)+6000))    
    sublist.append(reg+str(int(numbFull)+6000))    
    sublist.append(numbReg+str(int(numbFull)+6000))

    if numbFull[0] == "0":
        sublist.append(str(int(numbFull)+4000))
        sublist.append(reg+str(int(numbFull)+4000))
        sublist.append(numbReg+str(int(numbFull)+4000))
    else:
        sublist.append(numbFull[:0]+"3"+numbFull[0+1:])
        sublist.append(reg+(numbFull[:0]+"3"+numbFull[0+1:]))
        sublist.append(numbReg+(numbFull[:0]+"3"+numbFull[0+1:]))

    for indexLnhoif in listLnhoif:
        sublist.append(indexLnhoif)

    sublist.append(timeUtc)
    sublist.append(timeMsw)
    sublist.append(ipPlan)
    
    sublist.append(satell)
    sublist.append(eArfcn)
    sublist.append(ruRegion)
    sublist.append(ipS1)
    return reg, numb, sublist
def funcTestingOutList(listTest, index):
    print("======================TEST======================")
    count = 0
    for lists in listTest:
        count=count+1
        print(count," - ",lists)
    print("======================TEST======================")
    count = 0
    for listIndex in listTest[index]:
        for info in listIndex:
            print(str(count)," - ",info)
            count=count+1
    print("======================TEST======================")
    count = 0
    for listIndex in listTest[index]:
        count=count+1
        print(count, " - ", listIndex[0], " - ",listIndex)
    print("======================TEST======================")
    return listTest, index
def funcAddNumbers(listN, dfN):
    dfN = pd.DataFrame(listN)
    dfN.columns = ["Numbers"]
    return listN, dfN
def funcAddSublistFromTable(listFromTable, sublistFromTable, dfTable, lenObj, lenList, site):
    if checkTable(dfTable) == False:
        listTemp = dfTable.values.tolist()
        for indexLists in listTemp:
            for indexObject in indexLists:
                if ".0" in str(indexObject):
                    indexObject = str(int(indexObject))
                    sublistFromTable.append(indexObject)
                elif ("nan" in str(indexObject)) or ("NaN" in str(indexObject)):
                    indexObject = ""
                    sublistFromTable.append(str(indexObject))
                else:
                    sublistFromTable.append(str(indexObject))
    else:
        print("- There is no data "+site+" in the N_Data file from table (dfTable)")
        sublistTemp = []
        listTemp = []
        object = ""
        for indexLen in range(1,lenObj+1):
            sublistTemp.append(object)
        for indexLen in range(1, lenList+1):
            listTemp.append(sublistTemp)
        for indexLists in listTemp:
            for indexObject in indexLists:
                sublistFromTable.append(indexObject)
    listFromTable.append(sublistFromTable)
    return listFromTable, sublistFromTable, dfTable, lenObj, lenList, site
def funcAddListFromTable(mainList, subLsts, updateListTable, dfTable, lenObj, lenList, site):
    object = ""
    listTable = []
    if checkTable(dfTable) == False:
        listTable = dfTable.values.tolist()
        #print(listTable)
        for indexLists in listTable:
            #print(indexLists)
            updateIndexLists = []
            for indexObject in indexLists:
                #print(indexObject)
                #print(type(indexObject))
                if (".0" in str(indexObject)) and (".0." not in str(indexObject)) and (".0 " not in str(indexObject)):# добавил условие  ".0 ", 
                    #print(float(indexObject))
                    #print(int(float(indexObject)))
                    #print(str(int(float(indexObject))))
                    #indexObject = str(int(indexObject)) #Поменял так как 43.0 для мощности почему str не переводит на int, только через float
                    #indexLenObj = str(int(float(indexObject))) #Поменял так как не понятно почему indexLenObj а не indexObject
                    indexObject = str(int(float(indexObject)))
                elif ("nan" in str(indexObject)) or ("None" in str(indexObject)) or ("NaN" in str(indexObject)) or ("0x2a" in str(indexObject)):
                    indexObject = ""
                #print(indexObject)
                updateIndexLists.append(indexObject)
                subLsts.append(indexObject)#Убрал так как нету необходимости читать данные по каждому объекту
            #print(updateIndexLists)
            updateListTable.append(updateIndexLists)
        #print(subLsts)
        #print(updateListTable)
    else:
        print("- There is no data "+site+" in the table (dfTable)")
        for indexLenObj in range(0, lenObj):
            #print(indexLenObj)
            listTable.append(object)            
        print(listTable)
        for indexLenObj in range(1, lenList+1):
            #print(indexLenObj)
            updateListTable.append(listTable)
        print(updateListTable)        
        #for indexLists in updateListTable:
        #    for indexObject in indexLists:
        #        subLsts.append(indexObject)
        #print(subLsts)
    #mainList.append(subLsts)
    #mainList.append(updateListTable)
    #print(mainList)
    return mainList, subLsts, updateListTable, dfTable, lenObj, lenList, site
def funcMysqlPandas(fromExcel, df):
    conn = None
    listExcelLetters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR", "AS", "AT", "AU"]
    
    try:        
        # Установление соединения
        conn = mysql.connector.connect(
            host = settings.CONFIG_DATA.get("IPDBDJANGO"),
            user = settings.CONFIG_DATA.get("USERDBDJANGO"),
            passwd = settings.CONFIG_DATA.get("PASSWORDDBDJANGO"),
            database = settings.CONFIG_DATA.get("NAMEDBDJANGO"),
            #use_pure = True, # вместо С используем Python
        )
        if conn.is_connected():
            #print("Соединение с базой данных установлено успешно.")            
            # SQL-запрос, который мы хотим выполнить
            query = f"SELECT * FROM {fromExcel}"            
            # Использование pandas.read_sql_query для загрузки данных напрямую в DataFrame
            df = pd.read_sql_query(query, conn)
            df.columns = listExcelLetters[0:len(df.columns)]
            #print(f"\nДанные успешно загружены в DataFrame. Получено строк: {len(df)}")
    except Error as e:
        print(f"Ошибка при работе с MySQL: {e}")
    finally:
        # Закрытие соединения
        if conn is not None and conn.is_connected():
            conn.close()
            #print("Соединение с MySQL закрыто.")
    return fromExcel, df
def funcMysqlPandas3(df, dbQuerry, dbIp, dbUser, dbPasswd, dbName):
    conn = None
    listExcelLetters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL", "AM", "AN", "AO", "AP", "AQ", "AR", "AS", "AT", "AU"]

    try:
        # Установление соединения
        conn = mysql.connector.connect(
            host=dbIp,
            user=dbUser,
            passwd=dbPasswd,
            database=dbName,
            #use_pure=True,  # вместо С используем Python
        )
        if conn.is_connected():
            print("Соединение с базой данных установлено успешно.")
            # SQL-запрос, который мы хотим выполнить
            #testVar = "382663"
            query = dbQuerry
            #print(query)
            # Использование pandas.read_sql_query для загрузки данных напрямую в DataFrame
            df = pd.read_sql_query(query, conn)
            df.columns = listExcelLetters[0:len(df.columns)]
            # print(f"\nДанные успешно загружены в DataFrame. Получено строк: {len(df)}")
    except Error as e:
        print(f"Ошибка при работе с MySQL: {e}")
    finally:
        # Закрытие соединения
        if conn is not None and conn.is_connected():
            conn.close()
            # print("Соединение с MySQL закрыто.")
    return df, dbQuerry, dbIp, dbUser, dbPasswd, dbName
def funcFilterTables24G3G(col, table, g42, g3):
    copyCol=table[col]
    table.insert(0, "Site", copyCol)
    table["Site"] = table["Site"].str[:6]
    dfTemp1 = table.loc[table["Site"] == g42]
    dfTemp2 = table.loc[table["Site"] == g3]
    table = pd.concat([dfTemp1, dfTemp2])
    return col, table, g42, g3
def funcEricssonAddSublistSite(reg, numb, sublist, bb):
    numbFull = ""
    numbReg = ""
    timeUtc = ""
    timeMsw = ""
    ipPlan = ""
    subnetWork = ""
    satell = ""
    listLnhoif = []
    arfcnMin = 0
    arfcnMax = 0
    eArfcn = ""
    ruRegion = ""
    ipS1 = ""

    hostRdb = settings.CONFIG_DATA.get("HOSTRDB")
    sublist.append(reg)
    sublist.append(numb)

    numb, numbFull = funcCorrectNumbBS(numb, numbFull)
    reg, numbReg, listLnhoif, timeUtc, timeMsw, ipPlan, arfcnMin, arfcnMax, subnetWork, satell, eArfcn, ruRegion, ipS1 = funcCorrectRegBS(reg, numbReg, listLnhoif, timeUtc, timeMsw, ipPlan, arfcnMin, arfcnMax, subnetWork, satell, eArfcn, ruRegion, ipS1)

    sublist.append(numbFull)
    sublist.append(numbReg)
    sublist.append(numbReg+numbFull)
    sublist.append(reg+numbFull)
    sublist.append(reg+"00"+numbFull)
    sublist.append("https://"+hostRdb+"/p/list.aspx?op=list&k=c3a5t1r&v=c3a5ts5c1cs9r133&q="+reg+"00"+numbFull)

    sublist.append(numbFull[:0]+"3"+numbFull[0+1:])
    sublist.append(reg+(numbFull[:0]+"3"+numbFull[0+1:]))
    sublist.append(numbReg+(numbFull[:0]+"3"+numbFull[0+1:]))

    for indexLnhoif in listLnhoif:
        sublist.append(indexLnhoif)

    sublist.append(timeUtc)
    sublist.append(timeMsw)
    sublist.append(ipPlan)

    sublist.append(reg+numbFull+bb)
    sublist.append(reg+(str(int(numbFull)+3000))+bb)
    sublist.append("TCU_"+reg+numbFull)

    if ("-L" in bb) or ("-BL" in bb):
        bbUnit = 6620
        sublist.append(bbUnit)
    else:
        bbUnit = 6630
        sublist.append(bbUnit)

    sublist.append(str(int(numbFull)+3000))
    sublist.append(reg+(str(int(numbFull)+3000)))
    sublist.append(str(int(numbFull)+4000))
    sublist.append(reg+(str(int(numbFull)+4000)))

    sublist.append(str(arfcnMin))
    sublist.append(str(arfcnMax))
    sublist.append(subnetWork)
    sublist.append(bb)
    sublist.append(ruRegion)
    return reg, numb, sublist, bb
def funcEricssonRetList(reg, numb, bb, listForJson):
    listSite = []
    sublistSite = []

    reg, numb, sublistSite, bb = funcEricssonAddSublistSite(reg, numb, sublistSite, bb)
    listSite.append(sublistSite)
    listForJson.append(listSite)

    dfSheet, dfRet = funcMysqlPandas("ericsson_RET", pd.DataFrame())
    colDf, dfRet, sublistSite[5], sublistSite[9] = funcFilterTables24G3G("G", dfRet, sublistSite[5], sublistSite[9])
    #print(dfRet)
    
    dfRetBS = dfRet.reindex(columns=["G", "H", "K", "M", "S", "W"])
    dfRetBS["cols3"] = dfRetBS["S"].str[8:10]
    dfTemp1 = dfRetBS.loc[dfRetBS["cols3"] == "B1"]
    dfTemp2 = dfRetBS.loc[dfRetBS["cols3"] == "B2"]
    dfTemp3 = dfRetBS.loc[dfRetBS["cols3"] == "B3"]
    dfTemp4 = dfRetBS.loc[dfRetBS["cols3"] == "B4"]
    dfTemp5 = dfRetBS.loc[dfRetBS["cols3"] == "B5"]
    dfTemp6 = dfRetBS.loc[dfRetBS["cols3"] == "B6"]
    dfTemp1 = dfTemp1.rename(columns={"G":"GB1", "K":"KB1", "M":"MB1", "S":"SB1", "W":"WB1", "cols3":"cols3B1"})
    dfTemp2 = dfTemp2.rename(columns={"G":"GB2", "K":"KB2", "M":"MB2", "S":"SB2", "W":"WB2", "cols3":"cols3B2"})
    dfTemp3 = dfTemp3.rename(columns={"G":"GB3", "K":"KB3", "M":"MB3", "S":"SB3", "W":"WB3", "cols3":"cols3B3"})
    dfTemp4 = dfTemp4.rename(columns={"G":"GB4", "K":"KB4", "M":"MB4", "S":"SB4", "W":"WB4", "cols3":"cols3B4"})
    dfTemp5 = dfTemp5.rename(columns={"G":"GB5", "K":"KB5", "M":"MB5", "S":"SB5", "W":"WB5", "cols3":"cols3B5"})
    dfTemp6 = dfTemp6.rename(columns={"G":"GB6", "K":"KB6", "M":"MB6", "S":"SB6", "W":"WB6", "cols3":"cols3B6"})
    dfRetBS = pd.merge(dfTemp1, dfTemp2, left_on="H", right_on="H", how="outer")
    dfRetBS = pd.merge(dfRetBS, dfTemp3, left_on="H", right_on="H", how="outer")
    dfRetBS = pd.merge(dfRetBS, dfTemp4, left_on="H", right_on="H", how="outer")
    dfRetBS = pd.merge(dfRetBS, dfTemp5, left_on="H", right_on="H", how="outer")
    dfRetBS = pd.merge(dfRetBS, dfTemp6, left_on="H", right_on="H", how="outer")
    dfRetBS = dfRetBS.reindex(columns=["GB1", "H", "KB1", "MB1", "WB1", "KB2", "MB2", "WB2", "KB3", "MB3", "WB3", "KB4", "MB4", "WB4", "KB5", "MB5", "WB5", "KB6", "MB6", "WB6"])
    #print(dfRetBS)
    listForJson, sublistsTemp, listsTemp, dfRetBS, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(listForJson, [], [], dfRetBS, len(dfRetBS.columns), 0, sublistSite[5])
    listForJson.append(listsTemp)
    return reg, numb, bb, listForJson
def funcSort2Words(strSorting, strType, strName, strSubIndex):
    print(f"... Sorting list for objects: {strSorting}")
    strFilter = re.search(strSorting, strSubIndex, flags=re.IGNORECASE)
    if strFilter:
        #print("... Saving type in variables")
        strType = strFilter.group(0)
        #print("... Cut out the type")
        strName = re.sub(strSorting, "", strSubIndex, flags=re.IGNORECASE)
        #print("... Removing double spaces that may remain inside the line")
        strName = re.sub(r"\s+", " ", strName)
        #print("... Clearing the edges of the line from spaces and commas")
        strName = strName.strip(", ")
        print(f"+ Sort list: Type - {strType}, Name - {strName}")
        return strSorting, strType, strName, True
    return strSorting, strType, strName, False
# 2. СВЕРХБЫСТРАЯ ФУНКЦИЯ ОБРАБОТКИ АДРЕСА
def funcSort2Words2(address_str):
    if not address_str or not isinstance(address_str, str):
        return address_str
    parts = address_str.split(', ')
    new_parts = []
    for part in parts:
        if "\\" in part:
            new_parts.append(part)
            continue
        # Используем оператор присваивания := для скорости
        if m := RE_REGION.search(part):
            new_parts.append(f"{m.group(0)} {RE_SPACES.sub(' ', RE_REGION.sub('', part)).strip(', ')}")
        elif m := RE_RAYON.search(part):
            new_parts.append(f"{m.group(0)} {RE_SPACES.sub(' ', RE_RAYON.sub('', part)).strip(', ')}")
        elif m := RE_CITY.search(part):
            new_parts.append(f"{m.group(0)} {RE_SPACES.sub(' ', RE_CITY.sub('', part)).strip(', ')}")
        elif m := RE_VILLAGE.search(part):
            new_parts.append(f"{RE_SPACES.sub(' ', RE_VILLAGE.sub('', part)).strip(', ')} {m.group(0)}")
        elif m := RE_STREET.search(part):
            new_parts.append(f"{RE_SPACES.sub(' ', RE_STREET.sub('', part)).strip(', ')} {m.group(0)}")
        elif m := RE_TOWER.search(part):
            new_parts.append(f"{m.group(0)} {RE_SPACES.sub(' ', RE_TOWER.sub('', part)).strip(', ')}")
        elif m := RE_HOUSE.search(part):
            new_parts.append(f"{m.group(0)} {RE_SPACES.sub(' ', RE_HOUSE.sub('', part)).strip(', ')}")
        else:
            new_parts.append(part)
    return ", ".join(new_parts) if new_parts else address_str
def funcNokiaList(reg, numb, listForJson):
    listSite = []
    sublistSite = []

    listNumbers = list(range(1, 44))
    print(f"+ Add str objects data: {reg}, {numb}")

    reg, numb, sublistSite = funcNokiaAddSublistSite(reg, numb, sublistSite)
    #print(f"+ Add list sublistSite:\n {sublistSite}")
    listSite.append(sublistSite)
    listForJson.append(listSite)
    #print(f"+ Add list listForJson numeration 0:\n {listForJson}")

    # Запрашиваем из базы сразу первые 5 нужных колонок, чтобы не гонять лишний трафик
    strDbQuery = f"""
        SELECT * 
        FROM DjangoTemplate.FromDBTEST__site 
        WHERE `0_` = %s;
        """
    #print("... Executing the request")
    with connection.cursor() as cursor:
        cursor.execute(strDbQuery, [sublistSite[5]])  # Безопасная передача параметра
        rows = cursor.fetchall()
        listCols = [col[0] for col in cursor.description]
        #print(f"+ Add list listCols:\n {listCols}")
    dfSite = pd.DataFrame(rows, columns=listCols)
    #print(f"+ Add table dfSite:\n {dfSite}")
    if dfSite.empty:
        print(f"- Not founded BS {sublistSite[5]} in table FromDBTEST__site")
        return listForJson
    #print(f"... Correcting table dfSite")
    dfSite = dfSite.iloc[:, :5] # Обрезаем DataFrame до первых 5 колонок (так как далее вы переименовываете именно 5 полей). Может убрать?
    dfSite.columns = ["siteName", "siteType", "Address", "Status", "Plan"]
    dfSite["NewAddress"] = dfSite["Address"].apply(funcSort2Words2)
    dfSite = dfSite.reindex(columns=["siteName", "siteType", "NewAddress", "Status", "Plan"])
    dfSite["Region"] = sublistSite[3]
    dfSite["UTC"] = sublistSite[23]
    dfSite["MSW"] = sublistSite[24]
    dfSite["ipPlan"] = sublistSite[25]
    dfSite["Oblast"] = sublistSite[28]
    dfSite["ipS1"] = sublistSite[29]
    print(f"+ Correct table dfSite:\n {dfSite.to_string()}")
    listForJson, sublistsTemp, listsTemp, dfSite, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], dfSite, len(dfSite.columns), 0, sublistSite[5]
    )
    print(f"+ Add list listsTemp:\n {listsTemp}")
    listForJson.append(listsTemp)
    print(f"+ Correct list listForJson numeration 1:\n {listForJson}")

    '''# Готовим данные для фильтрации:
    print(sublistSite[9][2:])
    print(sublistSite[9])
    # Собираем данные из БД для таблиц dfWcel и Ran Data. dfWcel30000 необохимдо для объединяния таблицы с dfWcel40000
    strDbQuery30000 = f"""
            SELECT 
                    CONCAT('PLMN-PLMN/RNC-',b.`RNC`,'/WBTS-',b.`WBTS`,'/WCEL-',b.`WCEL`) AS dn,
                    e.`name`,
                    b.`LAC`,
                    e.`RAC`, e.`PriScrCode`, e.`UARFCN`, e.`URAId`, e.`Tcell`, e.`SectorID`,
                    -- Деление на 10.0 для получения дробного числа:
                    FORMAT(e.`PtxCellMax` / 10.0, 1) AS `PtxCellMax`, FORMAT(e.`PtxPrimaryCPICH` / 10.0, 1) AS `PtxPrimaryCPICH`,
                    -- Замена значений в столбце AdminCellState:
                    CASE b.`AdminCellState`
                        WHEN 1 THEN 'Unlocked'
                        WHEN 0 THEN 'Locked'
                        ELSE 'Unknown' -- на случай, если появится другое значение или NULL
                    END AS `AdminCellState`,    
                    -- SUBSTRING((CONCAT('PLMN-PLMN/RNC-',b.`RNC`,'/WBTS-',b.`WBTS`,'/WCEL-',b.`WCEL`)), LOCATE('RNC-', (CONCAT('PLMN-PLMN/RNC-',b.`RNC`,'/WBTS-',b.`WBTS`,'/WCEL-',b.`WCEL`))) + 4) AS R,
                    CASE 
                        WHEN e.`SectorID` IN ('3', '6', '9') THEN 3
                        WHEN e.`SectorID` IN ('2', '5', '8') THEN 2
                        WHEN e.`SectorID` IN ('1', '4', '7') THEN 1
                        ELSE 1
                    END AS S,
                    CASE b.`RNC`
                        WHEN '102' THEN 'RNCN-SAH102'
                        WHEN '28'  THEN 'RNCN-IRK028'
                        WHEN '120' THEN 'RNCN-IRK120'
                        WHEN '138' THEN 'RNCN-IRK138'
                        ELSE NULL -- Здесь можно указать '', если вместо NULL нужна пустая строка
                    END AS X,
                    CASE 
                        WHEN LEFT(e.`UARFCN`, 4) = '1056' THEN 1
                        WHEN LEFT(e.`UARFCN`, 4) = '1058' THEN 2
                        ELSE 3
                    END AS `SBTS 3G`    
                FROM config_Nokia3G_wcell.WCEL_begining b
                JOIN config_Nokia3G_wcell.WCEL_ending e 
                    ON b.`RNC` = e.`RNC` AND b.`WBTS` = e.`WBTS` AND b.`WCEL` = e.`SectorID` -- связка сектора и логического номера соты
                -- WHERE b.`WBTS` LIKE '%{sublistSite[9][2:]}%'
                WHERE e.`name` LIKE '%{sublistSite[9]}%' 
                  AND (b.`RNC` LIKE '%102%' OR b.`RNC` LIKE '%120%' OR b.`RNC` LIKE '%138%' OR b.`RNC` LIKE '%28%');
        """
    dfWcel30000, strDbQuery30000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery30000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    #print(dfWcel30000)
    # Корректируем таблицу
    copyCol = dfWcel30000["B"]
    dfWcel30000.insert(0, "Site", copyCol)
    dfWcel30000["Site"] = dfWcel30000["Site"].str[:6]
    print(f"+ Correct table dfWcel30000:\n {dfWcel30000.to_string()}")
    # Собираем данные из БД для таблиц dfBts и Ran Data.
    strDbQuery = f"""
            SELECT
                -- Блок изначального запроса BTS
                CONCAT('PLMN-PLMN/BSC-', b.`BSC`, '/BCF-', b.`BCF`, '/BTS-', b.`BTS`) AS dn,
                b.`BSC`, b.`BCF`, b.`BTS`, b.`nwName`, b.`sectorId`, b.`locationAreaIdLAC`, b.`rac`, b.`bsIdentityCodeBCC`, b.`bsIdentityCodeNCC`,
                CASE b.`frequencyBandInUse`
                    WHEN 1 THEN 'GSM 1800'
                    WHEN 0 THEN 'GSM 900'
                    ELSE 'Unknow'
                END AS frequencyBandName,
                CASE b.`hoppingMode`
                    WHEN 2 THEN 'SY'
                    WHEN 1 THEN 'BB'
                    WHEN 0 THEN 'Non'
                    ELSE 'Unknow'
                END AS hoppingMode,
                b.`hoppingSequenceNumber1`,
                CASE b.`usedMobileAllocation`
                    WHEN 0 THEN 'No MAL'
                    ELSE b.`usedMobileAllocation`
                END AS usedMobileAllocation,
                CASE b.`diversityUsed`
                    WHEN 1 THEN 'Y'
                    WHEN 0 THEN 'N'
                    ELSE 'Unknow'
                END AS diversityUsed,
                b.`maxGPRSCapacity`,
                CASE b.`adminState`
                    WHEN 1 THEN 'Unlocked'
                    WHEN 0 THEN 'Locked'
                    ELSE 'Unknow'
                END AS adminState,
                SUBSTRING((CONCAT('PLMN-PLMN/BSC-', b.`BSC`, '/BCF-', b.`BCF`, '/BTS-', b.`BTS`)), LOCATE('BSC-', (CONCAT('PLMN-PLMN/BSC-', b.`BSC`, '/BCF-', b.`BCF`, '/BTS-', b.`BTS`))) + 4) AS AA,
                SUBSTRING((CONCAT('PLMN-PLMN/BSC-', b.`BSC`, '/BCF-', b.`BCF`, '/BTS-', b.`BTS`)), LOCATE('BCF-', (CONCAT('PLMN-PLMN/BSC-', b.`BSC`, '/BCF-', b.`BCF`, '/BTS-', b.`BTS`))) + 4) AS AB,
                CONCAT(b.`BSC`, b.`BCF`) AS AC,
                CONCAT(b.`BSC`, LPAD(b.`BCF`, 4, '0'), LPAD(b.`BTS`, 4, '0')) AS SORT,
                SUBSTRING(b.`nwName`, 1, 6) AS AF,
                CASE b.`BSC`
                    WHEN 324697 THEN 'BSCN-NSK042'
                    WHEN 396402 THEN 'BSCN-IRK135'
                    WHEN 398453 THEN 'BSCN-SAH068'
                    WHEN 398471 THEN 'BSCN-MGD069'
                    WHEN 398493 THEN 'BSCN-KAM070'
                    WHEN 400877 THEN 'BSCN-IRK148'
                    WHEN 401255 THEN 'BSCN-IRK484'
                    WHEN 401256 THEN 'BSCN-IRK395'
                    WHEN 401257 THEN 'BSCN-IRK169'
                    WHEN 891018 THEN 'BSCN-BIR067'
                    WHEN 912222 THEN 'BSCN-KHB173'
                    WHEN 394228 THEN 'BSCN-KHB174'
                    WHEN 502308 THEN 'BSCN-IRK582'
                    ELSE 'Unknow'
                END AS AU,
                "Unknow" AS AY,
                -- СКОРРЕКТИРОВАННЫЕ СТОЛБЦЫ
                COALESCE(t_agg.AZ, 0) AS AZ,
                COALESCE(t_agg.BA, 0) AS BA,
                COALESCE(t_agg.initialFrequency, 0) AS TRX, -- Выводим частоту первого TRX, как в вашем условии
                ROW_NUMBER() OVER (
                    PARTITION BY SUBSTRING(b.`nwName`, 1, 6)
                    ORDER BY CONCAT(b.`BSC`, LPAD(b.`BCF`, 4, '0'), LPAD(b.`BTS`, 4, '0'))
                ) AS BE    
            FROM config_Nokia2G.BTS b
            LEFT JOIN (
                SELECT 
                    `BSC`, `BCF`, `BTS`,
                    COUNT(`TRX`) AS AZ,
                    ROUND(AVG(`trxRfPower` / 1000), 0) AS BA,
                    -- Находим initialFrequency для TRX с минимальным номером внутри BTS
                    SUBSTRING_INDEX(GROUP_CONCAT(`initialFrequency` ORDER BY CAST(`TRX` AS UNSIGNED)), ',', 1) AS initialFrequency
                FROM config_Nokia2G.TRX
                GROUP BY `BSC`, `BCF`, `BTS`
            ) t_agg 
                ON b.`BSC` = t_agg.`BSC` 
                AND b.`BCF` = t_agg.`BCF` 
                AND b.`BTS` = t_agg.`BTS`
            WHERE b.`nwName` LIKE '%{sublistSite[5]}%' 
            ORDER BY b.`sectorId`;
        """
    dfBts, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print(f"+ Add table dfBts:\n {dfBts.to_string()}")
    # Собираем данные Bsc и Rnc для таблицы Ran Data.
    listBscName = [
        ip.strip() for ip in (settings.CONFIG_DATA.get("LISTBSCNAME")).replace("', '", ",").replace("'", "").split(',')
    ]
    listBscDn = [
        ip.strip() for ip in (settings.CONFIG_DATA.get("LISTBSCDN")).replace("', '", ",").replace("'", "").split(',')
    ]
    listBscOam = [
        ip.strip() for ip in (settings.CONFIG_DATA.get("LISTBSCOAM")).replace("', '", ",").replace("'", "").split(',')
    ]
    dfBscRncName = pd.DataFrame()
    dfBscRncName["BSC/RNCname"] = listBscName
    dfBscRncName["dn"] = listBscDn
    dfBscRncName["OAM"] = listBscOam
    #print(dfBscRncName)
    # Объединяем таблицы dfWcel30000 и dfBts
    dfTemp1 = dfWcel30000.reindex(columns=["Site", "N", "C", "D", "G"])
    dfTemp2 = dfBts.reindex(columns=["V", "W"])
    # print(dfTemp2)
    dfTemp1 = dfTemp1.head(1)
    dfTemp1["Numbers"] = listNumbers[:len(dfTemp1)]
    dfTemp2["Numbers"] = listNumbers[:len(dfTemp2)]
    # Собираем данные таблицы Ran Data.
    dfRanData = pd.merge(dfTemp1, dfTemp2, left_on="Numbers", right_on="Numbers", how="outer")
    dfRanData = pd.merge(dfRanData, dfBscRncName, left_on="N", right_on="BSC/RNCname", how="outer")
    dfRanData = dfRanData.dropna()
    dfRanData = pd.merge(dfRanData, dfBscRncName, left_on="W", right_on="BSC/RNCname", how="outer")
    dfRanData = dfRanData.dropna()
    # Корректируем таблицу
    dfRanData = dfRanData.reindex(columns=["N", "dn_x", "W", "dn_y", "C", "D", "G"])
    print(f"+ Correct table dfRanData:\n {dfRanData.to_string()}")
    # Собираем данные в JSON:
    listForJson, sublistsTemp, listsTemp, dfRanData, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson,[], [], dfRanData, len(dfRanData.columns),0, sublistSite[5]
    )
    listForJson.append(listsTemp)

    # Готовим данные для фильтрации:
    print(sublistSite[4])
    print(sublistSite[10])
    print(sublistSite[13])
    print(sublistSite[16])

    # Собираем данные из БД MRBTS для таблиц Duname.
    strDbQuery0000 = f"""
            SELECT MRBTS, localIpAddr 
            FROM config_Nokia4G_LNRELW.IPADDRESSV4 
            WHERE `MRBTS` LIKE '%{sublistSite[4]}%' 
            AND localIpAddr LIKE '10.%'
            ORDER BY localIpAddr DESC
            LIMIT 1;
            """
    strDbQuery3000 = f"""
            SELECT MRBTS, localIpAddr 
            FROM config_Nokia4G_LNRELW.IPADDRESSV4 
            WHERE `MRBTS` LIKE '%{sublistSite[10]}%' 
            AND localIpAddr LIKE '10.%'
            ORDER BY localIpAddr DESC
            LIMIT 1;
            """
    strDbQuery6000 = f"""
            SELECT MRBTS, localIpAddr 
            FROM config_Nokia4G_LNRELW.IPADDRESSV4 
            WHERE `MRBTS` LIKE '%{sublistSite[13]}%' 
            AND localIpAddr LIKE '10.%'
            ORDER BY localIpAddr DESC
            LIMIT 1;
            """
    strDbQuery4000 = f"""
            SELECT MRBTS, localIpAddr 
            FROM config_Nokia4G_LNRELW.IPADDRESSV4 
            WHERE `MRBTS` LIKE '%{sublistSite[16]}%' 
            AND localIpAddr LIKE '10.%'
            ORDER BY localIpAddr DESC
            LIMIT 1;
            """
    dfMrbts0000, strDbQuery0000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery0000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    dfMrbts3000, strDbQuery3000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery3000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    dfMrbts6000, strDbQuery6000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery6000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    dfMrbts4000, strDbQuery4000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery4000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    #print(dfMrbts0000)
    #print(dfMrbts3000)
    #print(dfMrbts6000)
    #print(dfMrbts4000)

    # Объединяем таблицы Mrbts
    dfMrbts = pd.concat([dfMrbts0000, dfMrbts3000])
    dfMrbts = pd.concat([dfMrbts, dfMrbts6000])
    dfMrbts = pd.concat([dfMrbts, dfMrbts4000])
    #print(dfMrbts)

    # Собираем данные из БД MRBTS для таблиц Duname.
    print(sublistSite[4])
    print(sublistSite[10])
    print(sublistSite[13])
    print(sublistSite[16])
    strDbQuery0000 = f"""
            SELECT 
                `MRBTS`, 
                -- `speedAndDuplex`, 
                -- CASE 
                --    WHEN speedAndDuplex='0' THEN '1000MBIT_FULL'
                --    WHEN speedAndDuplex='1' THEN '1000MBIT_FULL'
                --    WHEN speedAndDuplex='2' THEN '1000MBIT_FULL'
                --    WHEN speedAndDuplex='' THEN '1000MBIT_FULL'
                --    ELSE 'Unknow'
                -- END AS speedAndDuplex, 
                'Unknow' AS `speedAndDuplex`, -- Есть параметры 10GBIT_FULL, 100MBIT_HALF, 100MBIT_FULL. В Запросе они не учитываются. Необходимо изменить колонку speedAndDuplex.
                -- `connectorLabel`, 
                CASE 
                    WHEN connectorLabel='1' THEN 'EIF1'
                    WHEN connectorLabel='2' THEN 'EIF2'
                    WHEN connectorLabel='3' THEN 'EIF3'
                    WHEN connectorLabel='4' THEN 'EIF4'
                    WHEN connectorLabel='5' THEN 'EIF5'
                    ELSE 'Unknow'
                END AS connectorLabel
            FROM config_Nokia4G.ETHLK WHERE `MRBTS` LIKE '%{sublistSite[4]}%';
            """
    strDbQuery3000 = f"""
            SELECT 
                `MRBTS`, 
                -- `speedAndDuplex`, 
                -- CASE 
                --    WHEN speedAndDuplex='0' THEN '1000MBIT_FULL'
                --    WHEN speedAndDuplex='1' THEN '1000MBIT_FULL'
                --    WHEN speedAndDuplex='2' THEN '1000MBIT_FULL'
                --    WHEN speedAndDuplex='' THEN '1000MBIT_FULL'
                --    ELSE 'Unknow'
                -- END AS speedAndDuplex, 
                'Unknow' AS `speedAndDuplex`, -- Есть параметры 10GBIT_FULL, 100MBIT_HALF, 100MBIT_FULL. В Запросе они не учитываются. Необходимо изменить колонку speedAndDuplex.
                -- `connectorLabel`, 
                CASE 
                    WHEN connectorLabel='1' THEN 'EIF1'
                    WHEN connectorLabel='2' THEN 'EIF2'
                    WHEN connectorLabel='3' THEN 'EIF3'
                    WHEN connectorLabel='4' THEN 'EIF4'
                    WHEN connectorLabel='5' THEN 'EIF5'
                    ELSE 'Unknow'
                END AS connectorLabel
            FROM config_Nokia4G.ETHLK WHERE `MRBTS` LIKE '%{sublistSite[10]}%';
            """
    strDbQuery6000 = f"""
            SELECT 
                `MRBTS`, 
                -- `speedAndDuplex`, 
                -- CASE 
                --    WHEN speedAndDuplex='0' THEN '1000MBIT_FULL'
                --    WHEN speedAndDuplex='1' THEN '1000MBIT_FULL'
                --    WHEN speedAndDuplex='2' THEN '1000MBIT_FULL'
                --    WHEN speedAndDuplex='' THEN '1000MBIT_FULL'
                --    ELSE 'Unknow'
                -- END AS speedAndDuplex, 
                'Unknow' AS `speedAndDuplex`, -- Есть параметры 10GBIT_FULL, 100MBIT_HALF, 100MBIT_FULL. В Запросе они не учитываются. Необходимо изменить колонку speedAndDuplex.
                -- `connectorLabel`, 
                CASE 
                    WHEN connectorLabel='1' THEN 'EIF1'
                    WHEN connectorLabel='2' THEN 'EIF2'
                    WHEN connectorLabel='3' THEN 'EIF3'
                    WHEN connectorLabel='4' THEN 'EIF4'
                    WHEN connectorLabel='5' THEN 'EIF5'
                    ELSE 'Unknow'
                END AS connectorLabel
            FROM config_Nokia4G.ETHLK WHERE `MRBTS` LIKE '%{sublistSite[13]}%';
            """
    strDbQuery4000 = f"""
            SELECT 
                `MRBTS`, 
                -- `speedAndDuplex`, 
                -- CASE 
                --    WHEN speedAndDuplex='0' THEN '1000MBIT_FULL'
                --    WHEN speedAndDuplex='1' THEN '1000MBIT_FULL'
                --    WHEN speedAndDuplex='2' THEN '1000MBIT_FULL'
                --    WHEN speedAndDuplex='' THEN '1000MBIT_FULL'
                --    ELSE 'Unknow'
                -- END AS speedAndDuplex, 
                'Unknow' AS `speedAndDuplex`, -- Есть параметры 10GBIT_FULL, 100MBIT_HALF, 100MBIT_FULL. В Запросе они не учитываются. Необходимо изменить колонку speedAndDuplex.
                -- `connectorLabel`, 
                CASE 
                    WHEN connectorLabel='1' THEN 'EIF1'
                    WHEN connectorLabel='2' THEN 'EIF2'
                    WHEN connectorLabel='3' THEN 'EIF3'
                    WHEN connectorLabel='4' THEN 'EIF4'
                    WHEN connectorLabel='5' THEN 'EIF5'
                    ELSE 'Unknow'
                END AS connectorLabel
            FROM config_Nokia4G.ETHLK WHERE `MRBTS` LIKE '%{sublistSite[16]}%';
            """
    dfEthlk0000, strDbQuery0000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery0000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    dfEthlk3000, strDbQuery3000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery3000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    dfEthlk6000, strDbQuery6000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery6000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    dfEthlk4000, strDbQuery4000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery4000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    #print(dfEthlk0000)
    #print(dfEthlk3000)
    #print(dfEthlk6000)
    #print(dfEthlk4000)

    # Объединяем таблицы dfEthlk
    dfEthlk = pd.concat([dfEthlk0000, dfEthlk3000])
    dfEthlk = pd.concat([dfEthlk, dfEthlk6000])
    dfEthlk = pd.concat([dfEthlk, dfEthlk4000])
    #print(dfEthlk)

    # Объединяем таблицы dfEthlk и dfMrbts для получения таблицы dfDuName.
    dfMrbts["A"] = dfMrbts["A"].astype("float")  # Возможно нужно будет убрать после поправки таблицы dfEthlk. Поправка: кже добавил dfEthlk. можно проверить
    #print(dfMrbts)
    #print(dfEthlk)
    # Необходимо учесть момент что Базовая станция может не существовать. Обычно в этот момент проиходит ошибка из-за пустых таблиц.
    try:
        dfDuName = pd.merge(dfMrbts, dfEthlk, left_on="A", right_on="A", how="outer")
    except ValueError:
        # Возможно стоит условия в отдельные функции переделать
        if checkTable(dfMrbts) == True:
            print("- There is no data for BS " + sublistSite[5] + " in the table")
            #print(len(dfMrbts.columns))
            object = "0"
            lenObj = len(dfMrbts.columns)
            listTable = []
            for indexLenObj in range(0, lenObj):
                #print(indexLenObj)
                listTable.append(object)
            #print(listTable)
            dfMrbts.loc[len(dfMrbts)] = listTable
            #print(dfMrbts)
        if checkTable(dfEthlk) == True:
            print("- There is no data for BS " + sublistSite[5] + " in the table")
            #print(len(dfMrbts.columns))
            object = "0"
            lenObj = len(dfEthlk.columns)
            listTable = []
            for indexLenObj in range(0, lenObj):
                #print(indexLenObj)
                listTable.append(object)
            #print(listTable)
            dfEthlk.loc[len(dfMrbts)] = listTable
            #print(dfEthlk)
        dfDuName = pd.merge(dfMrbts, dfEthlk, left_on="A", right_on="A", how="outer")
    #print(dfDuName)

    # Корректируем таблицу dfDuName
    dfDuName = dfDuName.reindex(columns=["A", "B_x", "C", "B_y"])
    dfDuName["A"] = dfDuName["A"].astype("int64") # Возможно Стоит убрать типы.
    dfDuName["dn"] = "PLMN-PLMN/MRBTS-" + dfDuName["A"].astype(str) # Возможно проще это перевести в html. dfDuName["A"].astype(str) имеется. просто в html его добавить и остюащиеся элементы
    dfDuName["getRet"] = (
            "any::com.nokia.srbts:MRBTS [ instance() = '" + dfDuName["A"].astype(str) +
            "'] / descendant::com.nokia.srbts.eqm:RETU"
    ) # Возможно проще это перевести в html. dfDuName["A"].astype(str) имеется. просто в html его добавить и остюащиеся элементы
    #print(dfDuName)
    print("ВНИМАНИЕ! Неизвестный объект B_y. Некорректно отображается в БД")

    # Собираем данные в JSON:
    listForJson, sublistsTemp, listsTemp, dfDuName, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], dfDuName, len(dfDuName.columns), 0, sublistSite[5]
    )
    listForJson.append(listsTemp)

    # Готовим данные для фильтрации:
    print(sublistSite)
    print(sublistSite[0])
    print(sublistSite[2])
    print(sublistSite[5])

    # Собираем данные из БД для таблицы df2gHwData:
    strDbQuery = f"""
            SELECT
                r.reg AS Reg,
                u.BSC, u.BCF, u.HW, u.SUBRACK, u.UNIT, u.unitType, u.serialNumber, u.identificationCode,
                CONCAT(LEFT(u.UNIT, 4), RIGHT(u.UNIT, 2)) AS J,
                CONCAT('BSC-', u.BSC, '/BCF-', u.BCF, (CONCAT(LEFT(u.UNIT, 4), RIGHT(u.UNIT, 2)))) AS K
            FROM config_Nokia4G.UNIT u
            JOIN (
                SELECT 'BI' AS reg, '891018' AS bsc_id UNION ALL
                SELECT 'IR', '28'     UNION ALL
                SELECT 'IR', '120'    UNION ALL
                SELECT 'IR', '396402' UNION ALL
                SELECT 'IR', '400877' UNION ALL
                SELECT 'IR', '401257' UNION ALL
                SELECT 'IR', '401256' UNION ALL
                SELECT 'IR', '401255' UNION ALL
                SELECT 'IR', '502308' UNION ALL
                SELECT 'IO', '396402' UNION ALL
                SELECT 'IO', '400877' UNION ALL
                SELECT 'IO', '401257' UNION ALL
                SELECT 'IO', '401256' UNION ALL
                SELECT 'IO', '401255' UNION ALL
                SELECT 'IO', '502308' UNION ALL
                SELECT 'KM', '398493' UNION ALL
                SELECT 'HB', '912222' UNION ALL
                SELECT 'HB', '394228' UNION ALL
                SELECT 'MD', '398471' UNION ALL
                SELECT 'MD', '324697' UNION ALL
                SELECT 'SA', '398453' UNION ALL
                SELECT 'SA', '102'
            ) r ON u.BSC = r.bsc_id
            WHERE u.BCF LIKE '%{sublistSite[2]}%' 
              AND r.reg = '{sublistSite[0]}'; -- Укажите нужный регион здесь (BI, IR, KM, HB, MD, SA)
        """
    df2gHwData, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    #print(df2gHwData)

    # Собираем данные в JSON:
    listForJson, sublistsTemp, listsTemp, df2gHwData, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], df2gHwData, len(df2gHwData.columns),0, sublistSite[5]
    )
    listForJson.append(listsTemp)

    # Готовим данные для фильтрации. в нашем случае - mrbts:
    print(sublistSite[4])
    print(sublistSite[10])
    print(sublistSite[13])
    print(sublistSite[16])

    # Собираем данные из БД для таблицы MRBTS Connetction Map:
    strDbQuery0000 = f"""SELECT 
                    ROW_NUMBER() OVER (ORDER BY main_data.AX, main_data.dn) AS T,
                    main_data.*,
                    CAST(CONCAT(main_data.MRBTS, ROW_NUMBER() OVER (ORDER BY AX, dn)) AS CHAR) AS AI,
                    CASE
                        WHEN main_data.U IS NULL AND (
                            CASE
                                WHEN main_data.U = 'FSMF' THEN 
                                    CONCAT(main_data.AC, IFNULL(main_data.Q, ''))
                                WHEN main_data.U IN ('FBBC', 'ABIA') THEN 
                                    CONCAT(
                                        MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX,
                                        main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '.BB',
                                        main_data.AC, 
                                        IFNULL(main_data.Q, '')
                                    )            
                                WHEN U IN ('ASIB', 'ASIA') THEN 
                                    main_data.AC
                                ELSE ''
                            END
                        ) IS NULL THEN 'DU2G'
                        ELSE CONCAT_WS(
                            ' ',
                            main_data.U,
                            (
                            CASE
                                WHEN main_data.U = 'FSMF' THEN 
                                    CONCAT(main_data.AC, IFNULL(main_data.Q, ''))
                                WHEN main_data.U IN ('FBBC', 'ABIA') THEN 
                                    CONCAT(
                                        MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX, 
                                        main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '.BB', 
                                        main_data.AC, 
                                        IFNULL(main_data.Q, ''))
                                WHEN main_data.U IN ('ASIB', 'ASIA') THEN 
                                    main_data.AC
                                ELSE ''
                            END
                            )
                        )
                    END AS AJ,
                    CONCAT(
                        main_data.W,
                        ' ',
                        (CASE 
                            WHEN main_data.W IN ('ABIA', 'FBBC', 'FBBA') THEN 
                                CONCAT(
                                    MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX, main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
                                    '.BB',
                                    main_data.AH,
                                    IFNULL(main_data.R, ''))
                            ELSE 
                                CONCAT(main_data.AH, IFNULL(main_data.R, ''))
                        END)
                    ) AS AK,
                    MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX, main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS AW
                FROM (
                    SELECT 
                        templateCablink.dn,
                        templateCablink.fiberLength,
                        templateCablink.linkCapacity,
                        templateCablink.linkSpeed,
                        templateCablink.firstEndpointDN,
                        templateCablink.secondEndpointDN,
                        templateHwsran1.cabinet AS I,
                        templateHwsran2.cabinet AS J,
                        templateHwsran1.smod AS K,
                        templateHwsran2.smod AS L,
                        templateHwsran1.bbmod AS M,
                        templateHwsran2.bbmod AS N,
                        templateHwsran1.rmod AS O,
                        templateHwsran2.rmod AS P,
                        templateCablink.Q,
                        templateCablink.R,
                        templateCablink.MRBTS,
                        templateHwsran1.AL AS U,
                        templateHwsran2.AL AS W,
                        CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END AS Y,
                        CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END AS Z,
                        CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) AS AA,
                        templateCablink.AB,
                        CONCAT(
                            ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END ),
                            ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END ),
                            ( CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) )
                        ) AS AC,
                        CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END AS AD,
                        CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END AS AE,
                        CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) AS AF,
                        templateCablink.AG,    
                        CONCAT(
                            ( CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END ), 
                            ( CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END ), 
                            ( CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) )
                        ) AS AH,
                        templateHwsran2.AM AS AN,
                        templateHwsran2.serialNumber AS AO,
                        CASE 
                            WHEN ( templateHwsran2.AL ) = 'FSMF' THEN ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                            WHEN ( templateHwsran1.AL ) IN ('FBBC', 'FBBA') THEN '3'
                            ELSE ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                        END AS AR,
                        CASE 
                            WHEN templateHwsran1.AL = 'ABIA' THEN (
                                CONCAT(
                                    ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END ),
                                    ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END ),
                                    ( CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) )
                                )
                            )
                            WHEN templateHwsran2.AL = 'ABIA' THEN (
                                CONCAT(
                                    ( CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END ), 
                                    ( CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END ), 
                                    ( CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) )
                                )
                            )
                            ELSE ''
                        END AS 'AS',
                        CASE WHEN templateHwsran2.AL IN ('ABIA', 'FSMF', 'FBBC', 'FBBA') THEN '0' ELSE templateCablink.firstEndpointPortId END AS 'AT',
                        CASE
                            WHEN ( templateHwsran1.AL ) = 'FSMF' THEN ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                            ELSE ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END )
                        END AS AV,
                        CONCAT(
                            templateCablink.MRBTS, 
                            ( CASE 
                                WHEN ( templateHwsran2.AL ) = 'FSMF' THEN ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                WHEN ( templateHwsran1.AL ) IN ('FBBC', 'FBBA') THEN '3'
                                ELSE ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                            END ), 
                            ( CASE 
                                WHEN templateHwsran1.AL = 'ABIA' THEN (
                                    CONCAT(
                                        ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END ),
                                        ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END ),
                                        ( CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) )
                                    )
                                )
                                WHEN templateHwsran2.AL = 'ABIA' THEN (
                                    CONCAT(
                                        ( CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END ), 
                                        ( CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END ), 
                                        ( CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) )
                                    )
                                )
                                ELSE ''
                            END ), 
                            ( CASE WHEN templateHwsran2.AL IN ('ABIA', 'FSMF', 'FBBC', 'FBBA') THEN '0' ELSE templateCablink.firstEndpointPortId END )
                        ) AS AX
                    FROM (
                        -- Базовая таблица CABLINK
                        SELECT
                            MRBTS,linkSpeed,firstEndpointDN,secondEndpointDN,firstEndpointPortId,secondEndpointPortId,linkMaxPhysicalCapacity,
                            CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/HWTOP_R-',HWTOP_R,'/CABLINK_R-',CABLINK_R) AS dn,
                            IF(fiberLength>0,ROUND(fiberLength/100,0),fiberLength) AS fiberLength,		
                            IF(linkMaxPhysicalCapacity='','',CONCAT('.',firstEndpointPortId)) AS Q,
                            IF(linkMaxPhysicalCapacity='','',CONCAT('.',secondEndpointPortId)) AS R,
                            IF(linkMaxPhysicalCapacity='' OR linkMaxPhysicalCapacity IS NULL,0,firstEndpointPortId) AS AB,
                            IF(linkMaxPhysicalCapacity='' OR linkMaxPhysicalCapacity IS NULL,'',secondEndpointPortId) AS AG,
                            IF(linkMaxPhysicalCapacity=0 OR linkMaxPhysicalCapacity IS NULL,'',CAST(linkMaxPhysicalCapacity AS SIGNED)) AS linkCapacity
                        FROM config_Nokia4G_REL.CABLINK_R
                        -- WHERE MRBTS LIKE '%382663%'
                    ) AS templateCablink
                    -- Первый джойн для firstEndpointDN
                    LEFT JOIN (
                        SELECT 
                            dn, cabinet, smod, bbmod, rmod, AL, AM, serialNumber 
                        FROM (
                            SELECT 
                                serialNumber,
                                CASE 
                                    WHEN configDN LIKE '%BBMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/BBMOD_R-',BBMOD_R)
                                    WHEN configDN LIKE '%RMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/RMOD_R-',RMOD_R)
                                    WHEN configDN LIKE '%SMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/SMOD_R-',SMOD_R)
                                END AS dn,
                                -- ABS(RIGHT(configDN, 2)) AS AP,
                                REGEXP_REPLACE(REGEXP_SUBSTR(configDN,'CABINET[^0-9]+[0-9]+'),'[^0-9]','') AS cabinet,
                                IF(configDN LIKE '%SMOD%',ABS(SUBSTR(configDN,LOCATE('SMOD',configDN)+4)),'') AS smod,
                                IF(configDN LIKE '%BBMOD%',ABS(SUBSTR(configDN,LOCATE('BBMOD',configDN)+5)),'') AS bbmod,
                                IF(configDN LIKE '%RMOD%',ABS(SUBSTR(configDN,LOCATE('RMOD',configDN)+4)),'') AS rmod,
                                CASE WHEN productName LIKE '%mmon' OR productName LIKE '%city' THEN LEFT(productName,4) ELSE RIGHT(productName,4) END AS AL,
                                AM
                            FROM (
                                SELECT 
                                    MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,BBMOD_R, 
                                    NULL AS RMOD_R, NULL AS SMOD_R,productName,'||||' AS AM
                                FROM config_Nokia4G.BBMOD_R
                                -- WHERE MRBTS LIKE '%382663%'
                                UNION ALL SELECT
                                    MRBTS,serialNumber,configDN,EQM_R,APEQM_R,
                                    NULL,NULL,RMOD_R,NULL,productName, 
                                    CONCAT('|',REPLACE(SUBSTRING_INDEX(activeGsmCellsList,'-',3),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeLteCellsList,'-',6),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeWcdmaCellsList,'-',9),'-',''),'|') AS AM 
                                FROM config_Nokia4G_REL.RMOD_R
                                -- WHERE MRBTS LIKE '%382663%'
                                UNION ALL SELECT
                                    MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,
                                    NULL,NULL,SMOD_R,productName,'||||' AS AM
                                FROM config_Nokia4G_REL.SMOD_R
                                -- WHERE MRBTS LIKE '%382663%'
                            ) AS hwsran1
                        ) AS hwsran2
                    ) AS templateHwsran1 ON CONCAT('PLMN-PLMN/', templateCablink.firstEndpointDN) = templateHwsran1.dn
                    -- Второй джойн для secondEndpointDN
                    LEFT JOIN (
                        SELECT 
                            dn, cabinet, smod, bbmod, rmod, AL, AM, serialNumber 
                        FROM (
                            SELECT 
                                serialNumber,
                                CASE 
                                    WHEN configDN LIKE '%BBMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/BBMOD_R-',BBMOD_R)
                                    WHEN configDN LIKE '%RMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/RMOD_R-',RMOD_R)
                                    WHEN configDN LIKE '%SMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/SMOD_R-',SMOD_R)
                                END AS dn,
                                -- ABS(RIGHT(configDN, 2)) AS AP,
                                REGEXP_REPLACE(REGEXP_SUBSTR(configDN,'CABINET[^0-9]+[0-9]+'),'[^0-9]','') AS cabinet,
                                IF(configDN LIKE '%SMOD%',ABS(SUBSTR(configDN,LOCATE('SMOD',configDN)+4)),'') AS smod,
                                IF(configDN LIKE '%BBMOD%',ABS(SUBSTR(configDN,LOCATE('BBMOD',configDN)+5)),'') AS bbmod,
                                IF(configDN LIKE '%RMOD%',ABS(SUBSTR(configDN,LOCATE('RMOD',configDN)+4)),'') AS rmod,
                                CASE WHEN productName LIKE '%mmon' OR productName LIKE '%city' THEN LEFT(productName,4) ELSE RIGHT(productName,4) END AS AL,
                                AM            
                            FROM (
                                SELECT 
                                    MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,BBMOD_R, 
                                    NULL AS RMOD_R, NULL AS SMOD_R,productName,'||||' AS AM
                                FROM config_Nokia4G.BBMOD_R
                                -- WHERE MRBTS LIKE '%382663%'
                                UNION ALL SELECT
                                    MRBTS,serialNumber,configDN,EQM_R,APEQM_R,
                                    NULL,NULL,RMOD_R,NULL,productName, 
                                    CONCAT('|',REPLACE(SUBSTRING_INDEX(activeGsmCellsList,'-',3),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeLteCellsList,'-',6),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeWcdmaCellsList,'-',9),'-',''),'|') AS AM 
                                FROM config_Nokia4G_REL.RMOD_R
                                -- WHERE MRBTS LIKE '%382663%'
                                UNION ALL SELECT
                                    MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,
                                    NULL,NULL,SMOD_R,productName,'||||' AS AM
                                FROM config_Nokia4G_REL.SMOD_R   
                                -- WHERE MRBTS LIKE '%382663%'
                            ) AS hwsran1
                        ) AS hwsran2
                    ) AS templateHwsran2 ON CONCAT('PLMN-PLMN/', templateCablink.secondEndpointDN) = templateHwsran2.dn
                    WHERE templateCablink.MRBTS LIKE '%{sublistSite[4]}%'
                ) AS main_data
                ORDER BY main_data.AX, main_data.dn;"""
    strDbQuery3000 = f"""SELECT 
                        ROW_NUMBER() OVER (ORDER BY main_data.AX, main_data.dn) AS T,
                        main_data.*,
                        CAST(CONCAT(main_data.MRBTS, ROW_NUMBER() OVER (ORDER BY AX, dn)) AS CHAR) AS AI,
                        CASE
                            WHEN main_data.U IS NULL AND (
                                CASE
                                    WHEN main_data.U = 'FSMF' THEN 
                                        CONCAT(main_data.AC, IFNULL(main_data.Q, ''))
                                    WHEN main_data.U IN ('FBBC', 'ABIA') THEN 
                                        CONCAT(
                                            MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX,
                                            main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '.BB',
                                            main_data.AC, 
                                            IFNULL(main_data.Q, '')
                                        )            
                                    WHEN U IN ('ASIB', 'ASIA') THEN 
                                        main_data.AC
                                    ELSE ''
                                END
                            ) IS NULL THEN 'DU2G'
                            ELSE CONCAT_WS(
                                ' ',
                                main_data.U,
                                (
                                CASE
                                    WHEN main_data.U = 'FSMF' THEN 
                                        CONCAT(main_data.AC, IFNULL(main_data.Q, ''))
                                    WHEN main_data.U IN ('FBBC', 'ABIA') THEN 
                                        CONCAT(
                                            MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX, 
                                            main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '.BB', 
                                            main_data.AC, 
                                            IFNULL(main_data.Q, ''))
                                    WHEN main_data.U IN ('ASIB', 'ASIA') THEN 
                                        main_data.AC
                                    ELSE ''
                                END
                                )
                            )
                        END AS AJ,
                        CONCAT(
                            main_data.W,
                            ' ',
                            (CASE 
                                WHEN main_data.W IN ('ABIA', 'FBBC', 'FBBA') THEN 
                                    CONCAT(
                                        MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX, main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
                                        '.BB',
                                        main_data.AH,
                                        IFNULL(main_data.R, ''))
                                ELSE 
                                    CONCAT(main_data.AH, IFNULL(main_data.R, ''))
                            END)
                        ) AS AK,
                        MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX, main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS AW
                    FROM (
                        SELECT 
                            templateCablink.dn,
                            templateCablink.fiberLength,
                            templateCablink.linkCapacity,
                            templateCablink.linkSpeed,
                            templateCablink.firstEndpointDN,
                            templateCablink.secondEndpointDN,
                            templateHwsran1.cabinet AS I,
                            templateHwsran2.cabinet AS J,
                            templateHwsran1.smod AS K,
                            templateHwsran2.smod AS L,
                            templateHwsran1.bbmod AS M,
                            templateHwsran2.bbmod AS N,
                            templateHwsran1.rmod AS O,
                            templateHwsran2.rmod AS P,
                            templateCablink.Q,
                            templateCablink.R,
                            templateCablink.MRBTS,
                            templateHwsran1.AL AS U,
                            templateHwsran2.AL AS W,
                            CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END AS Y,
                            CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END AS Z,
                            CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) AS AA,
                            templateCablink.AB,
                            CONCAT(
                                ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END ),
                                ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END ),
                                ( CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) )
                            ) AS AC,
                            CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END AS AD,
                            CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END AS AE,
                            CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) AS AF,
                            templateCablink.AG,    
                            CONCAT(
                                ( CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END ), 
                                ( CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END ), 
                                ( CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) )
                            ) AS AH,
                            templateHwsran2.AM AS AN,
                            templateHwsran2.serialNumber AS AO,
                            CASE 
                                WHEN ( templateHwsran2.AL ) = 'FSMF' THEN ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                WHEN ( templateHwsran1.AL ) IN ('FBBC', 'FBBA') THEN '3'
                                ELSE ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                            END AS AR,
                            CASE 
                                WHEN templateHwsran1.AL = 'ABIA' THEN (
                                    CONCAT(
                                        ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END ),
                                        ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END ),
                                        ( CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) )
                                    )
                                )
                                WHEN templateHwsran2.AL = 'ABIA' THEN (
                                    CONCAT(
                                        ( CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END ), 
                                        ( CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END ), 
                                        ( CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) )
                                    )
                                )
                                ELSE ''
                            END AS 'AS',
                            CASE WHEN templateHwsran2.AL IN ('ABIA', 'FSMF', 'FBBC', 'FBBA') THEN '0' ELSE templateCablink.firstEndpointPortId END AS 'AT',
                            CASE
                                WHEN ( templateHwsran1.AL ) = 'FSMF' THEN ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                ELSE ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END )
                            END AS AV,
                            CONCAT(
                                templateCablink.MRBTS, 
                                ( CASE 
                                    WHEN ( templateHwsran2.AL ) = 'FSMF' THEN ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                    WHEN ( templateHwsran1.AL ) IN ('FBBC', 'FBBA') THEN '3'
                                    ELSE ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                END ), 
                                ( CASE 
                                    WHEN templateHwsran1.AL = 'ABIA' THEN (
                                        CONCAT(
                                            ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END ),
                                            ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END ),
                                            ( CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) )
                                        )
                                    )
                                    WHEN templateHwsran2.AL = 'ABIA' THEN (
                                        CONCAT(
                                            ( CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END ), 
                                            ( CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END ), 
                                            ( CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) )
                                        )
                                    )
                                    ELSE ''
                                END ), 
                                ( CASE WHEN templateHwsran2.AL IN ('ABIA', 'FSMF', 'FBBC', 'FBBA') THEN '0' ELSE templateCablink.firstEndpointPortId END )
                            ) AS AX
                        FROM (
                            -- Базовая таблица CABLINK
                            SELECT
                                MRBTS,linkSpeed,firstEndpointDN,secondEndpointDN,firstEndpointPortId,secondEndpointPortId,linkMaxPhysicalCapacity,
                                CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/HWTOP_R-',HWTOP_R,'/CABLINK_R-',CABLINK_R) AS dn,
                                IF(fiberLength>0,ROUND(fiberLength/100,0),fiberLength) AS fiberLength,		
                                IF(linkMaxPhysicalCapacity='','',CONCAT('.',firstEndpointPortId)) AS Q,
                                IF(linkMaxPhysicalCapacity='','',CONCAT('.',secondEndpointPortId)) AS R,
                                IF(linkMaxPhysicalCapacity='' OR linkMaxPhysicalCapacity IS NULL,0,firstEndpointPortId) AS AB,
                                IF(linkMaxPhysicalCapacity='' OR linkMaxPhysicalCapacity IS NULL,'',secondEndpointPortId) AS AG,
                                IF(linkMaxPhysicalCapacity=0 OR linkMaxPhysicalCapacity IS NULL,'',CAST(linkMaxPhysicalCapacity AS SIGNED)) AS linkCapacity
                            FROM config_Nokia4G_REL.CABLINK_R
                            -- WHERE MRBTS LIKE '%382663%'
                        ) AS templateCablink
                        -- Первый джойн для firstEndpointDN
                        LEFT JOIN (
                            SELECT 
                                dn, cabinet, smod, bbmod, rmod, AL, AM, serialNumber 
                            FROM (
                                SELECT 
                                    serialNumber,
                                    CASE 
                                        WHEN configDN LIKE '%BBMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/BBMOD_R-',BBMOD_R)
                                        WHEN configDN LIKE '%RMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/RMOD_R-',RMOD_R)
                                        WHEN configDN LIKE '%SMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/SMOD_R-',SMOD_R)
                                    END AS dn,
                                    -- ABS(RIGHT(configDN, 2)) AS AP,
                                    REGEXP_REPLACE(REGEXP_SUBSTR(configDN,'CABINET[^0-9]+[0-9]+'),'[^0-9]','') AS cabinet,
                                    IF(configDN LIKE '%SMOD%',ABS(SUBSTR(configDN,LOCATE('SMOD',configDN)+4)),'') AS smod,
                                    IF(configDN LIKE '%BBMOD%',ABS(SUBSTR(configDN,LOCATE('BBMOD',configDN)+5)),'') AS bbmod,
                                    IF(configDN LIKE '%RMOD%',ABS(SUBSTR(configDN,LOCATE('RMOD',configDN)+4)),'') AS rmod,
                                    CASE WHEN productName LIKE '%mmon' OR productName LIKE '%city' THEN LEFT(productName,4) ELSE RIGHT(productName,4) END AS AL,
                                    AM
                                FROM (
                                    SELECT 
                                        MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,BBMOD_R, 
                                        NULL AS RMOD_R, NULL AS SMOD_R,productName,'||||' AS AM
                                    FROM config_Nokia4G.BBMOD_R
                                    -- WHERE MRBTS LIKE '%382663%'
                                    UNION ALL SELECT
                                        MRBTS,serialNumber,configDN,EQM_R,APEQM_R,
                                        NULL,NULL,RMOD_R,NULL,productName, 
                                        CONCAT('|',REPLACE(SUBSTRING_INDEX(activeGsmCellsList,'-',3),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeLteCellsList,'-',6),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeWcdmaCellsList,'-',9),'-',''),'|') AS AM 
                                    FROM config_Nokia4G_REL.RMOD_R
                                    -- WHERE MRBTS LIKE '%382663%'
                                    UNION ALL SELECT
                                        MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,
                                        NULL,NULL,SMOD_R,productName,'||||' AS AM
                                    FROM config_Nokia4G_REL.SMOD_R
                                    -- WHERE MRBTS LIKE '%382663%'
                                ) AS hwsran1
                            ) AS hwsran2
                        ) AS templateHwsran1 ON CONCAT('PLMN-PLMN/', templateCablink.firstEndpointDN) = templateHwsran1.dn
                        -- Второй джойн для secondEndpointDN
                        LEFT JOIN (
                            SELECT 
                                dn, cabinet, smod, bbmod, rmod, AL, AM, serialNumber 
                            FROM (
                                SELECT 
                                    serialNumber,
                                    CASE 
                                        WHEN configDN LIKE '%BBMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/BBMOD_R-',BBMOD_R)
                                        WHEN configDN LIKE '%RMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/RMOD_R-',RMOD_R)
                                        WHEN configDN LIKE '%SMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/SMOD_R-',SMOD_R)
                                    END AS dn,
                                    -- ABS(RIGHT(configDN, 2)) AS AP,
                                    REGEXP_REPLACE(REGEXP_SUBSTR(configDN,'CABINET[^0-9]+[0-9]+'),'[^0-9]','') AS cabinet,
                                    IF(configDN LIKE '%SMOD%',ABS(SUBSTR(configDN,LOCATE('SMOD',configDN)+4)),'') AS smod,
                                    IF(configDN LIKE '%BBMOD%',ABS(SUBSTR(configDN,LOCATE('BBMOD',configDN)+5)),'') AS bbmod,
                                    IF(configDN LIKE '%RMOD%',ABS(SUBSTR(configDN,LOCATE('RMOD',configDN)+4)),'') AS rmod,
                                    CASE WHEN productName LIKE '%mmon' OR productName LIKE '%city' THEN LEFT(productName,4) ELSE RIGHT(productName,4) END AS AL,
                                    AM            
                                FROM (
                                    SELECT 
                                        MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,BBMOD_R, 
                                        NULL AS RMOD_R, NULL AS SMOD_R,productName,'||||' AS AM
                                    FROM config_Nokia4G.BBMOD_R
                                    -- WHERE MRBTS LIKE '%382663%'
                                    UNION ALL SELECT
                                        MRBTS,serialNumber,configDN,EQM_R,APEQM_R,
                                        NULL,NULL,RMOD_R,NULL,productName, 
                                        CONCAT('|',REPLACE(SUBSTRING_INDEX(activeGsmCellsList,'-',3),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeLteCellsList,'-',6),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeWcdmaCellsList,'-',9),'-',''),'|') AS AM 
                                    FROM config_Nokia4G_REL.RMOD_R
                                    -- WHERE MRBTS LIKE '%382663%'
                                    UNION ALL SELECT
                                        MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,
                                        NULL,NULL,SMOD_R,productName,'||||' AS AM
                                    FROM config_Nokia4G_REL.SMOD_R   
                                    -- WHERE MRBTS LIKE '%382663%'
                                ) AS hwsran1
                            ) AS hwsran2
                        ) AS templateHwsran2 ON CONCAT('PLMN-PLMN/', templateCablink.secondEndpointDN) = templateHwsran2.dn
                        WHERE templateCablink.MRBTS LIKE '%{sublistSite[10]}%'
                    ) AS main_data
                    ORDER BY main_data.AX, main_data.dn;"""
    strDbQuery6000 = f"""SELECT 
                        ROW_NUMBER() OVER (ORDER BY main_data.AX, main_data.dn) AS T,
                        main_data.*,
                        CAST(CONCAT(main_data.MRBTS, ROW_NUMBER() OVER (ORDER BY AX, dn)) AS CHAR) AS AI,
                        CASE
                            WHEN main_data.U IS NULL AND (
                                CASE
                                    WHEN main_data.U = 'FSMF' THEN 
                                        CONCAT(main_data.AC, IFNULL(main_data.Q, ''))
                                    WHEN main_data.U IN ('FBBC', 'ABIA') THEN 
                                        CONCAT(
                                            MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX,
                                            main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '.BB',
                                            main_data.AC, 
                                            IFNULL(main_data.Q, '')
                                        )            
                                    WHEN U IN ('ASIB', 'ASIA') THEN 
                                        main_data.AC
                                    ELSE ''
                                END
                            ) IS NULL THEN 'DU2G'
                            ELSE CONCAT_WS(
                                ' ',
                                main_data.U,
                                (
                                CASE
                                    WHEN main_data.U = 'FSMF' THEN 
                                        CONCAT(main_data.AC, IFNULL(main_data.Q, ''))
                                    WHEN main_data.U IN ('FBBC', 'ABIA') THEN 
                                        CONCAT(
                                            MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX, 
                                            main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '.BB', 
                                            main_data.AC, 
                                            IFNULL(main_data.Q, ''))
                                    WHEN main_data.U IN ('ASIB', 'ASIA') THEN 
                                        main_data.AC
                                    ELSE ''
                                END
                                )
                            )
                        END AS AJ,
                        CONCAT(
                            main_data.W,
                            ' ',
                            (CASE 
                                WHEN main_data.W IN ('ABIA', 'FBBC', 'FBBA') THEN 
                                    CONCAT(
                                        MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX, main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
                                        '.BB',
                                        main_data.AH,
                                        IFNULL(main_data.R, ''))
                                ELSE 
                                    CONCAT(main_data.AH, IFNULL(main_data.R, ''))
                            END)
                        ) AS AK,
                        MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX, main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS AW
                    FROM (
                        SELECT 
                            templateCablink.dn,
                            templateCablink.fiberLength,
                            templateCablink.linkCapacity,
                            templateCablink.linkSpeed,
                            templateCablink.firstEndpointDN,
                            templateCablink.secondEndpointDN,
                            templateHwsran1.cabinet AS I,
                            templateHwsran2.cabinet AS J,
                            templateHwsran1.smod AS K,
                            templateHwsran2.smod AS L,
                            templateHwsran1.bbmod AS M,
                            templateHwsran2.bbmod AS N,
                            templateHwsran1.rmod AS O,
                            templateHwsran2.rmod AS P,
                            templateCablink.Q,
                            templateCablink.R,
                            templateCablink.MRBTS,
                            templateHwsran1.AL AS U,
                            templateHwsran2.AL AS W,
                            CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END AS Y,
                            CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END AS Z,
                            CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) AS AA,
                            templateCablink.AB,
                            CONCAT(
                                ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END ),
                                ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END ),
                                ( CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) )
                            ) AS AC,
                            CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END AS AD,
                            CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END AS AE,
                            CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) AS AF,
                            templateCablink.AG,    
                            CONCAT(
                                ( CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END ), 
                                ( CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END ), 
                                ( CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) )
                            ) AS AH,
                            templateHwsran2.AM AS AN,
                            templateHwsran2.serialNumber AS AO,
                            CASE 
                                WHEN ( templateHwsran2.AL ) = 'FSMF' THEN ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                WHEN ( templateHwsran1.AL ) IN ('FBBC', 'FBBA') THEN '3'
                                ELSE ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                            END AS AR,
                            CASE 
                                WHEN templateHwsran1.AL = 'ABIA' THEN (
                                    CONCAT(
                                        ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END ),
                                        ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END ),
                                        ( CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) )
                                    )
                                )
                                WHEN templateHwsran2.AL = 'ABIA' THEN (
                                    CONCAT(
                                        ( CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END ), 
                                        ( CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END ), 
                                        ( CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) )
                                    )
                                )
                                ELSE ''
                            END AS 'AS',
                            CASE WHEN templateHwsran2.AL IN ('ABIA', 'FSMF', 'FBBC', 'FBBA') THEN '0' ELSE templateCablink.firstEndpointPortId END AS 'AT',
                            CASE
                                WHEN ( templateHwsran1.AL ) = 'FSMF' THEN ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                ELSE ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END )
                            END AS AV,
                            CONCAT(
                                templateCablink.MRBTS, 
                                ( CASE 
                                    WHEN ( templateHwsran2.AL ) = 'FSMF' THEN ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                    WHEN ( templateHwsran1.AL ) IN ('FBBC', 'FBBA') THEN '3'
                                    ELSE ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                END ), 
                                ( CASE 
                                    WHEN templateHwsran1.AL = 'ABIA' THEN (
                                        CONCAT(
                                            ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END ),
                                            ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END ),
                                            ( CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) )
                                        )
                                    )
                                    WHEN templateHwsran2.AL = 'ABIA' THEN (
                                        CONCAT(
                                            ( CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END ), 
                                            ( CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END ), 
                                            ( CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) )
                                        )
                                    )
                                    ELSE ''
                                END ), 
                                ( CASE WHEN templateHwsran2.AL IN ('ABIA', 'FSMF', 'FBBC', 'FBBA') THEN '0' ELSE templateCablink.firstEndpointPortId END )
                            ) AS AX
                        FROM (
                            -- Базовая таблица CABLINK
                            SELECT
                                MRBTS,linkSpeed,firstEndpointDN,secondEndpointDN,firstEndpointPortId,secondEndpointPortId,linkMaxPhysicalCapacity,
                                CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/HWTOP_R-',HWTOP_R,'/CABLINK_R-',CABLINK_R) AS dn,
                                IF(fiberLength>0,ROUND(fiberLength/100,0),fiberLength) AS fiberLength,		
                                IF(linkMaxPhysicalCapacity='','',CONCAT('.',firstEndpointPortId)) AS Q,
                                IF(linkMaxPhysicalCapacity='','',CONCAT('.',secondEndpointPortId)) AS R,
                                IF(linkMaxPhysicalCapacity='' OR linkMaxPhysicalCapacity IS NULL,0,firstEndpointPortId) AS AB,
                                IF(linkMaxPhysicalCapacity='' OR linkMaxPhysicalCapacity IS NULL,'',secondEndpointPortId) AS AG,
                                IF(linkMaxPhysicalCapacity=0 OR linkMaxPhysicalCapacity IS NULL,'',CAST(linkMaxPhysicalCapacity AS SIGNED)) AS linkCapacity
                            FROM config_Nokia4G_REL.CABLINK_R
                            -- WHERE MRBTS LIKE '%382663%'
                        ) AS templateCablink
                        -- Первый джойн для firstEndpointDN
                        LEFT JOIN (
                            SELECT 
                                dn, cabinet, smod, bbmod, rmod, AL, AM, serialNumber 
                            FROM (
                                SELECT 
                                    serialNumber,
                                    CASE 
                                        WHEN configDN LIKE '%BBMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/BBMOD_R-',BBMOD_R)
                                        WHEN configDN LIKE '%RMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/RMOD_R-',RMOD_R)
                                        WHEN configDN LIKE '%SMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/SMOD_R-',SMOD_R)
                                    END AS dn,
                                    -- ABS(RIGHT(configDN, 2)) AS AP,
                                    REGEXP_REPLACE(REGEXP_SUBSTR(configDN,'CABINET[^0-9]+[0-9]+'),'[^0-9]','') AS cabinet,
                                    IF(configDN LIKE '%SMOD%',ABS(SUBSTR(configDN,LOCATE('SMOD',configDN)+4)),'') AS smod,
                                    IF(configDN LIKE '%BBMOD%',ABS(SUBSTR(configDN,LOCATE('BBMOD',configDN)+5)),'') AS bbmod,
                                    IF(configDN LIKE '%RMOD%',ABS(SUBSTR(configDN,LOCATE('RMOD',configDN)+4)),'') AS rmod,
                                    CASE WHEN productName LIKE '%mmon' OR productName LIKE '%city' THEN LEFT(productName,4) ELSE RIGHT(productName,4) END AS AL,
                                    AM
                                FROM (
                                    SELECT 
                                        MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,BBMOD_R, 
                                        NULL AS RMOD_R, NULL AS SMOD_R,productName,'||||' AS AM
                                    FROM config_Nokia4G.BBMOD_R
                                    -- WHERE MRBTS LIKE '%382663%'
                                    UNION ALL SELECT
                                        MRBTS,serialNumber,configDN,EQM_R,APEQM_R,
                                        NULL,NULL,RMOD_R,NULL,productName, 
                                        CONCAT('|',REPLACE(SUBSTRING_INDEX(activeGsmCellsList,'-',3),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeLteCellsList,'-',6),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeWcdmaCellsList,'-',9),'-',''),'|') AS AM 
                                    FROM config_Nokia4G_REL.RMOD_R
                                    -- WHERE MRBTS LIKE '%382663%'
                                    UNION ALL SELECT
                                        MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,
                                        NULL,NULL,SMOD_R,productName,'||||' AS AM
                                    FROM config_Nokia4G_REL.SMOD_R
                                    -- WHERE MRBTS LIKE '%382663%'
                                ) AS hwsran1
                            ) AS hwsran2
                        ) AS templateHwsran1 ON CONCAT('PLMN-PLMN/', templateCablink.firstEndpointDN) = templateHwsran1.dn
                        -- Второй джойн для secondEndpointDN
                        LEFT JOIN (
                            SELECT 
                                dn, cabinet, smod, bbmod, rmod, AL, AM, serialNumber 
                            FROM (
                                SELECT 
                                    serialNumber,
                                    CASE 
                                        WHEN configDN LIKE '%BBMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/BBMOD_R-',BBMOD_R)
                                        WHEN configDN LIKE '%RMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/RMOD_R-',RMOD_R)
                                        WHEN configDN LIKE '%SMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/SMOD_R-',SMOD_R)
                                    END AS dn,
                                    -- ABS(RIGHT(configDN, 2)) AS AP,
                                    REGEXP_REPLACE(REGEXP_SUBSTR(configDN,'CABINET[^0-9]+[0-9]+'),'[^0-9]','') AS cabinet,
                                    IF(configDN LIKE '%SMOD%',ABS(SUBSTR(configDN,LOCATE('SMOD',configDN)+4)),'') AS smod,
                                    IF(configDN LIKE '%BBMOD%',ABS(SUBSTR(configDN,LOCATE('BBMOD',configDN)+5)),'') AS bbmod,
                                    IF(configDN LIKE '%RMOD%',ABS(SUBSTR(configDN,LOCATE('RMOD',configDN)+4)),'') AS rmod,
                                    CASE WHEN productName LIKE '%mmon' OR productName LIKE '%city' THEN LEFT(productName,4) ELSE RIGHT(productName,4) END AS AL,
                                    AM            
                                FROM (
                                    SELECT 
                                        MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,BBMOD_R, 
                                        NULL AS RMOD_R, NULL AS SMOD_R,productName,'||||' AS AM
                                    FROM config_Nokia4G.BBMOD_R
                                    -- WHERE MRBTS LIKE '%382663%'
                                    UNION ALL SELECT
                                        MRBTS,serialNumber,configDN,EQM_R,APEQM_R,
                                        NULL,NULL,RMOD_R,NULL,productName, 
                                        CONCAT('|',REPLACE(SUBSTRING_INDEX(activeGsmCellsList,'-',3),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeLteCellsList,'-',6),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeWcdmaCellsList,'-',9),'-',''),'|') AS AM 
                                    FROM config_Nokia4G_REL.RMOD_R
                                    -- WHERE MRBTS LIKE '%382663%'
                                    UNION ALL SELECT
                                        MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,
                                        NULL,NULL,SMOD_R,productName,'||||' AS AM
                                    FROM config_Nokia4G_REL.SMOD_R   
                                    -- WHERE MRBTS LIKE '%382663%'
                                ) AS hwsran1
                            ) AS hwsran2
                        ) AS templateHwsran2 ON CONCAT('PLMN-PLMN/', templateCablink.secondEndpointDN) = templateHwsran2.dn
                        WHERE templateCablink.MRBTS LIKE '%{sublistSite[13]}%'
                    ) AS main_data
                    ORDER BY main_data.AX, main_data.dn;"""
    strDbQuery4000 = f"""SELECT 
                            ROW_NUMBER() OVER (ORDER BY main_data.AX, main_data.dn) AS T,
                            main_data.*,
                            CAST(CONCAT(main_data.MRBTS, ROW_NUMBER() OVER (ORDER BY AX, dn)) AS CHAR) AS AI,
                            CASE
                                WHEN main_data.U IS NULL AND (
                                    CASE
                                        WHEN main_data.U = 'FSMF' THEN 
                                            CONCAT(main_data.AC, IFNULL(main_data.Q, ''))
                                        WHEN main_data.U IN ('FBBC', 'ABIA') THEN 
                                            CONCAT(
                                                MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX,
                                                main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '.BB',
                                                main_data.AC, 
                                                IFNULL(main_data.Q, '')
                                            )            
                                        WHEN U IN ('ASIB', 'ASIA') THEN 
                                            main_data.AC
                                        ELSE ''
                                    END
                                ) IS NULL THEN 'DU2G'
                                ELSE CONCAT_WS(
                                    ' ',
                                    main_data.U,
                                    (
                                    CASE
                                        WHEN main_data.U = 'FSMF' THEN 
                                            CONCAT(main_data.AC, IFNULL(main_data.Q, ''))
                                        WHEN main_data.U IN ('FBBC', 'ABIA') THEN 
                                            CONCAT(
                                                MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX, 
                                                main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), '.BB', 
                                                main_data.AC, 
                                                IFNULL(main_data.Q, ''))
                                        WHEN main_data.U IN ('ASIB', 'ASIA') THEN 
                                            main_data.AC
                                        ELSE ''
                                    END
                                    )
                                )
                            END AS AJ,
                            CONCAT(
                                main_data.W,
                                ' ',
                                (CASE 
                                    WHEN main_data.W IN ('ABIA', 'FBBC', 'FBBA') THEN 
                                        CONCAT(
                                            MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX, main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
                                            '.BB',
                                            main_data.AH,
                                            IFNULL(main_data.R, ''))
                                    ELSE 
                                        CONCAT(main_data.AH, IFNULL(main_data.R, ''))
                                END)
                            ) AS AK,
                            MAX(NULLIF(main_data.AV, '')) OVER (ORDER BY main_data.AX, main_data.dn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS AW
                        FROM (
                            SELECT 
                                templateCablink.dn,
                                templateCablink.fiberLength,
                                templateCablink.linkCapacity,
                                templateCablink.linkSpeed,
                                templateCablink.firstEndpointDN,
                                templateCablink.secondEndpointDN,
                                templateHwsran1.cabinet AS I,
                                templateHwsran2.cabinet AS J,
                                templateHwsran1.smod AS K,
                                templateHwsran2.smod AS L,
                                templateHwsran1.bbmod AS M,
                                templateHwsran2.bbmod AS N,
                                templateHwsran1.rmod AS O,
                                templateHwsran2.rmod AS P,
                                templateCablink.Q,
                                templateCablink.R,
                                templateCablink.MRBTS,
                                templateHwsran1.AL AS U,
                                templateHwsran2.AL AS W,
                                CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END AS Y,
                                CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END AS Z,
                                CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) AS AA,
                                templateCablink.AB,
                                CONCAT(
                                    ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END ),
                                    ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END ),
                                    ( CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) )
                                ) AS AC,
                                CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END AS AD,
                                CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END AS AE,
                                CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) AS AF,
                                templateCablink.AG,    
                                CONCAT(
                                    ( CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END ), 
                                    ( CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END ), 
                                    ( CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) )
                                ) AS AH,
                                templateHwsran2.AM AS AN,
                                templateHwsran2.serialNumber AS AO,
                                CASE 
                                    WHEN ( templateHwsran2.AL ) = 'FSMF' THEN ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                    WHEN ( templateHwsran1.AL ) IN ('FBBC', 'FBBA') THEN '3'
                                    ELSE ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                END AS AR,
                                CASE 
                                    WHEN templateHwsran1.AL = 'ABIA' THEN (
                                        CONCAT(
                                            ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END ),
                                            ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END ),
                                            ( CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) )
                                        )
                                    )
                                    WHEN templateHwsran2.AL = 'ABIA' THEN (
                                        CONCAT(
                                            ( CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END ), 
                                            ( CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END ), 
                                            ( CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) )
                                        )
                                    )
                                    ELSE ''
                                END AS 'AS',
                                CASE WHEN templateHwsran2.AL IN ('ABIA', 'FSMF', 'FBBC', 'FBBA') THEN '0' ELSE templateCablink.firstEndpointPortId END AS 'AT',
                                CASE
                                    WHEN ( templateHwsran1.AL ) = 'FSMF' THEN ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                    ELSE ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END )
                                END AS AV,
                                CONCAT(
                                    templateCablink.MRBTS, 
                                    ( CASE 
                                        WHEN ( templateHwsran2.AL ) = 'FSMF' THEN ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                        WHEN ( templateHwsran1.AL ) IN ('FBBC', 'FBBA') THEN '3'
                                        ELSE ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END )
                                    END ), 
                                    ( CASE 
                                        WHEN templateHwsran1.AL = 'ABIA' THEN (
                                            CONCAT(
                                                ( CASE WHEN templateHwsran1.AL IN ('FBBC', 'FBBA', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran1.cabinet END ),
                                                ( CASE WHEN templateHwsran1.AL = 'FSMF' THEN '' ELSE templateHwsran1.smod END ),
                                                ( CONCAT(templateHwsran1.bbmod,templateHwsran1.rmod) )
                                            )
                                        )
                                        WHEN templateHwsran2.AL = 'ABIA' THEN (
                                            CONCAT(
                                                ( CASE WHEN templateHwsran2.AL IN ('FBBA', 'FBBC', 'ABIA', 'ASIA', 'ASIB') THEN '' ELSE templateHwsran2.cabinet END ), 
                                                ( CASE WHEN templateHwsran2.AL = 'FSMF' THEN '' ELSE templateHwsran2.smod END ), 
                                                ( CONCAT(templateHwsran2.bbmod, templateHwsran2.rmod) )
                                            )
                                        )
                                        ELSE ''
                                    END ), 
                                    ( CASE WHEN templateHwsran2.AL IN ('ABIA', 'FSMF', 'FBBC', 'FBBA') THEN '0' ELSE templateCablink.firstEndpointPortId END )
                                ) AS AX
                            FROM (
                                -- Базовая таблица CABLINK
                                SELECT
                                    MRBTS,linkSpeed,firstEndpointDN,secondEndpointDN,firstEndpointPortId,secondEndpointPortId,linkMaxPhysicalCapacity,
                                    CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/HWTOP_R-',HWTOP_R,'/CABLINK_R-',CABLINK_R) AS dn,
                                    IF(fiberLength>0,ROUND(fiberLength/100,0),fiberLength) AS fiberLength,		
                                    IF(linkMaxPhysicalCapacity='','',CONCAT('.',firstEndpointPortId)) AS Q,
                                    IF(linkMaxPhysicalCapacity='','',CONCAT('.',secondEndpointPortId)) AS R,
                                    IF(linkMaxPhysicalCapacity='' OR linkMaxPhysicalCapacity IS NULL,0,firstEndpointPortId) AS AB,
                                    IF(linkMaxPhysicalCapacity='' OR linkMaxPhysicalCapacity IS NULL,'',secondEndpointPortId) AS AG,
                                    IF(linkMaxPhysicalCapacity=0 OR linkMaxPhysicalCapacity IS NULL,'',CAST(linkMaxPhysicalCapacity AS SIGNED)) AS linkCapacity
                                FROM config_Nokia4G_REL.CABLINK_R
                                -- WHERE MRBTS LIKE '%382663%'
                            ) AS templateCablink
                            -- Первый джойн для firstEndpointDN
                            LEFT JOIN (
                                SELECT 
                                    dn, cabinet, smod, bbmod, rmod, AL, AM, serialNumber 
                                FROM (
                                    SELECT 
                                        serialNumber,
                                        CASE 
                                            WHEN configDN LIKE '%BBMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/BBMOD_R-',BBMOD_R)
                                            WHEN configDN LIKE '%RMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/RMOD_R-',RMOD_R)
                                            WHEN configDN LIKE '%SMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/SMOD_R-',SMOD_R)
                                        END AS dn,
                                        -- ABS(RIGHT(configDN, 2)) AS AP,
                                        REGEXP_REPLACE(REGEXP_SUBSTR(configDN,'CABINET[^0-9]+[0-9]+'),'[^0-9]','') AS cabinet,
                                        IF(configDN LIKE '%SMOD%',ABS(SUBSTR(configDN,LOCATE('SMOD',configDN)+4)),'') AS smod,
                                        IF(configDN LIKE '%BBMOD%',ABS(SUBSTR(configDN,LOCATE('BBMOD',configDN)+5)),'') AS bbmod,
                                        IF(configDN LIKE '%RMOD%',ABS(SUBSTR(configDN,LOCATE('RMOD',configDN)+4)),'') AS rmod,
                                        CASE WHEN productName LIKE '%mmon' OR productName LIKE '%city' THEN LEFT(productName,4) ELSE RIGHT(productName,4) END AS AL,
                                        AM
                                    FROM (
                                        SELECT 
                                            MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,BBMOD_R, 
                                            NULL AS RMOD_R, NULL AS SMOD_R,productName,'||||' AS AM
                                        FROM config_Nokia4G.BBMOD_R
                                        -- WHERE MRBTS LIKE '%382663%'
                                        UNION ALL SELECT
                                            MRBTS,serialNumber,configDN,EQM_R,APEQM_R,
                                            NULL,NULL,RMOD_R,NULL,productName, 
                                            CONCAT('|',REPLACE(SUBSTRING_INDEX(activeGsmCellsList,'-',3),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeLteCellsList,'-',6),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeWcdmaCellsList,'-',9),'-',''),'|') AS AM 
                                        FROM config_Nokia4G_REL.RMOD_R
                                        -- WHERE MRBTS LIKE '%382663%'
                                        UNION ALL SELECT
                                            MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,
                                            NULL,NULL,SMOD_R,productName,'||||' AS AM
                                        FROM config_Nokia4G_REL.SMOD_R
                                        -- WHERE MRBTS LIKE '%382663%'
                                    ) AS hwsran1
                                ) AS hwsran2
                            ) AS templateHwsran1 ON CONCAT('PLMN-PLMN/', templateCablink.firstEndpointDN) = templateHwsran1.dn
                            -- Второй джойн для secondEndpointDN
                            LEFT JOIN (
                                SELECT 
                                    dn, cabinet, smod, bbmod, rmod, AL, AM, serialNumber 
                                FROM (
                                    SELECT 
                                        serialNumber,
                                        CASE 
                                            WHEN configDN LIKE '%BBMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/BBMOD_R-',BBMOD_R)
                                            WHEN configDN LIKE '%RMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/RMOD_R-',RMOD_R)
                                            WHEN configDN LIKE '%SMOD%' THEN CONCAT('PLMN-PLMN/MRBTS-',MRBTS,'/EQM_R-',EQM_R,'/APEQM_R-',APEQM_R,'/CABINET_R-',CABINET_R,'/SMOD_R-',SMOD_R)
                                        END AS dn,
                                        -- ABS(RIGHT(configDN, 2)) AS AP,
                                        REGEXP_REPLACE(REGEXP_SUBSTR(configDN,'CABINET[^0-9]+[0-9]+'),'[^0-9]','') AS cabinet,
                                        IF(configDN LIKE '%SMOD%',ABS(SUBSTR(configDN,LOCATE('SMOD',configDN)+4)),'') AS smod,
                                        IF(configDN LIKE '%BBMOD%',ABS(SUBSTR(configDN,LOCATE('BBMOD',configDN)+5)),'') AS bbmod,
                                        IF(configDN LIKE '%RMOD%',ABS(SUBSTR(configDN,LOCATE('RMOD',configDN)+4)),'') AS rmod,
                                        CASE WHEN productName LIKE '%mmon' OR productName LIKE '%city' THEN LEFT(productName,4) ELSE RIGHT(productName,4) END AS AL,
                                        AM            
                                    FROM (
                                        SELECT 
                                            MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,BBMOD_R, 
                                            NULL AS RMOD_R, NULL AS SMOD_R,productName,'||||' AS AM
                                        FROM config_Nokia4G.BBMOD_R
                                        -- WHERE MRBTS LIKE '%382663%'
                                        UNION ALL SELECT
                                            MRBTS,serialNumber,configDN,EQM_R,APEQM_R,
                                            NULL,NULL,RMOD_R,NULL,productName, 
                                            CONCAT('|',REPLACE(SUBSTRING_INDEX(activeGsmCellsList,'-',3),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeLteCellsList,'-',6),'-',''),'|',REPLACE(SUBSTRING_INDEX(activeWcdmaCellsList,'-',9),'-',''),'|') AS AM 
                                        FROM config_Nokia4G_REL.RMOD_R
                                        -- WHERE MRBTS LIKE '%382663%'
                                        UNION ALL SELECT
                                            MRBTS,serialNumber,configDN,EQM_R,APEQM_R,CABINET_R,
                                            NULL,NULL,SMOD_R,productName,'||||' AS AM
                                        FROM config_Nokia4G_REL.SMOD_R   
                                        -- WHERE MRBTS LIKE '%382663%'
                                    ) AS hwsran1
                                ) AS hwsran2
                            ) AS templateHwsran2 ON CONCAT('PLMN-PLMN/', templateCablink.secondEndpointDN) = templateHwsran2.dn
                            WHERE templateCablink.MRBTS LIKE '%{sublistSite[16]}%'
                        ) AS main_data
                        ORDER BY main_data.AX, main_data.dn;"""
    dfCablink0000, strDbQuery0000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery0000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    dfCablink3000, strDbQuery3000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery3000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    dfCablink6000, strDbQuery6000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery6000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    dfCablink4000, strDbQuery4000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery4000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    #print(dfCablink0000)
    #print(dfCablink3000)
    #print(dfCablink6000)
    #print(dfCablink4000)

    # Растягиваем таблицы до определенного количества строк. в нашем случаем мы должны получить 26 строк.
    dfCablink0000 = dfCablink0000.reindex(columns=["R", "A", "AM", "AN", "AF", "AE", "D", "C"])
    dfCablink3000 = dfCablink3000.reindex(columns=["R", "A", "AM", "AN", "AF", "AE", "D", "C"])
    dfCablink6000 = dfCablink6000.reindex(columns=["R", "A", "AM", "AN", "AF", "AE", "D", "C"])
    dfCablink4000 = dfCablink4000.reindex(columns=["R", "A", "AM", "AN", "AF", "AE", "D", "C"])
    listNumbers, dfNumbers = funcAddNumbers(listNumbers[0:26], pd.DataFrame())
    dfCablink0000 = pd.merge(dfNumbers, dfCablink0000, left_on="Numbers", right_on="A", how="outer")
    dfCablink3000 = pd.merge(dfNumbers, dfCablink3000, left_on="Numbers", right_on="A", how="outer")
    dfCablink6000 = pd.merge(dfNumbers, dfCablink6000, left_on="Numbers", right_on="A", how="outer")
    dfCablink4000 = pd.merge(dfNumbers, dfCablink4000, left_on="Numbers", right_on="A", how="outer")
    #print(dfCablink0000)
    #print(dfCablink3000)
    #print(dfCablink6000)
    #print(dfCablink4000)

    # Объединяем таблиц dfCablinkХ000:
    dfConnectionMap = pd.merge(dfCablink0000, dfCablink3000, left_on="Numbers", right_on="Numbers", how="outer")
    dfConnectionMap = pd.merge(dfConnectionMap, dfCablink6000, left_on="Numbers", right_on="Numbers", how="outer")
    #print(dfConnectionMap)
    # 1. Словарь для переименования колонок
    mapping = {
        "R_x": "B18", "AM_x": "B", "AN_x": "C", "AF_x": "D", "AE_x": "E", "D_x": "F", "C_x": "G", "R_y": "H18",
        "AM_y": "H", "AN_y": "I", "AF_y": "J", "AE_y": "K", "D_y": "L", "C_y": "M", "R": "N18", "AM": "N", "AN": "O",
        "AF": "P", "AE": "Q", "D": "R", "C": "S_20"
    }
    # 2. Переименовываем, задаем новый порядок и удаляем лишние (A_x, A_y, A)
    newOrder = [
        "B18", "B", "C", "D", "E", "F", "G", "H18", "H", "I", "J", "K", "L", "M", "N18","N", "O", "P", "Q", "R",
        "S_20", "Numbers"
    ]
    dfConnectionMap = dfConnectionMap.rename(columns=mapping).reindex(columns=newOrder)
    #print(dfConnectionMap)
    dfConnectionMap = pd.merge(dfConnectionMap, dfCablink4000, left_on="Numbers", right_on="Numbers", how="outer")
    #print(dfConnectionMap)
    # 1. Словарь для переименования только нужных колонок
    mapping = {
        "R_y": "T18", "AM": "T", "AN": "U", "AF": "V", "AE": "W"
    }
    # 2. Переименовываем и сразу выстраиваем в финальный порядок
    newOrder = [
        "Numbers", "B18", "B", "C_x", "D_x", "E", "F", "G", "H18", "H", "I", "J", "K", "L", "M", "N18", "N", "O", "P",
        "Q", "R_x", "S_20", "T18", "T", "U", "V", "W", "D_y", "C_y"
    ]
    dfConnectionMap = dfConnectionMap.rename(columns=mapping).reindex(columns=newOrder)
    #print(dfConnectionMap)

    # Собираем данные в JSON:
    listForJson, sublistsTemp, listsTemp, dfConnectionMap, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], dfConnectionMap, len(dfConnectionMap.columns), 18, sublistSite[5])
    listForJson.append(listsTemp)
    #print(listForJson)

    # Готовим данные для фильтрации:
    print(sublistSite[5])

    # Собираем данные из БД для таблицы dfBcf:
    strDbQuery = f"""
               SELECT 
                   `name`, `btsCuPlaneIpAddress`, `SBTSId`, `lapdLinkName`,
                   CASE `btsSiteSubtype`
                       WHEN 255 THEN 'ESMx' -- 'No BTS sub site or Flexi Multiradio BTS (F)'
                       WHEN 3 THEN 'FSMF' -- 'Flexi Multiradio 10 BTS (R)'
                       ELSE 'Unknow'
                   END AS btsSiteSubtype,
                   CASE `synchEnabled`
                       WHEN 1 THEN 'T' -- 'Synch enabled (T)'
                       WHEN 0 THEN 'F' -- 'Synch disabled (F)'
                       ELSE 'Unknow'
                   END AS synchEnabled,
                   SUBSTRING((CASE `clockSource`
                       WHEN 1 THEN 'LMU (location measurement unit)'
                       WHEN 0 THEN 'NONE (remove clock source)'
                       WHEN 3 THEN 'PCM (independent mode)'
                       WHEN 7 THEN 'TOP'
                       ELSE 'Unknow'
                   END), 1, 4) AS clockSource,
                   'Unknow' AS paSatelliteUse, 
                   'Unknow' AS OmuSig
               FROM config_Nokia2G.BCF WHERE `name` LIKE '%{sublistSite[5]}%';
           """
    dfBcf, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    #print(dfBcf)

    # Корректируем таблицы:
    dfTemp1 = dfBcf.reindex(
        columns=["A", "E", "B", "I", "F", "G", "H", "D", "C"]
    )
    dfTemp2 = dfBts.reindex(
        columns=["E", "B", "C", "D", "F", "G", "H", "I", "J", "K", "L", "N", "M", "O", "P", "Q", "A", "V", "AA"]
    )

    # Объединяем таблицы, для получения данных в таблице 2G:
    df2g = pd.merge(dfTemp2, dfTemp1, left_on="V", right_on="A", how="outer")
    df2g = df2g.reindex(
        columns=["E_x", "B_x", "E_y", "C_x", "B_y", "H_y", "F_y", "G_y", "I_y", "D_y", "C_y", "D_x", "F_x", "G_x",
                 "H_x", "I_x", "J", "K", "AA", "L", "N", "M", "O", "P", "Q", "A_x"]
    )
    #print(df2g)

    # Собираем данные в JSON:
    listForJson, sublistsTemp, listsTemp, df2g, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], df2g, len(df2g.columns),0, sublistSite[5]
    )
    listForJson.append(listsTemp)

    # Готовим данные для фильтрации:
    print(sublistSite[9][2:])
    print(sublistSite[15][2:])

    # Собираем данные из БД для таблицы dfWcel:
    strDbQuery40000 = f"""
                SELECT 
                        CONCAT('PLMN-PLMN/RNC-',b.`RNC`,'/WBTS-',b.`WBTS`,'/WCEL-',b.`WCEL`) AS dn,
                        e.`name`,
                        b.`LAC`,
                        e.`RAC`, e.`PriScrCode`, e.`UARFCN`, e.`URAId`, e.`Tcell`, e.`SectorID`,
                        -- Деление на 10.0 для получения дробного числа:
                        FORMAT(e.`PtxCellMax` / 10.0, 1) AS `PtxCellMax`, FORMAT(e.`PtxPrimaryCPICH` / 10.0, 1) AS `PtxPrimaryCPICH`,
                        -- Замена значений в столбце AdminCellState:
                        CASE b.`AdminCellState`
                            WHEN 1 THEN 'Unlocked'
                            WHEN 0 THEN 'Locked'
                            ELSE 'Unknown' -- на случай, если появится другое значение или NULL
                        END AS `AdminCellState`,    
                        -- SUBSTRING((CONCAT('PLMN-PLMN/RNC-',b.`RNC`,'/WBTS-',b.`WBTS`,'/WCEL-',b.`WCEL`)), LOCATE('RNC-', (CONCAT('PLMN-PLMN/RNC-',b.`RNC`,'/WBTS-',b.`WBTS`,'/WCEL-',b.`WCEL`))) + 4) AS R,
                        CASE 
                            WHEN e.`SectorID` IN ('3', '6', '9') THEN 3
                            WHEN e.`SectorID` IN ('2', '5', '8') THEN 2
                            WHEN e.`SectorID` IN ('1', '4', '7') THEN 1
                            ELSE 1
                        END AS S,
                        CASE b.`RNC`
                            WHEN '102' THEN 'RNCN-SAH102'
                            WHEN '28'  THEN 'RNCN-IRK028'
                            WHEN '120' THEN 'RNCN-IRK120'
                            WHEN '138' THEN 'RNCN-IRK138'
                            ELSE NULL -- Здесь можно указать '', если вместо NULL нужна пустая строка
                        END AS X,
                        CASE 
                            WHEN LEFT(e.`UARFCN`, 4) = '1056' THEN 1
                            WHEN LEFT(e.`UARFCN`, 4) = '1058' THEN 2
                            ELSE 3
                        END AS `SBTS 3G`    
                    FROM config_Nokia3G_wcell.WCEL_begining b
                    JOIN config_Nokia3G_wcell.WCEL_ending e 
                        ON b.`RNC` = e.`RNC` AND b.`WBTS` = e.`WBTS` AND b.`WCEL` = e.`SectorID` -- связка сектора и логического номера соты
                    -- WHERE b.`WBTS` LIKE '%{sublistSite[15][2:]}%' 
                    WHERE e.`name` LIKE '%{sublistSite[15]}%' 
                      AND (b.`RNC` LIKE '%102%' OR b.`RNC` LIKE '%120%' OR b.`RNC` LIKE '%138%' OR b.`RNC` LIKE '%28%');
            """
    dfWcel40000, strDbQuery40000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery40000,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )

    # Корректируем таблицы:
    copyCol = dfWcel40000["B"]
    dfWcel40000.insert(0, "Site", copyCol)
    dfWcel40000["Site"] = dfWcel40000["Site"].str[:6]

    # Объединяем таблицы, для получения данных в таблице 3G:
    dfWcel = pd.concat([dfWcel30000, dfWcel40000])
    dfWcel = dfWcel.reindex(columns=["Site", "B", "F", "E", "I", "C", "D", "G", "H", "J", "K", "L", "A"])
    #print(dfWcel)
    print("ВНИМАНИЕ! Необходимо поправить колонку tcell. Отличаются от excel. Возможно в sql запрос при задании колнки нужно поправить, в виде условий.")

    # Собираем данные в JSON:
    listForJson, sublistsTemp, listsTemp, dfWcel, lenObjs, lenList, sublistSite[9] = funcAddListFromTable(
        listForJson, [], [], dfWcel, len(dfWcel.columns), 0, sublistSite[9]
    )
    listForJson.append(listsTemp)

    # Готовим данные для фильтрации:
    print(sublistSite[4])
    print(sublistSite[17])
    print(sublistSite[18])
    print(sublistSite[19])
    print(sublistSite[20])
    print(sublistSite[21])
    print(sublistSite[22])

    # Собираем данные из БД для таблицы dfLncel:
    strDbQuery = f"""
        SELECT 
            CONCAT('PLMN-PLMN/MRBTS-', b.`MRBTS`, '/LNBTS-', b.`LNBTS`, '/LNCEL-', b.`LNCEL`) AS dn,
            -- b.MRBTS, b.LNBTS, b.LNCEL, 
            SUBSTRING_INDEX( b.cellName, '_', 1) AS SITE,
            b.`LNCEL`,
            b.cellName,
            b.eutraCelId, 
            rf.earfcnDL,    
            -- rf.dlChBw,
            CASE rf.`dlChBw`
                WHEN 50 THEN '5 MHz'
                WHEN 100 THEN '10 MHz'
                WHEN 150 THEN '15 MHz'
                WHEN 200 THEN '20 MHz'        
                ELSE 'Unknow'
            END AS dlChBw,
            e.tac,    
            -- e.pMax,
            FORMAT(e.`pMax` / 10.0, 1) AS `pMax`,
            e.phyCellId,
            rf.rootSeqIndex,
            -- rf.dlMimoMode,
            CASE rf.`dlMimoMode`
                WHEN 40 THEN 'Closed Loop Mimo'
                WHEN 41 THEN 'Closed Loop MIMO (4x2)'
                WHEN 43 THEN 'Closed Loop MIMO (4x4)'
                WHEN 0 THEN 'SingleTX'
                ELSE 'Unknow'
            END AS dlMimoMode,
            rf.prachCS,
            -- b.administrativeState
            CASE b.`administrativeState`
                WHEN 1 THEN 'Unlocked'
                WHEN 0 THEN 'Locked'
                ELSE 'Unknow'
            END AS administrativeState,
            ROUND(POW(10, CAST(INSERT((FORMAT(e.`pMax` / 10.0, 1)), 3, 1, '.') AS DECIMAL(10,4)) / 10) / 1000, 0) AS Pmax,     
            CAST(IF(rf.earfcnDL = '6200', 7.5, LEFT((CASE rf.`dlChBw`
                WHEN 50 THEN '5 MHz'
                WHEN 100 THEN '10 MHz'
                WHEN 150 THEN '15 MHz'
                WHEN 200 THEN '20 MHz'        
                ELSE 'Unknow'
            END), CHARACTER_LENGTH((CASE rf.`dlChBw`
                WHEN 50 THEN '5 MHz'
                WHEN 100 THEN '10 MHz'
                WHEN 150 THEN '15 MHz'
                WHEN 200 THEN '20 MHz'        
                ELSE 'Unknow'
            END)) - 4)) AS DECIMAL(10,2)) AS BW,

            CASE 
                WHEN rf.prachCS = '14' THEN 'область (35км)'
                WHEN rf.prachCS = '2' THEN 'ограничение (2км)'
                ELSE 'город (15км)'
            END AS CellRange
        FROM config_Nokia4G_LNCEL.LNCEL_begin b
        INNER JOIN config_Nokia4G_LNCEL.LNCEL_end e 
            ON b.MRBTS = e.MRBTS AND b.LNBTS = e.LNBTS AND b.LNCEL = e.LNCEL
        LEFT JOIN (
            SELECT MRBTS, LNBTS, LNCEL, prachCS, dlMimoMode, rootSeqIndex, dlChBw, earfcnDL
            FROM config_Nokia4G.LNCEL_FDD
            UNION ALL
            SELECT MRBTS, LNBTS, LNCEL, prachCS, dlMimoMode, rootSeqIndex, chBw AS dlChBw, earfcn AS earfcnDL
            FROM config_Nokia4G.LNCEL_TDD
        ) rf 
            ON b.MRBTS = rf.MRBTS AND b.LNBTS = rf.LNBTS AND b.LNCEL = rf.LNCEL
        WHERE b.MRBTS LIKE '%{sublistSite[4]}%'
        order by b.LNCEL;
        """
    dfLncel, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBNOKIA"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    #print(dfLncel)

    # Корректируем таблицы. Данные столбцы необходимо только для BSS. В нашей таблице они не отобразятся. может стоит убрать ниже столбцы:
    dfLncel["LNHOIF_0"] = sublistSite[17]
    dfLncel["LNHOIF_1"] = sublistSite[18]
    dfLncel["LNHOIF_2"] = sublistSite[19]
    dfLncel["LNHOIF_3"] = sublistSite[20]
    dfLncel["LNHOIF_4"] = sublistSite[21]
    dfLncel["LNHOIF_5"] = sublistSite[22]
    # print(dfLncel)

    # Получаем данные в таблице 4G:
    df4g = dfLncel.reindex(
        columns=["B", "O", "P", "C", "F", "J", "K", "Q", "H", "LNHOIF_0", "LNHOIF_1", "LNHOIF_2", "LNHOIF_3",
        "LNHOIF_4", "LNHOIF_5", "D", "E", "L", "N", "A"]
    )
    #print(df4g)

    # Собираем данные в JSON:
    listForJson, sublistsTemp, listsTemp, df4g, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], df4g, len(df4g.columns), 0, sublistSite[5]
    )
    listForJson.append(listsTemp)'''
    return reg, numb, listForJson
def funcEricssonList(reg, numb, band, listForJson):
    listSite = []
    sublistSite = []
    listNumbers = list(range(1, 44))
    print(reg)
    print(numb)
    print(band)

    # Данные по умолчанию, готовится первый список:
    reg, numb, sublistSite, band = funcEricssonAddSublistSite(reg, numb, sublistSite, band)
    listSite.append(sublistSite)
    listForJson.append(listSite)
    #print(listSite)
    #print(listForJson)

    # Готовим данные для фильтрации. в нашем случае - Site:
    # print(sublistSite)
    #print(sublistSite[5])
    #print(sublistSite[3])
    #print(sublistSite[23])
    #print(sublistSite[24])
    #print(sublistSite[25])
    #print(sublistSite[28])
    #print(sublistSite[38])
    # Собираем данные из БД для таблицы Info Site. Скрипт загрузки в БД выполняется автоматически, по расписанию в ночное время.
    # print("... Sending a query to MySQL function funcMysqlDf()")
    strDbQuery = f"""
    select * from DjangoTemplate.FromDBTEST__site WHERE `0_` LIKE '%{sublistSite[5]}%';
    """
    dfSite, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBDJANGO"), settings.CONFIG_DATA.get("USERDBDJANGO"),
        settings.CONFIG_DATA.get("PASSWORDDBDJANGO"), settings.CONFIG_DATA.get("NAMEDBDJANGO")
    )
    # print("+ Get table dfSite from Mysql:")
    # print(dfSite.to_string())

    # print("... Correcting table dfSite")
    dfSite.columns = ["siteName", "siteType", "Address", "Status", "Plan"]
    # dfSite.loc[len(dfSite)] = ["IR2664", "30:трубостойкиTEST", "ИркутскийTEST Автономный Округ, УсольскийTEST Район, ГлубокийTEST Лог Деревня, НабережнаяTEST 2-я Улица", "TESTЭксплуатация", "ПланTEST емкости"] # Tamp String. Need delete
    print(dfSite.to_string())
    # print("... Getting list from column table df")
    subListColOldSite = dfSite["Address"].tolist()
    print(f"+ Get old list from column table df {subListColOldSite}")
    # print("... Correcting list")
    subListColNewSite = []

    for strIndex in subListColOldSite:
        # print(f"+ Get index from list: {strIndex}")
        # print("... Finding symbol ,")
        subListOldData = strIndex.split(', ')
        # print(f"+ Correct list {subListOldData}")
        subListNewData = []
        # for strSubIndex in subListColOldSite:
        for strSubIndex in subListOldData:
            # print(f"+ Get index from list: {strSubIndex}")
            # ИСКЛЮЧЕНИЕ: Если в строке есть слэш, оставляем её полностью без изменений
            if "\\" in strSubIndex:
                subListNewData.append(strSubIndex)
                continue
            strSorting, strType, strName, is_found = funcSort2Words(
                r"(автономный округ|автономная область|область|край|округ|республика)", "", "", strSubIndex, )
            if is_found:
                subListNewData.append(strType + " " + strName)
                continue
            strSorting, strType, strName, is_found = funcSort2Words(r"(район)", "", "", strSubIndex, )
            if is_found:
                subListNewData.append(strType + " " + strName)
                continue
            strSorting, strType, strName, is_found = funcSort2Words(r"(город)", "", "", strSubIndex, )
            if is_found:
                subListNewData.append(strType + " " + strName)
                continue
            strSorting, strType, strName, is_found = funcSort2Words(r"(деревня|поселок|посёлок|село)", "", "", strSubIndex, )
            if is_found:
                subListNewData.append(strName + " " + strType)
                continue
            strSorting, strType, strName, is_found = funcSort2Words(r"(улица)", "", "", strSubIndex, )
            if is_found:
                subListNewData.append(strName + " " + strType)
                continue
            strSorting, strType, strName, is_found = funcSort2Words(r"(вышка|амс)", "", "", strSubIndex, )
            if is_found:
                subListNewData.append(strType + " " + strName)
                continue
            strSorting, strType, strName, is_found = funcSort2Words(r"(дом)", "", "", strSubIndex, )
            if is_found:
                subListNewData.append(strType + " " + strName)
                continue
        #print(f"+ Correct list {subListNewData}")
        #strIndex = subListNewData[0] + ", " + subListNewData[1] + ", " + subListNewData[2] + ", " + subListNewData[3]
        strIndex = ", ".join(subListNewData) if subListNewData else strIndex
        # print(f"+ Get index from list: {strIndex}")
        subListColNewSite.append(strIndex)
    print(f"+ Get new list for column table df: {subListColNewSite}")

    # print("... Correcting table dfSite")
    dfSite["NewAddress"] = subListColNewSite
    dfSite = dfSite.reindex(columns=["siteName", "siteType", "NewAddress", "Status", "Plan"])
    dfSite["Region"] = sublistSite[3]
    dfSite["UTC"] = sublistSite[23]
    dfSite["MSW"] = sublistSite[24]
    dfSite["ipPlan"] = sublistSite[25]
    dfSite["TCU"] = sublistSite[28]
    dfSite["Oblast"] = sublistSite[38]
    print(dfSite.to_string())
    # Собираем данные в JSON:
    listForJson, sublistsTemp, listsTemp, dfSite, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], dfSite, len(dfSite.columns), 0, sublistSite[5]
    )
    listForJson.append(listsTemp)

    # Готовим данные для фильтрации. в нашем случае - df2gData:
    # print(sublistSite)
    #print(sublistSite[5])
    # Собираем данные из БД для таблицы RanData и 2G.
    strDbQuery = f"""
            select 
                BSC_NAME, CELL_NAME, CHGR_NAME,
                CASE 
                    WHEN BAND = '1' THEN 'GSM1800'
                    WHEN BAND = '0' THEN 'GSM900'
                    WHEN BAND = '' THEN 'Unknow'
                    ELSE 'Unknow'
                END AS band,    
                CASE 
                    WHEN connectedG12Tg != '' THEN SUBSTRING_INDEX(connectedG12Tg, 'vsDataG12Tg=', -1)
                    WHEN connectedG12Tg = '' THEN 'nan'
                    ELSE 'Unknow'
                END AS G12Tg,    
                CASE 
                    WHEN connectedG31Tg != '' THEN SUBSTRING_INDEX(connectedG31Tg, 'vsDataG31Tg=', -1)
                    WHEN connectedG31Tg = '' THEN 'nan'
                    ELSE 'Unknow'
                END AS G31Tg,
                CONCAT(
                    '[', 
                    CASE 
                        WHEN DCHNO_short = '' THEN DCHNO
                        WHEN DCHNO_short != '' THEN DCHNO_short
                        ELSE 'Unknow'
                    END, 
                    ']'
                ) AS dchNo,
                CONCAT(
                    BSC_NAME, 
                    CASE 
                        WHEN connectedG31Tg != '' THEN SUBSTRING_INDEX(connectedG31Tg, 'vsDataG31Tg=', -1)
                        WHEN connectedG31Tg = '' THEN 'nan'
                        ELSE 'Unknow'
                    END
                ) AS `AT`, 
                'Unknow' AS sigDel
                -- BAND, connectedG12Tg, connectedG31Tg, DCHNO_short, DCHNO
            from Config_Ericsson2g.CHANNEL_GROUP
            where CELL_NAME LIKE '%{sublistSite[5]}%';
        """
    dfChannelGroup, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print("dfChannelGroup:")
    #print(dfChannelGroup)
    dfChannelGroup.columns = ["BSC","Sector","ChannelGroupIdl","sys","otg","stg","dchNo","AT","sigDel",] # Возможно надо будет поменять политику добавления символов ко всем таблицам из БД
    #print(dfChannelGroup) #Возможно стоит обновить таблицу так чтобы на всех строках был заполнено в стоблце sys. И возможно придется искать в другое таблице БД sys.
    #Добавляем основную таблицу df2gData. Очень сложная процедура. возможно это можно упростить или в запросе или в коде ниже.
    #Делим значения ChannelGroupIdl на 0 и 1
    dfTemp1 = dfChannelGroup.loc[dfChannelGroup["ChannelGroupIdl"].astype(str) == "1"]#Добавил .astype(str) так как после перенос с excel в sql число 1 видел с типом int64, поэтому не отображались данные
    dfTemp2 = dfChannelGroup.loc[dfChannelGroup["ChannelGroupIdl"].astype(str) == "0"]
    print("dfTemp1, dfTemp2:")
    #print(dfTemp1)
    #print(dfTemp2)
    #listNullCol = ["", "", ""] # Моэет стоит nan сделать вместо пустых значений. Воможно нужно добавить значения для 4, 7, A, B, C.
    if (checkTable(dfTemp1) == True):
        print("ВНИМАНИЕ1! Необходимо проверить выполнение условий ниже именно с reindex VV0181 AM0581")
        #listF = [1,1,1]
        dfTemp1 = dfTemp2.reindex(columns=["BSC", "Sector", "ChannelGroupIdl", "sys", "otg", "stg", "AT", "sigDel"]) #Убрал ChannelGroupIdl, dchNo
        print("dfTemp1:")
        #print(dfTemp1)
        #dfTemp1["dchNo"] = listNullCol
        dfTemp1['dchNo'] = ""
        #newCols = list(dfTemp1.columns) + ["dchNo"]
        #dfTemp1 = dfTemp1.reindex(columns=newCols)
        #print(dfTemp1)
        #dfTemp1["ChannelGroupIdl"] = listF
        dfTemp1["ChannelGroupIdl"] = 1
        #print(dfTemp1)
        dfTemp1 = dfTemp1.reindex(columns=["BSC", "Sector", "ChannelGroupIdl", "sys", "otg", "stg", "dchNo", "AT", "sigDel"])
        #print(dfTemp1)
    elif (checkTable(dfTemp2) == True):
        print("ВНИМАНИЕ2! Необходимо проверить выполнение условий ниже именно с reindex VV0181 AM0581")
        #listF = [0,0,0]
        dfTemp2 = dfTemp1.reindex(columns=["BSC", "Sector", "ChannelGroupIdl", "sys", "otg", "stg", "AT", "sigDel"])
        #dfTemp2["dchNo"] = listNullCol
        #dfTemp2["ChannelGroupIdl"] = listF
        dfTemp2["dchNo"] = ""
        dfTemp2["ChannelGroupIdl"] = 0
        dfTemp2 = dfTemp2.reindex(columns=["BSC", "Sector", "ChannelGroupIdl", "sys", "otg", "stg", "dchNo", "AT", "sigDel"])
    #print(dfTemp1)
    #print(dfTemp2)
    # Думаю стоит убрать ниже код, так как делает не понятные и лишние манипуоляции с секторами  для пустых строк в таблицах
    listCell = [sublistSite[5]+"1", sublistSite[5]+"2", sublistSite[5]+"3", sublistSite[5]+"4", sublistSite[5]+"7"] # Если оставить тогда нужно добавить для секторов 4, 7, A, B, C. Если по шаблону смотреть
    #print(dfTemp1.shape[0])
    listNullCol = ["", "", ""]  # Моэет стоит nan сделать вместо пустых значений. Воможно нужно добавить значения для 4, 7, A, B, C.
    if dfTemp1.shape[0] != len(listNullCol):
        print("ВНИМАНИЕ1! Необходимо проверить выполнение условий ниже именно с reindex VV0181 BU0113. Еще заметил, что добавление идет тупо по секторам listCell (1,2,3) как в шаблоне. если естьа сектор 7, 8 ... - не посчитается. Может стоит убрать такую функцию")
        dfTemp=pd.DataFrame(listCell) #Не понятно для чего. просто на три сектора добавляет БС в 9
        print("dfTemp:")
        #print(dfTemp)
        renameCol=dfTemp[0]
        dfTemp.insert(0, "Sector0", renameCol)# Чтобы название колонки 0 было строчным а не символьным
        del dfTemp[0]
        #print(dfTemp)
        dfTemp = pd.merge(dfTemp, dfTemp1, left_on="Sector0", right_on="Sector", how="outer")
        #print(dfTemp)
        del dfTemp["Sector"] # Закомментировал, так как удаляет основное столбец
        renameCol=dfTemp["Sector0"]
        dfTemp.insert(0, "Sector", renameCol)
        del dfTemp["Sector0"]
        dfTemp.fillna("", inplace=True)
        # Закомментировал код, так как код Удаляет нужную колонку B, копирует не нужную колонку 0 и зачем-то перемещает в столбец B. Лишняя процедура.
        #print(dfTemp)
        dfTemp1=dfTemp
    elif dfTemp2.shape[0] != len(listNullCol):
        print("ВНИМАНИЕ2! Необходимо проверить выполнение условий ниже именно с reindex VV0181 BU0113. Еще заметил, что добавление идет тупо по секторам listCell (1,2,3) как в шаблоне. если естьа сектор 7, 8 ... - не посчитается. Может стоит убрать такую функцию")
        dfTemp=pd.DataFrame(listCell)
        renameCol=dfTemp[0]
        dfTemp.insert(0, "Sector0", renameCol)
        del dfTemp[0]
        dfTemp = pd.merge(dfTemp, dfTemp2, left_on="Sector0", right_on="Sector", how="outer")
        del dfTemp["Sector"]
        renameCol=dfTemp["Sector0"]
        dfTemp.insert(0, "Sector", renameCol)
        del dfTemp["Sector0"]
        dfTemp.fillna("", inplace=True)
        # Закомментировал код, так как код Удаляет нужную колонку B, копирует не нужную колонку 0 и зачем-то перемещает в столбец Sector. Лишняя процедура.
        # print(dfTemp)
        dfTemp2=dfTemp
    #print(dfTemp1)
    #print(dfTemp2)
    # Получение таблицы df2gData из таблицы dfChannelGroup
    df2gData = pd.merge(dfTemp1, dfTemp2, left_on="Sector", right_on="Sector", how="inner") # Надоориентироваться по _y
    print("df2gData:")
    #print(df2gData)
    # Собираем данные из БД для таблицы RanData и 2G.
    strDbQuery = f"""
        select 
            MeContext_id, noOfTxAntennas, GsmSector_id, trx_id,
            LEFT(GsmSector_id, 6) AS Site
        from Config_Ericsson_BB.Datatrx
        WHERE GsmSector_id LIKE '%{sublistSite[5]}%'
        order by trx_id DESC
        """
    dfTrx, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print("dfTrx:")
    #print(dfTrx)
    dfTrx.columns = ["NodeId", "BtsFunctionId", "Sector", "TrxId", "Site", ]  # Возможно надо будет поменять политику добавления символов ко всем таблицам из БД
    #print(dfTrx)
    # Возможно стоит поменять запрос из-за столбца noOfTxAntennas. думаю что столбец по данным похож на столбец из ексель BtsFunctionId. И возможно стоит убрать order by для  того чтобы скорость запроса была быстрее. Десь он необходим так как точнее учитывает 4 колоеку trx.
    # Корректируем  таблицу dfTrx. Очень сложная процедура. возможно это можно упростить или в запросе или в коде ниже.
    dfTrx = dfTrx.reindex(columns=["NodeId", "Site", "BtsFunctionId", "Sector", "TrxId"])
    #print(dfTrx)
    # Проверяем на заполнение таблицы dfTrx. если пристутсвуют данные - корректируем, нет - добавляем таблицу пустую, может ее можно поправить/убрать
    if checkTable(dfTrx) == False:
        print("FALSE dfTrx")
        listTrx = dfTrx.values.tolist()
        dfTemp1 = pd.DataFrame(listTrx)
        print("dfTemp1:")
        #print(dfTemp1)
        dfTemp1 = dfTemp1.drop_duplicates(3, keep="first")
        print(dfTemp1[4].dtype)
        if dfTemp1[4].dtype == "int64":
            dfTemp1[4] = dfTemp1[4] + 1
        elif dfTemp1[4].dtype == "object":
            dfTemp1[4] = dfTemp1[4].astype('int64') + 1
        #print(dfTemp1)
        # Зачем нужна процедура ниже не понятно. Возможно просто переименовать колонки, чтобы была возможность обращаться к ним по типу string
        renameCol=dfTemp1[3]
        #dfTemp1.insert(3, "3", renameCol)
        dfTemp1.insert(3, "Sector", renameCol)
        del dfTemp1[3]
        renameCol=dfTemp1[0]
        #dfTemp1.insert(0, "0", renameCol)
        dfTemp1.insert(0, "NodeId", renameCol)
        del dfTemp1[0]
        renameCol=dfTemp1[1]
        #dfTemp1.insert(1, "1", renameCol)
        dfTemp1.insert(1, "Site", renameCol)
        del dfTemp1[1]
        renameCol=dfTemp1[2]
        #dfTemp1.insert(2, "2", renameCol)
        dfTemp1.insert(2, "BtsFunctionId", renameCol)
        del dfTemp1[2]
        renameCol=dfTemp1[4]
        #dfTemp1.insert(4, "4", renameCol)
        dfTemp1.insert(4, "G31Trx", renameCol)
        del dfTemp1[4]
        #print(dfTemp1)
        dfTrx = dfTemp1
    else:
        #print("TRUE dfTrx")
        dfTemp1 = df2gData
        print("dfTemp1:")
        #print(dfTemp1)
        #copyCol=dfTemp1["Sector"]
        #dfTemp1.insert(1, "3", copyCol)
        #dfTemp1 = dfTemp1.reindex(columns=["3"])
        #dfTemp1.insert(1, "Sector0", copyCol)
        #dfTemp1 = dfTemp1.reindex(columns=["Sector0"])
        dfTemp1 = dfTemp1.reindex(columns=["Sector"])
        #print(dfTemp1)
        # Добавляем пустые колонки:
        #dfTemp1["0"] = listNullCol
        #dfTemp1["1"] = listNullCol
        #dfTemp1["2"] = listNullCol
        #dfTemp1["4"] = listNullCol
        #dfTemp1["NodeId"] = listNullCol
        #dfTemp1["Site"] = listNullCol
        #dfTemp1["BtsFunctionId"] = listNullCol
        #dfTemp1["G31Trx"] = listNullCol
        dfTemp1["NodeId"] = ""
        dfTemp1["Site"] = ""
        dfTemp1["BtsFunctionId"] = ""
        dfTemp1["G31Trx"] = ""
        #print(dfTemp1)
        dfTrx = dfTemp1
    # Лучше заменить название dfTrx на df2gData1. Чтобы была прежня таблица dfTrx
    print("dfTrx:")
    #print(dfTrx)
    # Получаем осонвную таблицу df2gData из dfTrx
    df2gData = pd.merge(df2gData, dfTrx, left_on="Sector", right_on="Sector", how="inner")
    print("df2gData:")
    #print(df2gData)
    # Собираем данные из БД для таблицы RanData и 2G.
    strDbQuery = f"""
            SELECT 
                -- t2.int_name, 
                t2.nwName, t2.BCC, t2.bcch,
                -- CONCAT_WS('-', t2.MCC, t2.MNC, t2.lac, t2.ci) AS cgi, 
                t1.G12Trxc, -- Добавили колонку из первой таблицы
                t2.NCC,
                CASE 
                    WHEN t2.adminState = '0' THEN 'HALTED'
                    WHEN t2.adminState = '1' THEN 'ACTIVE'
                    ELSE 'Unknow'
                END AS state,
                -- LEFT(t2.nwName, 6) AS Site,
                t2.MCC, t2.MNC, t2.lac, t2.ci
            FROM Config_all.Config t2
            INNER JOIN (
                SELECT
                    cell,
                    CASE 
                        WHEN chgr = 'ALL' THEN ''
                        ELSE GROUP_CONCAT(TRX12 ORDER BY TRX12 ASC SEPARATOR ',')
                    END AS G12Trxc
                FROM Config_Ericsson2g.bsm_trx
                WHERE site LIKE '{sublistSite[5]}'
                GROUP BY cell
            ) t1 ON t2.nwName = t1.cell
            WHERE t2.SectorName LIKE '%{sublistSite[5]}%'
        """
    dfGeranCell, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print("dfGeranCell:")
    #print(dfGeranCell)
    dfGeranCell.columns = ["Sector", "bcc", "bcchNo", "G12Trxc", "ncc", "Status", "MCC", "MNC", "lac", "ci",] # Возможно надо будет поменять политику добавления символов ко всем таблицам из БД
    #print(dfGeranCell)
    # Получаем осонвную таблицу df2gData из dfGeranCell
    df2gData = pd.merge(df2gData, dfGeranCell, left_on="Sector", right_on="Sector", how="inner")
    print("df2gData:")
    #print(df2gData)
    print(df2gData.columns)
    df2gData = df2gData.reindex(
        columns=["Sector", "BSC_y", "sys_x", "otg_y", "stg_y", "G12Trxc", "dchNo_y", "dchNo_x", "bcchNo", "ncc", "bcc",
                 "lac", "ci", "G31Trx", "sigDel_y", "Status", "MCC", "MNC"]
    )
    #print(df2gData)
    # Собираем данные в JSON:
    listForJson, sublistsTemp, listsTemp, df2gData, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], df2gData, len(df2gData.columns), 0, sublistSite[5]
    )
    listForJson.append(listsTemp)

    # Готовим данные для фильтрации. в нашем случае - UtranCell: C, G_y, C_y,
    # print(sublistSite)
    #print(sublistSite[5])
    #print(sublistSite[31])
    #print(sublistSite[33])
    # Собираем данные из БД для таблицы RanData и 3G.
    strDbQuery3000 = f"""
            SELECT 
                t1.id AS Sectorname,
                t2.rnc_name, t2.primaryScramblingCode, t2.UarfcnDl,
                t1.tCell,
                t2.lac, t2.uralist, t2.rac, t2.PrimaryCpichPower, t2.MaximumTransmissionPower,
                CASE 
                    WHEN t2.administrativeState='0' THEN 'LOCKED'
                    WHEN t2.administrativeState='1' THEN 'UNLOCKED'
                    ELSE 'Unknow'
                END AS administrativeState,
                SUBSTRING_INDEX(t1.id, '_', 1) AS Site,
                SUBSTRING_INDEX(t1.id, '_', -1) AS localcellid
            FROM Config_Ericsson3g_Params.xParam_UtranCell t1
            JOIN Config_all.config_3g t2 
                ON t1.id = t2.Sectorname
            WHERE t1.id LIKE '%{sublistSite[31]}%';
        """
    strDbQuery4000 = f"""
                SELECT 
                    t1.id AS Sectorname,
                    t2.rnc_name, t2.primaryScramblingCode, t2.UarfcnDl,
                    t1.tCell,
                    t2.lac, t2.uralist, t2.rac, t2.PrimaryCpichPower, t2.MaximumTransmissionPower,
                    CASE 
                        WHEN t2.administrativeState='0' THEN 'LOCKED'
                        WHEN t2.administrativeState='1' THEN 'UNLOCKED'
                        ELSE 'Unknow'
                    END AS administrativeState,
                    SUBSTRING_INDEX(t1.id, '_', 1) AS Site,
                    SUBSTRING_INDEX(t1.id, '_', -1) AS localcellid
                FROM Config_Ericsson3g_Params.xParam_UtranCell t1
                JOIN Config_all.config_3g t2 
                    ON t1.id = t2.Sectorname
                WHERE t1.id LIKE '%{sublistSite[33]}%';
        """
    dfUtranCell3000, strDbQuery3000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery3000,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    dfUtranCell4000, strDbQuery4000, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery4000,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    #print(dfUtranCell3000)
    #print(dfUtranCell4000)
    # Редактриуем таблицы dfUtranCell

    # Готовим данные для фильтрации. в нашем случае - UtranCell:
    # print(sublistSite)
    #print(sublistSite[5])

    # Объединяем таблицы dfUtranCell для таблицы df3g
    df3g = pd.concat([dfUtranCell3000, dfUtranCell4000])
    #print(df3g)
    # Собираем данные в JSON:
    listForJson, sublistsTemp, listsTemp, df3g, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], df3g, len(df3g.columns), 0, sublistSite[5]
    )
    listForJson.append(listsTemp)
    #print(listForJson)

    # Собираем данные из БД для таблицы 4G учел момент для таблиц БСС 4г парт.
    strDbQuery = f"""
        SELECT 
            CAST(ROUND(c.dlChannelBandwidth / 1000) AS SIGNED) AS dlChannelBandwidth,
            c.tac, c.Sectorname, c.earfcndl, c.PCI,
            CASE 
                WHEN e.cellRange = '1' THEN 'default (1км)'
                WHEN e.cellRange = '2' THEN 'ограничение (2км)'
                WHEN e.cellRange = '15' THEN 'город (15км)'
                WHEN e.cellRange = '35' THEN 'область (35км)'
                ELSE 'Unknow'
            END AS cellRange,
            c.RSI,
            CAST(ROUND(p.configuredMaxTxPower * 0.001) AS SIGNED) AS configuredMaxTxPower,
            CASE 
                WHEN c.administrativeState = '1' THEN 'UNLOCKED'
                WHEN c.administrativeState = '0' THEN 'LOCKED'
                ELSE 'Unknow'
            END AS administrativeState,
            c.Enodeb
            -- c.dlChannelBandwidth,  c.administrativeState, p.configuredMaxTxPower, e.cellRange
        FROM Config_Ericsson4g.Config c
        LEFT JOIN Config_Ericsson4g.Param_vsDataSectorCarrier p 
            ON c.Sectorname = p.VsDataContainer_id
        LEFT JOIN Config_Ericsson4g.EUtranCellFDD e 
            ON c.Sectorname = e.userlabel
        WHERE 
            c.Enodeb LIKE '%{sublistSite[5]}%' OR c.Enodeb LIKE '%{sublistSite[5]}%' OR  c.Enodeb LIKE '%{sublistSite[33]}%';
        """
    df4g, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print("df4g:")
    #print(df4g)
    df4g.columns = ["dlChannelBandwidth", "tac", "Sectorname", "earfcndl", "PCI", "cellRange", "RSI",
                    "configuredMaxTxPower","administrativeState","Enodeb", ] # Возможно надо будет поменять политику добавления символов ко всем таблицам из БД
    #print(df4g)
    # Собираем данные в JSON:
    listForJson, sublistsTemp, listsTemp, df4g, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], df4g, len(df4g.columns), 0, sublistSite[5]
    )
    listForJson.append(listsTemp)
    # print(listForJson)

    # Готовим данные для фильтрации. в нашем случае VV0203 VV3203 VV4203
    #print(sublistSite)
    #print(sublistSite[5])
    #print(sublistSite[31])
    #print(sublistSite[33])
    # Собираем данные из БД для таблицы DuData.
    strDbQuery = f"""        
        -- 1. Данные из Config_Ericsson_BB
        SELECT
            MeContext_id AS NodeId, SUBSTRING_INDEX(address, '/', 1) AS ipAddress
        FROM Config_Ericsson_BB.Param_IpInterface_cell_BB
        WHERE
            (VsDataContainer2_id LIKE '%OAM%') AND
            (MeContext_id LIKE '%{sublistSite[5]}%' OR MeContext_id LIKE '%{sublistSite[31]}%' OR MeContext_id LIKE '%{sublistSite[33]}%')
        -- 2. Данные из Config_EricssonTCU
        UNION ALL SELECT
            ManagedElement_id AS NodeId, ipAddress
        FROM Config_EricssonTCU.config_tcu
        WHERE
            (ManagedElement_id LIKE '%{sublistSite[5]}%' OR ManagedElement_id LIKE '%{sublistSite[31]}%' OR ManagedElement_id LIKE '%{sublistSite[33]}%')
        -- 3. Данные из Config_Ericsson3g_Params.Param_IP (с динамическим исключением)
        UNION ALL SELECT
            Ipid AS NodeId, nodeIpAddress AS ipAddress
        FROM Config_Ericsson3g_Params.Param_IP
        WHERE
            (Ipid LIKE '%{sublistSite[5]}%' OR Ipid LIKE '%{sublistSite[31]}%' OR Ipid LIKE '%{sublistSite[33]}%')
            -- Исключаем любые NodeId, которые уже есть в первых двух таблицах:
            AND Ipid NOT IN (
                SELECT
                    MeContext_id
                FROM Config_Ericsson_BB.Param_IpInterface_cell_BB
                WHERE
                    VsDataContainer2_id LIKE '%OAM%'
                UNION SELECT ManagedElement_id FROM Config_EricssonTCU.config_tcu
            );
        """
    dfGetIp, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print("dfGetIp:")
    #print(dfGetIp)
    dfGetIp.columns = ["NodeId", "ipAddress", ]  # Возможно надо будет поменять политику добавления символов ко всем таблицам из БД
    #print(dfGetIp)
    # Собираем данные из БД для таблицы DuData.
    strDbQuery = f"""        
        SELECT 
            ManagedElement_id, ethernetPortId,
            'Unknow' AS operOperatingMode
        FROM Config_Ericsson_BB.EthernetPort
        WHERE (ManagedElement_id LIKE '%{sublistSite[5]}%' OR ManagedElement_id LIKE '%{sublistSite[31]}%' OR ManagedElement_id LIKE '%{sublistSite[33]}%');   
        """
    dfBBEthPort, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print("dfBBEthPort:")
    #print(dfBBEthPort)
    dfBBEthPort.columns = ["NodeId", "EthernetPortId", "operOperatingMode",]  # Возможно надо будет поменять политику добавления символов ко всем таблицам из БД
    #print(dfBBEthPort)
    # Получаем таблицу DuData.
    dfDuData = pd.merge(dfGetIp, dfBBEthPort, on="NodeId", how="left")
    print("dfDuData:")
    #print(dfDuData)
    # Добавляем колонку для ссылок. 1. Создаем список условий (важно соблюдать правильный порядок)
    conditions = [
        dfDuData["NodeId"].str.startswith("TCU"),  # Начинается с TCU
        dfDuData["NodeId"].str.get(2).isin(["3", "4", "5"]),  # Второй символ (индекс 1) равен 3, 4 или 5
    ]
    # 2. Создаем динамические значения ссылок на основе колонки ipAddress
    choices = [
        "ssh://" + dfDuData["ipAddress"],
        "http://" + dfDuData["ipAddress"] + "/em/index.html",
    ]
    # 3. Применяем np.select, где default — это значение для "иначе"
    dfDuData["Link"] = np.select(conditions, choices, default="https://" + dfDuData["ipAddress"])
    #print(dfDuData)
    # Собираем данные в JSON:
    listForJson, sublistsTemp, listsTemp, dfDuData, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], dfDuData, len(dfDuData.columns), 0, sublistSite[5]
    )
    listForJson.append(listsTemp)
    #print(listForJson)

    # Готовим данные для фильтрации. в нашем случае VV0203 VV3203 VV4203
    #print(sublistSite)
    #print(sublistSite[5])
    #print(sublistSite[31])
    #print(sublistSite[33])
    # Собираем данные из БД для таблицы DuData.
    strDbQuery = f"""        
        SELECT
            sites.Site_Name,    
            -- Блок 3G OM (Данные только из IP_Plan)
            t2.VLAN_3G_OM, 
            t2.NodeB_3G_OM, 
            t2.Port_3G_OM,    
            -- Блок 4G OM (Приоритет IP_Plan, иначе OAM из Ericsson)
            COALESCE(t2.VLAN_4G_OM, t1.OAM_vlan) AS VLAN_4G_OM,
            COALESCE(t2.eNodeB_4G_OM, SUBSTRING_INDEX(t1.OAM_address, '/', 1)) AS eNodeB_4G_OM,
            COALESCE(t2.Port_4G_OM, t1.OAM_nextHop) AS Port_4G_OM,    
            -- Блок 2G CU (Приоритет IP_Plan, иначе Abis из Ericsson)
            COALESCE(t2.VLAN_2G_CU, t1.Abis_vlan) AS VLAN_2G_CU,
            COALESCE(t2.BTS_2G_CU, SUBSTRING_INDEX(t1.Abis_address, '/', 1)) AS BTS_2G_CU,
            COALESCE(t2.Port_2G_CU, t1.Abis_nextHop) AS Port_2G_CU,    
            -- Блок 3G CU (Приоритет IP_Plan, иначе IUB из Ericsson)
            COALESCE(t2.VLAN_3G_CU, t1.IUB_vlan) AS VLAN_3G_CU,
            COALESCE(t2.NodeB_3G_CU, SUBSTRING_INDEX(t1.IUB_address, '/', 1)) AS NodeB_3G_CU,
            COALESCE(t2.Port_3G_CU, t1.IUB_nextHop) AS Port_3G_CU,    
            -- Блок 4G CU (Приоритет IP_Plan, иначе S1 из Ericsson)
            COALESCE(t2.VLAN_4G_CU, t1.S1_vlan) AS VLAN_4G_CU,
            COALESCE(t2.eNodeB_4G_CU, SUBSTRING_INDEX(t1.S1_address, '/', 1)) AS eNodeB_4G_CU,
            COALESCE(t2.Port_4G_CU, t1.S1_nextHop) AS Port_4G_CU,    
            -- Блок TCU OM (Данные только из IP_Plan)
            t2.VLAN_TCU_OM, 
            t2.TCU_TCU_OM, 
            t2.GW_TCU_OM
        FROM (
            -- Шаг 1: Собираем полный список уникальных Site_Name из двух таблиц
            SELECT Site_Name FROM CreateSite.IP_Plan
            UNION
            SELECT DISTINCT LEFT(MeContext_id, 6) AS Site_Name FROM Config_Ericsson_BB.Param_IpInterface_cell_BB
        ) sites
        -- Шаг 2: Подтягиваем данные из IP_Plan
        LEFT JOIN CreateSite.IP_Plan t2 ON sites.Site_Name = t2.Site_Name
        -- Шаг 3: Подтягиваем данные из конфигурации Ericsson
        LEFT JOIN (
            SELECT
                LEFT(MeContext_id, 6) AS Clean_Site_Name,
                MAX(CASE WHEN VsDataContainer2_id = 'Abis' THEN address END) AS Abis_address,
                MAX(CASE WHEN VsDataContainer2_id = 'Abis' THEN addressNextHop END) AS Abis_nextHop,
                MAX(CASE WHEN VsDataContainer2_id = 'Abis' THEN vlanId END) AS Abis_vlan,        
                MAX(CASE WHEN VsDataContainer2_id = 'OAM' THEN address END) AS OAM_address,
                MAX(CASE WHEN VsDataContainer2_id = 'OAM' THEN addressNextHop END) AS OAM_nextHop,
                MAX(CASE WHEN VsDataContainer2_id = 'OAM' THEN vlanId END) AS OAM_vlan,        
                MAX(CASE WHEN VsDataContainer2_id = 'S1' THEN address END) AS S1_address,
                MAX(CASE WHEN VsDataContainer2_id = 'S1' THEN addressNextHop END) AS S1_nextHop,
                MAX(CASE WHEN VsDataContainer2_id = 'S1' THEN vlanId END) AS S1_vlan,        
                MAX(CASE WHEN VsDataContainer2_id = 'IUB' THEN address END) AS IUB_address,
                MAX(CASE WHEN VsDataContainer2_id = 'IUB' THEN addressNextHop END) AS IUB_nextHop,
                MAX(CASE WHEN VsDataContainer2_id = 'IUB' THEN vlanId END) AS IUB_vlan
            FROM Config_Ericsson_BB.Param_IpInterface_cell_BB
            WHERE VsDataContainer2_id IN ('Abis', 'OAM', 'S1', 'IUB')
            GROUP BY LEFT(MeContext_id, 6)
        ) t1 ON sites.Site_Name = t1.Clean_Site_Name
        -- Шаг 4: Фильтруем только по интересующим вас сайтам
        WHERE 
            sites.Site_Name LIKE '%{sublistSite[5]}%' OR sites.Site_Name LIKE '%{sublistSite[31]}%' OR sites.Site_Name LIKE '%{sublistSite[33]}%'
        ORDER BY sites.Site_Name;
        """
    dfIpPlan, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print("dfIpPlan:")
    #print(dfIpPlan)
    dfIpPlan.columns = ["Site_Name",
                        "VLAN_3G_OM", "NodeB_3G_OM", "Port_3G_OM", "VLAN_4G_OM", "eNodeB_4G_OM", "Port_4G_OM", "VLAN_2G_CU", "BTS_2G_CU", "Port_2G_CU",
                        "VLAN_3G_CU", "NodeB_3G_CU", "Port_3G_CU", "VLAN_4G_CU", "eNodeB_4G_CU", "Port_4G_CU", "VLAN_TCU_OM", "TCU_TCU_OM", "GW_TCU_OM", ]
    #print(dfIpPlan)
    #dfIpPlanLine1 = dfIpPlan.head(1)
    dfIpPlan = dfIpPlan.head(1)
    #dfIpPlanLine1 = dfIpPlanLine1.reindex(
    #    columns=["AF", "P", "S", "V", "Y", "AB", "AG", "Q", "T", "W", "Z", "AC", "AE", "O", "R", "U", "X", "AA"])
    #print("dfIpPlanLine1:")
    #print(dfIpPlan)
    listForJson, sublistsTemp, listsTemp, dfIpPlan, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], dfIpPlan, len(dfIpPlan.columns), 0, sublistSite[5])
    listForJson.append(listsTemp)

    # Готовим данные для фильтрации. в нашем случае VV0203 VV3203 VV4203
    #print(sublistSite[5])
    #print(sublistSite[31])
    #print(sublistSite[33])
    # Собираем данные из БД для таблицы dfProductData2 для BaseBand.
    strDbQuery = f"""        
        SELECT 
            mecontext_id, 
            LEFT(mecontext_id, 6) AS Site, -- Возможно можно убрать
            CONCAT(REPLACE(productname, ' ', ''), ' [', serialNumber, ']') AS J
        FROM Config_Ericsson_BB.xParam_vsDataFieldReplaceableUnit
        WHERE
            `mecontext_id` LIKE '%{sublistSite[5]}%' OR `mecontext_id` LIKE '%{sublistSite[31]}%' OR `mecontext_id` LIKE '%{sublistSite[33]}%';
        """
    dfProductData2, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print("dfProductData2:")
    #print(dfProductData2)
    dfProductData2.columns = ["Nodeid", "Site", "ProductName" ]
    #print(dfProductData2)
    # выделяяем только строки с Baseband
    dfProductData2 = dfProductData2[dfProductData2['ProductName'].str.contains('Baseband')]
    #print(dfProductData2)
    # Собираем данные из БД для таблицы dfProductData1 для Radio, учел момент для таблиц бсс в 4г.
    strDbQuery = f"""        
            SELECT DISTINCT
                rl.NodeId,
                LEFT(rl.NodeId, 6) AS Site,
                IFNULL(
                    CONCAT(REPLACE(rf.productname, ' ', ''), ' [', rf.serialNumber, ']'), 
                    ' []'
                ) AS L,
                rl.riLinkId,
                rl.riPortRef1,
                rl.RRU,
                -- rl.RRU_port,
                -- Формируем столбец L: если оборудование найдено, выводим имя и серийник, иначе - пустые скобки
                -- rf.serialNumber,
                CASE 
                    WHEN rf.productname = 'Radio 2212 B3' THEN 'Radio22xx'
                    WHEN rf.productname = 'Radio 2217 B20' THEN 'Radio22xx'
                    WHEN rf.productname = 'Radio 2217 B7' THEN 'Radio22xx'
                    WHEN rf.productname = 'Radio 2219 B1' THEN 'Radio22xx'
                    WHEN rf.productname = 'Radio 2219 B3' THEN 'Radio22xx'
                    WHEN rf.productname = 'Radio 2219 B8' THEN 'Radio22xx'
                    WHEN rf.productname = 'Radio 4418 B40' THEN 'Radio44xx'
                    WHEN rf.productname = 'Radio 4418 B40T' THEN 'Radio44xx'
                    WHEN rf.productname = 'Radio 4428 B3' THEN 'Radio44xx'
                    WHEN rf.productname = 'RRUS 01 B1' THEN 'RRUS01'
                    WHEN rf.productname = 'RRUS 01 B8' THEN 'RRUS01'
                    WHEN rf.productname = 'RRUS 11 B1' THEN 'RRUS12'
                    WHEN rf.productname = 'RRUS 11 B7' THEN 'RRUS12'
                    WHEN rf.productname = 'RRUS 12 B3' THEN 'RRUS12'
                    WHEN rf.productname = 'RRUS 12 B8' THEN 'RRUS12'
                    WHEN rf.productname = 'Radio 2279 22B8 22B20 C' THEN 'Radio22xx'
                    ELSE 'Unknow'
                END AS M,
                CASE 
                    WHEN rf.productname = 'Radio 2212 B3' THEN '2/2'
                    WHEN rf.productname = 'Radio 2217 B20' THEN '2/2'
                    WHEN rf.productname = 'Radio 2217 B7' THEN '2/2'
                    WHEN rf.productname = 'Radio 2219 B1' THEN '2/2'
                    WHEN rf.productname = 'Radio 2219 B3' THEN '2/2'
                    WHEN rf.productname = 'Radio 2219 B8' THEN '2/2'
                    WHEN rf.productname = 'Radio 4418 B40' THEN '4/4'
                    WHEN rf.productname = 'Radio 4418 B40T' THEN '4/4'
                    WHEN rf.productname = 'Radio 4428 B3' THEN '4/4'
                    WHEN rf.productname = 'RRUS 01 B1' THEN '1/2'
                    WHEN rf.productname = 'RRUS 01 B8' THEN '1/2'
                    WHEN rf.productname = 'RRUS 11 B1' THEN '1/2'
                    WHEN rf.productname = 'RRUS 11 B7' THEN '2/2'
                    WHEN rf.productname = 'RRUS 12 B3' THEN '2/2'
                    WHEN rf.productname = 'RRUS 12 B8' THEN '2/2'
                    WHEN rf.productname = 'Radio 2279 22B8 22B20 C' THEN '2/2'
                    ELSE 'Unknow'
                END AS N,
                CASE 
                    WHEN rf.productname = 'Radio 2212 B3' THEN 'AB'
                    WHEN rf.productname = 'Radio 2217 B20' THEN 'AB'
                    WHEN rf.productname = 'Radio 2217 B7' THEN 'AB'
                    WHEN rf.productname = 'Radio 2219 B1' THEN 'AB'
                    WHEN rf.productname = 'Radio 2219 B3' THEN 'AB'
                    WHEN rf.productname = 'Radio 2219 B8' THEN 'AB'
                    WHEN rf.productname = 'Radio 4418 B40' THEN 'ABCD'
                    WHEN rf.productname = 'Radio 4418 B40T' THEN 'ABCD'
                    WHEN rf.productname = 'Radio 4428 B3' THEN 'ABCD'
                    WHEN rf.productname = 'RRUS 01 B1' THEN 'AB'
                    WHEN rf.productname = 'RRUS 01 B8' THEN 'AB'
                    WHEN rf.productname = 'RRUS 11 B1' THEN 'AB'
                    WHEN rf.productname = 'RRUS 11 B7' THEN 'AB'
                    WHEN rf.productname = 'RRUS 12 B3' THEN 'AB'
                    WHEN rf.productname = 'RRUS 12 B8' THEN 'AB'
                    WHEN rf.productname = 'Radio 2279 22B8 22B20 C' THEN 'AB'
                    ELSE 'Unknow'
                END AS O,
                IF(LEFT(rf.mecontext_id, 2) = 'VV' AND RIGHT(rf.productname, 2) = 'B3', 'true', 'false') AS P
            FROM Config_Ericsson_BB.RiLink rl
            LEFT JOIN Config_Ericsson_BB.xParam_vsDataFieldReplaceableUnit rf
                -- Джойним по двум полям, что эквивалентно сравнению склеенной колонки H и колонки I
                ON rl.NodeId = rf.mecontext_id 
               AND rl.RRU = rf.VsDataContainer_id
            WHERE
                rl.NodeId LIKE '%{sublistSite[5]}%' OR rl.NodeId LIKE '%{sublistSite[31]}%' OR rl.NodeId LIKE '%{sublistSite[33]}%';
            """
    dfProductData1, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print("dfProductData1:")
    #print(dfProductData1)
    dfProductData1.columns = ["Nodeid", "Site", "ProductName", "RiLinkId", "RiPort", "FieldReplaceableUnit",
                              "RRUS", "TX/RX", "RfPort", "RfSharing"]
    #print(dfProductData1)
    # Сортируем по буквам
    dfProductData1 = dfProductData1.sort_values(by='RiPort', ascending=True)
    #print(dfProductData1)
    # добавляем основную таблицу dfBbHwdata, объединив таблицу с ББ и радиоблоками
    dfBbHwdata = pd.merge(dfProductData2, dfProductData1, left_on="Nodeid", right_on="Nodeid", how="outer")
    print("dfBbHwdata:")
    #print(dfBbHwdata)
    dfProductData2 = dfProductData2.reindex(columns=["Nodeid", "ProductName"])
    print("dfProductData2:")
    #print(dfProductData2)
    # Собираем данные в JSON:
    subListBbHwData = []
    if checkTable(dfProductData2) == False:
        listNameBB = dfProductData2.values.tolist()#Думаю можно заменить listNameBB на listProductData2
        print("listNameBB:")
        #print(listNameBB)
        listBbLetters = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q"]
        dfNumbers = pd.DataFrame()
        for nodeId in listNameBB:
            dfRadioXX = dfBbHwdata.loc[dfBbHwdata["Nodeid"] == nodeId[0]]#Думаю можно заменить dfRadioXX на dfBbHwdata
            print("dfRadioXX:")
            #print(dfRadioXX)
            # 2. Проверяем, существует ли колонка перед сортировкой
            #if "RiLinkId" in dfRadioXX.columns:
            #    dfRadioXX = dfRadioXX.sort_values(by="RiLinkId", ascending=True)
            #else:
            #    print(f"Внимание! Колонка RiLinkId отсутствует. Доступные колонки: {list(dfRadioXX.columns)}")
            dfRadioXX = dfRadioXX.sort_values(by="RiLinkId", ascending=True)
            dfRadioXX = dfRadioXX.reindex(columns=["RiLinkId","ProductName_y"])
            #print(dfRadioXX)
            dfRadioXX2 = dfProductData1.loc[dfProductData1["Nodeid"] == nodeId[0]]#Думаю можно заменить dfRadioXX2 на dfProductData1
            print("dfRadioXX2:")
            #print(dfRadioXX2)
            dfRadioXX2 = dfRadioXX2.reindex(columns=["RiPort","RRUS","TX/RX","RfPort","RfSharing"])
            #print(dfRadioXX2)
            dfNumbers["RiLinkId"] = listNumbers[0:15]
            dfNumbers["RiPort"] = listBbLetters[0:15]
            print("dfNumbers, dfRadioXX:")
            #print(dfNumbers)
            dfRadioXX["RiLinkId"] = dfRadioXX["RiLinkId"].astype(int) #Меняется тип так как в след строке необходимо будет склеивать таблицы по данному столбцу
            dfRadioXX = pd.merge(dfNumbers, dfRadioXX, left_on="RiLinkId", right_on="RiLinkId", how="outer")
            #print(dfRadioXX)
            dfRadioXX = pd.merge(dfRadioXX, dfRadioXX2, left_on="RiPort", right_on="RiPort", how="outer")
            #pd.set_option("future.no_silent_downcasting", True)
            #dfRadioXX.fillna("", inplace=True)
            #print(dfRadioXX)
            dfRadioXXM = dfRadioXX.reindex(columns=["RRUS"])
            dfRadioXXM = dfRadioXXM.T
            dfRadioXXN = dfRadioXX.reindex(columns=["TX/RX"])
            dfRadioXXN = dfRadioXXN.T
            dfRadioXXO = dfRadioXX.reindex(columns=["RfPort"])
            dfRadioXXO = dfRadioXXO.T
            dfRadioXXP = dfRadioXX.reindex(columns=["RfSharing"])
            dfRadioXXP = dfRadioXXP.T
            dfRadioXX = dfRadioXX.reindex(columns=["ProductName_y"])
            dfRadioXX = dfRadioXX.T
            #print(dfRadioXX)
            if (checkTable(dfRadioXX) == False) and (checkTable(dfRadioXXM) == False) and (checkTable(dfRadioXXN) == False) and (checkTable(dfRadioXXO) == False) and (checkTable(dfRadioXXP) == False):
                listBbHw= []#Думаю можно переименовать listBbHw на listTemp                
                listRadioXX = dfRadioXX.values.tolist()
                listRadioXXM = dfRadioXXM.values.tolist()
                listRadioXXN = dfRadioXXN.values.tolist()
                listRadioXXO = dfRadioXXO.values.tolist()
                listRadioXXP = dfRadioXXP.values.tolist()
                listBbHw.append(nodeId[0])
                print("listBbHw:")
                listBbHw.append(nodeId[1])
                #print(listBbHw)
                for radioXX in listRadioXX[0]:
                    listBbHw.append(radioXX)
                for radioXX in listRadioXXM[0]:
                    listBbHw.append(radioXX)
                for radioXX in listRadioXXN[0]:
                    listBbHw.append(radioXX)
                for radioXX in listRadioXXO[0]:
                    listBbHw.append(radioXX)
                for radioXX in listRadioXXP[0]:
                    listBbHw.append(radioXX)
                #print(listBbHw)
                subListBbHwData.append(listBbHw)
                print("subListBbHwData:")
                #print(subListBbHwData)
            else:
                print("- There is no data "+sublistSite[5]+" in the Er_Data file sheet RadioXX from table (dfRadioXX)")
    else:
        print("- There is no data "+sublistSite[5]+" in the Er_Data file sheet RadioXX from table (dfRadioXX)")
        listBbHwData = [["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                        "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                        "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]]
        print(listBbHwData)
    listForJson.append(subListBbHwData)

    # Готовим данные для фильтрации. в нашем случае VV0203 VV3203 VV4203, 203, VLD321
    #Ищем названием контроллера
    if len(listForJson[2]) == 0:
        sublistSite.append([["", "", "", "", "", "", "","", "", "", "", "", "", "","", "", "", ""]])
    else:
        sublistSite.append(listForJson[2])
    print("sublistSite:")
    #print(sublistSite)
    #print(sublistSite[-1][0][1])
    #print(sublistSite[-1][0][3])
    #print(sublistSite[5])
    #print(sublistSite[31])
    #print(sublistSite[33])
    # Собираем данные из БД для таблицы DU HW data. первая необохимдая таблица из БД - HW_2G
    strDbQuery = f"""        
        SELECT
        --	*
        --    BSC, rULogicalId, rUSerialNo, rULogicalIdExt,
            rSite,
        --    SUBSTRING(rSite, 4) AS G12TgId,
            CONCAT(`BSC`, '_OTG-', SUBSTRING(rSite, 4)) AS M,
            CONCAT(
                (CASE 
                    WHEN (
                        LEFT(
                            (CONCAT(
                                IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                            ))
                        , 20)
                    ) = 'CABI RBS 6601' THEN 'RBS6601'
                    WHEN (
                        LEFT(
                            (CONCAT(
                                IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                            ))
                        , 20)
                    ) = 'DX   DUG 20 01' THEN 'DUG2001'
                    WHEN (
                        LEFT(
                            (CONCAT(
                                IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                            ))
                        , 20)
                    ) = 'MCTR Radio 2219 B3' THEN 'Radio2219B3'
                    WHEN (
                        LEFT(
                            (CONCAT(
                                IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                            ))
                        , 20)
                    ) = 'MCTR Radio 2219 B8' THEN 'Radio2219B8'
                    WHEN (
                        LEFT(
                            (CONCAT(
                                IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                            ))
                        , 20)
                    ) = 'MCTR Radio 4428 B3' THEN 'Radio4428B3'
                    WHEN (
                        LEFT(
                            (CONCAT(
                                IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                            ))
                        , 20)
                    ) = 'MCTR RRUS 01 B3' THEN 'RRUS01B3'
                    WHEN (
                        LEFT(
                            (CONCAT(
                                IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                            ))
                        , 20)
                    ) = 'MCTR RRUS 01 B8' THEN 'RRUS01B8'
                    WHEN (
                        LEFT(
                            (CONCAT(
                                IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                            ))
                        , 20)
                    ) = 'MCTR RRUS 12 B3' THEN 'RRUS12B3'
                    WHEN (
                        LEFT(
                            (CONCAT(
                                IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                            ))
                        , 20)
                    ) = 'MCTR RRUS 12 B8' THEN 'RRUS12B8'
                    WHEN (
                        LEFT(
                            (CONCAT(
                                IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                            ))
                        , 20)
                    ) = 'SC   SUP 6601' THEN 'SUP6601'
                    WHEN (
                        LEFT(
                            (CONCAT(
                                IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                            ))
                        , 20)
                    ) = 'MCTR Radio 2279 22B8' THEN 'Radio227922B8'
                    ELSE 'Unknow'
                END), ' [', rUSerialNo,']'
            ) AS Q,
            CASE
                WHEN
                    # Find col T from excel:
                    (CASE 
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'CABI RBS 6601' THEN '21'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'DX   DUG 20 01' THEN '20'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR Radio 2219 B3' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR Radio 2219 B8' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR Radio 4428 B3' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR RRUS 01 B3' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR RRUS 01 B8' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR RRUS 12 B3' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR RRUS 12 B8' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'SC   SUP 6601' THEN '22'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR Radio 2279 22B8' THEN '01'
                        ELSE 'Unknow'
                    END) = '20'
                THEN '9'
                # Find col T from excel:
                WHEN 
                    (CASE 
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'CABI RBS 6601' THEN '21'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'DX   DUG 20 01' THEN '20'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR Radio 2219 B3' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR Radio 2219 B8' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR Radio 4428 B3' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR RRUS 01 B3' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR RRUS 01 B8' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR RRUS 12 B3' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR RRUS 12 B8' THEN '01'
                        WHEN (
                            LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'SC   SUP 6601' THEN '22'
                        WHEN # find col R from excel:
                            (LEFT(
                                (CONCAT(
                                    IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                    IF(rULogicalIdExt = 'nan' OR rULogicalIdExt IS NULL, '', rULogicalIdExt)
                                ))
                            , 20)
                        ) = 'MCTR Radio 2279 22B8' THEN '01'
                    ELSE 'Unknow'
                END) = '01'
                THEN (CAST(RIGHT(
                        (        
                            CONCAT(
                                IF(rULogicalId = 'nan' OR rULogicalId IS NULL, '', rULogicalId),
                                IF(rULogicalIdExt = 'nan' OR rULogicalIdExt = '' OR rULogicalIdExt IS NULL, '                                0', rULogicalIdExt)
                            )        
                        ), 2) AS SIGNED))        
                ELSE 'Unknow'
            END AS U
        FROM hwBSS_Ericsson.BTS_ENM
        WHERE 
            (BSC LIKE '%{sublistSite[-1][0][1]}%') AND (rSite LIKE '%{sublistSite[5]}%' OR rSite LIKE '%{sublistSite[31]}%' OR rSite LIKE '%{sublistSite[33]}%')
        --	rSite LIKE '%BU0161%' OR rSite LIKE '%BU3161%' OR rSite LIKE '%BU4161%' OR rSite LIKE '%BU5161%' OR
        --	rSite LIKE '%VV0203%' OR rSite LIKE '%VV3203%' OR rSite LIKE '%VV4203%' OR rSite LIKE '%VV5203%'
        order by U
        ; 
        """
    dfHw2g, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print("dfHw2g:")
    print("ВНИМАНИЕ! Не правильный порядок р/б.")
    # Не правильный порядок р/б.
    #print(dfHw2g)
    dfHw2g.columns = ["Site", "M", "Q", "R"]
    #print(dfHw2g)
    #Получаем глаывную таблицу dfDuHwData
    dfDuHwData = dfHw2g[~dfHw2g["R"].str.startswith("Unknow")]
    print("dfDuHwData:")
    #print(dfDuHwData)
    # Удаляем дубликацию в стобце Q и делаем сортировку строк (в приоритере DU) и нумерацию:
    dfDuHwData = dfDuHwData.reindex(columns=["Site", "M", "Q"])
    dfDuHwData = dfDuHwData.drop_duplicates()
    dfDuHwData = dfDuHwData.sort_values(by='Q', key=lambda x: ~x.str.startswith('DU'))
    #print(dfDuHwData)
    #print(len(dfDuHwData))
    #print(listNumbers[0:4])
    dfDuHwData["Numbers"] = listNumbers[0:len(dfDuHwData)]
    print(dfDuHwData.dtypes)
    #print(dfDuHwData)
    #dfDuHwData["U"] = dfDuHwData["U"].astype("int64")
    # Добавляем стоблец с нумерацией для фиксации строк в таблице, необходимо 5 (Здесь уже можно добавлять, если больше Р/бл будет)
    dfNumbers = pd.DataFrame()  # Уже дублировалась переменная, возможно стоит переименовать ее в dfTemp
    choselistNumbers, dfNumbers = funcAddNumbers(listNumbers[0:5], dfNumbers)
    print("dfNumbers:")
    #print(dfNumbers)
    dfDuHwData = pd.merge(dfDuHwData, dfNumbers, left_on="Numbers", right_on="Numbers", how="outer")
    #dfDuHwData = dfDuHwData.drop([4, 5, 6, 7])
    print("dfDuHwData:")
    #print(dfDuHwData)
    # Меняем форму таблицы
    dfDuHwData = dfDuHwData.reindex(columns=["Q"])
    #print(dfDuHwData)
    dfDuHwData = dfDuHwData.T
    #print(dfDuHwData)
    dfDuHwData = dfDuHwData.set_axis(['DU', '1', '2', '3', '4'], axis=1)
    dfDuHwData["Name"] = sublistSite[-1][0][1] + "_OTG-" + sublistSite[-1][0][3]
    #print(dfDuHwData)
    listForJson, sublistsTemp, listsTemp, dfDuHwData, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], dfDuHwData, len(dfDuHwData.columns), 0, sublistSite[5])
    listForJson.append(listsTemp)

    # Собираем данные из БД для таблицы DU HW data. первая необохимдая таблица из БД - duData. Данная таблица уже была по названию сопадает.
    strDbQuery = f"""        
        SELECT 
            node AS ManagedElement,
            SC,
            LEFT(`SC`, 1) AS Numb,
        --    productName, 
            CONCAT(node, LEFT(SC, 1)) AS U,
            CONCAT(REPLACE(productName, ' ', ''), ' [', serialNumber, ']') AS V 
        FROM Config_Ericsson4g.dbo_xParam4_AuxPlugInUnit 
        WHERE 
            `node` LIKE '%{sublistSite[5]}%' OR `node` LIKE '%{sublistSite[31]}%' OR `node` LIKE '%{sublistSite[33]}%'
        UNION ALL
        -- Второй запрос
        SELECT 
            ManagedElement,
            "" AS SC,
            "" AS Numb,
        --    SUBSTRING(manufacturerData, LOCATE('ProductName=', manufacturerData) + 12) AS productName, 
            ManagedElement AS U,
            CONCAT(REPLACE(SUBSTRING(manufacturerData, LOCATE('ProductName=', manufacturerData) + 12), ' ', ''), ' [', serialNumber, ']') AS V 
        FROM hwBSS_Ericsson.WBTS_LNBTS 
        WHERE (
            `ManagedElement` LIKE '%{sublistSite[5]}%' OR `ManagedElement` LIKE '%{sublistSite[31]}%' OR `ManagedElement` LIKE '%{sublistSite[33]}%'
        ) AND (manufacturerData LIKE '%DUW%' OR manufacturerData LIKE '%DUS%');
        """
    dfDuData, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print("dfDuData:")
    #rint(dfDuData)
    dfDuData.columns = ["NodeId", "hwName", "Numeric", "Sector", "productName"]
    #print(dfDuData)
    # Удаляем дубликацию в стобце Q и делаем сортировку строк (в приоритере DU) и нумерацию:
    dfDuData = dfDuData.sort_values(by='productName', key=lambda x: ~x.str.startswith('DU'))
    #print(dfDuData)
    print(len(dfDuData))
    #print(listNumbers[0:4])
    dfDuData["Numbers"] = listNumbers[0:len(dfDuData)]
    print(dfDuData.dtypes)
    #print(dfDuData)
    # Добавляем стоблец с нумерацией для фиксации строк в таблице, необходимо 5 (Здесь уже можно добавлять, если больше Р/бл будет)
    choselistNumbers, dfNumbers = funcAddNumbers(listNumbers[0:5], dfNumbers)
    print("dfNumbers:")
    #print(dfNumbers)
    dfDuData = pd.merge(dfDuData, dfNumbers, left_on="Numbers", right_on="Numbers", how="outer")
    print("dfDuData:")
    #print(dfDuData)
    # Меняем форму таблицы
    #node_id = dfDuData.loc[0, 'NodeId']
    print(dfDuData.loc[0, 'NodeId'])
    bsName = dfDuData.loc[0, 'NodeId']
    dfDuData = dfDuData.reindex(columns=["productName"])
    # print(dfDuData)
    dfDuData = dfDuData.T
    dfDuData = dfDuData.set_axis(['DU', '1', '2', '3', '4'], axis=1)
    dfDuData["Name"] = bsName
    #print(dfDuData)
    listForJson, sublistsTemp, listsTemp, dfDuData, lenObjs, lenList, sublistSite[5] = funcAddListFromTable(
        listForJson, [], [], dfDuData, len(dfDuData.columns), 0, sublistSite[5])
    listForJson.append(listsTemp)

    # Готовим данные для фильтрации. в нашем случае то что ввел пользователь, сумму TRX, Power, LTE Bandwidth
    #print(sublistSite)
    #print(sublistSite[5])
    # Собираем данные из БД для таблицы DU HW data. первая необохимдая таблица из БД - duData. Данная таблица уже была по названию сопадает.
    strDbQuery = f"""        
        SELECT 
            SITEID, 
            `GSMCellCarrierTRXERS`, `WCDMANumberofCellCarriersHWAC`, `OutputPower20WStep`,    
            `EricssonLeanCarrier`, --	Необходимо уточнить столбцы, тк имеются похожие совпадения: LTEFDDBasePackage, CarrierAggregation, LTEDifferentiatedMobileBroadband, FrequencySynchronization, HighLoadHandling, LTEOffloadtoWCDMA, MaximumCellRange, MixedModeRadioNodeLTE, MulticarrierLoadManagement, RANDataCollection, ServiceBasedMobility, SelfOrganizingNetworks, TNPerformanceMonitoring, CoMP, VoLTE, VoLTEPerformance, AdvancedCarrierAggregation, UplinkSpectrumAdaptation, EnergyEfficiencyLTE
            `GSMCellCarrierTRXERS` AS GSMCellCarrierTRXERSCapacity,
            `WCDMANumberofCellCarriersHWAC` AS WCDMANumberofCellCarriersHWACCapacity,
            ((`OutputPower20WStep`-`WCDMANumberofCellCarriersHWAC`+3)*20) AS OutputPower20WStepCapacity,
            (`EricssonLeanCarrier`*5) AS EricssonLeanCarrierCapacity
        FROM License_Ericsson.LICENSE
        WHERE 
            `SITEID` LIKE '%{sublistSite[5]}%'; -- BU0001, BU0085, BU0113, BU0161, VV0203, VV0067, VV0181
        """
    dfLicense, strDbQuery, strDbIp, strDbUser, strDbPasswd, strDbName = funcMysqlPandas3(
        pd.DataFrame(), strDbQuery,
        settings.CONFIG_DATA.get("IPDBERICSSON"), settings.CONFIG_DATA.get("USERDBNOKIA"),
        settings.CONFIG_DATA.get("PASSWORDDBNOKIA"), settings.CONFIG_DATA.get("NAMEDBNOKIA")
    )
    print("dfLicense:")
    #print(dfLicense)
    dfLicense.columns = ["site", "GSMCellCarrierTRXERS", "WCDMANumberofCellCarriersHWAC", "OutputPower20WStep",
                         "EricssonLeanCarrier", "GSMCellCarrierTRXERSCapacity", "WCDMANumberofCellCarriersHWACCapacity",
                         "OutputPower20WStepCapacity", "EricssonLeanCarrierCapacity"]
    #print(dfLicense)
    # Добавлем основную таблицу
    dfBbLicense = dfLicense.head(1) # Взял тупо перую строку, поэтому надо проверить
    print("dfBbLicense:")
    #print(dfBbLicense)
    sublistBbLicense = dfBbLicense.values.tolist()
    print("sublistBbLicense:")
    #print(sublistBbLicense)
    # Учитываем путсые значения. так как они нужны будут в дальнейшем:
    if len(sublistBbLicense) == 0:
        print("true")
        sublistBbLicense.append(["0", "0", "0", "0", "0", "0", "0", "0", "0"]) #  неободимо учесть пустые значения по длине списка.
    #print(sublistBbLicense)
    # Готовим данные для фильтрации. в нашем случае TRX, power, LTE Bandwidth. Выше уже есть такой код. стоит добавить в функцию.
    #Ищем название trx
    #print(listForJson[2])
    print("sublistSite:")
    #print(sublistSite)
    listTrx = [] # очистим прееменную
    # Перебираем каждую строку в таблице
    for index in sublistSite[-1]:
        # Берем 13-й элемент и добавляем в наш список
        listTrx.append(index[13])
    print("listTrx:")
    #print(listTrx)
    # Находим сумму:
    intTotalTrx = 0 # очистим прееменную
    print("strTemp:")
    for strTemp in listTrx:
        #print(strTemp)
        # необходимо проверить на наличие пустых значений и преобраовать в 0 если они есть
        if strTemp == "":
            strTemp = "0"
        #print(strTemp)
        intTotalTrx = intTotalTrx + int(strTemp)
    print("intTotalTrx:")
    #print(intTotalTrx)
    # Выше уже есть похожий код ниже. стоит добавить в функцию.
    #print(listForJson[4])
    if len(listForJson[4]) == 0:
        print("true")
        sublistSite.append([["", "", "", "","", "", "", "", "", "", "", ""]]) #  неободимо учесть пустые значения, по длине списка. лучше наверное 9 добавить
    else:
        print("false")
        sublistSite.append(listForJson[4])
    print("sublistSite:")
    #print(sublistSite)
    # Выше уже есть похожий код ниже. стоит добавить в функцию.
    listTemp2 = [] # очистим прееменную
    # Перебираем каждую строку в таблице
    for index in sublistSite[-1]:
        # Берем 1-й элемент и добавляем в наш список
        listTemp2.append(index[0])
    print("listTemp2:")
    #print(listTemp2)
    # Выше уже есть похожий код ниже. стоит добавить в функцию.
    # Находим сумму:
    intTotalBandwidth = 0  # очистим прееменную
    print("strTemp:")
    for strTemp in listTemp2:
        # print(strTemp)
        # необходимо проверить на наличие пустых значений и преобраовать в 0 если они есть
        if strTemp == "":
            strTemp = "0"
        #print(strTemp)
        intTotalBandwidth = intTotalBandwidth + int(strTemp)
    print("intTotalBandwidth:")
    #print(intTotalBandwidth)
    # Выше уже есть похожий код ниже. стоит добавить в функцию.
    listTemp2 = [] # очистим прееменную
    # Перебираем каждую строку в таблице
    for index in sublistSite[-1]:
        # Берем 1-й элемент и добавляем в наш список
        listTemp2.append(index[7])
    print("listTemp2:")
    #print(listTemp2)
    # Выше уже есть похожий код ниже. стоит добавить в функцию.
    # Находим сумму:
    intTotalPower= 0  # очистим прееменную
    print("strTemp:")
    for strTemp in listTemp2:
        # print(strTemp)
        # необходимо проверить на наличие пустых значений и преобраовать в 0 если они есть
        if strTemp == "":
            strTemp = "0"
        # print(strTemp)
        intTotalPower = intTotalPower + int(strTemp)
    print("intTotalPower:")
    #print(intTotalPower)
    # находим TRX по формуле: =ЕСЛИ(J12+J14+J15=0;9999;ЕСЛИ(K12-B40<0;0;K12-B40))&" TRX"
    #print(int(sublistBbLicense[0][1])) # J12
    #print(int(sublistBbLicense[0][4])) # J14
    #print(int(sublistBbLicense[0][3])) # J15
    #print(int(sublistBbLicense[0][5])) # K12
    #print(intTotalTrx) # B40
    intFreeTrx = 0
    if (int(sublistBbLicense[0][1]) + int(sublistBbLicense[0][4]) + int(sublistBbLicense[0][3])) == 0:
        intFreeTrx = 9999
    # ... ЕСЛИ(K12-B40<0; 0; K12-B40)
    elif (int(sublistBbLicense[0][5]) - intTotalTrx) < 0:
        intFreeTrx = 0
    else:
        intFreeTrx = int(sublistBbLicense[0][5]) - intTotalTrx
    print("intFreeTrx:")
    #print(intFreeTrx)
    # Находим LTE band =ЕСЛИ(J12+J14+J15=0;9999;ЕСЛИ(K14-C33<0;0;K14-C33))&" MHz" . формула повторяется, мб в функция добавить?
    #print(int(sublistBbLicense[0][8])) # K14
    #print(intTotalBandwidth) # C33
    intFreeMhz = 0
    if (int(sublistBbLicense[0][1]) + int(sublistBbLicense[0][4]) + int(sublistBbLicense[0][3])) == 0:
        intFreeMhz = 9999
    elif (int(sublistBbLicense[0][8]) - intTotalBandwidth) < 0:
        intFreeMhz = 0
    else:
        intFreeMhz = int(sublistBbLicense[0][8]) - intTotalBandwidth
    print("intFreeMhz:")
    #print(intFreeMhz)
    # Находим power =ЕСЛИ(J12+J14+J15=0;9999;ЕСЛИ(K15-B33<0;0;K15-B33))&" W" . формула повторяется, мб в функция добавить?
    #print(int(sublistBbLicense[0][7])) # K15
    #print(intTotalPower) # B33
    intFreeW = 0
    if (int(sublistBbLicense[0][1]) + int(sublistBbLicense[0][4]) + int(sublistBbLicense[0][3])) == 0:
        intFreeW = 9999
    elif (int(sublistBbLicense[0][7]) - intTotalPower) < 0:
        intFreeW = 0
    else:
        intFreeW = int(sublistBbLicense[0][7]) - intTotalPower
    print("intFreeW:")
    #print(intFreeW)
    # Добавляем полученные значения в список sublistBbLicense. Возможно стоит добавить в таблицу а не в список, чтобы был прядок в коде
    sublistBbLicense[0].extend([intFreeTrx, intFreeW, intFreeMhz])
    #print(sublistBbLicense)
    print("listForJson:")
    listForJson.append(sublistBbLicense)
    #print(listForJson)

    return reg, numb, band, listForJson
def getDjangoData(request):
    #listContents = Content.objects.all()
    listContents = Content.objects.only('id', 'title', 'idcard', 'idmenu', 'author', 'date')
    #print(listContents)
    jsonContents = {}

    for raw in listContents:
        #print(raw.idmenu)
        if raw.idmenu not in jsonContents:
            jsonContents[raw.idmenu] = [] # Добавить Menu из модели в словарь jsonContents
        jsonContents[raw.idmenu].append({
            'id': raw.id,
            'title': raw.title,
            'content': raw.content,
            'idcard': raw.idcard,
            'idmenu': raw.idmenu,
            'author': raw.author,
            'date': raw.date
        })# Добавить Весь контент из модели в словарь jsonContents
    #print(jsonContents)
    #for j_key, j_value in jsonContents.items():
        #print(j_key) # Отобразить на сайте ключ из словаря jsonContents type - str
        #print(j_value[0]) # Отобразить на сайте значения из словаря jsonContents type - dict
        #print(j_value[0]['idmenu']) # Отобразить на сайте значения idmenu из словаря jsonContents type - str
    #    for item in j_value:
            #print(item['idcard']) # Отобразить на сайте все значения idcard из словаря jsonContents type - str
    #        if item['idcard'] == 'MiniCard':
                #print(item['title'])
                #print(item['content'])            
    #            print("true") # Отобразить на сайте значения title и content из словаря, у которых idcard MiniCard

    combined_context = {
        **{'jsonContents': jsonContents},
        }
    #print(combined_context)
    return render(request, 'index.html', combined_context)
def funcEricssonRet(request):
    jsonContents = {}
    listMain = []

    listContents = Content.objects.all()
    for raw in listContents:
        if raw.idmenu not in jsonContents:
            jsonContents[raw.idmenu] = []
        jsonContents[raw.idmenu].append({
            "id": raw.id,
            "title": raw.title,
            "content": raw.content,
            "idcard": raw.idcard,
            "idmenu": raw.idmenu,
            "author": raw.author,
            "date": raw.date
        })

    if request.method == "POST":
        inputReg = request.POST.get("Reg")
        inputNumber = request.POST.get("NS")
        inputBB = request.POST.get("BB")
        inputReg, inputNumber, inputBB, listMain = funcEricssonRetList(inputReg, inputNumber, inputBB, listMain)
        print(listMain)
        #listMain, indexList = funcTestingOutList(listMain, 0)

    combined_context = {
        **{"jsonContents": jsonContents},
        **{"listMain": listMain},
        }
    return render(request, "pageEricssonRet.html", combined_context)
def funcNokia(request):
    jsonContents = {}
    listMain = []
    #Получаем данные из Админки
    #listContents = Content.objects.all()
    #listContents = Content.objects.only('id', 'title', 'idcard', 'idmenu', 'author', 'date')
    listContents = Content.objects.only('id', 'title', 'idcard', 'idmenu', 'author', 'date', 'content')
    for raw in listContents:
        if raw.idmenu not in jsonContents:
            jsonContents[raw.idmenu] = []
        jsonContents[raw.idmenu].append({
            "id": raw.id,
            "title": raw.title,
            "content": raw.content,
            "idcard": raw.idcard,
            "idmenu": raw.idmenu,
            "author": raw.author,
            "date": raw.date
        })

    # Получаем данные из Общих страниц
    if request.method == "POST":
        # Готовим данные которые ввел пользователь на странице:
        #inputReg = request.POST.get("Reg")
        #inputNumber = request.POST.get("NS")
        #inputBB = request.POST.get("BB")
        #inputNameBS = request.POST.get("NanemSS")
        inputNameBS = request.POST.get("NanemSS", "").strip()  # Получаем строку и убираем лишние пробелы
        #print(inputNameBS)
        #print(inputNameBS[:2])
        #print(inputNameBS[2:])
        # Готовим таблицы в виде json:
        #inputReg, inputNumber, listMain = funcNokiaList(inputNameBS[:2], str(int(inputNameBS[2:])), listMain)# str(int(inputNameBS[2:])) используется для того что бы учесть нули в комере БС 000x
        # Проверяем: если поле пустое или в нем меньше 3 символов (например, ввели только "IR")
        if not inputNameBS or len(inputNameBS) < 3:
            # Создаем контекст с ошибкой и сразу отдаем страницу, не ломая сервер
            combined_context = {
                "jsonContents": jsonContents,
                "listMain": listMain,
                "error_message": "Пожалуйста, введите корректное имя БС (например, IR2664)"
            }
            return render(request, "pageNokia.html", combined_context)
        # Если проверка прошла, безопасно обрабатываем имя БС
        try:
            inputReg = inputNameBS[:2]
            inputNumber = str(int(inputNameBS[2:]))  # Теперь здесь не будет ошибки, так как цифры точно есть
            # Вызываем нашу обновленную быструю функцию
            inputReg, inputNumber, listMain = funcNokiaList(inputReg, inputNumber, listMain)
        except ValueError:
            # На случай, если пользователь ввел буквы там, где должны быть цифры (например, "IRabcd")
            combined_context = {
                "jsonContents": jsonContents,
                "listMain": listMain,
                "error_message": "Неверный формат имени БС. После букв должны идти цифры."
            }
            return render(request, "pageNokia.html", combined_context)
        #print(listMain)
        # Тестируем список:
        #listMain, indexList = funcTestingOutList(listMain, 1)
    # Собираем JSONs:
    combined_context = {
        **{"jsonContents": jsonContents},
        **{"listMain": listMain},
        }
    return render(request, "pageNokia.html", combined_context)
def funcEricsson(request):
    jsonContents = {}
    listMain = []

    #Получаем данные из Админки
    #listContents = Content.objects.all()
    listContents = Content.objects.only('id', 'title', 'idcard', 'idmenu', 'author', 'date')
    for raw in listContents:
        if raw.idmenu not in jsonContents:
            jsonContents[raw.idmenu] = []
        jsonContents[raw.idmenu].append({
            "id": raw.id,
            "title": raw.title,
            "content": raw.content,
            "idcard": raw.idcard,
            "idmenu": raw.idmenu,
            "author": raw.author,
            "date": raw.date
        })

    # Получаем данные из Общих страниц
    if request.method == "POST":
        # Готовим данные которые ввел пользователь на странице:
        #inputReg = request.POST.get("Reg")
        #inputNumber = request.POST.get("NS")
        #inputBB = request.POST.get("BB")
        inputNameBS = request.POST.get("NanemSS")
        #print(inputNameBS)
        #print(inputNameBS[:2])
        #print(inputNameBS[2:])
        #print(inputNameBS[2:6])
        #print(inputNameBS[6:])
        # Готовим таблицы в виде json:
        inputReg, inputNumber, inputBand, listMain = funcEricssonList(inputNameBS[:2], str(int(inputNameBS[2:6])), inputNameBS[6:], listMain)# str(int(inputNameBS[2:])) используется для того что бы учесть нули в комере БС 000x
        #print(listMain)
        # Тестируем список:
        #listMain, indexList = funcTestingOutList(listMain, 1)

    # Собираем JSONs:
    combined_context = {
        **{"jsonContents": jsonContents},
        **{"listMain": listMain},
        }
    return render(request, "pageEricsson.html", combined_context)
def funcUpdateDbInfo(request):
    jsonContents = {}
    listMain = []

    #Получаем данные из Админки
    #listContents = Content.objects.all()
    listContents = Content.objects.only('id', 'title', 'idcard', 'idmenu', 'author', 'date')
    for raw in listContents:
        if raw.idmenu not in jsonContents:
            jsonContents[raw.idmenu] = []
        jsonContents[raw.idmenu].append({
            "id": raw.id,
            "title": raw.title,
            "content": raw.content,
            "idcard": raw.idcard,
            "idmenu": raw.idmenu,
            "author": raw.author,
            "date": raw.date
        })

    # Получаем данные из Общих страниц
    if request.method == "POST":
        from scripts import addDfMysql
        # Готовим таблицы в виде json:
        listMain = addDfMysql.funcRunBuntton()
        print("listMain:")
        print(listMain)
        # Тестируем список:
        #listMain, indexList = funcTestingOutList(listMain, 1)
    # Собираем JSONs:
    combined_context = {
        **{"jsonContents": jsonContents},
        **{"listMain": listMain},
        }
    return render(request, "pageUpdateDbInfo.html", combined_context)
