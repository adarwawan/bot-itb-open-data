# bot-itb-open-data
Bot collecting research and education open data of ITB

# Structure Folder
- app
-- settings
--- setting.json
--- template
-- src
--- crawler
--- extractor
-- start.sh
- web
-- css
-- js
-- index.html
- resource
- scheme

# Tools
- scrapy : for crawling webpages
- inaNLP : for text processing in Indonesia Language
- NLTK : for text processing in English Language
- Anystyle-parser : for parsing string bibliography

- mysql : for collecting url crawling data
- mongodb : for collecting extraction data

# DONE
- 

# TO-DO
- crawl.py
- classificationPage.py
- detectionData.py
- extractData.py
- main.py

# Databases
- CrawledURL
-- id
-- url
-- anchor_text
-- referrer
-- frontier
-- access_date
-- classification
-- is_extracted

- ExtractedData
-- id
-- url
-- classification
-- faculty
-- programme
-- access_time
-- data