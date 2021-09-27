import os
import json
import requests
from dotenv import load_dotenv
from ics import Calendar
from Notion import NotionEvent, get_id, notion_to_dict, convert_to_RFC_datetime
from pprint import pprint as pp

if not load_dotenv():
    print('can\'t find .env file')
    exit(1)

DATABASE_ID = os.environ['DATABASE_ID']
NOTION_TOKEN = os.environ['NOTION_TOKEN']
HEADERS = {
    'Notion-Version': '2021-08-16',
    'Authorization': f"Bearer {NOTION_TOKEN}",
    'Content-Type': 'application/json'
}
Q1 = [*[f'S-INFO-0{x}' for x in [21, 26, 28, 23]], 'I-ILIA-208']
Q2 = [*[f'S-INFO-{x}' for x in ['044', '027', '810', '075', ]], 'I-ILIA-011']
CURSUS = [*Q1, *Q2]
URL_ICS = os.environ['URL_ICS']


def get_filtered_calendar(url, filter):
    raw_ics = requests.get(url).text
    c = Calendar(raw_ics)
    filtered_calendar = Calendar()
    for event in c.timeline:
        id = event.name.split(' - ')[0]
        if id in filter:
            filtered_calendar.events.add(event)
    return filtered_calendar


def get_notion_calendar():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    has_more = True
    cal = []
    next_token = None
    while has_more:
        payload = json.dumps({
            "start_cursor": f"{next_token}"
        }) if next_token else ""
        response = requests.request('POST', url, headers=HEADERS, data=payload)
        dico = response.json()
        cal += dico['results']
        has_more = dico['has_more']
        next_token = dico['next_cursor']
    return cal


def need_update(ics_event, notion_event):
    notion_dict = notion_to_dict(notion_event)
    if get_id(ics_event.uid) == notion_dict["id"]:
        return (ics_event.name != notion_dict["Name"]
        or convert_to_RFC_datetime(ics_event.begin) != notion_dict["begin"].replace('.000', '')
        or convert_to_RFC_datetime(ics_event.end) != notion_dict["end"].replace('.000', '')
        or ics_event.location != notion_dict["Location"]
        or ics_event.description != notion_dict["Description"])
    return False


def add_event(event):
    url = "https://api.notion.com/v1/pages"
    notion_event = NotionEvent(event)
    payload = json.dumps({
        "parent": {
            "database_id": DATABASE_ID
        },
        "properties": notion_event.to_query()
    })

    response = requests.request('POST', url, headers=HEADERS, data=payload)

    if response.status_code != 200:
        pp(response.json())
    else:
        print(f"{event.name} has been added")


def update_event(event_id, ics_event):
    url = f"https://api.notion.com/v1/pages/{event_id}"
    notion_event = NotionEvent(ics_event)
    payload = json.dumps({
        "properties": notion_event.to_query()
    })

    response = requests.request('PATCH', url, headers=HEADERS, data=payload)

    if response.status_code != 200:
        pp(response.json())
    else:
        print(f"{ics_event.name} has been updated")


def delete_event(event_id):
    url = f"https://api.notion.com/v1/blocks/{event_id}"
    response = requests.request('DELETE', url, headers=HEADERS)
    if response.status_code != 200:
        pp(response.json())
    else:
        print(f"{response.json()['child_page']['title']} has been deleted")


def add_new_events(ics_calendar, notion_calendar):
    events_id = set()
    for event in notion_calendar:
        if len(event['properties']["id"]["rich_text"]) > 0:
            events_id.add(event['properties']["id"]
                          ["rich_text"][0]["text"]["content"])
    for event in ics_calendar.timeline:
        if get_id(event.uid) not in events_id:
            add_event(event)


def update_existing_events(ics_calendar):
    mapping = {}
    notion_calendar = get_notion_calendar()
    for event in notion_calendar:
        mapping[event['properties']["id"]
                ["rich_text"][0]["text"]["content"]] = event
    for event in ics_calendar.timeline:
        if need_update(event, mapping[get_id(event.uid)]):
            update_event(mapping[get_id(event.uid)]["id"], event)


def delete_old_events(ics_calendar, notion_calendar):
    events_id = set()
    for event in ics_calendar.timeline:
        events_id.add(get_id(event.uid))
    for event in notion_calendar:
        if len(event['properties']["id"]["rich_text"]) == 0:
            delete_event(event['id'])
        elif event['properties']["id"]["rich_text"][0]["text"]["content"] not in events_id:
            delete_event(event['id'])


def delete_all_events():
    notion_calendar = get_notion_calendar()
    for event in notion_calendar:
        delete_event(event['id'])


def main():
    ics_cal = get_filtered_calendar(URL_ICS, CURSUS)
    notion_calendar = get_notion_calendar()
    add_new_events(ics_cal, notion_calendar)
    delete_old_events(ics_cal, notion_calendar)
    update_existing_events(ics_cal)


if __name__ == '__main__':
    main()
