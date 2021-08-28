
from datetime import datetime

import browser_cookie3
import mechanicalsoup
import requests
import re

from scripts.enums import Browser, Action
from scripts import gconfig
from pathlib import Path

def new_scribblehub(
    chapter_title,
    chapter_content,
    local_series_id,
    action=None,
    browser_type=Browser.NONE,
):
    """Creates a new scribblehub draft or chapter using mechanicalsoup to access a stateful browser.
    Returns the new chapter_id if successful, None if unsuccessful."""
    if (action == Action.UPDATE_DRAFT or action == Action.UPDATE_CHAPTER):
        print("wrong function, use update_scribblehub")
        return None

    series_id = gconfig.getStoryInfo(local_series_id)["general"]["scribblehub"]["series_id"]

    host_url = "www.scribblehub.com"
    new_chapter_url = f"https://www.scribblehub.com/addchapter/{series_id}"

    scribble_editedtitle = chapter_title
    scribble_editedinfo = chapter_content

    scribble_action = "wi_addeditchapter"
    if(action == Action.NEWDRAFT):
        scribble_edittype = "savedraft"
    elif(action == Action.NEWCHAPTER):
        scribble_edittype = "publish"
    else:
        print("unsupported action")
        return None
    scribble_postid = f"addchapter-{series_id}"


    now = datetime.now()  # current date and time
    scribble_editdatetime = now.strftime("%b %d, %Y %I:%M %p")

    # Start using mechanicalsoup
    browser = mechanicalsoup.StatefulBrowser()
    if browser_type == Browser.CHROME:
        cj = browser_cookie3.chrome(domain_name="www.scribblehub.com")
    elif browser_type == Browser.FIREFOX:
        cj = browser_cookie3.firefox(domain_name="www.scribblehub.com")
    elif browser_type == Browser.OPERA:
        cj = browser_cookie3.opera(domain_name="www.scribblehub.com")
    elif browser_type == Browser.EDGE:
        cj = browser_cookie3.edge(domain_name="www.scribblehub.com")
    elif browser_type == Browser.CHROMIUM:
        cj = browser_cookie3.chromium(domain_name="www.scribblehub.com")
    else:
        cj = browser_cookie3.load(domain_name="www.scribblehub.com")
    # print(cj)
    browser.set_cookiejar(cj)
    browser.open(new_chapter_url)

    # browser.launch_browser()

    headers = {
        "Scheme": "https",
        "Host": host_url,
        "Filename": "/wp-admin/admin-ajax.php",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    formdata = {
        "action": scribble_action,
        "editedinfo": scribble_editedinfo,
        "editedtitle": scribble_editedtitle,
        "edittype": scribble_edittype,
        "editdatetime": scribble_editdatetime,
        "mypostid": scribble_postid,
    }
    r = requests.post(
        "https://www.scribblehub.com/wp-admin/admin-ajax.php",
        headers=headers,
        data=formdata,
        cookies=browser.get_cookiejar(),
    )

    if r.status_code == 200:
        print(f"Successfully posted new draft chapter. Chapter postid: {r.text}")

        m = re.split('\s+', re.sub(r"[\x00-\x1F\x7F]", ' ', r.text))
        result = ' '.join(m).encode("ascii", "ignore").decode("ascii").strip()
        
        # print("result:", result)

        return result
    else:
        print(
            f"Failed to post new draft chapter.\nResponse text: {r.text}\nReason: {r.reason}\nRequest: {r.request.body}"
        )
        return None

def update_scribblehub(
    chapter_title,
    chapter_content,
    local_series_id,
    postid,
    action=None,
    browser_type=Browser.NONE,
):
    """Updates a scribblehub draft or chapter using mechanicalsoup to access a stateful browser.
    Returns True if successful, None if unsuccessful."""
    if (action == Action.NEW_CHAPTER or action == Action.NEW_DRAFT):
        print("wrong function, use new_scribblehub")
        return None

        series_id = gconfig.getStoryInfo(local_series_id)["general"]["scribblehub"]["series_id"]

    host_url = "www.scribblehub.com"
    new_chapter_url = f"https://www.scribblehub.com/addchapter/{series_id}"

    scribble_editedtitle = chapter_title
    scribble_editedinfo = chapter_content

    scribble_action = "wi_addeditchapter"
    if(action == Action.UPDATEDRAFT):
        scribble_edittype = "savedraft"
    elif(action == Action.UPDATECHAPTER):
        scribble_edittype = "publish"
    else:
        print("unsupported action")
        return None
    scribble_postid = f"{postid}"


    now = datetime.now()  # current date and time
    scribble_editdatetime = now.strftime("%b %d, %Y %I:%M %p")

    # Start using mechanicalsoup
    browser = mechanicalsoup.StatefulBrowser()
    if browser_type == Browser.CHROME:
        cj = browser_cookie3.chrome(domain_name="www.scribblehub.com")
    elif browser_type == Browser.FIREFOX:
        cj = browser_cookie3.firefox(domain_name="www.scribblehub.com")
    elif browser_type == Browser.OPERA:
        cj = browser_cookie3.opera(domain_name="www.scribblehub.com")
    elif browser_type == Browser.EDGE:
        cj = browser_cookie3.edge(domain_name="www.scribblehub.com")
    elif browser_type == Browser.CHROMIUM:
        cj = browser_cookie3.chromium(domain_name="www.scribblehub.com")
    else:
        cj = browser_cookie3.load(domain_name="www.scribblehub.com")
    # print(cj)
    browser.set_cookiejar(cj)
    browser.open(new_chapter_url)

    # browser.launch_browser()

    headers = {
        "Scheme": "https",
        "Host": host_url,
        "Filename": "/wp-admin/admin-ajax.php",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    formdata = {
        "action": scribble_action,
        "editedinfo": scribble_editedinfo,
        "editedtitle": scribble_editedtitle,
        "edittype": scribble_edittype,
        "editdatetime": scribble_editdatetime,
        "mypostid": scribble_postid,
    }
    r = requests.post(
        "https://www.scribblehub.com/wp-admin/admin-ajax.php",
        headers=headers,
        data=formdata,
        cookies=browser.get_cookiejar(),
    )

    if r.status_code == 200:
        print(f"Successfully posted new draft chapter. Chapter postid: {r.text}")
        print(repr(r.text))
        return True
    else:
        print(
            f"Failed to post new draft chapter.\nResponse text: {r.text}\nReason: {r.reason}\nRequest: {r.request.body}"
        )
        return None
