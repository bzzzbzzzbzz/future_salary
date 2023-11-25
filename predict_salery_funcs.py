import requests


def predict_salary(from_salary, to_salary):
    if not to_salary:
        return from_salary * 1.2
    elif not from_salary:
        return to_salary * 0.8
    else:
        return (from_salary + to_salary) / 2


def predict_rub_salary_hh(vacansy):
    salary = vacansy['salary']
    if not salary:
        return None
    currency = salary['currency']
    if currency != 'RUR':
        return None
    from_salary = salary['from']
    to_salary = salary['to']
    return predict_salary(from_salary, to_salary)


def predict_rub_salary_superjob(vacancy):
    from_salary = vacancy['payment_from']
    to_salary = vacancy['payment_to']
    if from_salary or to_salary:
        currency = vacancy['currency']
        if currency != 'rub':
            return None
        return predict_salary(from_salary, to_salary)
    return None


def add_response_to_list(url, payload, list_nums, headers=None):
    response = requests.get(url, params=payload, headers=headers)
    response.raise_for_status()
    page_data = response.json()
    list_nums.append(page_data)
