import os

import BestChange
import requests
import json
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs
import time

ua = UserAgent()

result = dict()


def get_num_coin_bestchange():
    if not os.path.exists(f'num_coin_bestchange.json'):
        response = requests.get('https://www.bestchange.ru/', headers={'User-Agent': ua.random})
        only_crypto = []
        soup = bs(response.content, 'lxml')
        for i in soup.select('#currency_lc > optgroup:nth-child(1) > option'):
            only_crypto.append(i.get_attribute_list('value'))
        only_crypto = [int(i[0]) for i in only_crypto]

        with open('num_coin_bestchangejson', 'w', encoding='Windows-1251') as file:
            json.dump(only_crypto, file, indent=4, ensure_ascii=False)


def get_binance_api(api_methods):
    base_url = 'https://api.binance.com'
    url = base_url + api_methods
    response = requests.get(url, headers={'User-Agent': ua.random})
    if response.status_code == 429:
        time.sleep(2)
        print('WARNING: Нарушение кол-ва запросов в Binance')
    data = response.json()
    return data


def filter_coin(coin, coin_lists):
    return list(filter(lambda i: i['symbol'].endswith(coin), coin_lists))


def parse_coin_price_binance(symbol):
    res_binance_api = get_binance_api(f'/api/v3/depth?limit=5&symbol={symbol}')

    if len(res_binance_api['bids']) > 0:
        course_coin_buy = res_binance_api['bids'][-1][0]
        course_coin_sell = res_binance_api['asks'][-1][0]
        # with open('pairs_coin_binance.json', 'a', encoding='Windows-1251') as file:
        #     json.dump({symbol: {'buy': course_coin_buy, 'sell': course_coin_sell},}, file, indent=4, ensure_ascii=False)

        return {symbol: {'buy': course_coin_buy, 'sell': course_coin_sell}}


def app(start_capital=100, reviews=100, coin='USDT', data_coin=None):
    if data_coin is None:
        print('Нет данных')
        return 'Ошибка данных'
    api = BestChange.BestChange()
    exchangers = api.exchangers().get()
    currencies = api.currencies()
    try:
        with open('num_coin_bestchange.json') as file:
            num_coins = json.load(file)
    except:
        pass

    # Убираем дубликаты разных сетей
    num_coins_new = list(filter(lambda i: i not in [10, 163, 180, 208, 50, 110, 228, 235, 128, 131, 186, ], num_coins))

    # USDT: 36 ERC20, 10, 163, 180, 208, 50 | USDC: 23 ERC20, 110, 228, 235
    stable_coin = dict(USDT=36, BUSD=206, USDC=23)
    print('Ищем рабочие связки...')
    for dir_from in num_coins_new:
        res = dict()
        dir_to = stable_coin[coin]
        if dir_from == dir_to:
            continue
        rows = api.rates().filter(dir_from, dir_to)
        coin_from = currencies.get_by_id(dir_to).split(' ')[-1].replace('(', '').replace(')', '')
        coin_to = currencies.get_by_id(dir_from).split(' ')[-1].replace('(', '').replace(')', '')
        pairs = coin_from + coin_to
        if not len(rows) and pairs[:4] == coin:
            continue
        for val in rows:
            # {'give_id': 209, 'get_id': 36, 'exchange_id': 1013, 'rate': 0.563888575617458, 'reserve': 399832.83, 'reviews': '0.2528', 'min_sum': 546.0, 'max_sum': 10918.0, 'give': 1, 'get': 1.7734}
            id_exchange = exchangers[val['exchange_id']]['id']
            res[id_exchange] = {
                'name_exchange': exchangers[val['exchange_id']]['name'],
                'availible_sum': val['reserve'],
                'id_exchange': id_exchange,
                'give_coin': val['give'],
                'get_coin': val['get'],
                'sum_reviews': int(val['reviews'].split('.')[-1]),
                'reserve_coin': val['reserve'],
                'min_sum_coin': val['min_sum'],
                'max_sum_coin': val['max_sum'],
                'link_on_exchange': f"https://www.bestchange.ru/click.php?id={val['exchange_id']}&from={dir_from}&to={dir_to}&city=0{0}",
                'link_bestchange_exchange': f'https://www.bestchange.ru/index.php?from={dir_from}&to={dir_to}'
            }

        result[pairs] = res
        pairs_for_binance = coin_to + coin_from
        for i in data_coin:
            binance_url = f"https://www.binance.com/ru/trade/{i['symbol'][:-4]}_{i['symbol'][-4:]}?theme=dark&type=spot"
            if pairs_for_binance == i['symbol']:
                pairs_with_price_binance = parse_coin_price_binance(
                    i['symbol'])
                if pairs_with_price_binance is None:
                    continue
                course_binance = float(pairs_with_price_binance[pairs_for_binance]['sell'])
                buy_coin_binance = start_capital / course_binance

                for j in result[pairs]:
                    if result[pairs][j]['get_coin'] == 1:
                        course_bectchange = round(result[pairs][j]['give_coin'], 5)
                        sell_bestchange_coin = buy_coin_binance / course_bectchange
                    else:
                        course_bectchange = round(result[pairs][j]['get_coin'], 5)
                        sell_bestchange_coin = buy_coin_binance * course_bectchange

                    # print(f"Купили на binance {buy_coin_binance} монет по курсу {course_binance}")
                    # print(f"Продаем на BestChange {buy_coin_binance} монет по курсу {course_bectchange} получаем {sell_bestchange_coin} {i['symbol'][-4:]}")
                    if (result[pairs][j]['sum_reviews'] > reviews) and (
                            buy_coin_binance > result[pairs][j]['min_sum_coin']) and (buy_coin_binance < result[pairs][j]['max_sum_coin']):
                        if sell_bestchange_coin > start_capital: # Проверяем есть ли выручка
                            print(f"1. Binance: {i['symbol'][-4:]} -> {i['symbol'][:-4]}")
                            print(f'Ссылка на валютную пару:\n{binance_url}')
                            print(
                                f"Цена: {round(start_capital / float(pairs_with_price_binance[pairs_for_binance]['buy']) / start_capital, 5)}\n")

                            print(f"2. BestChange: {i['symbol'][:-4]} -> {i['symbol'][-4:]}")
                            print(f"Цена: {course_bectchange}")
                            print(f"Обменник:{result[pairs][j]['name_exchange']}")
                            print(f"Рейтинг обменника: {result[pairs][j]['sum_reviews']}")
                            print(f"Ссылка на Обменник: \n{result[pairs][j]['link_on_exchange']}")
                            print(f"Ссылка на BestChange: \n{result[pairs][j]['link_bestchange_exchange']} \n")

                            print(f"К продаже: примерно {buy_coin_binance} {i['symbol'][:-4]}")
                            print(f"К получению: примерно {sell_bestchange_coin} {i['symbol'][-4:]}\n")
                            print(f"Спред: {round(((sell_bestchange_coin - start_capital) / start_capital) * 100, 3)}%\n")

                            print(f"Итоговый заработок: {round(sell_bestchange_coin - start_capital, 8)}")

                            print('<----------------------------------|---------------------------------->')


    # Можно выгрузить в JSON
    # with open('BestChange_res.json', 'w', encoding='Windows-1251') as file:
    #     json.dump(result, file, indent=4, ensure_ascii=False)


def get_data(coin_lists, coin='USDT'):
    result_data_coin = []
    if coin == 'USDT':
        result_data_coin = filter_coin('USDT', coin_lists)
    elif coin == 'BUSD':
        result_data_coin = filter_coin('BUSD', coin_lists)
    elif coin == 'USDC':
        result_data_coin = filter_coin('USDC', coin_lists)
    return result_data_coin

def filter_data_coin(coin):
    return get_data(
        list(filter(lambda i: 'symbol' in i,
                    get_binance_api('/api/v3/ticker/price'))),
        coin)  # Получаем список пар монет по фильтру USDT, BUSD, USDC

def main():
    coin = input('Введите стартовую монету (USDT - по умолчанию, USDC, BUSD): ')
    if coin not in ['USDT', 'USDC', 'BUSD'] and coin != '':
        while coin not in ['USDT', 'USDC', 'BUSD']:
            coin = input('Введите стартовую монету (USDT - по умолчанию, USDC, BUSD): ')
    elif coin == '':
        coin = 'USDT'

    while True:
        try:
            start_capital = int(input('Введите стартовый капитал в долларах (например 1000): '))
            break
        except:
            print('Это не число..')
    # start_capital = 100
    while True:
        try:
            reviews = int(input('Введите минимальное кол-во отзывов обменников (например 200): '))
            break
        except:
            print('Это не число..')
    # reviews = 100
    while True:
        try:
            seconds_repeat = int(input('Введите через сколько повторять проверки (например через каждые 10 минут): '))
            break
        except:
            print('Ввести надо целое число, например 5, 10 или 60 минут')

    print('Если захотите выйти из программы нажмите crtl + c')
    data_coin = filter_data_coin(coin)
    get_num_coin_bestchange()
    while True:
        app(start_capital=start_capital, reviews=reviews, coin=coin, data_coin=data_coin)
        print(f'В данный момент рабочих связок нет.. Проверим через {seconds_repeat} минут')
        time.sleep(seconds_repeat * 60)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
