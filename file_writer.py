import csv
from print_colors import bcolors


class FileWriter ():

    firstrow_dictionary = {
                            'kanjireadings.csv' : ['漢字','音訓','読み方','表内読み'],
                            'kanjigeneralinfo.csv' : ['漢字', '説明', '画数', '部首', '区点コード', 'Unicode', '漢字検定対象級', '成り立ち', '分類', '分類2', '習う学年', 'JIS漢字水準' ,'補足'],
                            'kanjimeaning.csv' : ['漢字', '意味'],
                            'kanjivariant.csv' : ['漢字', '異体字'],
                            'kanjimisc.csv' : ['漢字', '解説・構成'],
                            'kanjinamereadings.csv' : ['漢字', '名乗り訓'],
                            'relatedkanji.csv' : ['漢字', '関連項目']
                        }

    def create_csv_file(self, file_name : str, firstrow : list):
        with open(file_name, encoding='UTF-8', mode='w') as readings_file:
            readings_writer = csv.writer(readings_file, delimiter=',', quotechar='"', lineterminator='\n')
            readings_writer.writerow(firstrow)
            readings_file.close()

    def create_all_csv_files(self):
        for file in self.firstrow_dictionary.items():
            self.create_csv_file(file[0], file[1])


    def write_entry(self, file_name : str, line : list):
        while True:
            try:
                with open(file_name, encoding='UTF-8', mode='a') as file:
                    writer = csv.writer(file, delimiter=',', quotechar='"', lineterminator='\n')
                    writer.writerow(line)
                    file.close()
                    break
            except PermissionError:
                print(bcolors.WARNING + "PERMISSION ERROR OCURRED!!!!" + bcolors.ENDC)
                continue


    def delete_the_last_x_rows_of_file(self, file_string : str, x : int):
        if x <= 0: return
        file = open(file_string, encoding='UTF-8', mode = "r")
        lines = file.readlines()
        lines = lines[:-x]
        file.close()
        file = open(file_string, encoding='UTF-8', mode = "w")
        file.writelines(lines)
        file.close()

    def create_log_txt(self):
        file = open('log.txt', encoding='UTF-8', mode = "w")
        file.write("LOG:\n")
        file.close()

    def write_in_log_txt(self, string : str):
        file = open('log.txt', encoding='UTF-8', mode = "a")
        file.write(string)
        file.close()