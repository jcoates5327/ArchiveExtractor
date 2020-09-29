from html.parser import HTMLParser
from bs4 import BeautifulSoup


# run regex
# select: <html> -> <body> -> <div id='main-wrap'> -> <table> -> all <td>'s
# each entry containted in a <div>
# grab the first <div> of each <td>
# - if for some reason it doesn't exist, handle gracefully and move on
# - if the <div> is NOT class='paragraph', throw the whole <td> out
# stripped_strings generator will be useful
# also should track current genre

genres = ['fiction', 'nonfiction', 'creative nonfiction', 'multimedia', 'poetry']


f = open('april-2014.html', 'r')
soup = BeautifulSoup(f, 'html.parser')
f.close()

tds = soup.select('html body div#main-wrap table td')

cur_genre = None
entries = {}
authors = []

for td in tds:
    divs = td.find_all('div')
    
    for div in divs:
        print(div.get_text())
        
                


    
























def parse_archive():

    f = open('archives.html', 'r')
    soup = BeautifulSoup(f, 'html.parser')
    f.close()

    # get <div> holding archive list
    ar_list = soup.find(id='main-wrap')

    # grab all the <a> tags
    links = ar_list.find_all('a')

    # parse list of links, each pointing to a month archive
    for link in links:
        try:
            parse_month_archive(link)
        except FileNotFoundError:
            # print("no: ", link.get('href'))
            pass

def parse_month_archive(month):
    genres = ['fiction', 'nonfiction', 'poetry', 'multimedia', 'creative nonfiction']

    f = open(month.get('href'))
    month_page = BeautifulSoup(f, 'html.parser')
    f.close()
    print('parsing month: ', month.get('href'))

    # grab main section
    author_list = month_page.find(id='main-wrap')
    tbl = author_list.table
    
    # extract <td>
    tds = tbl.find_all('td')
    # last <td> in the <tr> is junk
    tds = tds[:len(tds)-1]

    # each new <td> will start a new genre listing
    # (genre listings do not always start and end with <td>'s though)
    # we can loop through each <td> entry and process depending on tag type:
    #   - <a> tags are links to each author's page, need to extract 'href' attr and
    #     associate it with cur author
    #   - genre categories are often in <font> tags, but not always
    #   - any other tags can just have raw strings extracted

    fname = '!' + month.get('href') + '.txt'
    f = open(fname, 'w')

    cur_genre = None
    out_str = ''
    for td in tds:
        for child in td.div.contents:
            tag_str = child.string
            if tag_str == None:
                continue

            tag_str = tag_str.lower()
            if tag_str in genres:
                # new genre category
                # reset and output
                f.write(out_str)
                f.write('\r\n\r\n')
                print(out_str + '\n')
                out_str = ''
                cur_genre = tag_str
            else:
                out_str += tag_str
    f.write(out_str)
    f.write('\r\n\r\n')
    f.close()
    print(out_str)
                
        

    # cur_genre = None
    # cur_entry = ''
    # br_count = 0

    # for td in tds:
    #     s = ''
    #     for child in td.div:
    #         s += str(child)
    #     print(s.split('.\t'))
        # for child in td.div.children:
        #     if br_count >= 2:
        #         br_count = 0
        #         # end of current entry; close and begin new one
                

        #     # check for a genre heading
        #     raw_text = child.string
        #     if raw_text != None and raw_text.lower() in genres:
        #         cur_genre = raw_text.lower()
        #         # new genre found - close current doc and open new one
        #         br_count = 0
        #         print(cur_genre)

        #     # each entry is delimited by two consecutive line break tags <br/>
        #     elif (child.name == 'br'):
        #         br_count += 1

    

    # print(td[0].div.get('class'))


# parse_archive()