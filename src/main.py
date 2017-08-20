# main.py
# Author: Ahmad Darmawan

from flask import Flask, request, jsonify
from crawler import *

app = Flask(__name__)

# main form for crawl
@app.route('/crawl_form')
def crawlForm():
    return render_template('html/crawl_form.html')

# main form for extract
@app.route('/extract_form')
def extractForm():
    return render_template('html/extract_form.html')

# process for crawl
@app.route('/crawl', methods=['POST'])
def crawlingFile():
    url=request.form['url']
    classify = request.form['class']
    crawl = Crawler()
    if classify == 'academic':
        year = request.form['year']
        semester = request.form['semester']
        data = crawl.start_crawl_academic(url, year, semester)
    else if classify == 'research':
        info = request.form['info'] # info url (Nama Fakultas / Jurusan / KK)
        data = crawl.start_crawl_research(url, info)

    data.headers["Content-Disposition"] = "attachment; filename=export.csv"
    data.headers["Content-type"] = "text/csv"

    return data

# process for extract
@app.route('/extract', methods=['POST'])
def extractorFile():
    pass
    

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8888")
    )