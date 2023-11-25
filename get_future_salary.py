import os
from dotenv import load_dotenv
from predict_salery_funcs import predict_rub_salary_superjob, add_response_to_list, predict_rub_salary_hh
from terminaltables import AsciiTable
import requests

PROG_LANGS = ['Python', 'Javascript', 'PHP', 'Go', 'C++']


def get_vacancies_hh():
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for lang in PROG_LANGS:
        url = 'https://api.hh.ru/vacancies'
        final_dict = {}
        number_of_days = 30
        page = 0
        pages_number = 1
        pages_data = []
        city = 1
        searching_text = f'Программист {lang}'
        while page < pages_number:
            payload = {'text': searching_text,
                       'area': city,
                       'page': page,
                       'period': number_of_days}
            page_response = requests.get(url, params=payload)
            page_response.raise_for_status()
            page_data = page_response.json()
            pages_data.append(page_data)
            pages_number = page_data['pages']
            page += 1

        vacancies_processed = 0
        empty_list = []

        for page in pages_data:
            vacancies = page['items']
            for vacancy in vacancies:
                if predict_rub_salary_hh(vacancy):
                    vacancies_processed += 1
                    empty_list.append(predict_rub_salary_hh(vacancy))

        vacancies_found = page['found']
        try:
            average_salary = sum(empty_list) / len(empty_list)
        except ZeroDivisionError:
            print(f'No vacancies for {lang}')
            continue
        final_dict[lang] = {'vacancies_processed': vacancies_processed,
                            'vacancies_found': vacancies_found,
                            'average_salary': int(average_salary)}
        table_data.append([
            f'Программист {lang}',
            vacancies_found,
            vacancies_processed,
            int(average_salary),
        ])

    return table_data


def get_vacancies_ss(url, headers):
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for lang in PROG_LANGS:
        keyword = f'Программист {lang}'
        city_id = 4
        catalogue_id = 48
        period = 0
        page = 0
        pages_number = 1
        pages_data = []
        final_dict = {}
        while page < pages_number:
            params = {'keyword': keyword,
                      'town': city_id,
                      'catalogues': catalogue_id,
                      'page': page,
                      'period': period}

            add_response_to_list(url, params, pages_data, headers)
            pages = [p['total'] for p in pages_data]
            pages_number = pages[0] // 20
            page += 1

        vacancies_found = [p['total'] for p in pages_data][0]
        vacancies_processed = 0
        empty_list = []
        for page in pages_data:
            vacancies = page['objects']
            for vacancy in vacancies:
                if predict_rub_salary_superjob(vacancy):
                    empty_list.append(predict_rub_salary_superjob(vacancy))
                    vacancies_processed += 1
        try:
            average_salary = sum(empty_list) / len(empty_list)
        except ZeroDivisionError:
            print(f'No vacancies for {lang}')
            continue
        final_dict[f'Программист {lang}'] = {'vacancies_processed': vacancies_processed,
                                             'vacancies_found': vacancies_found,
                                             'average_salary': int(average_salary)}
        table_data.append([
            f'Программист {lang}',
            vacancies_found,
            vacancies_processed,
            int(average_salary),
        ])
    return table_data


if __name__ == '__main__':
    load_dotenv()
    url_ss = 'https://api.superjob.ru/2.0/vacancies/'
    headers_ss = {'X-Api-App-Id': os.environ['SECRET_KEY']}
    table_data_ss = get_vacancies_ss(url_ss, headers_ss)
    table_ss = AsciiTable(table_data_ss)
    table_ss.title = 'SuperJob Moscow'
    table_ss.justify_columns[3] = 'right'

    table_data_hh = get_vacancies_hh()
    table_hh = AsciiTable(table_data_hh)
    table_hh.title = 'HeadHunter Moscow'
    table_hh.justify_columns[3] = 'right'
    print(table_ss.table)
    print(table_hh.table)
