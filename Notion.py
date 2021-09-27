import datetime


class NotionEvent:
    def __init__(self, event):
        self.name = event.name
        self._cursus = get_cursus(event.name.split(' - ')[0])
        self._begin = convert_to_RFC_datetime(event.begin)
        self._end = convert_to_RFC_datetime(event.end)
        self.location = event.location
        self.description = event.description
        self._id = get_id(event.uid)

    @property
    def begin(self):
        return self._begin

    @begin.setter
    def begin(self, new_date):
        self._begin = convert_to_RFC_datetime(new_date)

    @property
    def cursus(self):
        return self._cursus

    @cursus.setter
    def cursus(self, new_cursus):
        self._cursus = get_cursus(new_cursus)

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, new_date):
        self._end = convert_to_RFC_datetime(new_date)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, new_id):
        self._id = get_id(new_id)

    def to_query(self):
        return {
            "Name": {
                "title": [{
                    "text": {"content": self.name}
                }]
            },
            "Cursus": {
                "select": {
                    "name": self.cursus
                }
            },
            "Date": {
                "date": {
                    "start": self.begin,
                    "end": self.end
                }
            },
            "Location": {
                "rich_text": [{
                    "text": {"content": self.location if self.location else ''}
                }]
            },
            "Description": {
                "rich_text": [{
                    "text": {"content": self.description if self.description else ''}
                }]
            },
            "id": {
                "rich_text": [{
                    "text": {"content": self.id}
                }]
            }
        }


def get_cursus(name):
    mapping = {
        "S-INFO-021": "graph",
        "S-INFO-026": "crypto",
        "S-INFO-028": "network",
        "S-INFO-023": "calc",
        "I-ILIA-208": "cloud",
        "S-INFO-044": "cybersec",
        "S-INFO-027": "krr",
        "S-INFO-810": "selected_ia",
        "S-INFO-075": "ml",
        "I-ILIA-011": "web",
    }
    return mapping[name]


def get_id(uid):
    return ''.join(uid.split('-')[1:3])


def convert_to_RFC_datetime(arr):
    dt = utc_to_local(datetime.datetime(arr.naive.year, arr.naive.month,
                      arr.naive.day, arr.naive.hour, arr.naive.minute, 0)).isoformat()
    return dt


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)


def notion_to_dict(notion_event):
    res = {}
    res["notion_id"] = notion_event["id"]
    props = notion_event["properties"]
    res["Name"] = props["Name"]["title"][0]["text"]["content"]
    res["Cursus"] = props["Cursus"]["select"]["name"]
    res["begin"] = props["Date"]["date"]["start"]
    res["end"] = props["Date"]["date"]["end"]
    res["Location"] = props["Location"]["rich_text"][0]["text"]["content"] if props["Location"]["rich_text"][0]["text"]["content"] else None
    res["Description"] = props["Description"]["rich_text"][0]["text"]["content"] if props["Description"]["rich_text"][0]["text"]["content"] else None
    res["id"] = props["id"]["rich_text"][0]["text"]["content"]
    return res
