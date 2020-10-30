import logging
from bs4 import BeautifulSoup


# TODO: output author data to one file per author instead of genre (temp.)
# takes in a file and extracts the piece of literature it contains (poem, short story, etc.)
def read_main_div(file):
    try:
        f = open(file, 'r', encoding='utf-8')
        soup = BeautifulSoup(f, 'html.parser')
        f.close()

        div_main = soup.find('div', id='main-wrap')
        if div_main is None:
            logging.error('no <div id="main-wrap"> found in %s', file)
            return None
        return str(div_main)
    except FileNotFoundError:
        logging.error('file not found: %s', file)
        return None


# TODO: NON-MULTIMEDIA
# - get main img data: URL, title, descr., alt text
# - get content: title, author, text
# - get 'about' section: image, text
#
# - just return a tuple? add to an author_page obj in mpp?
def read_content(file):
    try:
        f = open(file, 'r', encoding='utf-8')
        soup = BeautifulSoup(f, 'html.parser')
        f.close()

        # main img data


        # content
        div_para = soup.find('div', class_='paragraph')
        if div_para is None:
            logging.warning('no <div class="paragraph"> found in: %s', file)
            return None

        # let's try looking for:
        # - work title in a <font> tag
        # - author name in an <em>
        #   (we obv already know the author name but worth checking, also gives us a way
        #    to definitively distinguish between content and metadata)
        font = div_para.find('font')
        if font is None:
            logging.info('no <font> in: %s', file)
            return None


        return str(div_para)

        # about
        
    except FileNotFoundError:
        logging.error('file not found: %s', file)
        return None


