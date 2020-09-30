import re
from html.parser import HTMLParser
from bs4 import BeautifulSoup


# parse main archives html file, extract each month entry + corresponding url
# for each month entry:
# - extract <table> tag which will contain all of the author data for that month
# - run <table> through preprocessor to make data extraction far easier
# - for now, write processed <table> to tmp file for testing
# - TODO: use these new, clean files as a base to continue data extraction functions
# - TODO: still should probably make sure more of the <a> tags in author entries aren't malformed

def process_months():
    months = build_month_list()

    for month in months:
        url = months[month]
        parse_archive_page(url)


def build_month_list():
    f = open('archives.html', 'r', encoding='utf-8')
    soup = BeautifulSoup(f, 'html.parser')
    f.close()

    # grab main content of the archive
    div_main = soup.select('html body div#main-wrap')[0]
    months = {}

    for a_tag in div_main.select('a'):
        months[a_tag.get_text().strip()] = a_tag.get('href')
    
    return months


def parse_archive_page(url):
    in_dir = r'C:\Users\jcoat\Desktop\gravel archive html copy'
    out_dir = r'C:\Users\jcoat\Desktop\test 1'
    genres = ['fiction', 'nonfiction', 'creative nonfiction', 'multimedia', 'poetry']


    f = open(in_dir + '\\' + url, 'r', encoding='utf-8')
    soup = BeautifulSoup(f, 'html.parser')
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
    out = preprocess_html(str(table))
    fname = out_dir + '\\' + url
    f = open(fname, 'w', encoding='utf-8')
    f.write(out)
    f.close()

    # tds = table.find_all('td')
    # tds = tds[:len(tds)-1] # last entry is junk

    # cur_genre = None
    # entries = {}
    # authors = []

    # for td in tds:
    #     divs = td.find_all('div')
        
    #     # a div is either: 1) a genre heading, 2) an author entry, 3) something else we can disregard
    #     for div in divs:
    #         if div.get_text().lower() in genres:
    #             # new genre
    #             #print(div.get_text())
    #             entries[cur_genre] = authors
    #             cur_genre = div.get_text().lower()
    #         else:
    #             # sanity check
    #             if div.a is None:
    #                 continue

    #             author = {}

    #             # - get <strong> tag, if exists
    #             # - get_text().strip(), save as $name
    #             # - check if <strong> contains <a>
    #             #   - if yes: extract() <a> tag
    #             #   - if no: decompose() <strong> tag, grab <a> from <div>
    #             # - grab 'href', save as $url
    #             # - save remaining <div> text as $blurb
	#
	#			  # - <div> may not have a link; see october-2017.html -> Aden Thomas
    #             strong_tag = div.find('strong')
    #             if strong_tag is not None:
    #                 author['name'] = strong_tag.get_text().strip()
    #                 a_tag = strong_tag.find('a')
    #                 if a_tag is not None:
    #                     a_tag = strong_tag.a.extract()
    #                 else:
    #                     div.strong.decompose()
    #                     a_tag = div.a
    #                 author['blurb'] = div.get_text().strip()
    #                 author['url'] = a_tag.get('href')
    #             #print(author)
	

def preprocess_html(html):
    # apply regex sub
    s = re.sub(r'</?span.*?>', '', html)
    s = re.sub(r'&nbsp;', '', s)
    s = re.sub(r'<br />', r'<br/>', s)
    s = re.sub(r'<br/>(\s*<br/>)+', r'<br/>', s)
    s = re.sub(r'(<a ?\S*>\s*)(<br/>\s*)+', r'<br/>\1', s)
    s = re.sub(r'<br/>\s*', r'</div><div>', s)
    s = re.sub(r'<div ?/>', '', s)
    s = re.sub(r'<a href=".+?"\s*/>', '', s)
    s = re.sub(r'<a href="http://www.gravelmag.com/william-james.html"\s*>\s*</a>', '', s)
    s = re.sub(r'(<div>\s*​</div>\s*)+', '', s)
    
    return s
    
#parse_archive_page('august-2015.html')
process_months()