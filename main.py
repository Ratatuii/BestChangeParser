import BestChange
from datetime import datetime
import requests
import json
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs
import time
import asyncio
import aiofiles

start_time = time.time()
ua = UserAgent()

headers = {
    'User-Agent': ua.random,
}
result = []


async def collect_data():
    response = requests.get('https://www.bestchange.ru/', headers=headers)
    only_crypto = []
    soup = bs(response.content, 'lxml')

    for i in soup.select('#currency_lc > optgroup:nth-child(1) > option'):
        only_crypto.append(i.get_attribute_list('value'))
    only_crypto = [int(i[0]) for i in only_crypto]
    # print(only_crypto)
    return only_crypto


async def app(only_crypto):
    api = BestChange.BestChange()
    exchangers = api.exchangers().get()
    currencies = api.currencies()

    for dir_from in only_crypto:

        for dir_to in only_crypto:
            res = []
            # dir_from = 131
            # dir_to = 73
            if dir_from == dir_to:
                continue
            from_to = f'{api.currencies().get_by_id(dir_from)} -> {api.currencies().get_by_id(dir_to)}'
            rows = api.rates().filter(dir_from, dir_to)
            if not len(rows):
                continue
            print(f'BestChange: {from_to}')

            print(f'Ссылка на BestChange: \nhttps://www.bestchange.ru/index.php?from={dir_from}&to={dir_to}')
            link_bestchange_exchange = f'Ссылка на BestChange: \nhttps://www.bestchange.ru/index.php?from={dir_from}&to={dir_to}'
            print('<---------------------------------|--------------------------------->')
            # result.append({'link_bestchange_exchange': link_bestchange_exchange})

            for val in rows:

                print(f"Название обменника = {exchangers[val['exchange_id']]['name']}")
                name_exchange = f"Название обменника = {exchangers[val['exchange_id']]['name']}"
                print(
                    f"Доступная сумма обменника {currencies.get_by_id(dir_from)} -> {currencies.get_by_id(dir_to)} = {val['reserve']}")
                availible_sum = f"Доступная сумма обменника {currencies.get_by_id(dir_from)} -> {currencies.get_by_id(dir_to)} = {val['reserve']}"
                print(f"ID обменника (exchangers) = {exchangers[val['exchange_id']]['id']}")
                id_exchange = f"ID обменника (exchangers) = {exchangers[val['exchange_id']]['id']}"
                # print(f"ID обменника (rates)= {val['exchange_id']}")
                print(
                    f"Курс обмена {currencies.get_by_id(dir_from).split(' ')[-1]} -> {currencies.get_by_id(dir_to).split(' ')[-1]} = {val['rate']}")
                rate_exchange = f"Курс обмена {currencies.get_by_id(dir_from).split(' ')[-1]} -> {currencies.get_by_id(dir_to).split(' ')[-1]} = {val['rate']}"
                print(f"Отдаем {currencies.get_by_id(dir_from)} {val['give']}")
                give_coin = f"Отдаем {currencies.get_by_id(dir_from)} {val['give']}"
                print(f"Получаем {currencies.get_by_id(dir_to)} {val['get']}")
                get_coin = f"Получаем {currencies.get_by_id(dir_to)} {val['get']}"
                print(f"Кол-во отзывов = {val['reviews'].split('.')[-1]}")
                sum_reviews = f"Кол-во отзывов = {val['reviews'].split('.')[-1]}"
                print(f"Резерв {currencies.get_by_id(dir_to)} = {val['reserve']}")
                reserve_coin = f"Резерв {currencies.get_by_id(dir_to)} = {val['reserve']}"
                print(f"Минимальная сумма сделки = {val['min_sum']}")
                min_sum_coin = f"Минимальная сумма сделки = {val['min_sum']}"
                print(f"Максимальная сумма сделки = {val['max_sum']}")
                max_sum_coin = f"Максимальная сумма сделки = {val['max_sum']}"
                print(
                    f"Ссылка на обменник {exchangers[val['exchange_id']]['name']} \nhttps://www.bestchange.ru/click.php?id={val['exchange_id']}&from={dir_from}&to={dir_to}&city=0{0}")
                link_on_exchange = f"Ссылка на обменник {exchangers[val['exchange_id']]['name']} \nhttps://www.bestchange.ru/click.php?id={val['exchange_id']}&from={dir_from}&to={dir_to}&city=0{0}"

                res.append(
                    {
                        'name_exchange': name_exchange,
                        'availible_sum': availible_sum,
                        'id_exchange': id_exchange,
                        'rate_exchange': rate_exchange,
                        'give_coin': give_coin,
                        'get_coin': get_coin,
                        'sum_reviews': sum_reviews,
                        'reserve_coin': reserve_coin,
                        'min_sum_coin': min_sum_coin,
                        'max_sum_coin': max_sum_coin,
                        'link_on_exchange': link_on_exchange
                    }
                )
            result.append([link_bestchange_exchange, res])
        break
    async with open('result.json', 'w') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

async def main():
    await collect_data()

if __name__ == '__main__':
    asyncio.run(main())

print("--- %s seconds ---" % (time.time() - start_time))