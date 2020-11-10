import os
import shutil
import logging
import month_page_parser as mpp
from bs4 import BeautifulSoup


# dumb hardcoded dir for vscode weirdness
os.chdir('C:\\Users\\jcoat\\Desktop\\archive extractor')
cwd = os.getcwd()

# default output directory
out_dir = os.path.join(cwd, 'out')
if os.path.exists(out_dir):
    print('output dir exists - deleting')
    shutil.rmtree(out_dir)
os.mkdir(out_dir)

# DEBUG
out_dir2 = os.path.join(cwd, 'out 2')
if os.path.exists(out_dir2):
    print('output dir 2 exists - deleting')
    shutil.rmtree(out_dir2)
os.mkdir(out_dir2)

# the dir containing all of our html files
# (site archive was given as a flat dump with no directory structure)
source_dir = os.path.join(cwd, 'gravel archive html copy')


def main():
    # set up logging
    logging.basicConfig(filename='out\\errors.log',
                        format='%(levelname)s:%(message)s',
                        level=logging.INFO)


    month_list = get_month_list(os.path.join(source_dir, 'archives.html'))
    
    if month_list is not None:
        month_dict = process_months(month_list)

        # TODO: seems to verify that month_dict contains the same entries that are written to 'out', but we need to check somehow
        # for the debugging
        for month, genres in month_dict.items():
            # create dir for each month
            month_dir = os.path.join(out_dir2, month)
            os.mkdir(month_dir)

            mf = open(os.path.join(month_dir, month + '.html'), 'w', encoding='utf-8')
            mf.write('<html><body>')

            for genre, authors in genres.items():
                # create dir for each genre
                genre_dir = os.path.join(month_dir, genre)
                os.mkdir(genre_dir)
                
                mf.write(f'<h1>{genre}</h1>')

                for author, content in authors.items():
                    author_path = os.path.join(genre_dir, author + '.html')
                    mf.write(content)
                    try:
                        f = open(author_path, 'w', encoding='utf-8')
                        f.write(content)
                        f.close()
                    except OSError:
                        logging.critical('invalid author name "%s" in %s', author, genre_dir)
                
            mf.close()
        pass
    else:
        logging.critical('month_list is None, something terrible has happened')
        print('BAD THING. Check errors.log')


def process_months(month_list):
    month_dict = {}

    for month in month_list:
        if '2013' in month:
            # TODO: handle 2013 differently
            pass
        else:
            print('parsing:', month)
            # new dir to hold current month's content
            cur_month_dir = os.path.join(out_dir, month)
            os.mkdir(cur_month_dir)
            # literally just the file name
            month_url = month_list[month]

            # open cur month file and read into a bs4 object
            try:
                f = open(os.path.join(source_dir, month_url), 'r', encoding='utf-8')
                soup = BeautifulSoup(f, 'html.parser')
                f.close()

                # each month page contains a table, which contains a list of genres and authors
                # - each author entry links to a page for that work
                # - pull out the <table>, which can then be passed on for further processing
                # - there is no convenient structure here, preprocess first to make data extraction simpler
                table = soup.select('html body div#main-wrap table')
                if len(table) > 1:
                    logging.error('%s tables found in %s', str(len(table)), month_url)
                elif len(table) == 0:
                    # this shouldn't happen, but if it does just note and move on
                    logging.error('no table found in %s', month_url)
                    continue
                table = table[0]

                # TODO: clean up function args
                # now process the <table> and extract author data
                entries = mpp.read_authors_from_table(table,
                                                      month_url,
                                                      cur_month_dir,
                                                      out_dir,
                                                      source_dir)

                month_dict[month] = entries

                # entries = {
                #     'poetry': {
                #         'John Doe': '<div class="paragraph">'
                #         'Jane B.': ...
                #     }
                #     'fiction': {
                #         'Bob Lasagna': ...
                #     }
                # }
            except FileNotFoundError:
                logging.error('file not found in process_months(): %s', month_url)

    return month_dict


# extracts the list of archived months to process from inputted file
def get_month_list(src):
    try:
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
    except FileNotFoundError:
        logging.error('file not found in get_month_list(): %s', src)
        return None



if __name__ == '__main__':
    main()