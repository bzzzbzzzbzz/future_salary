import os
from dotenv import load_dotenv
from predict_salery_funcs import predict_rub_salary_superjob, predict_rub_salary_hh
from terminaltables import AsciiTable
import requests

PROG_LANGS = ['Python', 'Javascript', 'PHP', 'Go', 'C++']


def parse_vacancies_hh():
    vacancies_info = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for lang in PROG_LANGS:
        url = 'https://api.hh.ru/vacancies'
        number_of_days = 30
        page = 0
        pages_number = 1
        all_pages = []
        city = 1
        searching_text = f'Программист {lang}'
        while page < pages_number:
            payload = {'text': searching_text,
                       'area': city,
                       'page': page,
                       'period': number_of_days}
            page_response = requests.get(url, params=payload)
            page_response.raise_for_status()
            one_page = page_response.json()
            all_pages.append(one_page)
            pages_number = one_page['pages']
            page += 1

        all_salaries = []

        for page in all_pages:
            vacancies = page['items']
            for vacancy in vacancies:
                salary = predict_rub_salary_hh(vacancy)
                if salary:
                    all_salaries.append(salary)

        vacancies_found = page['found']
        try:
            average_salary = sum(all_salaries) / len(all_salaries)
        except ZeroDivisionError:
            average_salary = 0
        vacancies_processed = len(all_salaries)
        vacancies_info.append([
            f'Программист {lang}',
            vacancies_found,
            vacancies_processed,
            int(average_salary),
        ])

    return vacancies_info


def parse_vacancies_ss(url, headers):
    vacancies_info = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for lang in PROG_LANGS:
        keyword = f'Программист {lang}'
        city_id = 4
        catalogue_id = 48
        period = 0
        page = 0
        pages_number = 1
        all_pages = []
        while page < pages_number:
            payload = {'keyword': keyword,
                       'town': city_id,
                       'catalogues': catalogue_id,
                       'page': page,
                       'period': period}

            page_response = requests.get(url, params=payload, headers=headers)
            page_response.raise_for_status()
            one_page = page_response.json()
            all_pages.append(one_page)
            pages = one_page['total']
            pages_number = pages // 20
            page += 1

        vacancies_found = all_pages[0]['total']
        all_salaries = []
        for page in all_pages:
            vacancies = page['objects']
            for vacancy in vacancies:
                salary = predict_rub_salary_superjob(vacancy)
                if salary:
                    all_salaries.append(salary)

        try:
            average_salary = sum(all_salaries) / len(all_salaries)
        except ZeroDivisionError:
            average_salary = 0
        vacancies_processed = len(all_salaries)
        vacancies_info.append([
            f'Программист {lang}',
            vacancies_found,
            vacancies_processed,
            int(average_salary),
        ])
    return vacancies_info


if __name__ == '__main__':
    load_dotenv()
    url_ss = 'https://api.superjob.ru/2.0/vacancies/'
    headers_ss = {'X-Api-App-Id': os.environ['SS_SECRETKEY']}
    ss_vacancies = parse_vacancies_ss(url_ss, headers_ss)
    ss_table = AsciiTable(ss_vacancies)
    ss_table.title = 'SuperJob Moscow'
    ss_table.justify_columns[3] = 'right'

    hh_vacancies = parse_vacancies_hh()
    hh_table = AsciiTable(hh_vacancies)
    hh_table.title = 'HeadHunter Moscow'
    hh_table.justify_columns[3] = 'right'
    print(ss_table.table)
    print(hh_table.table)
