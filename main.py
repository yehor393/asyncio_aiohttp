import asyncio
from datetime import datetime, timedelta, date
import logging
import argparse
import aiohttp

logging.basicConfig(level=logging.ERROR)


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                logging.error(f"Error status: {resp.status} for {url}")
                return None
        except aiohttp.ClientConnectorError as err:
            logging.error(f"Connection error: {str(err)}")
            return None


async def get_exchange_on_date(date_obj: date):
    date_with_time = datetime.combine(date_obj, datetime.min.time())
    formatted_date = date_with_time.strftime("%d.%m.%Y")
    url = f'https://api.privatbank.ua/p24api/exchange_rates?date={formatted_date}'
    result = await request(url)
    return result


async def get_exchange(currency_code: str, days: int):
    exchange_list = []
    today = datetime.now().date()

    for i in range(days):
        current_date = today - timedelta(days=i)
        result = await get_exchange_on_date(current_date)
        if result:
            rates = result.get("exchangeRate")
            exc = next((element for element in rates if element["currency"] == currency_code), None)
            if exc:
                exchange_info = {
                    current_date.strftime("%d.%m.%Y"): {
                        currency_code: {
                            'sale': exc['saleRateNB'],
                            'purchase': exc['purchaseRateNB']
                        }
                    }
                }
                exchange_list.append(exchange_info)

    return exchange_list


async def main():
    parser = argparse.ArgumentParser(description='Get exchange rates for USD and EUR from PrivatBank API.')
    parser.add_argument('days', type=int, help='Number of days to retrieve exchange rates (up to 10 days)')

    args = parser.parse_args()

    if args.days > 10:
        print("Error: You can retrieve exchange rates for up to 10 days only.")
        return

    currencies = ['CAD']
    exchange_data = []

    for currency in currencies:
        data = await get_exchange(currency, args.days)
        exchange_data.extend(data)

    print(exchange_data)


if __name__ == "__main__":
    asyncio.run(main())
