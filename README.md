# bupa_mvs_bot
Bupa MVS auto slot check in Australia

## IMPORTANT
- Im'm not responsible for any relevant penalty applied while you're using this script. Education purpose only :).
- Do not run the script frequently otherwise your IP maybe goes into Bupa's blacklist.
- The default param is for 2 people with 501/502 category check. Please reach out if you want to custom this.

## Usage

### Install required library
```
requests
BeautifulSoup
telegram_send (If you want to notify via Telegram)
```

### Run
```bash
python3 book.py
```

### Demo log
```
######
2000
{166: {'location': 'SYDNEY-Bondi', 'slots': ['[2022-May-10] - Slot > 10:00']}, 60: {'location': 'SYDNEY-Paramatta', 'slots': ['[2022-June-02] - Slot > 8:00 | 8:15 | 12:15 | 12:30 | 12:45 | 13:00 | 13:15 | 13:30']}}
######
3000
{129: {'location': 'MELBOURNE-Forrest Hill', 'slots': ['[2022-April-12] - Slot > 13:00 | 13:15 | 13:30 | 14:15 | 14:30 | 14:45 | 15:00']}}
######
4000
{61: {'location': 'BRISBANE CENTRE', 'slots': ['[2022-January-31] - Slot > 13:30 | 14:30 | 14:45']}}
######
6000
{63: {'location': 'PERTH CENTRE', 'slots': ['[2022-January-21] - Slot > 15:15']}}
```
