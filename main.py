import requests
from bs4 import BeautifulSoup
from file_writer import FileWriter
from file_checker import *
from print_colors import bcolors


class KanjiInfoFetcher():

    entry_dict = dict()
    url = 'https://kanjitisiki.com/syogako/syogaku1/72.html'
    headers= {'user-agent': 
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0',
          'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
          #'accept-encoding': 'gzip, deflate, br',
          'accept-language': 'ja,pt-BR;q=0.9,pt;q=0.8,en-US;q=0.7,en;q=0.6'}
    needs_reprocessing = False
    

    def __init__(self) -> None:
        self.read_urls()
        FileWriter().create_all_csv_files()
        FileWriter().create_log_txt()
        counter = int(1)
        for url in self.url_list:
            self.needs_reprocessing = False
            while True:
                print(bcolors.OKGREEN + "Run number: " + str(counter) + "/" + str(len(self.url_list)) + " " + str(round(100*counter/len(self.url_list), 2)) + "%, URL: " + url + bcolors.ENDC)
                self.entry_dict = dict()
                self.page_content = self.fetch_page_content_by_url(url)
                self.soup = self.html_page_parser(page_content = self.page_content)
                self.main_content = self.soup.body.find(id = "main")
                self.terciary_infos = self.main_content.find_all('h3')
                self.secondary_infos = self.main_content.find_all('h2')
                self.fetch_infos()
                self.write_in_csvs()
                if self.needs_reprocessing: 
                    error_url = "ERROR IN Run number: " + str(counter) + ", URL: " + url+ "\n"
                    print(bcolors.FAIL + error_url + bcolors.ENDC)
                    FileWriter().write_in_log_txt(error_url)
                    continue
                counter = counter + 1
                break
            """ for info in self.entry_dict.items():
                print(info) """    

    def read_urls(self):
        f = open("kanjilinks.txt", "r")
        self.url_list = f.read().split("\n")


    def fetch_page_content_by_url(self, url : str) -> bytes:
        while True:
            try:
                page = requests.get(url=url, headers=self.headers)
                if page.url == url:
                    return page.content
            except: pass

    def html_page_parser(self, page_content : bytes) -> BeautifulSoup:
        return BeautifulSoup(page_content, "html.parser")
    
    def fetch_kanji(self):
        self.general_count = self.general_count + 1
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
            self.meaning_count = self.meaning_count + 1
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
        self.related_kanji_count = len(related_itens)
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
        self.readings_count = len(readings_entry)
        for line in readings_entry:
            FileWriter().write_entry('kanjireadings.csv', line)

    def alocate_none_values_to_umatched_fields(self):
        try: self.entry_dict['漢字検定対象級']
        except: self.entry_dict.update({'漢字検定対象級': 'NULL'})
        try: self.entry_dict['成り立ち']  
        except: self.entry_dict.update({'成り立ち': 'NULL'})
        try: self.bunrui = self.entry_dict['分類']['分類']
        except: self.bunrui = 'NULL'
        try: self.bunrui2 = self.entry_dict['分類']['分類2']
        except: self.bunrui2 = 'NULL'
        try: self.naraugakunen = self.entry_dict['分類']['習う学年']
        except: self.naraugakunen = 'NULL'
        try: self.jis = self.entry_dict['分類']['JIS漢字水準']
        except: self.jis = 'NULL'
        try: self.entry_dict['異体字']
        except: self.entry_dict.update({'異体字': 'NULL'})
        try: self.entry_dict['解説・構成']
        except: self.entry_dict.update({'解説・構成': 'NULL'})
        try: self.entry_dict['補足']
        except: self.entry_dict.update({'補足': 'NULL'})
        try: self.entry_dict['関連項目']
        except: self.entry_dict.update({'関連項目': 'NULL'})
        try: self.entry_dict['名乗り訓']
        except: self.entry_dict.update({'名乗り訓': 'NULL'})

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
        FileWriter().write_entry('kanjigeneralinfo.csv', entry)
        



    def write_meaning_in_csv(self):
        meaning_entry = list()
        for meaning in self.entry_dict['意味']:
            meaning_entry.append((self.entry_dict['漢字'], meaning))
        for line in meaning_entry:
            FileWriter().write_entry('kanjimeaning.csv', line)


    def write_variant_in_csv(self):
        if self.entry_dict['異体字'] != None and self.entry_dict['異体字'] != 'NULL':
            variant_forms_entry = list()
            for variant in self.entry_dict['異体字']:
                self.variant_count = self.variant_count + 1
                variant_forms_entry.append((self.entry_dict['漢字'], variant))
            for line in variant_forms_entry:
                FileWriter().write_entry('kanjivariant.csv', line)


    def write_misc_in_csv(self):
        if self.entry_dict['解説・構成'] != None and self.entry_dict['解説・構成'] != 'NULL':
            misc_list_entry = list()
            for misc in self.entry_dict['解説・構成']:
                misc_list_entry.append((self.entry_dict['漢字'], misc))
                self.misc_count = self.misc_count + 1
            for line in misc_list_entry:
                FileWriter().write_entry('kanjimisc.csv', line)

    def write_name_readings_in_csv(self):
        if self.entry_dict['名乗り訓'] != None and self.entry_dict['名乗り訓'] != 'NULL':
            name_readings_list = self.entry_dict['名乗り訓'].split('」「')
            name_readings_list[0] = name_readings_list[0][1:]
            name_readings_list[len(name_readings_list)-1] = name_readings_list[len(name_readings_list)-1][:len(name_readings_list[len(name_readings_list)-1])-1]
            self.name_readings_count = len(name_readings_list)
            name_readings_list_entry = list()
            for reading in name_readings_list:
                 name_readings_list_entry.append((self.entry_dict['漢字'], reading))
            for line in  name_readings_list_entry:
                FileWriter().write_entry('kanjinamereadings.csv', line)

    def write_related_entries_entry_in_csv(self):
        if self.entry_dict['関連項目'] != None and self.entry_dict['関連項目'] != 'NULL':
            related_kanji_list = list()
            for entry in self.entry_dict['関連項目']:
                related_kanji_list.append((self.entry_dict['漢字'], entry))
            for line in related_kanji_list:
                FileWriter().write_entry('relatedkanji.csv', line)
    

    def write_in_csvs(self):
        if  self.entry_dict['漢字'] in ['', None]:
            self.needs_reprocessing = True
            return
        self.write_general_info_in_csv() 
        control_general = entry_was_successfull(self.entry_dict['漢字'], 'kanjigeneralinfo.csv', self.general_count)
        if control_general[0] in [1, -1]:
            FileWriter().delete_the_last_x_rows_of_file('kanjigeneralinfo.csv', control_general[1])
            self.needs_reprocessing = True
            return
        self.write_meaning_in_csv()
        control_meaning = entry_was_successfull(self.entry_dict['漢字'], 'kanjimeaning.csv', self.meaning_count)
        if control_meaning[0] in [1, -1]:
            FileWriter().delete_the_last_x_rows_of_file('kanjigeneralinfo.csv', control_general[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjimeaning.csv', control_meaning[1])
            self.needs_reprocessing = True
            return
        self.write_variant_in_csv()
        control_variant = entry_was_successfull(self.entry_dict['漢字'], 'kanjivariant.csv', self.variant_count)
        if control_variant[0] in [1, -1]:
            FileWriter().delete_the_last_x_rows_of_file('kanjigeneralinfo.csv', control_general[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjimeaning.csv', control_meaning[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjivariant.csv', control_variant[1])
            self.needs_reprocessing = True
            return
        self.write_misc_in_csv()
        control_misc = entry_was_successfull(self.entry_dict['漢字'], 'kanjimisc.csv', self.misc_count)
        if control_misc[0] in [1, -1]:
            FileWriter().delete_the_last_x_rows_of_file('kanjigeneralinfo.csv', control_general[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjimeaning.csv', control_meaning[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjivariant.csv', control_variant[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjimisc.csv', control_misc[1])
            self.needs_reprocessing = True
            return
        self.write_readings_in_csv()
        control_readings = entry_was_successfull(self.entry_dict['漢字'], 'kanjireadings.csv', self.readings_count)
        if control_readings[0] in [1, -1]:
            FileWriter().delete_the_last_x_rows_of_file('kanjigeneralinfo.csv', control_general[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjimeaning.csv', control_meaning[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjivariant.csv', control_variant[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjimisc.csv', control_misc[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjireadings.csv', control_readings[1])
            self.needs_reprocessing = True
            return
        self.write_name_readings_in_csv()
        control_name_readings = entry_was_successfull(self.entry_dict['漢字'], 'kanjinamereadings.csv', self.name_readings_count)
        if control_name_readings[0] in [1, -1]:
            FileWriter().delete_the_last_x_rows_of_file('kanjigeneralinfo.csv', control_general[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjimeaning.csv', control_meaning[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjivariant.csv', control_variant[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjimisc.csv', control_misc[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjireadings.csv', control_readings[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjinamereadings.csv', control_name_readings[1])
            self.needs_reprocessing = True
            return
        self.write_related_entries_entry_in_csv()
        control_related = entry_was_successfull(self.entry_dict['漢字'], 'relatedkanji.csv', self.related_kanji_count)
        if control_related[0] in [1, -1]:
            FileWriter().delete_the_last_x_rows_of_file('kanjigeneralinfo.csv', control_general[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjimeaning.csv', control_meaning[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjivariant.csv', control_variant[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjimisc.csv', control_misc[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjireadings.csv', control_readings[1])
            FileWriter().delete_the_last_x_rows_of_file('kanjinamereadings.csv', control_name_readings[1])
            FileWriter().delete_the_last_x_rows_of_file('relatedkanji.csv', control_related[1])
            self.needs_reprocessing = True
            return
        self.needs_reprocessing = False

    def fetch_infos(self):
        self.general_count = int(0)
        self.readings_count = int(0)
        self.meaning_count = int(0)
        self.misc_count = int(0)
        self.name_readings_count = int(0)
        self.variant_count = int(0)
        self.related_kanji_count = int(0)
        self.fetch_kanji()
        self.fetch_description()
        self.fetch_secondary_informations()
        self.fetch_terciary_informations()
        self.alocate_none_values_to_umatched_fields()


if __name__ == '__main__':
    kanji_info = KanjiInfoFetcher()