from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import json
import time
import csv
#
url="https://igis-transport.ru/izh/"
#
headers = {
    "Accept": "*/*",
}
def get_tranport_type():
    req = requests.get(url,headers=headers)
    src = req.text
    soup = BeautifulSoup(src,"lxml")
    all_transport_hrefs = soup.find(class_="col-6-m").find(class_="city").find_all(class_="full")
    transport_categories_dict = {}
    for item in all_transport_hrefs:
        #print(item.find(class_="transport-label"))
        if(item.find(class_="transport-label") != None):
            transport_name = item.find(class_="transport-label").get_text().replace('\n','',2).strip()
            transport_href = "https://igis-transport.ru" + item.get("href")
            transport_categories_dict[transport_name] = transport_href
    with open("all_categories_dict.json", "w") as file:
        json.dump(transport_categories_dict, file,indent=4,ensure_ascii=False)



def get_transport_num():
    with open("all_categories_dict.json","r") as file:
        all_categories = json.load(file)
    for category_name, category_href in all_categories.items():
        req=requests.get(url=category_href,headers=headers)
        src=req.text
        soup = BeautifulSoup(src,"lxml")
        #Собираю заголовки таблицы
        table_head = soup.find("table",class_="route").find("thead").find("tr").find_all("th")
        route_num = table_head[0].text
        final_stops = table_head[1].text
        with open(f"data/{category_name}.csv","w",encoding='utf-8',newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    final_stops,route_num,"url"
                ]
            )
        with open(f"data/{category_name}.json", "w") as file:
            json.dump({"response":{}},file,indent=4,ensure_ascii=False)
        with open(f"data/{category_name}.json", "r") as file:
            data = json.load(file)
        transport_data = soup.find("table", class_="route").find("tbody").find_all("tr")
        for item in transport_data:
            transport_td = item.find_all("td")
            transport_data_stops = transport_td[1].text.strip()
            transport_data_num = transport_td[0].text.strip()
            transport_data_href ="https://igis-transport.ru" + transport_td[1].find("a").get("href")
            with open(f"data/{category_name}.csv", "a",newline='',encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([transport_data_stops,transport_data_num,transport_data_href])
            data['response'][str(transport_data_num)]=[transport_data_stops,transport_data_href]
            if(int(transport_data_num) == 79):
                break
        with open(f"data/{category_name}.json", "w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


# Функция парсера
def parse(url):
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    return soup


#Функция подгружает страницу вместе со всеми скриптами, а после возвращает html код
def page_load(url):
    src=r"D:\chromedriver.exe"
    browse = webdriver.Chrome(executable_path=src)
    try:
        browse.get(url=url)
        time.sleep(3)
        elem = browse.page_source
        with open("page.html", "w", encoding="UTF-8") as file:
            file.write(elem)
    except Exception as e:
        print(e)


#Иследование расположения транспорта
def position(transport_num,type_transport):
    #transport_num = "29"
    #type_transport = "Автобус"
    with open(f"data/{type_transport}.json","r") as file:
        all_categories = json.load(file)
    for item in all_categories:
        for item1 in all_categories[str(item)]:
            if(int(item1)==int(transport_num)):
                url = all_categories[str(item)][str(item1)][1]
                page_load(url)
                with open("page.html","r",encoding="UTF-8") as file:
                    src = file.read()
                soup = BeautifulSoup(src,"lxml")
                data = soup.find(class_="swipe-route").find(class_="row swipe-out").find_all(class_="col col-6-m route")
                dict_transport = []
                flag = True
                for i in data:
                    data_row = i.find_all(class_="row")
                    count = 0
                    for j in data_row:
                        if(j.find(class_="position") != None and j.find(class_="position").find("a") != None):
                            dict_row ={}
                            data_name=j.find(class_="name").text.strip()
                            if(len(data_name)>=2):
                                dict_row['Position']="Stops"
                                dict_row['Stops']=data_name.strip()
                                if flag == True:
                                    dict_row['Orient'] = "Left"
                                    dict_row['Ending_Stops'] = data[0].find(class_="summary").text.strip()
                                else:
                                    dict_row['Orient'] = "Right"
                                    dict_row['Ending_Stops'] = data[1].find(class_="summary").text.strip()
                            else:
                                list_two_tops=[data_row[count-1].find(class_="name").text.strip(),data_row[count+1].find(class_="name").text.strip()]
                                dict_row['Position'] = "Between_Stops"
                                dict_row['Stops'] = list_two_tops
                                if flag==True:
                                    dict_row['Orient']="Left"
                                    dict_row['Ending_Stops']=data[0].find(class_="summary").text.strip()
                                else:
                                    dict_row['Orient']="Right"
                                    dict_row['Ending_Stops'] = data[1].find(class_="summary").text.strip()
                            dict_transport.append(dict_row)
                        count+=1
                    flag=False
                break
    with open("data/transport_position.json","w") as file:
        json.dump(dict_transport,file,indent=4,ensure_ascii=False)
    return dict_transport
#get_tranport_type()
#position("29","Автобус")
