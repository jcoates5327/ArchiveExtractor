import re
import os
from html.parser import HTMLParser
from bs4 import BeautifulSoup

#TODO: keep preprocessed HTML in case of error for debugging
debug_outdir = 'C:\\Users\\jcoat\\Desktop\\debug'
os.mkdir(debug_outdir)


# parse main archives html file, extract each month entry + corresponding url
# for each month entry:
# - extract <table> tag which will contain all of the author data for that month
# - run <table> through preprocessor to make data extraction far easier
# - for now, write processed <table> to tmp file for testing
# - TODO: use these new, clean files as a base to continue data extraction functions
# - TODO: still should probably make sure more of the <a> tags in author entries aren't malformed

def process_months():
    # directory stuff
    cwd = os.getcwd()
    parent = os.path.abspath(os.path.join(cwd, os.pardir))
    in_dir = parent + '\\gravel archive html copy'

    # extract list of months we need to parse from the archives page
    months = build_month_list()

    # do the stuff
    for month in months:
        print('processing month: ' + month)
        url = months[month]
        parse_archive_page(url, in_dir)


def build_month_list():
    f = open('archives.html', 'r', encoding='utf-8')
    soup = BeautifulSoup(f, 'html.parser')
    f.close()

    # grab main content of the archive
    div_main = soup.select('html body div#main-wrap')[0]
    months = {}

    # luckily the whole archive list is all of the <a> tags in this <div>
    for a_tag in div_main.select('a'):
        months[a_tag.get_text().strip()] = a_tag.get('href')
    
    return months


def parse_archive_page(url, in_dir):
    genres = ['fiction', 'nonfiction', 'creative nonfiction', 'multimedia', 'poetry', 'book review', 'flash fiction', 'flash creative nonfiction']
    is_error = False
    err = None

    f = open(in_dir + '\\' + url, 'r', encoding='utf-8')
    soup = BeautifulSoup(f, 'lxml')
    f.close()

    # extract <table> which contains author data
    table = soup.select('html body div#main-wrap table')
    if len(table) > 1:
        print('ERROR: unexpected table found in: ' + url)
    elif len(table) == 0:
        print('ERROR: no table found in: ' + url)
        return
    table = table[0]



    # preprocessing
    # - clean up HTML
    out = preprocess_html(str(table))
    
    table = BeautifulSoup(out, 'html.parser').table
    f = open(debug_outdir + '\\table-' + url, 'w', encoding='utf-8')
    f.write(out)
    f.close()

    if table is None:
        # something terrible has happened
        print('ERROR: no table found after preprocessing in: ' + url)
        return

    tds = table.find_all('td')
    tds = tds[:len(tds)-1] # last entry is junk

    cur_genre = None
    entries = {}
    authors = []

    outs = []
    for td in tds:
        divs = td.find_all('div')
        
        # a div is either: 1) a genre heading, 2) an author entry, 3) something else we can disregard
        for div in divs:
            if len(div.contents) > 0:
                # DEBUG: printing contents of each child element
                # TODO: not all <strong>'s are direct children of <div>'s
                for child in div.contents:
                    if child.name == 'strong':
                        outs.append('name: ' + str(child) + '\n')
                outs.append('----------------------------\n')
                

                if div.get_text().strip().lower() in genres:
                    # new genre
                    #print(div.get_text())
                    entries[cur_genre] = authors
                    cur_genre = div.get_text().strip().lower()
                else:
                    author = {}

                    # TODO: this is garbage - find a better way to extract author data

                    



        # end <div> loop
    # end <td> loop
    f = open(debug_outdir + '\\contents-' + url, 'w', encoding='utf-8')
    f.writelines(outs)
    f.close()



def preprocess_html(html):
    s = re.sub(r'</?span.*?>', '', html)
    s = re.sub(r'<br/>(\s*<br/>)+', '</div><div>', s)
    s = re.sub(r'<br>\s*<br/>(\s*<br>\s*<br/>)+', '</div><div>', s)
    s = re.sub(r'<br>\s*</br>', '', s)
    s = re.sub(r'(<div>\s*</div>)+', '', s)
    s = re.sub('<br/>', '', s)
    s = re.sub('<div/>', '', s)

    # apply regex sub
    # s = re.sub(r'</?span.*?>', '', html)
    # s = re.sub(r'&nbsp;', '', s)
    # s = re.sub(r'<br />', r'<br/>', s)
    # s = re.sub(r'<br/>(\s*<br/>)+', r'<br/>', s)
    # s = re.sub(r'(<a ?\S*>\s*)(<br/>\s*)+', r'<br/>\1', s)
    # s = re.sub(r'(<br/>\s*)+', r'</div><div>', s)
    # s = re.sub(r'<div ?/>', '', s)
    # s = re.sub(r'<a href=".+?"\s*/>', '', s)
    # s = re.sub(r'<a href="http://www.gravelmag.com/william-james.html"\s*>\s*</a>', '', s)
    
    return s
    
#parse_archive_page('august-2015.html')
process_months()