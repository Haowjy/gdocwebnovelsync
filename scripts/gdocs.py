import json
import os
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path

import browser_cookie3
import mechanicalsoup
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]

parent = Path(".")
local_storage_path = parent / Path("localstorage")
secrets_folder_path = parent /  Path("secrets")

# print(Path(config["settings"]["localstorage"]))

def handleTextStyle(text_run):
    if len(text_run.get("textStyle")) == 0:
        # print('no more text style')
        return text_run
    else:
        if text_run.get("textStyle").get("bold"):
            # delete bold
            text_run.get("textStyle").pop("bold")
            # add bold tags to front and back
            text_run.update(content="<strong>" + text_run.get("content") + "</strong>")
            return handleTextStyle(text_run)

        elif text_run.get("textStyle").get("italic"):
            text_run.get("textStyle").pop("italic")  # delete italic
            text_run.update(
                content="<em>" + text_run.get("content") + "</em>"
            )  # add bold italic to front and back
            return handleTextStyle(text_run)

        elif text_run.get("textStyle").get("underline"):
            text_run.get("textStyle").pop("underline")  # delete underline
            text_run.update(
                content='<span style="text-decoration: underline;">'
                + text_run.get("content")
                + "</span>"
            )  # add underline tags to front and back
            return handleTextStyle(text_run)

        elif text_run.get("textStyle").get("strikethrough"):
            text_run.get("textStyle").pop("strikethrough")  # delete strikethrough
            text_run.update(
                content='<span style="text-decoration: line-through;">'
                + text_run.get("content")
                + "</span>"
            )  # add strikethrough tags to front and back
            return handleTextStyle(text_run)
        else:
            print("unrecognized styles remain")
            return text_run


def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

    Args:
        element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get("textRun")
    if not text_run:
        if element.get("horizontalRule"):
            return "<hr />", False
        return ""
    text_run = handleTextStyle(text_run)
    return text_run.get("content"), True


def read_strucutural_elements(elements, addPTag=True):
    """Recurses through a list of Structural Elements to read a document's text where text may be
    in nested elements.

    Args:
        elements: a list of Structural Elements.
    """
    text = ""
    for value in elements:
        if "paragraph" in value:
            elements = value.get("paragraph").get("elements")

            elements_text = ""
            # addPTag = True
            for elem in elements:
                elem_text, addPTag = read_paragraph_element(elem)
                elements_text += elem_text

            if addPTag:
                if elements_text[-1] == "\n":
                    text += "<p>" + elements_text[:-1] + "</p>\n"
                else:
                    text += "<p>" + elements_text + "</p>"
            else:
                text += elements_text
        elif "table" in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            # style="border-collapse: collapse; width: 100%;"
            text += "<table><tbody>"
            table = value.get("table")
            for row in table.get("tableRows"):
                text += "<tr>"
                cells = row.get("tableCells")
                for cell in cells:
                    # style="width: 50%;"
                    text += (
                        "<td>"
                        + read_strucutural_elements(cell.get("content"))
                        + "</td>"
                    )
                text += "</tr>"
            text += "</tbody></table>"
        elif "tableOfContents" in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get("tableOfContents")
            text += read_strucutural_elements(toc.get("content"))
    return text

def read_google_document(gdoc_id, series_name):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(secrets_folder_path / "token.json"):
        creds = Credentials.from_authorized_user_file(
            secrets_folder_path / "token.json", SCOPES
        )
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                secrets_folder_path / "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(secrets_folder_path / "token.json", "w") as token:
            token.write(creds.to_json())

    service = build("docs", "v1", credentials=creds)

    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=gdoc_id).execute()
    doc_content = document.get("body").get("content")

    # doc_dumps = json.dumps(doc_content, indent=4)
    # print(doc_dumps)
    # print('The title of the document is: {}'.format(document.get('title')))

    chapter_title = document.get("title")
    chapter_content = read_strucutural_elements(doc_content)
    # print(chapter_title)
    # print(chapter_content)
    storage_folder = Path("localstorage")

    (storage_folder / Path(series_name)).mkdir(parents=True, exist_ok=True)

    path = storage_folder / series_name / f"{chapter_title}"
    print("path",path)

    with open(storage_folder / series_name / f"{chapter_title}", "w") as file:
        file.write(chapter_content)
    
    return chapter_title, chapter_content, f"{path}"

if __name__ == "__main__":
    read_google_document("1Tc8H2qqPOvZLSKEFNz67IWyfUnORy8eXkNsWWQQCiaA")