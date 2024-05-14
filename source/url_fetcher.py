import requests
from bs4 import BeautifulSoup

class KanjiListsURLFetcher():
    url_list = list()
    kanji_lists_urls = ['https://kanjitisiki.com/jis1/', 'https://kanjitisiki.com/jis2/', 'https://kanjitisiki.com/jis3/', 'https://kanjitisiki.com/jis4/']
    

    def __init__(self):
        for url in self.kanji_lists_urls:
            self.get_urls_from_kanji_list(url)
        self.url_list = set(self.url_list)
        self.write_urls_in_file()
    
    def get_urls_from_kanji_list(self, url : str):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        link_content = soup.body.find(id = 'main').find(class_ = 'itiran_kakoi').find_all('a')
        for link in link_content:
            self.url_list.append(link['href'])

    def write_urls_in_file(self):
        f = open("source/kanjilinks.txt", "w")
        f.write("\n".join(self.url_list))
        f.close()

KanjiListsURLFetcher()