# Notion ics sync
Python script for synchronising and filtering events from my cursus ics to a Notion database using Notion API.
## Requirements
Install python requirements
```shell
pip install -r requirements.txt
```
Create a `.env` file and add these three variables:
```shell
NOTION_TOKEN=<Your notion token>
DATABASE_ID=<Your database id>
URL_ICS=<Your ics URL>
```