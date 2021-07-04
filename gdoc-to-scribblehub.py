from __future__ import print_function
import os
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import json
import mechanicalsoup
import requests
from datetime import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

# The ID of a document.
secrets_folder = Path("secrets")
print(os.path.exists(secrets_folder / "secrets.json") )
with open(secrets_folder / "secrets.json") as f:
  secrets = json.load(f)

DOCUMENT_ID = secrets['google_docs']['gdoc_id']

# * Horizontal line will return '<hr />'

def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get('textRun')
    if not text_run:
        if element.get('horizontalRule'):
            return '<hr />'
        return ''
    return "<p>"+text_run.get('content').replace("\n","</p>\n")


def read_strucutural_elements(elements):
    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            elements: a list of Structural Elements.
    """
    text = ''
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                text += read_paragraph_element(elem)
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get('table')
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    text += read_strucutural_elements(cell.get('content'))
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_strucutural_elements(toc.get('content'))
    return text

def new_scribblehub_chapter(chapter_title, chapter_content, draft=True):
    """Creates a new scribblehub chapter using mechanicalsoup to access a stateful browser.
    Returns True if successful, False if unsuccessful."""
    series_id = secrets["scribblehub"]["series_id"]
    username = secrets["scribblehub"]["username"]
    password = secrets["scribblehub"]["password"]

    host_url = "www.scribblehub.com"
    login_url = "https://www.scribblehub.com/login/"
    new_chatper_url = f"https://www.scribblehub.com/addchapter/{series_id}"

    chapter_title = chapter_title
    chapter_content = chapter_content

    now = datetime.now() # current date and time
    editdatetime = now.strftime("%b %d, %Y %I:%M %p")

    # Start using mechanicalsoup
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(login_url)

    browser.select_form('form[name="loginform"]')
    browser["reg_username"] = username
    browser["reg_password"] = password
    response = browser.submit_selected()
    browser.open(new_chatper_url)
    headers = {
        "Scheme": "https",
        "Host": host_url,
        "Filename":"/wp-admin/admin-ajax.php",
    }

    formdata = {
        "action": "wi_addeditchapter",
        "editedinfo": chapter_content,
        "editedtitle": chapter_title,
        "edittype": "savedraft",
        "editdatetime": editdatetime,
        "mypostid": f"addchapter-{series_id}"
    }

    r = requests.post("https://www.scribblehub.com/wp-admin/admin-ajax.php",headers=headers,data=formdata, cookies=browser.get_cookiejar())

    if(r.status_code==200):
        draftString=""
        if(draft):
            draftString = "draft"
        print(f"Successfully posted {draftString} chapter. Chapter postid: {r.text}")
        return True
    else:
        print(f"Failed. Response text: {r.text}")
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

    print(f"Successful: {new_scribblehub_chapter(chapter_title, chapter_content, draft=True)}")


if __name__ == '__main__':
    main()