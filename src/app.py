# app.py
from extractor.table_extractor import TableExtractor 
from extractor.run import RunExtractor
from extractor.template_extractor import TemplateExtractor 
from db.manage_db import DBAcademic

class App(object):
    def __init__(self):
        print("Yey")

    def interface(self, option):
        print("Silahkan pilih menu yang akan dijalankan:")
        print("1. Crawling Akademik")
        print("2. Ekstraksi Akademik")
        print("3. Crawling Penelitian")
        print("4. Ekstraksi Penelitian")
        print("0. Exit")
        try:
            mode=int(raw_input('Input: '))
        except ValueError:
            print "Not a number"
        return mode

a = App()
option = 5
while option != 0:
    option = a.interface(option)