import sqlite3, os, numpy
import pandas as pd

conn = sqlite3.connect('skkuri.db')
cs = conn.cursor()

xls = pd.read_excel('동아리 정리.xlsx')
header = xls.columns.tolist()
contents = xls.values.tolist()[:50]
def ColumnSelect(HEADER, a, b):
    text=""
    for i in range(a, b) :
        text += '"'+HEADER[i]+'",'
    text=text[:-1]
    return text

def InsertValue(CONTENTS, a, b, k):
    text=""
    for i in range(a,b):
        v = CONTENTS[k][i]
        if type(v) is float :
            v = str(v)
        text+='"'+v+'",'
    text=text[:-1]
    return text

COLUMN=ColumnSelect(header, 0, len(header))

for i in range(len(contents)):
    VALUES=InsertValue(contents,0,len(header),i)

    query = f'INSERT INTO club ({COLUMN}) values ({VALUES});'
    print(query)