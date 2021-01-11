import sys
import os
import gzip
import shutil
import re
import json
import yaml
import datetime
sys.path.append('C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python39\\lib\\site-packages')
from grab import Grab
from sqlitedb import SqliteDB
import urllib.request
class ApiWeather:
    def __init__(self):
       conf = self.get_conf()
       self.login=conf["login"]
       self.password=conf["password"]
       print(self.login)
       print(self.password)
       self.g = Grab(log_file='out.html')
       self.sql_conn = SqliteDB()
       self.app_id=""

    def set_app(self):
       if self.app_id:
           return
       app_id=""
       F = self.open_file('app.id')
       if(F):
          app_id = F.read()
          F.close()
       if(app_id):
           print("Берем закешированный app.id")
           self.app_id = app_id
       else:
           print("Запрашиваем app.id")
           self.g.go('https://home.openweathermap.org/api_keys')
           self.g.doc.set_input("user[email]", self.login)
           self.g.doc.set_input("user[password]", self.password)
           self.g.submit()
           my_file = open('app.id','w')
           my_file.write(self.g.doc.select('//pre').text())
           my_file.close
           self.app_id=self.g.doc.select('//pre').text()
           print("Готово")

    def get_app(self):
        self.set_app()
        return self.app_id

    def get_city_file(self):
        url = "http://bulk.openweathermap.org/sample/city.list.json.gz"
        destination = url.rsplit('/', 1)[1]
        new_dest = re.sub('\.gz', '', destination)
        F = self.open_file('city.list.json')
        if(F):
            F.close
        else:
            urllib.request.urlretrieve(url, destination)
            with gzip.open(destination, 'rb') as f_in:
                with open(new_dest, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        if(self.open_file(destination)):
            os.remove(destination)

        return new_dest

    def open_file(self,path):
        try:
            my_file = open(path, 'r')
        except FileNotFoundError:
            print("файла не существует ",path)
            return 0
        else:
            return my_file

    def get_conf(self):
        stream = self.open_file("conf.yaml")
        try:
           return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
           print(exc)
           return 0
        finally:
            stream.close

    def read_cities(self,name):
        file_path = self.get_city_file()
        with open(file_path,"r",encoding="utf-8") as f:
            jsonstr = f.read()
#        print(jsonstr)
        data = json.loads(jsonstr)
        for i,d in enumerate(data):
            if d["name"] == name:
                return d
        return {}

    def get_city_weather(self,city):
        data = self.sql_conn.get_value_by_city(city)
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        if(data):
            if(data[2] == today):
                print("Данные найдены в БД")
                return data
            else:
                print("Обращаемся к ресурсу openweather")
                city_weather = self.api_get_city_weather(city)
                if not city_weather:
                    return "Погода не найдена для города "+str(city)
                print("Редактирование данных в БД")
                value = (city_weather["name"], today, city_weather["main"]["temp"], city_weather["weather"][0]["id"])
                self.sql_conn.edit_value(value[0],value[1],value[2],value[3])
                print("Готово")
                return value
        else:
            print("Обращаемся к ресурсу openweather")
            city_weather = self.api_get_city_weather(city)
            if not city_weather:
                return "Погода не найдена для города " + str(city)
            print("Добавление данных в БД")
            value = (city_weather["name"],today,city_weather["main"]["temp"],city_weather["weather"][0]["id"])
            self.sql_conn.add_values([value])
            print("Готово")
            return value

    def api_get_city_weather(self,city):
        data = self.read_cities(city)
        if((bool(data) == True) & ('id' in data.keys())):
            url = "http://api.openweathermap.org/data/2.5/weather?id="+str(data["id"])+"&units=metric&appid="+str(self.get_app())
            print("Обращаемся к "+url)
            resp = urllib.request.urlopen(url)
            text = resp.read()
            data = json.loads(text)
            return data
        else:
            print('такого города не найдено на ресурсе openweather ' + city)
            return ""