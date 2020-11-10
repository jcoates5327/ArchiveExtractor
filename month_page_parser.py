import re
import os
import shutil
import logging
import author_page_parser as app
from bs4 import BeautifulSoup
from GravelAuthor import *


add_manually = ['emily-jalloul.html', 'ginger-beck.html']

genres = ['fiction', 'nonfiction', 'creative nonfiction', 'multimedia', 'poetry', \
          'book review', 'flash fiction', 'flash creative nonfiction', 'flash/hybrid', \
          'art', 'book reviews', 'flash prose', 'book reviews/author interviews', \
          'flash', 'flash nonfiction', 'trumped-up']


# TODO: clean up args
def read_authors_from_table(table, month_url, cur_month_dir, out_dir, source_dir):

    tds = table.find_all('td')
    tds = tds[:len(tds)-1] # last entry is junk
    
    # build a list of all of the <div> tags in the <table>
    # each one has an author entry
    # - sometimes more than one, log and handle on a case by case basis for now
    divs = []
    for td in tds:
        for div in td.find_all('div'):
            if len(div.contents) >= 1:
                divs.append(div)
    
    # DEBUG
    # f = open(os.path.join(out_dir, 'tbl-' + month_url), 'w', encoding='utf-8')
    # for d in divs:
    #     f.write(str(d))
    # f.close()

    genre_entries = [] # <GravelGenre>
    cur_genre = None

    for div in divs:
        a_tags = []
        is_valid_author_data = False

        for child in div.contents:
            # look for genre text
            if child.name is None:
                txt = child.string
                if txt is not None:
                    txt = txt.strip().lower()
                    if txt in genres:
                        # handle genre detection here
                        txt = re.sub('/', '-', txt)
                        if cur_genre is not None:
                            genre_entries.append(cur_genre)

                        cur_genre = GravelGenre(txt)

            # in almost every case, multiple <a> tags in a <div> is just one author name
            #   split into multiple tags for reasons(?)
            # in this case we can just extract the strings and concatenate, record as author_name
            # maybe at some point check the href's and make sure they match (very edge case though)
            # either way, if a second <a> encountered, append its string onto existing author_name
            elif child.name == 'a':
                a_tags.append(child)

                # grab inner <a> text as author name
                # href attr has link to author's page

                author_name = child.string
                author_url = child.get('href')
                if author_name is not None:
                    # weird edge case - some names are not actually valid
                    if re.search(r'^\s+$', author_name) is None:
                        if author_url is not None:
                            author_data = GravelAuthor(author_name.strip(), author_url)
                            is_valid_author_data = True
                        else:
                            logging.error('no author url (no href attr) in <a> tag in %s\n%s',
                                          month_url,
                                          '\t'+str(child))
                else:
                    logging.error('no author name in <a> tag in %s\n%s',
                                  month_url,
                                  '\t'+str(child))
         
        if is_valid_author_data:
            # check for multiple <a> tags in one <div>
            if len(a_tags) > 1:
                # log error
                logging.info('multiple <a> tags in %s\n%s',
                             month_url,
                             '\n'.join('\t'+str(a) for a in a_tags))

                # concatenate <a> tag strings and update author name
                # new_name = ''
                # for a_tag in a_tags:
                #     if a_tag.string is not None:
                #         new_name += a_tag.string.strip()
                # author_data.name = new_name
        
            # record entry
            # TODO: prob delete this
            cur_genre.add_entry(author_data)
    
    if cur_genre is not None:
        cur_genre.add_entry(author_data)
    else:
        logging.warning('last genre is none in %s', cur_month_dir)

    # /////////////////////////////////////////////////////////////////////////////////
    # TODO: should split into two functions here, this is doing too many things at once
    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


    # parse author pages
    # write contents to current month dir
    # create a dir for each genre, write each author entry to a separate file

    out_dict = {} # maps genre name -> dict containing author entries
    author_dict = {} # maps author name -> content

    # entries = {
    #     'poetry': {
    #         'John Doe': '<div class="paragraph">'
    #         'Jane B.': ...
    #     }
    #     'fiction': {
    #         'Bob Lasagna': ...
    #     }
    # }

    for genre in genre_entries:
        genre_dir = os.path.join(cur_month_dir, genre.name)
        os.mkdir(genre_dir)

        for author_entry in genre.entries:
            # check for external URL
            if 'https' in author_entry.url or 'http' in author_entry.url:
                logging.debug('external URL found: %s', author_entry.url)

                # look for local file
                base = os.path.basename(author_entry.url)

                if base == '':
                    # probably a URL like: http://www.XYZ.com/
                    logging.error('blank URL basename: %s', author_entry.url)
                    continue
                else:
                    # a few don't have an extension
                    if not base.endswith('.html'):
                        base = base + '.html'
                    author_entry.url = base

            # DEBUG
            author_page_raw = app.read_main_div(os.path.join(source_dir,
                                                             author_entry.url))
            if author_page_raw is None:
                logging.error('author_page_raw is None for %s, url: %s',
                                author_entry.name,
                                author_entry.url)
            else:
                f = open(os.path.join(genre_dir, 'raw-'+author_entry.url),
                                     'w', encoding='utf-8')
                f.write(author_page_raw + '\n')
                f.close()


            # a few edge cases are easier to deal with manually; check for them here
            # if author_entry.url in add_manually:
            #     logging.warning('%s encountered - skipping', author_entry.name)
            #     continue

            # read data from the current author's page
            if genre.name != 'multimedia' and genre.name != 'art':
                author_page_content = app.read_content(os.path.join(source_dir,
                                                                    author_entry.url))
                if author_page_content is None:
                    logging.error('author_page_content is None for %s, url: %s',
                                author_entry.name,
                                os.path.join(genre_dir, author_entry.url))
                elif author_page_content == 'scribd':
                    # embedded Scribd doc, handle this later
                    logging.info('Scribd embed found in: %s', os.path.join(genre_dir, author_entry.url))
                else:
                    # at this point we have valid content, record
                    # writing to a file for debugging
                    author_page = AuthorPage(author_entry, author_page_content)
                    f = open(os.path.join(genre_dir, author_entry.url),
                                         'w', encoding='utf-8')
                    f.write(author_page_content + '\n')
                    f.close()

                    author_dict[author_entry.name] = author_page_content
            else:
                # handle multimedia content
                pass
        
        # record entries for output
        out_dict[genre.name] = author_dict
        author_dict = {}

    return out_dict

                
class AuthorPage:
    def __init__(self, author, content):
        self.author = author
        self.content = content               

# keeping for reference for now, not actually in use
# regex that was applied to html in preprocessing
def preprocess_html(html):
    s = re.sub(r'</?span.*?>', '', html)
    s = re.sub(r'</?font.*?>', '', s)
    s = re.sub(r'</?strong.*?>', '', s)
    s = re.sub(r'</?em.*?>', '', s)
    s = re.sub(r'<br ?/>(\s*<br ?/>)*', '</div><div>', s)
    s = re.sub(r'<br>\s*<br/>(\s*<br>\s*<br/>)*', '</div><div>', s)
    s = re.sub(r'<br>\s*</br>', '', s)
    s = re.sub(r'(<div>\s*</div>)+', '', s)
    s = re.sub('<br ?/>', '', s)
    s = re.sub('<div/>', '', s)
    # &#\w+?;   -> ''
    # <div.*?> -> '<div>' (fix class="main-wrap" first)
    return s
