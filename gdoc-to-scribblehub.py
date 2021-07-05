from __future__ import print_function
import os
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import browser_cookie3
import json
import mechanicalsoup
import requests
from datetime import datetime

from enum import Enum
class Action(Enum):
    NEW_DRAFT = 0
    UPDATE_DRAFT = 1
    # ! TODO: haven't built any of the other functionality
    NEW_CHAPTER = 2
    UPDATE_CHAPTER = 3

class Browser(Enum):
    CHROME = 0
    FIREFOX = 1
    OPERA = 2
    EDGE = 3
    CHROMIUM = 4

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

# The ID of a document.
secrets_folder = Path("secrets")
with open(secrets_folder / "secrets.json") as f:
  secrets = json.load(f)

DOCUMENT_ID = secrets['google_docs']['gdoc_id']

# * Horizontal line will return '<hr />'

def handleTextStyle(text_run):
    if(len(text_run.get('textStyle'))==0):
        # print('no more text style')
        return text_run
    else:
        if(text_run.get('textStyle').get('bold')):
            # delete bold
            text_run.get('textStyle').pop('bold')
            # add bold tags to front and back
            text_run.update(content = '<strong>'+text_run.get('content')+'</strong>')
            return handleTextStyle(text_run)

        elif(text_run.get('textStyle').get('italic')):
            text_run.get('textStyle').pop('italic')             # delete italic
            text_run.update(content = '<em>'+text_run.get('content')+'</em>') # add bold italic to front and back
            return handleTextStyle(text_run)

        elif(text_run.get('textStyle').get('underline')):
            text_run.get('textStyle').pop('underline')             # delete underline
            text_run.update(content = '<span style="text-decoration: underline;">'+text_run.get('content')+'</span>') # add underline tags to front and back
            return handleTextStyle(text_run)

        elif(text_run.get('textStyle').get('strikethrough')):
            text_run.get('textStyle').pop('strikethrough')             # delete strikethrough
            text_run.update(content = '<span style="text-decoration: line-through;">'+text_run.get('content')+'</span>') # add strikethrough tags to front and back
            return handleTextStyle(text_run)
        else:
            print('unrecognized styles remain')
            return text_run

def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get('textRun')
    if not text_run:
        if element.get('horizontalRule'):
            return '<hr />', False
        return ''
    text_run = handleTextStyle(text_run)
    return text_run.get('content'), True


def read_strucutural_elements(elements, addPTag=True):
    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            elements: a list of Structural Elements.
    """
    text = ''
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')

            elements_text = ''
            # addPTag = True
            for elem in elements:
                elem_text, addPTag = read_paragraph_element(elem)
                elements_text += elem_text
            
            if(addPTag):
                if(elements_text[-1]=='\n'):
                    text+= '<p>'+elements_text[:-1]+'</p>\n'
                else:
                    text += '<p>'+elements_text+'</p>'
            else:
                text += elements_text
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            #style="border-collapse: collapse; width: 100%;"
            text+='<table><tbody>'
            table = value.get('table')
            for row in table.get('tableRows'):
                text+='<tr>'
                cells = row.get('tableCells')
                for cell in cells:
                    #style="width: 50%;"
                    text +=  '<td>' + read_strucutural_elements(cell.get('content')) + '</td>'
                text+='</tr>'
            text+='</tbody></table>'
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_strucutural_elements(toc.get('content'))
    return text

def new_scribblehub_chapter(chapter_title, chapter_content, action=Action.NEW_DRAFT, postid=None, browser_type=Browser.FIREFOX):
    """Creates a new scribblehub chapter using mechanicalsoup to access a stateful browser.
    Returns True if successful, False if unsuccessful."""
    if(postid is None and action==Action.UPDATE_DRAFT):
        print('need postid to update draft')
        return False

    series_id = secrets["scribblehub"]["series_id"]
    # username = secrets["scribblehub"]["username"]
    # password = secrets["scribblehub"]["password"]

    host_url = "www.scribblehub.com"
    # login_url = "https://www.scribblehub.com/login/"
    new_chapter_url = f"https://www.scribblehub.com/addchapter/{series_id}"

    scribble_editedtitle = chapter_title
    scribble_editedinfo = chapter_content

    if(action==Action.NEW_DRAFT):
        scribble_action = 'wi_addeditchapter'
        scribble_edittype = 'savedraft'
        scribble_postid = f"addchapter-{series_id}"

    elif(action==Action.UPDATE_DRAFT):
        scribble_action = 'wi_addeditchapter'
        scribble_edittype = 'savedraft'
        scribble_postid = postid
    
    elif(action==Action.NEW_CHAPTER):
        # !
        print('TODO!!!')
        return False
    
    elif(action==Action.UPDATE_CHAPTER):
        # !
        print('TODO !!!')
        return False

    now = datetime.now() # current date and time
    scribble_editdatetime = now.strftime("%b %d, %Y %I:%M %p")

    # Start using mechanicalsoup
    browser = mechanicalsoup.StatefulBrowser()
    if(browser_type==Browser.CHROME):
        cj = browser_cookie3.chrome(domain_name='www.scribblehub.com')
    elif(browser_type==Browser.FIREFOX):
        cj = browser_cookie3.firefox(domain_name='www.scribblehub.com')
    elif(browser_type==Browser.OPERA):
        cj = browser_cookie3.opera(domain_name='www.scribblehub.com')
    elif(browser_type==Browser.EDGE):
        cj = browser_cookie3.edge(domain_name='www.scribblehub.com')
    elif(browser_type==Browser.CHROMIUM):
        cj = browser_cookie3.chromium(domain_name='www.scribblehub.com')
    else:
        cj = browser_cookie3.load(domain_name='www.scribblehub.com')
    print(cj)
    browser.set_cookiejar(cj)
    browser.open(new_chapter_url)

    # browser.launch_browser()

    headers = {
        "Scheme": "https",
        "Host": host_url,
        "Filename":"/wp-admin/admin-ajax.php",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept":"*/*",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    formdata = {
        "action": scribble_action,
        "editedinfo": scribble_editedinfo,
        "editedtitle": scribble_editedtitle,
        "edittype": scribble_edittype,
        "editdatetime": scribble_editdatetime,
        "mypostid": scribble_postid
    }
    r = requests.post("https://www.scribblehub.com/wp-admin/admin-ajax.php",headers=headers,data=formdata, cookies=browser.get_cookiejar())

    if(r.status_code==200):
        print(f"Successfully posted {action.name} chapter. Chapter postid: {r.text}")
        print(repr(r.text))
        return True
    else:
        print(f"Failed in {action.name}.\nResponse text: {r.text}\nReason: {r.reason}\nRequest: {r.request.body}")
        return False

def main():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(secrets_folder / 'token.json'):
        creds = Credentials.from_authorized_user_file(secrets_folder / 'token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                secrets_folder / 'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(secrets_folder / 'token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('docs', 'v1', credentials=creds)

    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=DOCUMENT_ID).execute()
    doc_content = document.get('body').get('content')
    # doc_dumps = json.dumps(doc_content, indent=4)
    # print(doc_dumps)
    # print('The title of the document is: {}'.format(document.get('title')))

    chapter_title = document.get('title')
    chapter_content = read_strucutural_elements(doc_content)
    print(chapter_title)
    print(chapter_content)

    print(f"Successful: {new_scribblehub_chapter(chapter_title, chapter_content, action=Action.NEW_DRAFT, postid='314255')}")


if __name__ == '__main__':
    main()