import csv

def create_readings_file():
    with open('kanjireadings.csv', encoding='UTF-8', mode='w') as readings_file:
        readings_writer = csv.writer(readings_file, delimiter=',', quotechar='"', lineterminator='\n')
        readings_writer.writerow(['漢字','音訓','読み方','表内読み'])

def create_general_info_file():
    with open('kanjigeneralinfo.csv', encoding='UTF-8', mode='w') as general_file:
        general_writer = csv.writer(general_file, delimiter=',', quotechar='"', lineterminator='\n')
        general_writer.writerow(['漢字', '説明', '画数', '部首', '区点コード', 'Unicode', '漢字検定対象級', '成り立ち', '分類', '分類2', '習う学年', 'JIS漢字水準' ,'補足'])

def create_meaning_file():
    with open('kanjimeaning.csv', encoding='UTF-8', mode='w') as meaning_file:
        meaning_writer = csv.writer(meaning_file, delimiter=',', quotechar='"', lineterminator='\n')
        meaning_writer.writerow(['漢字', '意味'])

def create_variant_file():
    with open('kanjivariant.csv', encoding='UTF-8', mode='w') as variant_file:
        variant_writer = csv.writer(variant_file, delimiter=',', quotechar='"', lineterminator='\n')
        variant_writer.writerow(['漢字', '異体字'])


def create_misc_file():
    with open('kanjimisc.csv', encoding='UTF-8', mode='w') as misc_file:
        misc_writer = csv.writer(misc_file, delimiter=',', quotechar='"', lineterminator='\n')
        misc_writer.writerow(['漢字', '解説・構成'])

def create_name_readings_file():
    with open('kanjinamereadings.csv', encoding='UTF-8', mode='w') as name_readings_file:
        name_readings_writer = csv.writer(name_readings_file, delimiter=',', quotechar='"', lineterminator='\n')
        name_readings_writer.writerow(['漢字', '名乗り訓'])

def create_related_entries_file():
    with open('relatedkanji.csv', encoding='UTF-8', mode='w') as related_entries_file:
        related_entries_writer = csv.writer(related_entries_file, delimiter=',', quotechar='"', lineterminator='\n')
        related_entries_writer.writerow(['漢字', '関連項目'])



###############################################################
"""
SEPARATOR
"""
###############################################################

def write_readings_entry(line : list):
    with open('kanjireadings.csv', encoding='UTF-8', mode='a') as readings_file:
        readings_writer = csv.writer(readings_file, delimiter=',', quotechar='"', lineterminator='\n')
        readings_writer.writerow(line)

def write_general_info_entry(line : list):
    with open('kanjigeneralinfo.csv', encoding='UTF-8', mode='a') as general_file:
        general_writer = csv.writer(general_file, delimiter=',', quotechar='"', lineterminator='\n')
        general_writer.writerow(line)

def write_meaning_entry(line : list):
    with open('kanjimeaning.csv', encoding='UTF-8', mode='a') as meaning_file:
        meaning_writer = csv.writer(meaning_file, delimiter=',', quotechar='"', lineterminator='\n')
        meaning_writer.writerow(line)

def write_variant_entry(line : list):
    with open('kanjivariant.csv', encoding='UTF-8', mode='a') as variant_file:
        variant_writer = csv.writer(variant_file, delimiter=',', quotechar='"', lineterminator='\n')
        variant_writer.writerow(line)

def write_misc_entry(line : list):
    with open('kanjimisc.csv', encoding='UTF-8', mode='a') as misc_file:
        misc_writer = csv.writer(misc_file, delimiter=',', quotechar='"', lineterminator='\n')
        misc_writer.writerow(line)

def write_name_readings_entry(line : list):
    with open('kanjinamereadings.csv', encoding='UTF-8', mode='a') as name_readings_file:
        name_readings_writer = csv.writer(name_readings_file, delimiter=',', quotechar='"', lineterminator='\n')
        name_readings_writer.writerow(line)

def write_related_entries_entry(line : list):
    with open('relatedkanji.csv', encoding='UTF-8', mode='a') as related_entries_file:
        related_entries_writer = csv.writer(related_entries_file, delimiter=',', quotechar='"', lineterminator='\n')
        related_entries_writer.writerow(line)

