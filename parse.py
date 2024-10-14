import xml.etree.ElementTree as etree
import mwparserfromhell as mw
import wikitextparser as wtp
import regex as re


def do_xml_parse(fp, tag):
    """ 
    Iteratively parses XML files for a specific tag
    """
    # Go to the start of the file
    fp.seek(0)

    #Go through the xml file iteratively
    for event, elem in etree.iterparse(fp, events=('start', 'end')):
        #If the event has the tag that we want to look for, return the element
        if event == 'end' and elem.tag == tag:
            yield elem
            elem.clear()  # Clear the element to free memory 

def sanitize_filename(title):
    '''Gets rid of invalid file path characters with an underscore'''
    # Use regex to replace any character that is not a valid filename character
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', title)


file_path = "/Users/arezkhidr/Desktop/enwiki-20241001-pages-articles-multistream.xml"
f = open(file_path, "rb")

try:
    for page in do_xml_parse(f, "{http://www.mediawiki.org/xml/export-0.11/}page"): 
        #Title and the text are elements that are subchildren, not attributes
        #So in order to grab them we use find text
    
        #Get the title and text of the pages
        title = page.findtext('./{http://www.mediawiki.org/xml/export-0.11/}title') 

        #The text element is inside the revision of the file so we have to find it in the subchild of that 
        #Thenw e can grab the text from that
        revision = page.find('./{http://www.mediawiki.org/xml/export-0.11/}revision') 
        text = revision.findtext('./{http://www.mediawiki.org/xml/export-0.11/}text')

        #Call the wikimediaparser from hell on every page text to get the list of teh links
        links = mw.parse(text).filter_wikilinks()
        title_links = []

        for link in links: 
            title_links.append(str(link.title))


        #Use the wtp to just get hte text
        filtered_text = wtp.parse(text).plain_text()
        #Make all the text be on one line as a string
        filtered_text = filtered_text.replace("\n", "")

        #If the file is not a redirect then go ahead and create its file
        if not filtered_text.split(" ")[0] == "#REDIRECT": 
            print("file was created")
            file_path = "/Users/arezkhidr/Desktop/WikiData"
            #Write all of these to a new file
            file_name = sanitize_filename(title)
            new_file = open("/Users/arezkhidr/Desktop/WikiData/" + file_name + ".txt", "w")
            #Wrtite the title to the first line
            new_file.write(title + '\n')
            #Write the list of all the linked articles to the second line
            new_file.write(','.join(title_links) + '\n')
            #Write all of the text to the third line
            new_file.write(filtered_text)

            new_file.close()
        else: 
            print(title + " was a redirect")
except: 
    print("File failed to be created")
#Close the xml parser file
f.close()
