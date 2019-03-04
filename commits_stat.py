"""
Get insights data from github.com, count commits, parse and write data into CSV file
"""
import json
import datetime
import calendar
import tempfile
import os
import random
import requests

from matplotlib import pyplot as plt
from matplotlib import style

GITHUB_URL = "https://api.github.com/orgs/dcodeteam/repos"
GITHUB_TOKEN = "token 70d832c6ebac06bb933819c68fc0b2f670e994b7"

now_date = str(datetime.datetime.now())[:10]


def date_check(current_date, start_date, end_date):
    """
    Check if date is in this date interval
    """
    current_date = datetime.datetime.strptime(current_date, "%Y-%m-%d")

    return start_date <= current_date <= end_date


def get_github_data(start, end):
    """
    Get data about about commits over from all repositories and check the date
    """
    # Get all repositories
    user_and_date = []
    try:
        response = requests.get(
            url=GITHUB_URL,
            headers={
                "Authorization": GITHUB_TOKEN,
            },
        )
    except requests.exceptions.ConnectionError:
        print("No internet connection")
    else:
        json_data = json.loads(response.text)

        for raw in json_data:
            try:
                response = requests.get(
                    url=raw['commits_url'].replace('{/sha}', ''),
                    headers={
                        "Authorization": GITHUB_TOKEN,
                    },
                )
            except requests.exceptions.ConnectionError:
                print("No internet connection")
            else:
                data = json.loads(response.content)

                for item in data:
                    if isinstance(item, dict):
                        author_name = item['commit']['author']['name']
                        commit_date = item['commit']['author']['date'][:10]

                        if date_check(commit_date, start, end):
                            user_and_date.append((commit_date, author_name))
                    else:
                        continue

    return user_and_date


def parse_and_draw(start_date, end_date=now_date):
    """
    Parsing data and add it to CSV file
    Draw graph from csv by matplotlib
    """
    rand_num = random.randint(1, 999)

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    actual_date = start_date - datetime.timedelta(days=1)
    date_sequence = []

    __, tmp_name = tempfile.mkstemp(suffix='.csv', prefix='tmp', dir=None, text=False)

    tmp_file = open(tmp_name, 'r+')

    while end_date != actual_date:
        actual_date = actual_date + datetime.timedelta(days=1)

        current_date = actual_date.strftime('%Y-%m-%d')

        date_sequence.append(current_date)
    user_and_date = get_github_data(start_date, end_date)

    name_sequence = set()

    result = {}

    for (date_commit, name_commit) in user_and_date:
        name_sequence.add(name_commit)

        if date_commit not in result:
            result[date_commit] = {}

        if name_commit not in result[date_commit]:
            result[date_commit][name_commit] = 0

        result[date_commit][name_commit] += 1

    name_sequence = list(name_sequence)
    name_sequence.sort()

    for name_person in name_sequence:
        line_person = [name_person]
        for date_commit in date_sequence:
            commits_number = result.get(date_commit, {}).get(name_person, 0)
            datetime_object = datetime.datetime.strptime(date_commit, '%Y-%m-%d')
            weekday = calendar.day_name[datetime_object.weekday()]
            line_person.append(date_commit + ' ' + weekday[:3])
            line_person.append(str(commits_number))
        tmp_file.write(','.join(line_person) + ',\n')
    tmp_file.close()

    # Drawing graph

    tmp_file = open(tmp_name, 'r+')

    style.use('ggplot')
    csv_data = tmp_file.readlines()
    for i in range(0, len(csv_data)):
        csv_split_data = csv_data[i].split(',')
        x = []
        y = []
        for j in range(1, len(csv_split_data) - 1, 2):
            x.append(csv_split_data[j])
            y.append(int(csv_split_data[j+1]))
        plt.plot(x, y, label=csv_split_data[0])
        plt.xticks(x, x, rotation='vertical')
    plt.xlabel('Date')
    plt.ylabel('Commits')
    plt.title('D:CODE GitHub commits')
    plt.legend()
    plt.gcf().set_size_inches(16, 9)
    plt.savefig('plot' + str(rand_num) + '.png', bbox_inches='tight', dpi=100)
    plt.gcf().clear()
    tmp_file.close()
    os.remove(tmp_name)

    return rand_num
