import requests
from bs4 import BeautifulSoup
import pandas as pd
import lxml
import mysql.connector

connection = mysql.connector.connect(
    host="127.0.0.1",
    port="3306",
    user="root",
    password="",
    database="grand_slams")
cursor=connection.cursor()
#cursor.execute("CREATE TABLE champions (Year VARCHAR(255) PRIMARY KEY, Australian_Open VARCHAR(255), Roland_Garros VARCHAR(255), Wimbledon VARCHAR(255), US_Open VARCHAR(255))")

url="https://en.wikipedia.org/wiki/List_of_Grand_Slam_men%27s_singles_champions"
data = requests.get(url)
soup=BeautifulSoup(data.text,'html.parser')
tables= soup.findAll('table')
table=tables[3]
t=table.findAll('tr')
#c=t[148].findAll('td')
#print(len(c))
for i in t:
    c=i.findAll('td')
    if len(c)==5:
        Year=c[0].text[0:4]
        Australian_Open=c[1].text
        Roland_Garros=c[2].text
        Wimbledon=c[3].text
        US_OPEN=c[4].text
        print(Year,Australian_Open,Roland_Garros,Wimbledon,US_OPEN)
        values=(Year,Australian_Open,Roland_Garros,Wimbledon,US_OPEN)
        sql = "INSERT INTO champions (Year, Australian_Open, Roland_Garros, Wimbledon, US_Open) VALUES (%s, %s, %s, %s, %s)"
        try :
            cursor.execute(sql,values)
            connection.commit()
        except mysql.connector.IntegrityError as e:
            print(f"Primary Key error conflict: {e}")
    elif len(c)!=0:
        Year=c[0].text[0:4]
        Australian_Open="Nan"
        Roland_Garros="Nan"
        Wimbledon="Nan"
        US_OPEN="Nan"
        sql = "INSERT INTO champions (Year, Australian_Open, Roland_Garros, Wimbledon, US_Open) VALUES (%s, %s, %s, %s, %s)"
        values=(Year,Australian_Open,Roland_Garros,Wimbledon,US_OPEN)
        
        try :
            cursor.execute(sql,values)
            connection.commit()
        except mysql.connector.IntegrityError as e:
            print(f"Primary Key error conflict: {e}")