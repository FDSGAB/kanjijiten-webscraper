from source.url_fetcher import KanjiListsURLFetcher
from source.file_management.file_writer import FileWriter


class RunSetup():

    def setup(self) -> list:
        KanjiListsURLFetcher()
        FileWriter().create_all_csv_files()
        FileWriter().create_log_txt()
        self.read_urls()
        return self.url_list
        
    def read_urls(self):
        f = open("source/kanjilinks.txt", "r")
        self.url_list = f.read().split("\n")