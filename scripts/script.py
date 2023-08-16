import json
import pandas as pd
from datetime import datetime
from os import listdir
from os.path import isfile, join
import re

maps_to_ignore = [
    '24255', '25441', '24807', '24808',
    '24809', '25442', '25443', '25444',
    '25445', '25452', '24903', '25461',
    '24905', '25462', '25463', '24992',
    '25465', '25468', '25473', '25045',
    '25472', '25474', '25475'
]

# returns the names of the spreadsheets
def get_spreadsheets():
    return [join('./material/spreadsheets/', f) for f in listdir('./material/spreadsheets') if isfile(join('./material/spreadsheets', f)) and f.endswith('csv')]

# reads a certain json file and returns it as a json object
def read_json(number: str):
    file_name = 'nodeset' + number + '.json'
    path = join('./material/all_json', file_name)
    if not isfile(path):
        print(file_name, "does not exist")
        return
    with open(path, encoding="utf8") as file:
        json_data = json.load(file)
        return json_data

# filters out the date of a spreadsheet by its name (returns datetime object)
def filter_date(filename):
    filename = filename[24:]
    date_as_string = re.sub(r'cuties?testrun', '', filename)
    date_as_string = re.sub(r'\.csv', '', date_as_string)
    return datetime.strptime(date_as_string, '%d%B%Y')

# counts all nodes of certain type and schemes in json file
def count_nodes(type: str, json_number: str, date: datetime, schemes=[]):
    file = read_json(json_number)
    ct = 0
    for node in file['nodes']:
        if node['type'] == type:
            if schemes:
                if "scheme" in node and node["scheme"] in schemes:
                    ct += 1
            else:
                ct += 1
        
    return ct

# gets the text excerpt of a part of a testrun
def get_excerpt2(part_num: str, date: datetime):
    folder_name = date.strftime('%d-%m-%Y') + '/'
    file_name = date.strftime('%d-%m-%Y') + '.txt'
    path = join('./material/qt30/', folder_name, file_name)
    with open(path, encoding="utf8") as file:
        lines = file.readlines()
        i = 0
        excerpt = ''
        while i < len(lines):
            line = lines[i].strip()
            if (len(line) > 4 and line[:4] == 'Part' and line[5] == part_num):
                #print('line: ' + line[5])
                #print('part: ' + part_num)
                excerpt = ''
                j = i + 1
                while j < len(lines):
                    line = lines[j].strip()
                    if (len(line) > 4 and line[:4] == 'Part'):
                       return excerpt 
                    else:
                        excerpt += lines[j]
                    j += 1        
                return excerpt
            i += 1
        return excerpt

# returns the json numbers for all parts of a certain date
def get_json_numbers(filename: str):
    maps = pd.read_csv(
        './material/map_sheet.csv', header=None)
    maps = maps[[str(x) in filename for x in maps[0]]]
    nums = []
    numsMissing=[]

    for idx, row in maps.iterrows():
        a = ''
        if str(row[11] != "nan"):
            a = str(row[11])
        if a not in maps_to_ignore:
            if a in get_all_json_files():
                nums.append(a)
            else:
                numsMissing.append(a)
                
    return list(dict.fromkeys(nums)), list(dict.fromkeys(numsMissing))

# returns the name of the testrun of a certain spreadsheet
def get_testrun_name(filename: str): 
    result = re.sub(r"../material/spreadsheets/", "", filename)
    return re.sub(r"\.csv", "", result) 

# returns all available json files
def get_all_json_files():
    files = [f for f in listdir('./material/all_json')]
    files = [re.sub(r'nodeset', '', x) for x in files]
    return [re.sub(r'\.json', '', x) for x in files]

# gets the required data from the spreadsheet
def get_spreadsheet_data(filename: str, partnum: str):
    df = pd.read_csv(filename, header=None)
    for idx, row in df.iterrows():
        edge_case = False
        if filename == "./material/spreadsheets/cutietestrun4June2020.csv" and 29 < int(partnum) < 48:
            edge_case = True
        if row[0] == partnum or (edge_case and re.sub(r"^1", "", str(row[0])) == partnum):
            result = {}
            result["Analyst name"] = row[1]
            if not re.search(r"2020", filename):
                result["Analysis duration"] = row[20]
                result["Review duration"] = row[21]
            else:
                result["Analysis duration"] = row[16]
                result["Review duration"] = row[17]
            
            if len(str(result["Analysis duration"])) > 5:
                result["Analysis duration"] = re.sub(":00", "", result["Analysis duration"])
            if len(str(result["Review duration"])) > 5:
                result["Review duration"] = re.sub(":00", "", result["Review duration"])
            
            return result
        
def get_part(json_num: str, filename: str):
    maps = pd.read_csv(
        './material/map_sheet.csv', header=None)
    maps = maps[[str(x) in filename for x in maps[0]]]
    for idx, row in maps.iterrows():
        if row[11] == json_num:
            if row[9] == "IMC":
                return 'none'
            return re.sub(r'part\s', '', row[9])
    print("no partnumber found for " + json_num + " in " + filename)

# loops through all spreadsheets and populate the rows for the statistics df from there
if __name__ == '__main__':
    df = pd.read_csv('./material/statistics.csv')
    spreadsheets = get_spreadsheets()
    df = pd.DataFrame(columns=["Testrun","Json ID","Part number","Part text","Analyst name","Review duration","Number of locutions","Number of propositions",
                "Number of YAs (asserting)","Number of YAs (pure questioning, assertiv questioning, rhetorical questioning)",
                "Number of YAs (all of the rest)","Number of TAs","Number of MAs","Number of RAs","Number of CAs"])
    for spreadsheet in spreadsheets:
        json_nums, y = get_json_numbers(spreadsheet)
        testrun = get_testrun_name(spreadsheet)
        date = filter_date(spreadsheet)
        for num in json_nums:
            part = get_part(num, spreadsheet)
            if part == "none":
                continue
            sdata = get_spreadsheet_data(spreadsheet, part)
            if sdata == None:
                print("error in part " + part + " of testrun " + str(spreadsheet))
                continue
            row = {}
            row["Testrun"] = testrun
            row["Json ID"] = num
            row["Part number"] = part
            row["Part text"] = get_excerpt(part, date)
            row["Analyst name"] = sdata["Analyst name"]
            row["Number of words"] = len(row["Part text"])
            row["Analysis duration"] = sdata["Analysis duration"]
            row["Review duration"] = sdata["Review duration"]
            row["Number of locutions"] = count_nodes("L", num, date) / 2
            row["Number of propositions"] = count_nodes("I", num, date)
            row["Number of YAs (asserting)"] = count_nodes("YA", num, date, ["Asserting"])
            row["Number of YAs (pure questioning, assertiv questioning, rhetorical questioning)"] = count_nodes("YA", num, date, ["PureQuestioning", "AssertiveQuestioning", "RhetoricalQuestioning"])
            row["Number of YAs (all of the rest)"] = count_nodes("YA", num, date) - row['Number of YAs (asserting)'] - row['Number of YAs (pure questioning, assertiv questioning, rhetorical questioning)']
            row["Number of TAs"] = count_nodes("TA", num, date)
            row["Number of MAs"] = count_nodes("MA", num, date)
            row["Number of RAs"] = count_nodes("RA", num, date)
            row["Number of CAs"] = count_nodes("CA", num, date)
            row = pd.DataFrame([row])
            df = pd.concat([df,row])
    df.to_csv("./result.csv", index=None)
