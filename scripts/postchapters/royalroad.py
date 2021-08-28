
from datetime import datetime

import browser_cookie3
import mechanicalsoup
import requests

from scripts.enums import Browser
from scripts.enums import Action
from scripts import gconfig

def new_royalroad(
    chapter_title,
    chapter_content,
    local_series_id,
    action=None,
    browser_type=Browser.NONE,
):
    """Creates a new royalroad draft or chapter using mechanicalsoup to access a stateful browser.
        Returns True if successful, False if unsuccessful."""
    if (action == Action.UPDATE_DRAFT or action == Action.UPDATE_CHAPTER):
        print("wrong function, use update_royalroad")
        return None

        series_id = gconfig.getStoryInfo(local_series_id)["general"]["royalroad"]["series_id"]

    host_url = "www.royalroad.com"
    new_chapter_url = f"https://www.royalroad.com/author-dashboard/chapters/new/{series_id}"

    # Start using mechanicalsoup
    browser = mechanicalsoup.StatefulBrowser()
    if browser_type == Browser.CHROME:
        cj = browser_cookie3.chrome(domain_name=host_url)
    elif browser_type == Browser.FIREFOX:
        cj = browser_cookie3.firefox(domain_name=host_url)
    elif browser_type == Browser.OPERA:
        cj = browser_cookie3.opera(domain_name=host_url)
    elif browser_type == Browser.EDGE:
        cj = browser_cookie3.edge(domain_name=host_url)
    elif browser_type == Browser.CHROMIUM:
        cj = browser_cookie3.chromium(domain_name=host_url)
    else:
        cj = browser_cookie3.load(domain_name=host_url)
    # print(cj)
    browser.set_cookiejar(cj)
    new_chapter_page = browser.open(new_chapter_url)

    __RequestVerificationToken = new_chapter_page.soup.find('input',{'name':'__RequestVerificationToken'})['value']

    # browser.launch_browser()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': host_url,
        'Connection': 'keep-alive',
        'Referer': new_chapter_url,
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'
        }
    
    royalroad_status = "New"

    if(action == Action.NEWDRAFT):
        royalroad_action = 'draft'
    elif(action == Action.NEWCHAPTER):
        royalroad_action = "publish"
    else:
        print("unsupported action")
        return None

    formdata = {
        'Status': royalroad_status,
        'fid': series_id,
        'Title': chapter_title,
        'PreAuthorNotes': '',
        'Content': chapter_content,
        'PostAuthorNotes': '',
        'AdjustedScheduledRelease': '',
        'ScheduledRelease': '',
        'PollQuestion': '',
        'PollPublic': 'true',
        'PollBelowChapter': 'false',
        'PollOptions[0].option': '',
        'PollOptions[0].votes': '0',
        'PollOptions[1].option': '',
        'PollOptions[1].votes': '0',
        'PollMultiple': '1',
        'DeleteDraft': 'true',
        'action': royalroad_action,
        '__RequestVerificationToken': __RequestVerificationToken,
        'PollPublic': 'false',
        'PollClosed': 'false'
    }
    r = requests.post(
        new_chapter_url,
        headers=headers,
        data=formdata,
        cookies=browser.get_cookiejar(),
    )

    if r.status_code == 200:
        print(f"Successfully posted new draft chapter. Response: {r.text}")
        print(repr(r.text))
        return True
    else:
        print(
            f"Failed to post new draft chapter.\nResponse text: {r.text}\nReason: {r.reason}\nRequest: {r.request.body}"
        )
        return None

def update_royalroad(
    chapter_title,
    chapter_content,
    local_series_id,
    edit_id,
    action=None,
    browser_type=Browser.NONE,
):
    """Updates a royalroad draft or chapter using mechanicalsoup to access a stateful browser.
    Returns True if successful, None if unsuccessful."""
    if (action == Action.NEW_CHAPTER or action == Action.NEW_DRAFT):
        print("wrong function, use new_royalroad")
        return None

        series_id = gconfig.getStoryInfo(local_series_id)["general"]["royalroad"]["series_id"]

    host_url = "www.royalroad.com"
    new_chapter_url = f"https://www.royalroad.com/author-dashboard/chapters/new/{edit_id}"


    # Start using mechanicalsoup
    browser = mechanicalsoup.StatefulBrowser()
    if browser_type == Browser.CHROME:
        cj = browser_cookie3.chrome(domain_name=host_url)
    elif browser_type == Browser.FIREFOX:
        cj = browser_cookie3.firefox(domain_name=host_url)
    elif browser_type == Browser.OPERA:
        cj = browser_cookie3.opera(domain_name=host_url)
    elif browser_type == Browser.EDGE:
        cj = browser_cookie3.edge(domain_name=host_url)
    elif browser_type == Browser.CHROMIUM:
        cj = browser_cookie3.chromium(domain_name=host_url)
    else:
        cj = browser_cookie3.load(domain_name=host_url)
    # print(cj)
    browser.set_cookiejar(cj)
    new_chapter_page = browser.open(new_chapter_url)

    __RequestVerificationToken = new_chapter_page.soup.find('input',{'name':'__RequestVerificationToken'})['value']

    # browser.launch_browser()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': host_url,
        'Connection': 'keep-alive',
        'Referer': new_chapter_url,
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'
        }
    
    royalroad_status = "Published"

    if(action == Action.UPDATEDRAFT):
        royalroad_action = 'draft'
    elif(action == Action.UPDATECHAPTER):
        royalroad_action = "publish"
    else:
        print("unsupported action")
        return None

    formdata = {
        'Id': edit_id,
        'Status': royalroad_status,
        'fid': series_id,
        'Title': chapter_title,
        'PreAuthorNotes': '',
        'Content': chapter_content,
        'PostAuthorNotes': '',
        'AdjustedScheduledRelease': '',
        'ScheduledRelease': '',
        'PollQuestion': '',
        'PollPublic': 'true',
        'PollBelowChapter': 'false',
        'PollOptions[0].option': '',
        'PollOptions[0].votes': '0',
        'PollOptions[1].option': '',
        'PollOptions[1].votes': '0',
        'PollMultiple': '1',
        'DeleteDraft': 'true',
        'action': royalroad_action,
        '__RequestVerificationToken': __RequestVerificationToken,
        'PollPublic': 'false',
        'PollClosed': 'false'
    }
    
    r = requests.post(
        new_chapter_url,
        headers=headers,
        data=formdata,
        cookies=browser.get_cookiejar(),
    )

    if r.status_code == 200:
        print(f"Successfully updated new draft or chapter. Chapter postid: {r.text}")
        print(repr(r.text))
        return True
    else:
        print(
            f"Failed to post new draft chapter.\nResponse text: {r.text}\nReason: {r.reason}\nRequest: {r.request.body}"
        )
        return None