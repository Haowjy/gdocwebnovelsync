from __future__ import print_function

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

from scripts import gconfig, gdocs
from scripts.postchapters import royalroad, scribblehub
from scripts.enums import Browser, Action

if __name__ == "__main__":
    series_name = "Summoned Slinger"
    gdoc_chapter_id = "13QlKoYu2QqJhv132jq7KGB4aaIMXumgmsXSK5_VSZF8"

    title, content, path = gdocs.read_google_document(gdoc_chapter_id, series_name)
    postid = scribblehub.new_scribblehub(title, content, 0, action=Action.NEWDRAFT, browser_type=Browser.FIREFOX)
    
    # print("postid:", postid)
    
    # gconfig.registerChapterLocally(0, path, scribblehub=postid)