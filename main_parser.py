from parser_api_weather import ApiWeather
city = input("Введите название города на латинице (например,Paris): ")
api_weather = ApiWeather()
print(api_weather.get_city_weather(city))
