import requests
import json

from bs4 import BeautifulSoup


url = f'https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2'

response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, 'html.parser')
tlist = soup.find_all('td')

countries: list = []
countries_finale: list = []

def end_is_vowel(string: str) -> bool:
    vowels = ['у','е','э','о','а','ы','я','и','ю']
    for vowel in vowels:
        if string.endswith(vowel):
            return True
    return False

def end_is_capital(string: str) -> bool:
    upper = ['Й','Ц','У','К','Е','Н','Г','Ш','Щ','З','Х','Ъ','Ф','Ы','В','А','П','Р','О','Л','Д','Ж','Э','Я','Ч','С','М','И','Т','Ь','Б','Ю']
    for letter in upper:
        if string.endswith(letter):
            return True
    return False

def have_number(string: str) -> bool:
    for i in range(10):
        if string.find(str(i)) != -1:
            return True
    return False

for element in tlist:
    country_name = element.text.strip()
    if country_name != '' and not have_number(country_name):
        if countries.count(country_name) == 0:
            countries.append(country_name)
    
for country in countries:
    if not end_is_capital(country):
        if end_is_vowel(country):
            country = country[:-1]
    countries_finale.append(country)


with open('countries.txt', 'w', encoding='utf-8') as file:
    country_str = '\n'.join(countries_finale)
    file.write(country_str)
    print('done')
            

with open('filter_words.json', 'r') as file:
    filter_words = json.load(file)

for country in countries_finale:
    filter_words['international'].append(country)
    
with open('filter_words.json', 'w') as file:
    json.dump(filter_words, file)
