import BestChange

import requests

from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs

ua = UserAgent()

headers = {
    'User-Agent': ua.random,
}
def collect_data():
    response = requests.get('https://www.bestchange.ru/', headers=headers)
    result = []
    soup = bs(response.content, 'lxml')

    for i in soup.select('#currency_lc > optgroup > option'):
        result.append(i.get_attribute_list('value'))
    result = [int(i[0]) for i in result]
    print(result)
    return result


def main():
    api = BestChange.BestChange()
    exchangers = api.exchangers().get()
    dir_from = 36
    dir_to = 203
    from_to = f'{api.currencies().get_by_id(dir_from)} -> {api.currencies().get_by_id(dir_to)}'
    rows = api.rates().filter(dir_from, dir_to)
    print(f'BestChange: {from_to}')
    print(f'Ссылка на BestChange: \nhttps://www.bestchange.ru/index.php?from={dir_from}&to={dir_to}')
    # print(f'https://www.bestchange.ru/click.php?id={api.currencies()[2]}&from={dir_from}&to={dir_to}&city=0{0}')
    # for val in rows[:2]:
    #     print('{} {}'.format(exchangers[val['exchange_id']]['name'], val))



if __name__ == '__main__':
    main()
    collect_data()