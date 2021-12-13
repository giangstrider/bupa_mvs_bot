from re import M
import requests
from bs4 import BeautifulSoup
import datetime
import telegram_send


########################################## HELPER ############################################################

headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36',
        'sec-ch-ua':  '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"'
    }



def re_get_atts(r_content, target_dict):
    soup = BeautifulSoup(r_content, 'html.parser')
    atts = ['__EVENTARGUMENT', '__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION']
    atts_value = {}

    for att in atts:
        e = soup.find(id=att).get('value')
        atts_value[att] = e
    # atts_value['__EVENTTARGET'] = target_value
    atts_value = {**atts_value, **target_dict}
    return atts_value


def get_call_url(r_session, input_url,  data=None, cookies_url=None):
    if cookies_url:
        resp = r_session.get(input_url, headers=headers, cookies=cookies_url, data=data)
    else:
        resp = r_session.get(input_url, headers=headers)
    
    return resp


def post_call_url(r_session, input_url, data, cookies_url=None):
    resp = r_session.post(input_url, headers=headers, data=data, cookies=cookies_url)
    return resp


def process_stage(r_session, input_url, stage_payload):
    soup_get = get_call_url(r_session, input_url)
    atts = re_get_atts(soup_get.text, stage_payload)
    soup_post = post_call_url(r_session, input_url, atts, dict(soup_get.cookies))
    return soup_post


def process_stage(r_session, input_url, stage_payload):
    soup_get = get_call_url(r_session, input_url)
    atts = re_get_atts(soup_get.text, stage_payload)
    soup_post = post_call_url(r_session, input_url, atts, dict(soup_get.cookies))
    return soup_post


def process_stage_direct(r_session, input_url, payload, support_soup):
    atts = re_get_atts(support_soup.text, payload)
    soup_post = post_call_url(r_session, input_url, atts, dict(support_soup.cookies))
    return soup_post


def conversion(minutes):
    sec_value = int(minutes) * 60 % (24 * 3600)
    hour_value = sec_value // 3600
    sec_value %= 3600
    min = sec_value // 60
    sec_value %= 60
    if min == 0:
        min_s = '00'
    else:
        min_s = min
    return '{}:{}'.format(hour_value, min_s)


def send_telegram(data_dict):
    messages = []
    for location_id, value in data_dict.items():
        message = 'Location: {}\n'.format(value['location'])
        for slot in value['slots']:
            message += 'Date {}\n\n'.format(slot)
        telegram_send.send(messages=[message], conf='/Users/hoanggiangtrinh/giang/bupa-mvs-booking/channel1.conf')
    # print(messages)
    # import telegram_send
    # telegram_send.send(messages=messages, conf='/Users/hoanggiangtrinh/giang/bupa-mvs-booking/channel1.conf')


#################################### POSTODE HELPER
mapping = {
    168: 'SYDNEY CENTRE',
    166: 'SYDNEY-Bondi',
    60: 'SYDNEY-Paramatta',
    170: 'SYDNEY-Bankstown',
    141: 'SYDNEY-Tamworth',
    135: 'MELBOURNE CENTRE',
    84: 'MELBOURNE-Greenborough',
    138: 'MELBOURNE-Preston',
    129: 'MELBOURNE-Forrest Hill',
    162: 'MELBOURNE-Ringwood',
    132: 'CANBERRA-Belconnen',
    61: 'BRISBANE CENTRE',
    142: 'BRISBANE-Robina',
    63: 'PERTH CENTRE',
    154: 'PERTH-Bunbury',
    62: 'ADELAIDE CENTRE',
    133: 'ADELAIDE Royal Park'
}

def process_postcode(r_session, postcode_data, appointment_soup):
    get_postcode_payload = {
        'ctl00$ContentPlaceHolder1$SelectLocation1$txtSuburb': postcode_data['postcode'],
        'ctl00$ContentPlaceHolder1$SelectLocation1$btnSearch': 'search',
        'ctl00$ContentPlaceHolder1$SelectLocation1$hdnSearchCoord': postcode_data['latitude']
    }
    url = 'https://bmvs.onlineappointmentscheduling.net.au/oasis/Location.aspx'
    get_postcode_soup = process_stage_direct(r_session, url, get_postcode_payload, appointment_soup)

    get_postcode_soup_parser = BeautifulSoup(get_postcode_soup.text, 'html.parser')

    data_dict = {}
    for location_id in postcode_data['location_ids']:
        extracted_latitude_according = str(get_postcode_soup_parser.find(id='{}hidCoords'.format(location_id)).get('value'))
        location_status = process_location(r_session, postcode_data['postcode'], location_id, extracted_latitude_according, get_postcode_soup)
        if location_status:
            data_dict[location_id] = {'location': mapping[location_id], 'slots': location_status, }

    return data_dict
        

def process_location(r_session, postcode_number, location_id, extracted_latitude_according, get_postcode_soup):
    location_payload = {
        '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$btnCont',
        'ctl00$ContentPlaceHolder1$SelectLocation1$txtSuburb': postcode_number,
        'rbLocation': location_id,
        'ctl00$ContentPlaceHolder1$SelectLocation1$hdnSearchCoord': extracted_latitude_according,
        'ctl00$ContentPlaceHolder1$hdnLocationID': location_id,
        'ctl00$ContentPlaceHolder1$SelectLocation1$ddlState': None
    }
    url = 'https://bmvs.onlineappointmentscheduling.net.au/oasis/Location.aspx'
    location_soup = process_stage_direct(r_session, url, location_payload, get_postcode_soup)
    product_status_info = process_product(r_session, location_soup)
    return product_status_info



def process_product(r_session, location_soup):
    url = 'https://bmvs.onlineappointmentscheduling.net.au/oasis/Products.aspx'
    product_payload = {
        '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$btnCont',
        'TestProduct1': 489,
        'TestProduct1': 492,
        'TestProduct2': 489,
        'TestProduct2': 492,
        'ctl00$ContentPlaceHolder1$hdnSelectedProducts': '1=489,492,|2=489,492,|',
        'ctl00$ContentPlaceHolder1$hdnMMPDscr1': None,
        'ctl00$ContentPlaceHolder1$hdnMMPDscr2': None,
        'ctl00$ContentPlaceHolder1$hdnMMPDscr3': None,
        'ctl00$ContentPlaceHolder1$hdnMMPPrice1': None,
        'ctl00$ContentPlaceHolder1$hdnMMPPrice2': None,
        'ctl00$ContentPlaceHolder1$hdnMMPPrice3': None,
    }
    product_soup = process_stage_direct(r_session, url, product_payload, location_soup)

    import re
    matches = re.findall(r'gAvailSlotText\[.+?appointments available\';',product_soup.text)
    date_slot_statuses = []
    for i in matches:
        splittext = i.split(')] = \'')
        split_date = splittext[0].split('(')[1].split(',')
        year = int(split_date[0])
        month = int(split_date[1]) + 1
        day = int(split_date[2])

        date_obj = datetime.date(year, month, day)
        date_slot_status = process_slot(r_session, date_obj, product_soup)
        if date_slot_status:
            date_slot_statuses.append(date_slot_status)
        # return

        if date_slot_statuses:
            return date_slot_statuses
        else:
            return None


def process_slot(r_session, date_obj, product_soup):
    url = 'https://bmvs.onlineappointmentscheduling.net.au/oasis/AppointmentTime.aspx'
    slot_payload = {
        '_EVENTTARGET': 'ctl00_ContentPlaceHolder1_SelectTime1_btnAppSearch',
        '__EVENTARGUMENT': 'click',
        'ctl00$ContentPlaceHolder1$SelectTime1$txtAppDate': date_obj.strftime('%-d/%m/%Y'),
        'ctl00$ContentPlaceHolder1$hdnSelectedDateDisplay': date_obj.strftime('%A, %-d %B %Y'),
        'ctl00$ContentPlaceHolder1$hdnSelectedDate': date_obj.strftime('%Y-%m-%d'),
        'ctl00$ContentPlaceHolder1$hdnSelectedTime': '480'
    }

    slot_soup = process_stage_direct(r_session, url, slot_payload, product_soup)
    available_slots = process_slot_status(slot_soup)
    if available_slots:
        message = '[{}] - Slot > {}'.format(date_obj.strftime('%Y-%B-%d'), available_slots)
        # print(message)
        return message
    else:
        None

def process_slot_status(slot_soup):
    if 'No available times on this date' not in slot_soup.text:
        soup = BeautifulSoup(slot_soup.text, 'html.parser')
        #time = soup.find(id='ContentPlaceHolder1_SelectTime1_rblResults_0').get('value')
        rs = soup.findAll('input', id=lambda x: x and x.startswith('ContentPlaceHolder1_SelectTime1_rblResults_'))
        e = [conversion(r.get('value')) for r in rs]
        return " | ".join(e)
    else:
        None

##############

############## MAIN PROCESS START HERE
postcode_list = [
    {
        'postcode': 2000,
        'latitude': '-33.86051951,151.2015802',
        'location_ids': [168, 166, 60, 170, 141]
    },
    {
        'postcode': 3000,
        'latitude': '-37.8133386,144.9722006',
        'location_ids': [135, 84, 138, 129, 162]
    },
    {
        'postcode': 4000,
        'latitude': '-27.466785,153.027153',
        'location_ids': [61, 142]
    },
    {
        'postcode': 6000,
        'latitude': '-31.9534613,115.8536536',
        'location_ids': [63, 154]
    },
    {
        'postcode': 5000,
        'latitude': '-34.92849902,138.600746',
        'location_ids': [62, 133]
    },
    {
        'postcode': 2600,
        'latitude': '-35.30731337,149.1404425',
        'location_ids': [132]
    },
]


########################################## START ############################################################
session = requests.Session()

######################################## DEFAULT.ASPX
url = 'https://bmvs.onlineappointmentscheduling.net.au/oasis/Default.aspx'
default_payload = {'__EVENTTARGET': 'ctl00$ContentPlaceHolder1$btnFam'}
default_soup = process_stage(session, url, default_payload)


######################################## AppointmentType.ASPX
url = 'https://bmvs.onlineappointmentscheduling.net.au/oasis/AppointmentType.aspx'
appointment_payload = {'__EVENTTARGET': 'ctl00$ContentPlaceHolder1$btnCont'}
appointment_soup = process_stage(session, url, appointment_payload)


######################################## POSTCODE stage


for postcode_data in postcode_list:
    info = process_postcode(session, postcode_data, appointment_soup)
    print("######")
    print(postcode_data['postcode'])
    # send_telegram(info)
