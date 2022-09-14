import requests
import json
from fake_useragent import UserAgent
import time


def get_binance_list_coin(api_methods, param=None):
    ua = UserAgent()
    base_url = 'https://api.binance.com'
    url = base_url + api_methods
    params = {'symbol': param}
    response = requests.get(url, params=params, headers={'User-Agent': ua.random})
    if response.status_code == 429:
        time.sleep(2)
        print('WARNING: Нарушение кол-ва запросов в Binance')
    data = response.json()

    return data


def filter_coin(coin, coin_lists):
    return list(filter(lambda i: i['symbol'].endswith(coin), coin_lists))


# def get_naim_and_price(coin):
#     for i in data:
#         if coin == i['symbol']:
#             print(f"Цена монет {i['symbol']} на Binance стоит - {i['price']}")
#             break
#     else:
#         print('Нет таких пар монет')
def parse_coin_price(coin, start_capital):
    res = []
    for i in coin:
        res.append(i['symbol'])
        try:
            course_coin_buy = get_binance_list_coin('/api/v3/depth?limit=5', i['symbol'])['asks'][-1][0]
            # print(
            #     f"Курс для покупки {i['symbol'][:-4]} за {i['symbol'][-4:]} = {course_coin_buy} На бютжет из {start_capital}$ = {start_capital / float(course_coin_buy)} {i['symbol'][:-4]}")
        except:
            pass

    with open(f'coin_{res[0][-4:]}.json', 'w') as file:
        json.dump(res, file, indent=4, ensure_ascii=False)

def main():
    # start_capital = int(input('Введите стартовый капитал'))
    start_capital = 100
    coin_lists = get_binance_list_coin('/api/v3/ticker/price')

    data_with_USDT = filter_coin('USDT', coin_lists)
    data_with_BUSD = filter_coin('BUSD', coin_lists)
    data_with_USDC = filter_coin('USDC', coin_lists)
    print(data_with_USDT)
    parse_coin_price(data_with_USDT, start_capital)





if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
