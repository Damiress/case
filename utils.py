from datetime import datetime, timedelta
import flet as ft
import requests
import hashlib
import random
import bcrypt



def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def get_usd_eur_rates():
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        usd_buy_rate = None
        usd_sell_rate = None
        eur_buy_rate = None
        eur_sell_rate = None
        for rate in data:
            if rate["cc"] == "USD":
                usd_buy_rate = rate["rate"]
                usd_sell_rate = round(rate["rate"] * 1.01, 2)
            elif rate["cc"] == "EUR":
                eur_buy_rate = rate["rate"]
                eur_sell_rate = round(rate["rate"] * 1.01, 2)
            if usd_buy_rate is not None and usd_sell_rate is not None and eur_buy_rate is not None and eur_sell_rate is not None:
                break
        if usd_buy_rate is None or usd_sell_rate is None or eur_buy_rate is None or eur_sell_rate is None:
            return ["Помилка під час отримання курсів валют"]
        else:
            usd_eur_buy_rate = round(eur_buy_rate / usd_buy_rate, 4)
            usd_eur_sell_rate = round(eur_sell_rate / usd_sell_rate, 4)
            return [
                ft.Row([ft.Icon(ft.icons.ATTACH_MONEY, color=ft.colors.GREEN), ft.Text(f"USD: Купівля {usd_buy_rate}, Продаж {usd_sell_rate}")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([ft.Icon(ft.icons.EURO_SYMBOL, color=ft.colors.BLUE), ft.Text(f"EUR: Купівля {eur_buy_rate}, Продаж {eur_sell_rate}")], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([ft.Icon(ft.icons.SWAP_HORIZ, color=ft.colors.PURPLE), ft.Text(f"EUR/USD: Купівля {usd_eur_buy_rate}, Продаж {usd_eur_sell_rate}")], alignment=ft.MainAxisAlignment.CENTER)
            ]
    else:
        return ["Помилка під час отримання курсів валют"]

def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10

def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0

def generate_card_number():
    card_number = random.randint(4000000000000000, 4999999999999999)
    while not is_luhn_valid(card_number):
        card_number = random.randint(4000000000000000, 4999999999999999)
    return card_number

def generate_cvv():
    return random.randint(100, 999)

def generate_expiry_date():
    now = datetime.now()
    expiry_date = now + timedelta(days=365 * 5)
    return expiry_date.strftime("%m/%y")