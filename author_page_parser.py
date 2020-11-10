import logging
import re
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


# TODO: check for empty div_para (see Apr 2014 -> Robert Kirvel)
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

        # verify that we should process this like text and doesn't have any weird embeds or images
        # for now just checking for Scribd embeds
        if soup.find('div', class_='wsite-scribd'):
            return 'scribd'

        # IMG DATAs


        # CONTENT
        div_para = soup.find('div', class_='paragraph')
        if div_para is None:
            logging.warning('no <div class="paragraph"> found in: %s', file)
            return None
        else:
            return str(div_para)

        # D+S just delete this whole thing
        # no point in separating title/auth/content - the html is too janky and irregular
        # we can treat the <div class="para"> as the smallest division
        # need to differentiate b/w the one with content and the one with 'About the Author'
        # (About will basically never come before content)
        # TODO: switch find(div_para) to find_all(), note number of divs found

        # title = None
        # author_name = None
        # content = None
        # cont_start_index = -1

        # children = div_para.contents
        # for i in range(0, len(children)):
        #     child = children[i]
        #     if child is None:
        #         # bad thing, shouldn't happen. log and move on
        #         logging.error('child [%s] is None in <div>: %s', i, str(div_para))
        #     elif child.name is None or child.name != 'br':
        #         child_str = child.get_text().strip() if child.name is not None else str(child).strip()
        #         if re.search(r'^\s*$', child_str):
        #             # string is only whitespace, ignore
        #             continue
        #         else:
        #             # title, name, or content
        #             if title is None:
        #                 title = child_str
        #             elif author_name is None:
        #                 author_name = child_str
        #                 cont_start_index = i + 1
        #                 if cont_start_index >= len(children):
        #                     logging.error('cont_start_index out of bounds in file: %s', file)
        #                     return None
        #                 break
        #             else:
        #                 # bad thing, shouldn't happen. log and move on
        #                 logging.error('title, author_name, and content are None in child: %s of file: %s', str(child), file)
        #                 return None
        #     # elif child.name != 'br':
        #     #     # use get_text() or .string to check for text content in tag
        #     #     # if so, determine which type of content and record
        #     #     if child.get_text() is not None:
        #     #         if re.search(r'^\s*$', str(child.string)):
        #     #             # string is only whitespace, ignore
        #     #             continue
        #     #         else:
        #     #             # title, name, or content
        #     #             if title is None:
        #     #                 title = str(child.string).strip()
        #     #             elif author_name is None:
        #     #                 author_name = str(child.string).strip()
        #     #             elif content is None:
        #     #                 # grab content based on current index i
        #     #                 cont_start_index = i
        #     #                 break
        #     #             else:
        #     #                 # bad thing, shouldn't happen. log and move on
        #     #                 logging.error('title, author_name, and content are None in child: %s of file: %s', str(child), file)
        #     #                 return None
        #     #     else:
        #     #         # shouldn't happen but not critical
        #     #         logging.warning('non-<br/> child has None .string: %s', str(child))

        # if cont_start_index > -1:
        #     content = ''.join([str(s) for s in children[i:len(children)]])
        # else:
        #     logging.error('cont_start_index is -1 for div: %s in file: %s',
        #                    str(div_para), file)
        #     return None
        
        # return content
        
    except FileNotFoundError:
        logging.error('file not found: %s', file)
        return None


