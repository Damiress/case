from utils import hash_password, luhn_checksum, is_luhn_valid, generate_card_number, generate_cvv, generate_expiry_date
from employee_interface import employee_interface
from client_interface import client_interface
from utils import hash_password
from datetime import datetime
import flet as ft
import sqlite3
import random
import bcrypt
import re



def login_handler(page, user_login, user_pass):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT password_hash FROM login_employees WHERE username=?", (user_login.value,))
    hashed_password = cursor.fetchone()

    if hashed_password:
        if bcrypt.checkpw(user_pass.value.encode('utf-8'), hashed_password[0].encode('utf-8')):
            cursor.execute("SELECT first_name, last_name FROM employee_data WHERE id=(SELECT id FROM login_employees WHERE username=?)", (user_login.value,))
            employee_data = cursor.fetchone()
            employee_name = f"{employee_data[0]} {employee_data[1]}"
            welcome_text = employee_interface(page, employee_name)
            page.navigation_bar = None
            page.update()
            employee_name = f"{employee_data[0]} {employee_data[1]}"
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Не вірній логін або пароль."))
            page.snack_bar.open = True
    else:

        user = None
        cursor.execute("SELECT * FROM login_users WHERE username=?", (user_login.value,))
        user = cursor.fetchone()

        if user:
            hashed_password = user[2]
            if bcrypt.checkpw(user_pass.value.encode('utf-8'), hashed_password.encode('utf-8')):
                account_status = user[4]  # Получаем статус аккаунта из базы данных
                if account_status == 0:
                    cursor.execute("SELECT first_name, last_name FROM client_data WHERE id=?", (user[0],))
                    client_data = cursor.fetchone()
                    client_name = f"{client_data[0]} {client_data[1]}"
                    conn.close()
                    client_interface(page, client_name)
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Ваш акаунт заблоковано. Будь ласка, зверніться до підтримки банку за номером 3700."))
                    page.snack_bar.open = True
                    page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Не вірній логін або пароль."))
                page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Не вірній логін або пароль."))
            page.snack_bar.open = True

# ...

def register_handler(page, reg_first_name, reg_last_name, reg_middle_name, reg_birth_date, reg_passport_nummber, reg_special_nummber, reg_phone_nummber, reg_real_address, reg_birth_address, reg_income_amount, reg_login, reg_pass):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    hashed_password = hash_password(reg_pass.value)
    reg_current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    income_amount = int(reg_income_amount.value)
    if income_amount >= 0 and income_amount <= 8000:
        reg_customer_value = "Mass"
    elif income_amount > 8000 and income_amount <= 25000:
        reg_customer_value = "Mass+"
    elif income_amount > 25000 and income_amount <= 50000:
        reg_customer_value = "Mass Affluent"
    elif income_amount > 50000 and income_amount <= 200000:
        reg_customer_value = "Affluent"
    else:
        reg_customer_value = "Hight Affluent"
    


    try:
        cursor.execute("INSERT INTO client_data (first_name, last_name, middle_name, birth_date, passport_number, special_number, phone_number, registration_date,  addres_real, birzday_city,income_amount,customer_value) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)",
                       (reg_first_name.value, reg_last_name.value, reg_middle_name.value, reg_birth_date.value, reg_passport_nummber.value, reg_special_nummber.value, reg_phone_nummber.value, reg_current_date,  reg_real_address.value, reg_birth_address.value,reg_income_amount.value, reg_customer_value ))

        insert_query = "INSERT INTO login_users (username, password_hash, role_id, account_status) VALUES (?, ?, ?, ?)"
        print(f"Executing query: {insert_query}, with values: {(reg_login.value, hashed_password, 1, 0)}")
        cursor.execute(insert_query, (reg_login.value, hashed_password, 1, 0))

        card_number = generate_card_number()
        cvv = generate_cvv()
        expiry_date = generate_expiry_date()
        account_type = "Debit"
        currency = 'No Active'
        balance = 0
        agent_system = 'Visa Platinum'

        def generate_iban_number():
            base_account = "UA74300522000002909"
            random_digits = ''.join(random.choices('0123456789', k=8))
            return f"{base_account}{random_digits}"
        
        reg_iban = generate_iban_number()

        first_name = reg_first_name.value
        middle_name = reg_middle_name.value if reg_middle_name.value else ''
        last_name = reg_last_name.value

        full_name = f"{first_name} {middle_name} {last_name}".strip()

        cursor.execute("INSERT INTO card_accounts (owner_full_name, account_number, expiration_date, security_code, currency, account_type, balance, agent_system, card_number,iban_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)",
                       (full_name, reg_special_nummber.value, expiry_date, cvv, currency, account_type, balance, agent_system, card_number, reg_iban))

        conn.commit()
        page.snack_bar = ft.SnackBar(ft.Text('Регістрація успішна! Ви можете увійти до застосунку'))
        page.snack_bar.open = True
    except Exception as e:
        print(f"Error: {e}")
        page.snack_bar = ft.SnackBar(ft.Text('Помилка! Будь ласка, зверніться до підтримки банку за номером 3700.'))
        page.snack_bar.open = True

    conn.close()

def apply_phone_mask(event):
    value = event.control.value
    
    cleaned_value = re.sub(r'[^0-9+]', '', value)

    if cleaned_value == "+38":
        masked_value = cleaned_value
    if not cleaned_value.startswith("+38"):
        cleaned_value = "+38 " + cleaned_value.replace("+38", "")
    
    masked_value = cleaned_value[:4]
    if len(cleaned_value) > 4:
        masked_value += "-" + cleaned_value[4:7]
        if len(cleaned_value) > 7:
            masked_value += "-" + cleaned_value[7:9]
            if len(cleaned_value) > 9:
                masked_value += "-" + cleaned_value[9:]
    
    event.control.value = masked_value
    event.control.cursor_position = len(masked_value)
    event.control.update()

def forgot_password_handler(page: ft.Page):
    page.clean()
    def check_card_details(e):
        card_number = card_number_field.value
        cvv = cvv_field.value
        expiry_date = expiry_date_field.value

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.id
            FROM client_data c
            INNER JOIN card_accounts ca ON c.id = ca.id
            WHERE ca.card_number = ? AND ca.security_code = ? AND ca.expiration_date = ?
        """, (card_number, cvv, expiry_date))
        client_id = cursor.fetchone()

        conn.close()  # Закрываем соединение после выполнения запроса

        if client_id:
            client_id = client_id[0]

            page.clean()
            new_password_field = ft.TextField(label="Новий пароль", password=True)
            confirm_password_field = ft.TextField(label="Повторіть пароль", password=True)

            def update_password(e):
                new_password = new_password_field.value
                confirm_password = confirm_password_field.value

                if new_password == confirm_password:
                    hashed_password = hash_password(new_password)

                    conn = sqlite3.connect('bank.db')  # Создаем новое соединение внутри функции
                    cursor = conn.cursor()

                    cursor.execute("UPDATE login_users SET password_hash=? WHERE id=?", (hashed_password, client_id))
                    conn.commit()
                    conn.close()

                    page.snack_bar = ft.SnackBar(ft.Text("Пароль успішно зміненно"))
                    page.snack_bar.open = True
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Паролі не співпадають"))
                    page.snack_bar.open = True

            save_button = ft.ElevatedButton(text="Зберегти зміни", on_click=update_password)
            page.add(new_password_field, confirm_password_field, save_button)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Не вірно введені дані картки! Будь ласка, перевірте правильність введених даних"))
            page.snack_bar.open = True

    # ... остальной код ...

    card_number_field = ft.TextField(label="Номер картки", max_length=16)
    cvv_field = ft.TextField(label="CVV", password=True, max_length=3)
    expiry_date_field = ft.TextField(label="Строк дії картки (ММ/РР)", max_length=5)

    check_button = ft.ElevatedButton(text="Змінити пароль", on_click=check_card_details)

    page.add(card_number_field, cvv_field, expiry_date_field, check_button)