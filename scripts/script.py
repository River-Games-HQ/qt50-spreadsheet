import json
import pandas as pd
from datetime import datetime
from os import listdir
from os.path import isfile, join
import re

# returns the names of the spreadsheets
def get_spreadsheets():
    return [join('../material/speadsheets/', f) for f in listdir('../material/spreadsheets') if isfile(join('../material/spreadsheets', f)) and f.endswith('csv')]

# reads a certain json file and returns it as a json object
def read_json(date: datetime, number: str):
    folder_name = date.strftime('%d-%m-%Y') + '/'
    file_name = 'nodeset' + number + '.json'
    path = join('../material/qt30/', folder_name, file_name)
    with open(path) as file:
        json_data = json.load(file)
        return json_data

# filters out the date of a spreadsheet by its name (returns datetime object)
def filter_date(filename):
    filename = filename[24:]
    date_as_string = re.sub(r'cuties?testrun', '', filename)
    date_as_string = re.sub(r'\.csv', '', date_as_string)
    return datetime.strptime(date_as_string, '%d%B%Y')

# counts all nodes of certain type in json file
def count_nodes(type: str, json_number: str, date: datetime):
    file = read_json(date, json_number)
    ct = 0
    for node in file['nodes']:
        if node['type'] == type:
            ct += 1
    return ct

# gets the text excerpt of a part of a testrun
def get_excerpt(part_num: str, date: datetime):
    folder_name = date.strftime('%d-%m-%Y') + '/'
    file_name = date.strftime('%d-%m-%Y') + '.txt'
    path = join('../material/qt30/', folder_name, file_name)
    with open(path) as file:
        lines = file.readlines()
        lines = "\n".join(lines)
        lines = lines.split("\n")
        for l in lines:
            if not re.search('Part ' + part_num, l):
                lines.remove(l)
            else:
                lines.remove(l)
                break
        excerpt = ''
        for l in lines:
            if not re.search('Part', l):
                excerpt += l + '\n'
            else:
                break
        return excerpt
    
# should return the json numbers for all parts of a certain date
def get_json_numbers(filename: str):
    return    
            
# should loop through all spreadsheets and build the rows for the statistics df from there
if __name__ == '__main__':
    df = pd.read_csv('../material/statistics.csv')
    spreadsheets = get_spreadsheets()
    
    
    