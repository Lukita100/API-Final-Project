import requests
from bs4 import BeautifulSoup
import pandas as pd
import lxml
import mysql.connector


url="https://en.wikipedia.org/wiki/List_of_Grand_Slam_men%27s_singles_champions"
data = requests.get(url)
soup=BeautifulSoup(data.text,'html.parser')
tables= soup.findAll('table')
table=tables[4]
t=table.findAll('tr')

connection = mysql.connector.connect(
    host="127.0.0.1",
    port="3306",
    user="root",
    password="",
    database="grand_slams")
cursor=connection.cursor()
creation=("CREATE TABLE titles (Titles VARCHAR(255), Player VARCHAR(255) PRIMARY KEY, Amateur_Era VARCHAR(255), Open_Era VARCHAR(255), Australian_Open VARCHAR(255), Roland_Garros VARCHAR(255), Wimbledon VARCHAR(255), US_Open VARCHAR(255), Years VARCHAR(225))")
cursor.execute(creation)

a=0
for i in t:
    c=i.findAll('td')
    Titles=i.findAll('th')
    if len(Titles)==0:
        Titles=a
    else:
        Titles=Titles[0].text.strip()
        a=Titles
    if len(c)==8:
        Player=c[0].text.strip()
        Amateur_Era=c[1].text.strip()
        Open_Era=c[2].text.strip()
        Australian_Open=c[3].text.strip()
        Roland_Garros=c[4].text.strip()
        Wimbledon=c[5].text.strip()
        US_OPEN=c[6].text.strip()
        Years=c[7].text.strip()
        #print(Titles,Player,Amateur_Era,Open_Era,Australian_Open,Roland_Garros,Wimbledon,US_OPEN,Years)
        
        insertion = "INSERT INTO titles (Titles,Player,Amateur_Era,Open_Era,Australian_Open,Roland_Garros,Wimbledon,US_OPEN,Years) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values=(Titles,Player,Amateur_Era,Open_Era,Australian_Open,Roland_Garros,Wimbledon,US_OPEN,Years)
        cursor.execute(insertion,values)
        connection.commit()




