import requests
from bs4 import BeautifulSoup

def char_is_hiragana(c) -> bool:
    return u'\u3040' <= c <= u'\u309F'
def string_is_hiragana(s: str) -> bool:
    return all(char_is_hiragana(c) for c in s)

def get_okurigana(kunyomi_reading : str, full_reading : str) -> str:
    kunyomi_reading = list(kunyomi_reading)
    full_reading = list(full_reading)
    for character in kunyomi_reading:
        full_reading.remove(character)
    return "".join(full_reading)



def get_full_readings(text : str) -> list:
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


#url = 'https://kanjitisiki.com/syogako/syogaku3/040.html'
entry_dict = dict()
url = 'https://kanjitisiki.com/jis4/0295.html'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
content = soup.body.find(id = "main")
terciary_infos = content.find_all('h3')
secondary_infos = content.find_all('h2')
entry_dict.update({"漢字":content.h1.text})
entry_dict.update({"説明":content.find_all("p", limit=2)[1].get_text()})
for element in secondary_infos:
    next_content = element.find_next()
    if element.text == "読み":
        full_readings_list = element.find_next().text
        full_readings_list = get_full_readings(full_readings_list)
        #print(full_readings_list)
        onyomi_list = list()
        try:     
            onyomi = next_content.find(alt="音読み")
            while True:
                #print(onyomi.find_next())
                if onyomi.find_next().get('class')[0] in ['red_bold', 'bold']:
                    onyomi = onyomi.find_next()
                    okurigana = get_okurigana(onyomi.text, full_readings_list[0])
                    full_readings_list.pop(0)
                    onyomi_list.append((onyomi.text, okurigana, onyomi.get('class')[0]))
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
        kunyomi_list = list()
        try:
            kunyomi = next_content.find(alt="訓読み")
            while True:
                #print(kunyomi.find_next())
                if kunyomi.find_next().get('class')[0] in ['red_bold', 'bold']:
                    kunyomi = kunyomi.find_next()
                    okurigana = get_okurigana(kunyomi.text, full_readings_list[0])
                    full_readings_list.pop(0)
                    kunyomi_list.append((kunyomi.text, okurigana, kunyomi.get('class')[0]))
                else:
                    if kunyomi.find_next().get('class')[0] in ['zigi']:
                        kunyomi = kunyomi.find_next()
                        continue
                    if kunyomi.find_next().get('class')[0] in ['icon']:
                        kunyomi = kunyomi.find_next()
                        continue
                    if kunyomi.find_next().get('name')[0] in ['p']:
                        break 
        except: pass
        entry_dict.update({"読み":{"音読み":onyomi_list,"訓読み":kunyomi_list}})
        continue
    if element.text == "意味":
        """ meaning_list = next_content.get_text().split("\n")
        meaning_list.remove('')
        meaning_list.remove('')
        entry_dict.update({"意味":meaning_list}) """
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
            print(imi_list)
            print("MARKER: ",meaning_marker)
            print("TEXT: ", meaning_text)
            imi_list.append(meaning_marker2+get_okurigana(meaning_marker,meaning_text))
        entry_dict.update({"意味":imi_list})
        continue
    if element.text == "画数":
        strokes = next_content.get_text()
        entry_dict.update({"画数":strokes})
        continue
    if element.text == "異体字":
        variant_forms = list(next_content.text)
        variant_forms_list = next_content.find_all_next(id="itaizi")
        for form in variant_forms_list:
            variant_forms.append(form.text)
        entry_dict.update({"異体字":variant_forms})
        continue
    if element.text == "成り立ち":
        composition = next_content.get_text()
        entry_dict.update({"成り立ち":composition})
        continue
    if element.text == "漢字検定対象級":
        grade = next_content.get_text()
        entry_dict.update({"漢字検定対象級":grade})
        continue
    if element.text == "部首":
        radical = next_content.find('img')['alt']
        entry_dict.update({"部首":radical})
        continue
    print(element.text,next_content)
for element in terciary_infos:
    next_content = element.find_next()
    if element.text == "名乗り訓":
        name_readings = next_content.get_text()
        entry_dict.update({"名乗り訓":name_readings})
        continue
    if element.text == "解説・構成":
        misc = [next_content.text]
        misc_list = next_content.find_all_next('p')
        misc_list.pop(len(misc_list)-1)
        for info in misc_list:
            if info.text[0:9] == 'スポンサードリンク':
                break
            misc.append(info.text)
        entry_dict.update({"解説・構成":misc})
        continue
    if element.text == "コード":
        code_dict = dict()
        titles = next_content.find_all("dt")
        codes = next_content.find_all("dd")
        for i in range(0,len(titles),1):
            code_dict.update({titles[i].text.strip(): codes[i].text.strip()})
        entry_dict.update({"コード":code_dict})
        continue
    if element.text == "分類":
        info_dict = dict()
        titles = next_content.find_all("dt")
        codes = next_content.find_all("dd")
        for i in range(0,len(titles),1):
            info_dict.update({titles[i].text: codes[i].text})
        entry_dict.update({"分類":info_dict})
        continue
    print(element.text,next_content)








try:
    entry_dict['漢字検定対象級']
except:
    entry_dict.update({'漢字検定対象級': None})
try:
    entry_dict['成り立ち']  
except:
    entry_dict.update({'成り立ち': None})
try:
    a = entry_dict['分類']['分類']
except:
    a = None
try:
    b = entry_dict['分類']['分類2']
except:
    b = None
try:
    c = entry_dict['分類']['習う学年']
except:
    c = None
try:
    d = entry_dict['分類']['JIS漢字水準']
except:
    d = None
try:
    entry_dict['異体字']
except:
    entry_dict.update({'異体字': None})
try:
    entry_dict['解説・構成']
except:
    entry_dict.update({'解説・構成': None})
try:
    entry_dict['補足']
except:
    entry_dict.update({'補足': None})



for info in entry_dict.items():
    print(info)
