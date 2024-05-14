import pandas as pd
from style.print_colors import bcolors
from source.file_management.file_writer import FileWriter

def entry_was_successfull(kanji : str, file_name : str, number_of_entries_found : int) -> tuple:
    info = pd.read_csv(file_name, encoding='UTF-8', delimiter=',', index_col = False, usecols=[0]) 
    entries_in_file = info["漢字"].loc[info["漢字"] == kanji].count()
    if entries_in_file == number_of_entries_found: return (0, entries_in_file)
    if entries_in_file != number_of_entries_found: 
        error_string = "Error in " + kanji + " found in: " + file_name + "\nEntries in csv: " + str(entries_in_file) + "\nEntries found: " + str(number_of_entries_found) + "\n"
        print(bcolors.FAIL + error_string + bcolors.ENDC)
        FileWriter().write_in_log_txt(error_string)
        return (1, entries_in_file)