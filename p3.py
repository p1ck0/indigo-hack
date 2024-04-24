import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
import urllib.parse
import json

cookie_token = "PHPSESSID=3dc283f8a0ef662af6d4bd5fb0d46b1d"
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': '*/*',
    'Accept-Language': 'ru',
    'Accept-Encoding': 'gzip, deflate',
    'Host': '83.219.130.176',
    'Origin': 'http://83.219.130.176',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
    'Connection': 'keep-alive',
    'Referer': 'http://83.219.130.176/',
    'Content-Length': '17',
    'X-Requested-With': 'XMLHttpRequest',
    "Cookie":cookie_token
}

field_names = ["Task", "Answers"]
filename = "C:/Users/хихи/text7.csv"


existing_data = {}
if Path(filename).exists():
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t", lineterminator="\n")
        for row in reader:
            existing_data[row["Task"]] = row["Answers"]



user_action = 'start'

for i in range(22):
    q = requests.post(
    "http://83.219.130.176/modules/testing/testing.php",
        headers=headers,
        data=f"user_action={user_action}"
)
    soup = BeautifulSoup(q.text, 'html.parser')
    question_text = soup.findAll('span')[1].text

    answers_from_file = existing_data.get(question_text)
    tr_answers = soup.findAll('tr')

    answers_and_ids = []
    is_table = False
    for tr in tr_answers:
        if tr.get('valign'):
            break
        input = tr.find('input')
        if input:
            answers_and_ids.append((input['res_answer_id'], tr.find('label').text))
        else:
            is_table = True
            left_col = tr.find('td', class_='left_column').text
            right_col = tr.find('td', class_='right_column')
            fixed_row_id = right_col.find('select')['id']
            answer_values = right_col.findAll('option')
            for v in answer_values:
                if left_col in answers_from_file:
                    answer = json.loads(answers_from_file.replace("'",'"'))
                    if answer[0][left_col] == v.text:
                        requests.post(
                            "http://83.219.130.176/modules/testing/submit.php",
                            headers=headers,
                            data=f'position={i}&fixed_row_id={fixed_row_id}&answer_value={v["value"]}'
                        )
                        break


    if answers_and_ids and not is_table:
        for idx, answer_text in answers_and_ids:
            if answer_text in answers_from_file:
                send_answer_request = requests.post(
                    "http://83.219.130.176/modules/testing/submit.php",
                    headers=headers,
                    data=f"position={i}&res_answer_id={idx}&answer_value=1"
                )
    elif not is_table:
        safe_string = urllib.parse.quote_plus(answers_from_file[2:-2])
        requests.post(
                    "http://83.219.130.176/modules/testing/submit.php",
                    headers=headers,
                    data=f"position={i}&answer_value={safe_string}"
                )
    
    user_action = 'next'
    
print(answers_and_ids)
