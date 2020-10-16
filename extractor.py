import re
import os
import shutil
from html.parser import HTMLParser
from bs4 import BeautifulSoup

errors = []

genres = ['fiction', 'nonfiction', 'creative nonfiction', 'multimedia', 'poetry', \
          'book review', 'flash fiction', 'flash creative nonfiction', 'flash/hybrid', \
          'art', 'book reviews', 'flash prose', 'book reviews/author interviews', 'flash']


# dumb hardcoded dir for vscode weirdness
os.chdir('C:\\Users\\jcoat\\Desktop\\archive extractor')
cwd = os.getcwd()

# default output directory
out_dir = os.path.join(cwd, 'out')
if os.path.exists(out_dir):
    print('output dir exists - deleting')
    shutil.rmtree(out_dir)
os.mkdir(out_dir)

# the dir containing all of our html files
# (site archive was given as a flat dump with no directory structure)
source_dir = os.path.join(cwd, 'gravel archive html copy')

def main():
    month_list = get_month_list(os.path.join(source_dir, 'archives.html'))
    process_months(month_list)
    
    f = open(os.path.join(out_dir, 'errors.txt'), 'w', encoding='utf-8')
    f.writelines(errors)
    f.close()

def process_months(month_list):
    for month in month_list:
        if '2013' in month:
            # handle 2013 differently
            pass
        else:
            # new dir to hold current month's content
            cur_month_dir = os.path.join(out_dir, month)
            os.mkdir(cur_month_dir)
            # literally just the file name
            month_url = month_list[month]

            # open cur month file and read into a bs4 object
            f = open(os.path.join(source_dir, month_url), 'r', encoding='utf-8')
            soup = BeautifulSoup(f, 'html.parser')
            f.close()

            # each month page contains a table, which contains a list of genres and authors
            # - each author entry links to a page for that work
            # - pull out the <table>, which can then be passed on for further processing
            # - there is no convenient structure here, preprocess first to make data extraction simpler
            table = soup.select('html body div#main-wrap table')
            if len(table) > 1:
                errors.append('error: ' + str(len(table)) + ' tables found in ' + month_url + '\n')
                errors.append('\n\n')
            elif len(table) == 0:
                # this shouldn't happen, but if it does just note and move on
                errors.append('error: no table found in ' + month_url + '\n')
                errors.append('\n\n')
                continue
            table = table[0]

            # preprocessing
            table_str = preprocess_html(str(table))
            table = BeautifulSoup(table_str, 'html.parser').table

            if table is None:
                # this shouldn't happen, but if it does just note and move on
                errors.append('error: no table found after preprocessing in ' + month_url)
                continue

            # DEBUG
            # f = open(os.path.join(out_dir, 'table-' + month_url), 'w', encoding='utf-8')
            # f.write(str(table))
            # f.close()

            # now process the <table> and extract author data
            entries = read_authors_from_table(table, month_url, cur_month_dir)


def read_authors_from_table(table, month_url, cur_month_dir):
    tds = table.find_all('td')
    tds = tds[:len(tds)-1] # last entry is junk
    
    # build a list of all of the <div> tags in the <table>
    # each one has an author entry
    # - sometimes more than one, log and handle on a case by case basis for now
    divs = []
    for td in tds:
        for div in td.find_all('div'):
            divs.append(div)
    
    # DEBUG
    f = open(os.path.join(out_dir, 'tbl-' + month_url), 'w', encoding='utf-8')
    f.write(str(table))
    f.close()

    # map a genre to an array of author dicts
    genre_entries = {}
    author_entries = []
    cur_genre = None

    for div in divs:
        div_contents = div.contents
        if len(div_contents) == 0:
            continue

        author_data = {}
        a_tags = []
        is_valid_author_data = False

        for child in div_contents:
            # look for genre text
            if child.name is None:
                txt = child.string
                if txt is not None:
                    txt = txt.strip().lower()
                    if txt in genres:
                        # handle genre detection here
                        txt = re.sub('/', '-', txt)
                        if cur_genre is not None:
                            genre_entries[cur_genre] = author_entries
                            author_entries = []
                        cur_genre = txt
                        continue

            # in almost every case, multiple <a> tags in a <div> is just one author name
            #   split into multiple tags for reasons(?)
            # in this case we can just extract the strings and concatenate, record as author_name
            # maybe at some point check the href's and make sure they match (very edge case though)
            # either way, if a second <a> encountered, append its string onto existing author_name
            if child.name == 'a':
                a_tags.append(child)

                # grab inner <a> text as author name
                # href attr has link to author's page

                author_name = child.string
                author_url = child.get('href')
                if author_name is not None:
                    if author_url is not None:
                        author_data['name'] = author_name.strip()
                        author_data['url'] = author_url
                        is_valid_author_data = True
                    else:
                        errors.append('error: no author url (no href attr) in <a> tag in ' + month_url + '\n')
                        errors.append(str(child) + '\n')
                        errors.append('\n\n')
                else:
                    errors.append('error: no author name in <a> in ' + month_url + '\n')
                    errors.append(str(child) + '\n')
                    errors.append('\n\n')
            
        if len(a_tags) > 1:
            # log error
            errors.append('warning: multiple <a> tags in ' + month_url + '\n')
            for a_tag in a_tags:
                errors.append(str(a_tag) + '\n')
            errors.append('\n\n')

            # concatenate <a> tag strings and update author name
            if is_valid_author_data:
                new_name = ''
                for a_tag in a_tags:
                    if a_tag.string is not None:
                        new_name += a_tag.string.strip()
                author_data['name'] = new_name
        
        # record entry
        author_entries.append(author_data)

    # TODO: figure out why last genre entry not being written
    #       also some seem to just not be recognized?
    # write contents to current month dir
    for genre in genre_entries:
        fname = genre + '.txt'
        f = open(os.path.join(cur_month_dir, fname), 'w', encoding='utf-8')

        for author_entry in genre_entries[genre]:
            try:
                f.write('name: ' + author_entry['name'] + '\n')
                f.write('url: ' + author_entry['url'] + '\n')
            except KeyError:
                # means more than likely it's a genre tag
                errors.append('error: KeyError in: ' + cur_month_dir + '\\' + fname + '\n')
            f.write('----------------\n')
        f.close()
                


# TODO: finish <table> parsing
# takes in a file and extracts the piece of literature it contains (poem, short story, etc.)
def read_author_content_from_file(file):
    f = open(file, 'r', encoding='utf-8')
    soup = BeautifulSoup(f, 'html.parser')
    f.close()

    # similar to the month listings, what we want in author files is in one of the tables in a main div
    table = soup.select('html body div#main-wrap table')
    if table is None:
        return None
    
    # second <td> of first <tr>
    # first <div> might be picture, second content
    td = table.find_all('td')
    if td is None or len(td) < 2:
        # bad, record the error
        return

    td = td[1]
    divs = td.find_all('div')
    if divs is None:
        # error
        pass
    elif len(divs) < 2:
        # no picture maybe?
        pass
    else:
        # get image and content
        pass
    
    

# extracts the list of archived months to process from inputted file
def get_month_list(src):
    f = open(src, 'r', encoding='utf-8')
    soup = BeautifulSoup(f, 'html.parser')
    f.close()

    # grab main content of the archive
    div_main = soup.select('html body div#main-wrap')[0]
    months = {}

    # luckily the whole archive list is all of the <a> tags in this <div>
    for a_tag in div_main.select('a'):
        months[a_tag.get_text().strip()] = a_tag.get('href')
    
    return months


def preprocess_html(html):
    s = re.sub(r'</?span.*?>', '', html)
    s = re.sub(r'</?font.*?>', '', s)
    s = re.sub(r'</?strong.*?>', '', s)
    s = re.sub(r'</?em.*?>', '', s)
    s = re.sub(r'<br/>(\s*<br/>)*', '</div><div>', s)
    s = re.sub(r'<br>\s*<br/>(\s*<br>\s*<br/>)*', '</div><div>', s)
    s = re.sub(r'<br>\s*</br>', '', s)
    s = re.sub(r'(<div>\s*</div>)+', '', s)
    s = re.sub('<br/>', '', s)
    s = re.sub('<div/>', '', s)

    return s


if __name__ == '__main__':
    main()