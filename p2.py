import collections
import csv
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

file_ansewrs = "C:/Users/хихи/text7.csv"
cookie_token = "PHPSESSID="
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

def start_test(test_number: int) -> None:
    requests.post(
        'http://83.219.130.176/modules/testing/start.php',
        headers=headers,
        data='test_id=1174'
    )

    time.sleep(5)

    requests.post(
        'http://83.219.130.176/modules/testing/testing.php',
        headers=headers,
        data='user_action=finish_testing'
    )
    
    
    print(f'Вызван тест №{test_number}')
    

def write_questions_to_csv(questions_and_answers, filename: str) -> None:
    field_names = ["Task", "Answers"]

    existing_data = {}
    if Path(filename).exists():
        with open(filename, "r") as csvfile:
            reader = csv.DictReader(csvfile, delimiter="\t", lineterminator="\n")
            for row in reader:
                existing_data[row["Task"]] = row["Answers"]

    for question, answer in questions_and_answers.items():
        if question not in existing_data:
            existing_data[question] = answer

    with open(filename, "w") as csvfile:
        writer = csv.DictWriter(csvfile, delimiter="\t", lineterminator="\n", fieldnames=field_names)
        writer.writeheader()

        od = collections.OrderedDict(
            (k, {"Task": k, "Answers": v}) for k, v in sorted(existing_data.items())
        )
        writer.writerows(od.values())



def get_questions_ids() -> list:
    r = requests.post(
        'http://83.219.130.176/modules/testing/testing.php',
        headers=headers,
        data="user_action=show_protocol"
    )

    soup = BeautifulSoup(r.text, "html.parser")
    questionDivs = soup.findAll('div', class_='questions_list_item')

    return [v['value'] for v in questionDivs]


def get_answer_for_radiobutton_and_checkboxes(soup: BeautifulSoup) -> list:
    answers = []
    tr = soup.findAll("tr")

    if tr:
        for v in tr:
            if v.find('input', checked=True) or v.find('input', checked=True, type='radio'):
                answers.append(v.findAll('td')[1].text)
    
    return answers

def get_table_answers(soup: BeautifulSoup) -> list:
    answers = []
    table_tags = soup.findAll("table")

    if len(table_tags) == 2:
        table_tags = table_tags[1]
        table = dict()

        table_questions = table_tags.findAll('td', class_="left_column")
        table_answers = table_tags.findAll('td', class_="right_column")
        for q, a in zip(table_questions, table_answers):
            table[q.text] = a.text.replace('\n', '')[:-1]

        answers.append(table)

    return answers

def get_input_answer(soup: BeautifulSoup):
    return [soup.findAll('input')[1]['value']]


def main():
    for i in range(1, 20):
        questions = dict()
        start_test(i)

        for questionID in get_questions_ids():  
            r = requests.post(
                'http://83.219.130.176/modules/results/question.php',
                    data="object_id="+ str(questionID),
                    headers=headers
            )
            soup = BeautifulSoup(r.text, "html.parser")
            task_question = soup.find("div", class_="question_sub_panel ui-corner-all").find("span").text

            questions[task_question] = get_answer_for_radiobutton_and_checkboxes(soup) or get_table_answers(soup) or get_input_answer(soup)

        write_questions_to_csv(questions, file_ansewrs)

if __name__ == '__main__':
    main()
