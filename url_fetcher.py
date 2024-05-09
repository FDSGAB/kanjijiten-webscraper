import requests
from bs4 import BeautifulSoup

url_list = list()
url = 'https://kanjitisiki.com/jis1/'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
link_content = soup.body.find(id = 'main').find(class_ = 'itiran_kakoi').find_all('a')
for link in link_content:
    url_list.append(link['href'])
print(len(url_list))
url = 'https://kanjitisiki.com/jis2/'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
link_content = soup.body.find(id = 'main').find(class_ = 'itiran_kakoi').find_all('a')
for link in link_content:
    url_list.append(link['href'])
print(len(url_list))
url = 'https://kanjitisiki.com/jis3/'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
link_content = soup.body.find(id = 'main').find(class_ = 'itiran_kakoi').find_all('a')
for link in link_content:
    url_list.append(link['href'])
print(len(url_list))
url = 'https://kanjitisiki.com/jis4/'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
link_content = soup.body.find(id = 'main').find(class_ = 'itiran_kakoi').find_all('a')
for link in link_content:
    url_list.append(link['href'])
print(len(url_list))
f = open("kanjilinks.txt", "w")
f.write("\n".join(url_list))
f.close()

#open and read the file after the appending:
f = open("kanjilinks.txt", "r")
print(f.read())