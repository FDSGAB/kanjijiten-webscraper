import requests
from bs4 import BeautifulSoup
from file_writer import *
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class KanjiInfoFetcher():

    entry_dict = dict()
    url = 'https://kanjitisiki.com/syogako/syogaku1/72.html'
    headers= {'user-agent': 
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0',
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
          #'accept-encoding': 'gzip, deflate, br',
          'accept-language': 'ja,pt-BR;q=0.9,pt;q=0.8,en-US;q=0.7,en;q=0.6'}
    

    def __init__(self) -> None:
        self.read_urls()
        self.create_all_files()
        counter = int(1)
        for url in self.url_list:
            print("Run number: " + str(counter) + ", Current URL: ", url)
            self.entry_dict = dict()
            self.page_content = self.fetch_page_content_by_url(url)
            self.soup = self.html_page_parser(page_content = self.page_content)
            self.main_content = self.soup.body.find(id = "main")
            self.terciary_infos = self.main_content.find_all('h3')
            self.secondary_infos = self.main_content.find_all('h2')
            self.fetch_infos()
            self.write_in_csvs()
            counter = counter + 1
            """ for info in self.entry_dict.items():
                print(info) """    

    def read_urls(self):
        f = open("kanjilinks.txt", "r")
        self.url_list = f.read().split("\n")


    def fetch_page_content_by_url(self, url : str) -> bytes:
        """ session = requests.Session()
        retry = Retry(total=None, connect=10000, read=10000, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        page = session.get(url) """
        while True:
            try:
                page = requests.get(url=url, headers=self.headers)
                if page.url == url:
                    return page.content
            except: pass

    def html_page_parser(self, page_content : bytes) -> BeautifulSoup:
        return BeautifulSoup(page_content, "html.parser")
    
    def fetch_kanji(self):
        self.entry_dict.update({"漢字" : self.main_content.h1.text})

    def fetch_description(self):
        self.entry_dict.update({"説明" : self.main_content.find_all("p", limit=2)[1].get_text()})

    def fetch_secondary_informations(self):
        for element in self.secondary_infos:
            next_content = element.find_next()
            if element.text == "読み":
                self.fetch_readings(element, next_content)
                continue
            if element.text == "意味":
                self.fetch_meaning(next_content)
                continue
            if element.text == "画数":
                self.fetch_number_of_strokes(next_content)
                continue
            if element.text == "異体字":
                self.fetch_variant_forms(next_content)
                continue
            if element.text == "成り立ち":
                self.fetch_composition(next_content)
                continue
            if element.text == "漢字検定対象級":
                self.fetch_grade(next_content)
                continue
            if element.text == "部首":
                self.fetch_radicals(next_content)
                continue
            if element.text == "解説・構成":
                self.fetch_misc(next_content)
                continue
            if element.text == "補足":
                self.fetch_footnote(next_content)
                continue
            print(element.text, next_content)
    
    def fetch_readings(self, element, next_content):
        self.full_readings_list = element.find_next().text
        self.full_readings_list = self.get_full_readings(self.full_readings_list)
        self.onyomi_list = list()
        self.get_onyomi_readings(next_content)      
        self.kunyomi_list = list()
        self.get_kunyomi_readings(next_content)
        self.entry_dict.update({"読み" : {"音読み" : self.onyomi_list, "訓読み" : self.kunyomi_list}})


    def get_onyomi_readings(self, next_content):
        try:     
            onyomi = next_content.find(alt="音読み")
            while True:
                if onyomi.find_next().get('class')[0] in ['red_bold', 'bold']:
                    onyomi = onyomi.find_next()
                    okurigana = self.get_okurigana(onyomi.text, self.full_readings_list[0])
                    self.full_readings_list.pop(0)
                    self.onyomi_list.append((onyomi.text, okurigana, onyomi.get('class')[0]))
                else:
                    if onyomi.find_next().get('class')[0] in ['icon']:
                        onyomi = onyomi.find_next()
                        continue
                    if onyomi.find_next().get('class')[0] in ['zigi']:
                        onyomi = onyomi.find_next()
                        continue
                    if onyomi.find_next().get('name')[0] in ['icon']:
                        break 
        except: pass     

    def get_kunyomi_readings(self, next_content):
        try:
            kunyomi = next_content.find(alt="訓読み")
            while True:
                if kunyomi.find_next().get('class')[0] in ['red_bold', 'bold']:
                    kunyomi = kunyomi.find_next()
                    okurigana = self.get_okurigana(kunyomi.text, self.full_readings_list[0])
                    self.full_readings_list.pop(0)
                    self.kunyomi_list.append((kunyomi.text, okurigana, kunyomi.get('class')[0]))
                else:
                    if kunyomi.find_next().get('class')[0] in ['zigi']:
                        kunyomi = kunyomi.find_next()
                        continue
                    if kunyomi.find_next().get('class')[0] in ['icon']:
                        kunyomi = kunyomi.find_next()
                        continue
                    if kunyomi.find_next().get('p')[0] in ['img']:
                        break
        except: pass



    def get_okurigana(self, kunyomi_reading : str, full_reading : str) -> str:
        kunyomi_reading = list(kunyomi_reading)
        full_reading = list(full_reading)
        for character in kunyomi_reading:
            full_reading.remove(character)
        return "".join(full_reading)



    def get_full_readings(self, text : str) -> list:
        new_string_list = list()
        word = list()
        is_reading = False
        for e in text:
            if e == '「':
                word = list()
                is_reading = True
                continue
            if e == '」':
                new_string_list.append("".join(word))
                is_reading = False
            if is_reading:
                word.append(e)
        return new_string_list
    

    def fetch_meaning(self, next_content):  
        imi_list = list()
        meaning_list = next_content.find_all("li")
        for meaning in meaning_list:
            meaning_text = str()
            meaning_marker = str()
            meaning_marker2 = str()
            meaning_text = meaning.get_text()
            try:
                if meaning.find_next().get('class')[0][0:4] in ['zigi']:
                    meaning_marker = meaning.find_next().get_text()
                    meaning_marker2 = "◦" + meaning_marker + " "
            except: pass
            imi_list.append(meaning_marker2 + self.get_okurigana(meaning_marker,meaning_text))
        self.entry_dict.update({"意味" : imi_list})
    
    def fetch_number_of_strokes(self, next_content):
        strokes = next_content.get_text().strip()
        self.entry_dict.update({"画数" : strokes})    


    def fetch_variant_forms(self, next_content):
        variant_forms = list(next_content.text)
        variant_forms_list = next_content.find_all_next(id="itaizi")
        for form in variant_forms_list:
            variant_forms.append(form.text.strip())
        self.entry_dict.update({"異体字" : variant_forms})    

    def fetch_composition(self, next_content):
        composition = next_content.get_text()
        self.entry_dict.update({"成り立ち" : composition})

    def fetch_grade(self, next_content):
        grade = next_content.get_text()
        self.entry_dict.update({"漢字検定対象級" : grade})


    def fetch_radicals(self, next_content):
        radical = next_content.find('img')['alt']
        self.entry_dict.update({"部首" : radical})

    def fetch_terciary_informations(self):
        for element in self.terciary_infos:
            next_content = element.find_next()
            if element.text == "名乗り訓":
                self.fetch_name_readings(next_content)
                continue
            if element.text == "解説・構成":
                self.fetch_misc(next_content)
                continue
            if element.text == "コード":
                self.fetch_codes(next_content)
                continue
            if element.text == "分類":
                self.fetch_classifications(next_content)
                continue
            if element.text == "関連項目":
                self.fetch_related_itens(next_content)
                continue
            if element.text == "補足":
                self.fetch_footnote(next_content)
                continue
            print(element.text,next_content)

    def fetch_name_readings(self, next_content):
        name_readings = next_content.get_text().strip()
        self.entry_dict.update({"名乗り訓" : name_readings})


    def fetch_misc(self, next_content):
        misc = [next_content.text]
        misc_list = next_content.find_all_next('p')
        misc_list.pop(len(misc_list)-1)
        for info in misc_list:
            if info.text[0:9] == 'スポンサードリンク':
                break
            misc.append(info.text.strip())
        self.entry_dict.update({"解説・構成" : misc})

    
    def fetch_codes(self, next_content):
        code_dict = dict()
        titles = next_content.find_all("dt")
        codes = next_content.find_all("dd")
        for i in range(0,len(titles),1):
            code_dict.update({titles[i].text.strip(): codes[i].text.strip()})
        self.entry_dict.update({"コード" : code_dict})


    def fetch_classifications(self, next_content):
        info_dict = dict()
        titles = next_content.find_all("dt")
        infos = next_content.find_all("dd")
        for i in range(0,len(titles),1):
            info_dict.update({titles[i].text.strip(): infos[i].text.strip()})
        self.entry_dict.update({"分類" : info_dict})

    def fetch_related_itens(self, next_content):
        related_itens = next_content.get_text().split("\n")
        related_itens.remove('')
        self.entry_dict.update({"関連項目" : related_itens})
        related_itens = ''

    def fetch_footnote(self, next_content):
        footnote = next_content.get_text()
        self.entry_dict.update({"補足" : footnote})


    def write_readings_in_csv(self):
        readings_entry = []
        try:
            for kunreading in self.entry_dict['読み']['訓読み']:
                if kunreading[2] == 'red_bold':
                    regularity = '表内読み'
                if kunreading[2] == 'bold':
                    regularity = '表外読み'
                readings_entry.append([self.entry_dict['漢字'], "訓",kunreading[0],kunreading[1],regularity])
        except: pass
        try:
            for onreading in self.entry_dict['読み']['音読み']:
                if onreading[2] == 'red_bold':
                    regularity = '表内読み'
                if onreading[2] == 'bold':
                    regularity = '表外読み'
                readings_entry.append([self.entry_dict['漢字'], "音",onreading[0],onreading[1],regularity])
        except: pass
        for line in readings_entry:
            write_readings_entry(line)

    def alocate_none_values_to_umatched_fields(self):
        try:
            self.entry_dict['漢字検定対象級']
        except:
            self.entry_dict.update({'漢字検定対象級': None})
        try:
            self.entry_dict['成り立ち']  
        except:
            self.entry_dict.update({'成り立ち': None})
        try:
            self.bunrui = self.entry_dict['分類']['分類']
        except:
            self.bunrui = None
        try:
            self.bunrui2 = self.entry_dict['分類']['分類2']
        except:
            self.bunrui2 = None
        try:
            self.naraugakunen = self.entry_dict['分類']['習う学年']
        except:
            self.naraugakunen = None
        try:
            self.jis = self.entry_dict['分類']['JIS漢字水準']
        except:
            self.jis = None
        try:
            self.entry_dict['異体字']
        except:
            self.entry_dict.update({'異体字': None})
        try:
            self.entry_dict['解説・構成']
        except:
            self.entry_dict.update({'解説・構成': None})
        try:
            self.entry_dict['補足']
        except:
            self.entry_dict.update({'補足': None})
        try:
            self.entry_dict['関連項目']
        except:
            self.entry_dict.update({'関連項目': None})
        try:
            self.entry_dict['名乗り訓']
        except:
            self.entry_dict.update({'名乗り訓': None})

    def write_general_info_in_csv(self):
        entry = [ 
                self.entry_dict['漢字'], self.entry_dict['説明'], 
                int(self.entry_dict['画数'][0:len(self.entry_dict['画数'])-1]),
                self.entry_dict['部首'][3:len(self.entry_dict['部首'])-1],
                self.entry_dict['コード']['区点コード'],
                self.entry_dict['コード']['Unicode'],
                self.entry_dict['漢字検定対象級'],
                self.entry_dict['成り立ち'] ,
                self.bunrui,
                self.bunrui2,
                self.naraugakunen,
                self.jis,
                self.entry_dict['補足']
                ]
        write_general_info_entry(entry)


    def write_meaning_in_csv(self):
        meaning_entry = list()
        for meaning in self.entry_dict['意味']:
            meaning_entry.append((self.entry_dict['漢字'], meaning))
        for line in meaning_entry:
            write_meaning_entry(line)


    def write_variant_in_csv(self):
        if self.entry_dict['異体字'] != None:
            variant_forms_entry = list()
            for variant in self.entry_dict['異体字']:
                variant_forms_entry.append((self.entry_dict['漢字'], variant))
            for line in variant_forms_entry:
                write_variant_entry(line)


    def write_misc_in_csv(self):
        if self.entry_dict['解説・構成'] != None:
            misc_list_entry = list()
            for misc in self.entry_dict['解説・構成']:
                misc_list_entry.append((self.entry_dict['漢字'], misc))
            for line in misc_list_entry:
                write_misc_entry(line)

    def write_name_readings_in_csv(self):
        if self.entry_dict['名乗り訓'] != None:
            name_readings_list = self.entry_dict['名乗り訓'].split('」「')
            name_readings_list[0] = name_readings_list[0][1:]
            name_readings_list[len(name_readings_list)-1] = name_readings_list[len(name_readings_list)-1][:len(name_readings_list[len(name_readings_list)-1])-1]
            name_readings_list_entry = list()
            for reading in name_readings_list:
                 name_readings_list_entry.append((self.entry_dict['漢字'], reading))
            for line in  name_readings_list_entry:
                write_name_readings_entry(line)

    def write_related_entries_entry_in_csv(self):
        if self.entry_dict['関連項目'] != None:
            related_kanji_list = list()
            for entry in self.entry_dict['関連項目']:
                related_kanji_list.append((self.entry_dict['漢字'], entry))
            for line in related_kanji_list:
                write_related_entries_entry(line)

    def create_all_files(self):
        create_variant_file()
        create_general_info_file()
        create_meaning_file()
        create_misc_file()
        create_readings_file()
        create_name_readings_file()
        create_related_entries_file()
    

    def write_in_csvs(self):
        self.write_general_info_in_csv()
        self.write_meaning_in_csv()
        self.write_variant_in_csv()
        self.write_misc_in_csv()
        self.write_readings_in_csv()
        self.write_name_readings_in_csv()
        self.write_related_entries_entry_in_csv()

    def fetch_infos(self):
        self.fetch_kanji()
        self.fetch_description()
        self.fetch_secondary_informations()
        self.fetch_terciary_informations()
        self.alocate_none_values_to_umatched_fields()


if __name__ == '__main__':
    kanji_info = KanjiInfoFetcher()