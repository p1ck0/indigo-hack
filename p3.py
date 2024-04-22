import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path

cookie_token = "PHPSESSID=e43c4e5fcc5c3dc714a7c8f24e0ba871"
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
filename = 'text7.csv'


existing_data = {}
if Path(filename).exists():
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t", lineterminator="\n")
        for row in reader:
            existing_data[row["Task"]] = row["Answers"]



start = requests.post(
    "http://83.219.130.176/modules/testing/testing.php",
    headers=headers,
    data="user_action=start"
)

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

    try:
        answers_and_ids = [(tr.find('input')['res_answer_id'], tr.find('label').text) for tr in tr_answers]

        for idx, answer_text in answers_and_ids:
            if answer_text in answers_from_file:
                send_answer_request = requests.post(
                    "http://83.219.130.176/modules/testing/submit.php",
                    headers=headers,
                    data=f"position={i}&res_answer_id={idx}&answer_value=1"
                )
    except:
        requests.post(
                    "http://83.219.130.176/modules/testing/submit.php",
                    headers=headers,
                    data=f"position={i}&answer_value={answers_from_file[2:-2]}"
                )

    
    user_action = 'next'
    
print(answers_and_ids)
