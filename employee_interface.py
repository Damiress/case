from flet import AppBar, ElevatedButton, Page, Text, TextField, View, colors
from datetime import datetime, timedelta
import flet as ft
import sqlite3
import random

card_info_content = None
deposit_info_content = None
credit_info_content = None

def toggle_prolong_deposit(page: ft.Page, deposit_id):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    # Получение текущего статуса пролонгации
    cursor.execute("SELECT prolong FROM deposits WHERE id=?", (deposit_id,))
    current_prolong = cursor.fetchone()[0]

    # Обновление статуса пролонгации (1 -> 0, 0 -> 1)
    new_prolong = 0 if current_prolong else 1
    cursor.execute("UPDATE deposits SET prolong=? WHERE id=?", (new_prolong, deposit_id))
    conn.commit()
    conn.close()

    page.snack_bar = ft.SnackBar(ft.Text(f"Пролонгация депозита {'включена' if new_prolong else 'отключена'}"))
    page.snack_bar.open = True
    page.update()

def change_credit_limit(page: ft.Page, card_number):
    new_credit_limit = ft.TextField(label="Новый кредитный лимит", keyboard_type=ft.KeyboardType.NUMBER)
    save_button = ft.ElevatedButton("Сохранить", on_click=lambda _: update_credit_limit(page, card_number, new_credit_limit.value))

    def close_dialog(page: ft.Page):
        page.dialog.open = False
        page.update()
        
    page.dialog = ft.AlertDialog(
        title=ft.Text("Изменение кредитного лимита"),
        content=ft.Column([new_credit_limit, save_button]),
        actions=[ft.TextButton("Отмена", on_click=lambda _: close_dialog(page))]
    )
    page.dialog.open = True
    page.update()

def update_credit_limit(page: ft.Page, card_number, new_limit):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE card_accounts SET credit_limit=? WHERE card_number=?", (new_limit, card_number))
    conn.commit()
    conn.close()

    page.dialog.open = False
    page.snack_bar = ft.SnackBar(ft.Text("Кредитный лимит успешно изменен"))
    page.snack_bar.open = True
    page.update()

def main_page(page: Page, employee_name):
    current_date_for_employee = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    welcome_text = ft.Text(f"Ласкаво просимо, {employee_name}! Сьогодні {current_date_for_employee}", size=20)
    return ft.Column(
        [
            welcome_text,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

def block_card(page: ft.Page, card_number):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    # Обновление статуса карты на "No Active"
    cursor.execute("UPDATE card_accounts SET currency='No Active' WHERE card_number=?", (card_number,))
    conn.commit()
    conn.close()

    page.snack_bar = ft.SnackBar(ft.Text("Карта успешно заблокирована"))
    page.snack_bar.open = True
    page.update()

def unblock_card(page: ft.Page, card_number):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    # Обновление статуса карты на "Active"
    cursor.execute("UPDATE card_accounts SET currency='Active' WHERE card_number=?", (card_number,))
    conn.commit()
    conn.close()

    page.snack_bar = ft.SnackBar(ft.Text("Карта успешно разблокирована"))
    page.snack_bar.open = True
    page.update()

def open_card_info_page(page, client_id, client_name, navigation_rail):
    global card_info_content
    card_info_content = card_info_page(page, client_id, client_name, navigation_rail)
    page.clean()
    page.add(
        AppBar(title=Text("Информация о карте")),
        ft.Row([
            navigation_rail,
            ft.VerticalDivider(width=1),
            card_info_content
        ], expand=True)
    )
    page.update()

def open_deposit_info_page(page, client_id, client_name, navigation_rail):
    global deposit_info_content
    deposit_info_content = deposit_info_page(page, client_id, client_name, navigation_rail)
    page.clean()
    page.add(
        AppBar(title=Text("Информация о депозитах")),
        ft.Row([
            navigation_rail,
            ft.VerticalDivider(width=1),
            deposit_info_content
        ], expand=True)
    )
    page.update()

def open_credit_info_page(page, client_id, client_name, navigation_rail):
    global credit_info_content
    credit_info_content = credit_info_page(page, client_id, client_name, navigation_rail)
    page.clean()
    page.add(
        AppBar(title=Text("Информация о кредитах")),
        ft.Row([
            navigation_rail,
            ft.VerticalDivider(width=1),
            credit_info_content
        ], expand=True)
    )
    page.update()
def credit_info_page(page: Page, client_id, client_name, navigation_rail):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM client_data WHERE id=?", (client_id,))
    client_data = cursor.fetchone()

    cursor.execute("SELECT * FROM credits WHERE client_id=?", (client_id,))
    credit_data = cursor.fetchone()

    update_current_client_button(page, navigation_rail, client_name)

    if client_data and credit_data:
        label_width = 150
        field_width = 200

        first_name_label = ft.Container(content=ft.Text("Ім'я:", text_align=ft.TextAlign.RIGHT), width=label_width)
        first_name = ft.TextField(value=client_data[1], read_only=True, width=field_width)

        last_name_label = ft.Container(content=ft.Text("Прізвище:", text_align=ft.TextAlign.RIGHT), width=label_width)
        last_name = ft.TextField(value=client_data[2], read_only=True, width=field_width)

        middle_name_label = ft.Container(content=ft.Text("По-Батькові:", text_align=ft.TextAlign.RIGHT), width=label_width)
        middle_name = ft.TextField(value=client_data[3], read_only=True, width=field_width)

        birth_date_label = ft.Container(content=ft.Text("Дата народження:", text_align=ft.TextAlign.RIGHT), width=label_width)
        birth_date = ft.TextField(value=client_data[4], read_only=True, width=field_width)

        credit_number_label = ft.Container(content=ft.Text("Номер кредиту:", text_align=ft.TextAlign.RIGHT), width=label_width)
        credit_number = ft.TextField(value=credit_data[2], read_only=True, width=field_width)

        credit_amount_label = ft.Container(content=ft.Text("Сума кредиту:", text_align=ft.TextAlign.RIGHT), width=label_width)
        credit_amount = ft.TextField(value=str(credit_data[3]), read_only=True, width=field_width)

        credit_term_label = ft.Container(content=ft.Text("Строк дії кредиту:", text_align=ft.TextAlign.RIGHT), width=label_width)
        credit_term = ft.TextField(value=str(credit_data[6]), read_only=True, width=field_width)

        credit_rate_label = ft.Container(content=ft.Text("Відсоткова ставка:", text_align=ft.TextAlign.RIGHT), width=label_width)
        credit_rate = ft.TextField(value=str(credit_data[7]), read_only=True, width=field_width)

        credit_open_date_label = ft.Container(content=ft.Text("Дата відкриття:", text_align=ft.TextAlign.RIGHT), width=label_width)
        credit_open_date = ft.TextField(value=credit_data[4], read_only=True, width=field_width)

        credit_close_date_label = ft.Container(content=ft.Text("Дата закриття:", text_align=ft.TextAlign.RIGHT), width=label_width)
        credit_close_date = ft.TextField(value=credit_data[5], read_only=True, width=field_width)

        cards_button = ft.ElevatedButton("Картки", icon=ft.icons.CREDIT_CARD, on_click=lambda _: open_card_info_page(page, client_id, client_name, navigation_rail))
        deposits_button = ft.ElevatedButton("Депозити", icon=ft.icons.ACCOUNT_BALANCE, on_click=lambda _: open_deposit_info_page(page, client_id, client_name, navigation_rail))
        credits_button = ft.ElevatedButton("Кредити", icon=ft.icons.MONETIZATION_ON, on_click=lambda _: open_credit_info_page(page, client_id, client_name, navigation_rail))

        return ft.Column(
            [
                ft.Row([first_name_label, first_name, credit_number_label, credit_number]),
                ft.Row([last_name_label, last_name, credit_amount_label, credit_amount]),
                ft.Row([middle_name_label, middle_name, credit_term_label, credit_term]),
                ft.Row([birth_date_label, birth_date, credit_rate_label, credit_rate]),
                ft.Row([credit_open_date_label, credit_open_date, credit_close_date_label, credit_close_date]),
                ft.Row([cards_button, deposits_button, credits_button], alignment=ft.MainAxisAlignment.CENTER),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=20,
        )
    else:
        conn.close()
        return ft.Text("Інформації про кредити не знайденно")

def deposit_info_page(page: Page, client_id, client_name, navigation_rail):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM client_data WHERE id=?", (client_id,))
    client_data = cursor.fetchone()

    cursor.execute("SELECT * FROM deposits WHERE id=?", (client_id,))
    deposit_data = cursor.fetchone()

    update_current_client_button(page, navigation_rail, client_name)

    if client_data and deposit_data:
        label_width = 150
        field_width = 200

        first_name_label = ft.Container(content=ft.Text("Ім'я:", text_align=ft.TextAlign.RIGHT), width=label_width)
        first_name = ft.TextField(value=client_data[1], read_only=True, width=field_width)

        last_name_label = ft.Container(content=ft.Text("Прізвище:", text_align=ft.TextAlign.RIGHT), width=label_width)
        last_name = ft.TextField(value=client_data[2], read_only=True, width=field_width)

        middle_name_label = ft.Container(content=ft.Text("По-Батькові:", text_align=ft.TextAlign.RIGHT), width=label_width)
        middle_name = ft.TextField(value=client_data[3], read_only=True, width=field_width)

        birth_date_label = ft.Container(content=ft.Text("Дата народження:", text_align=ft.TextAlign.RIGHT), width=label_width)
        birth_date = ft.TextField(value=client_data[4], read_only=True, width=field_width)

        deposit_number_label = ft.Container(content=ft.Text("Номер депозиту:", text_align=ft.TextAlign.RIGHT), width=label_width)
        deposit_number = ft.TextField(value=deposit_data[3], read_only=True, width=field_width)

        deposit_amount_label = ft.Container(content=ft.Text("Сума депозиту:", text_align=ft.TextAlign.RIGHT), width=label_width)
        deposit_amount = ft.TextField(value=str(deposit_data[5]), read_only=True, width=field_width)

        deposit_term_label = ft.Container(content=ft.Text("Срок депозиту:", text_align=ft.TextAlign.RIGHT), width=label_width)
        deposit_term = ft.TextField(value=deposit_data[6], read_only=True, width=field_width)

        deposit_rate_label = ft.Container(content=ft.Text("Відсоткова ставка:", text_align=ft.TextAlign.RIGHT), width=label_width)
        deposit_rate = ft.TextField(value=str(deposit_data[7]), read_only=True, width=field_width)

        deposit_open_date_label = ft.Container(content=ft.Text("Дата відкриття:", text_align=ft.TextAlign.RIGHT), width=label_width)
        deposit_open_date = ft.TextField(value=deposit_data[9], read_only=True, width=field_width)

        deposit_close_date_label = ft.Container(content=ft.Text("Дата закриття:", text_align=ft.TextAlign.RIGHT), width=label_width)
        deposit_close_date = ft.TextField(value=deposit_data[10], read_only=True, width=field_width)
        
        iban_deposit_label = ft.Container(content=ft.Text("IBAN:", text_align=ft.TextAlign.RIGHT), width=label_width)
        iban_deposit = ft.TextField(value=deposit_data[4], read_only=True, width=field_width)

        prolong_deposit_label = ft.Container(content=ft.Text("Пролонгація:", text_align=ft.TextAlign.RIGHT), width=label_width)
        prolong_deposit = ft.TextField(value=deposit_data[11], read_only=True, width=field_width)


        cards_button = ft.ElevatedButton("Картки", icon=ft.icons.CREDIT_CARD, on_click=lambda _: open_card_info_page(page, client_id, client_name, navigation_rail))
        deposits_button = ft.ElevatedButton("Депозити", icon=ft.icons.ACCOUNT_BALANCE, on_click=lambda _: open_deposit_info_page(page, client_id, client_name, navigation_rail))
        credits_button = ft.ElevatedButton("Кредити", icon=ft.icons.MONETIZATION_ON, on_click=lambda _: open_credit_info_page(page, client_id, client_name, navigation_rail))

        prolong_button = ft.ElevatedButton(
            "Вкл/Відкл пролонгацію",
            icon=ft.icons.REPEAT,
            on_click=lambda _: toggle_prolong_deposit(page, deposit_data[0])  # deposit_data[0] - это id депозита
        )

        return ft.Column(
            [
                ft.Row([first_name_label, first_name, deposit_number_label, deposit_number]),
                ft.Row([last_name_label, last_name, deposit_amount_label, deposit_amount]),
                ft.Row([middle_name_label, middle_name, deposit_term_label, deposit_term]),
                ft.Row([birth_date_label, birth_date, deposit_rate_label, deposit_rate]),
                ft.Row([deposit_open_date_label, deposit_open_date, deposit_close_date_label, deposit_close_date]),
                ft.Row([iban_deposit_label,iban_deposit, prolong_deposit_label, prolong_deposit]),
                ft.Row([cards_button, deposits_button, credits_button, prolong_button], alignment=ft.MainAxisAlignment.CENTER),

            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=20,
        )
    else:
        conn.close()
        return ft.Text("Інформація про депозити не знайдена")

def card_info_page(page: Page, client_id, client_name, navigation_rail):
    
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM client_data WHERE id=?", (client_id,))
    client_data = cursor.fetchone()

    cursor.execute("SELECT * FROM card_accounts WHERE id=?", (client_id,))
    card_data = cursor.fetchone()

    update_current_client_button(page, navigation_rail, client_name)

    if client_data and card_data:
        label_width = 150
        field_width = 200

        first_name_label = ft.Container(content=ft.Text("Ім'я:", text_align=ft.TextAlign.RIGHT), width=label_width)
        first_name = ft.TextField(value=client_data[1], read_only=True, width=field_width)

        last_name_label = ft.Container(content=ft.Text("Прізвище:", text_align=ft.TextAlign.RIGHT), width=label_width)
        last_name = ft.TextField(value=client_data[2], read_only=True, width=field_width)

        middle_name_label = ft.Container(content=ft.Text("По-Батькові:", text_align=ft.TextAlign.RIGHT), width=label_width)
        middle_name = ft.TextField(value=client_data[3], read_only=True, width=field_width)

        birth_date_label = ft.Container(content=ft.Text("Дата народження:", text_align=ft.TextAlign.RIGHT), width=label_width)
        birth_date = ft.TextField(value=client_data[4], read_only=True, width=field_width)

        inn_label = ft.Container(content=ft.Text("ІПН:", text_align=ft.TextAlign.RIGHT), width=label_width)
        inn = ft.TextField(value=client_data[6], read_only=True, width=field_width)

        passport_number_label = ft.Container(content=ft.Text("Номер паспорту:", text_align=ft.TextAlign.RIGHT), width=label_width)
        passport_number = ft.TextField(value=client_data[5], read_only=True, width=field_width)

        phone_number_label = ft.Container(content=ft.Text("Номер телефону:", text_align=ft.TextAlign.RIGHT), width=label_width)
        phone_number = ft.TextField(value=client_data[7], read_only=True, width=field_width)

        card_number_label = ft.Container(content=ft.Text("Номер картки:", text_align=ft.TextAlign.RIGHT), width=label_width)
        card_number = ft.TextField(value=card_data[3], read_only=True, width=field_width)

        card_expiry_label = ft.Container(content=ft.Text("Срок дії:", text_align=ft.TextAlign.RIGHT), width=label_width)
        card_expiry = ft.TextField(value=card_data[4], read_only=True, width=field_width)

        card_status_label = ft.Container(content=ft.Text("Статус картки:", text_align=ft.TextAlign.RIGHT), width=label_width)
        card_status = ft.TextField(value=card_data[6], read_only=True, width=field_width)

        card_type_label = ft.Container(content=ft.Text("Тип картки:", text_align=ft.TextAlign.RIGHT), width=label_width)
        card_type = ft.TextField(value=card_data[7], read_only=True, width=field_width)

        card_balance_label = ft.Container(content=ft.Text("Баланс картки:", text_align=ft.TextAlign.RIGHT), width=label_width)
        card_balance = ft.TextField(value=str(card_data[9]), read_only=True, width=field_width)

        card_credit_label = ft.Container(content=ft.Text("Кредитний баланс:", text_align=ft.TextAlign.RIGHT), width=label_width)
        card_credit = ft.TextField(value=str(card_data[8]), read_only=True, width=field_width)

        card_payment_system_label = ft.Container(content=ft.Text("Платіжна система:", text_align=ft.TextAlign.RIGHT), width=label_width)
        card_payment_system = ft.TextField(value=card_data[10], read_only=True, width=field_width)

        cards_button = ft.ElevatedButton("Картки", icon=ft.icons.CREDIT_CARD, on_click=lambda _: open_card_info_page(page, client_id, client_name, navigation_rail))
        deposits_button = ft.ElevatedButton("Депозити", icon=ft.icons.ACCOUNT_BALANCE, on_click=lambda _: open_deposit_info_page(page, client_id, client_name, navigation_rail))
        credits_button = ft.ElevatedButton("Кредити", icon=ft.icons.MONETIZATION_ON, on_click=lambda _: open_credit_info_page(page, client_id, client_name, navigation_rail))


        block_card_button = ft.ElevatedButton("Заблокувати картку", icon=ft.icons.LOCK_OUTLINED, icon_color="red", on_click=lambda _: block_card(page, card_data[3]))
        unblock_card_button = ft.ElevatedButton("Розблокувати картку", icon=ft.icons.LOCK_OPEN, icon_color="green", on_click=lambda _: unblock_card(page, card_data[3]))
        change_credit_limit_button = ft.ElevatedButton("Змінити кредитний ліміт", icon=ft.icons.APP_REGISTRATION_ROUNDED, on_click=lambda _: change_credit_limit(page, card_data[3]))



        cursor.execute("SELECT * FROM card_statement WHERE card_number=?", (card_data[3],))
        statement_data = cursor.fetchall()

        statement_table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Дата")),
                ft.DataColumn(label=ft.Text("Тип операції")),
                ft.DataColumn(label=ft.Text("Сума")),
                ft.DataColumn(label=ft.Text("Отримувач")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(data[4])),
                        ft.DataCell(ft.Text(data[2])),
                        ft.DataCell(ft.Text(str(data[3]))),
                        ft.DataCell(ft.Text(str(data[5]))),
                    ]
                )
                for data in statement_data
            ],
        )

        conn.close()

        return ft.Column(
            [
                ft.Row([first_name_label, first_name, inn_label, inn, card_number_label, card_number, card_balance_label, card_balance]),
                ft.Row([last_name_label, last_name, passport_number_label, passport_number, card_expiry_label, card_expiry, card_credit_label, card_credit]),
                ft.Row([middle_name_label, middle_name, phone_number_label, phone_number, card_status_label, card_status, card_payment_system_label, card_payment_system]),
                ft.Row([birth_date_label, birth_date, ft.Container(), ft.Container(), card_type_label, card_type, ft.Container(), ft.Container()]),
                ft.Row([cards_button, deposits_button, credits_button, change_credit_limit_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([block_card_button, unblock_card_button]),
                ft.Container(height=20),
                statement_table,
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=20,
        )
    else:
        conn.close()
        return ft.Text("Інформація про карте не знайдена")

def update_current_client_button(page, navigation_rail, client_name):
    for destination in navigation_rail.destinations:
        if destination.label.startswith("Поточний клієнт"):
            navigation_rail.destinations.remove(destination)
            break
    navigation_rail.destinations.append(
        ft.NavigationRailDestination(
            icon=ft.icons.PERSON_OUTLINE,
            selected_icon=ft.icons.PERSON,
            label=f"Поточний клієнт: {client_name}",
        )
    )
    navigation_rail.update()

def search_page(page: Page, navigation_rail, employee_name):
    def search_clients(e):
        first_name = first_name_field.value
        last_name = last_name_field.value
        middle_name = middle_name_field.value
        passport_number = passport_number_field.value
        phone_number = phone_number_field.value
        
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        query = "SELECT * FROM client_data WHERE 1=1"
        parameters = []

        if first_name:
            query += " AND first_name=?"
            parameters.append(first_name)
        if last_name:
            query += " AND last_name=?"
            parameters.append(last_name)
        if middle_name:
            query += " AND middle_name=?"
            parameters.append(middle_name)
        if passport_number:
            query += " AND passport_number=?"
            parameters.append(passport_number)
        if phone_number:
            query += " AND phone_number=?"
            parameters.append(phone_number)

        cursor.execute(query, parameters)
        results = cursor.fetchall()
        conn.close()

        search_results.controls.clear()

        if results:
            for result in results:
                client_id = result[0]
                client_name = f"{result[1]} {result[2]} {result[3]}"
                search_results.controls.append(
                    ft.ListTile(
                        title=ft.Text(client_name),
                        on_click=lambda _, client_id=client_id, client_name=client_name, employee_name=employee_name: on_client_click(_, client_id, client_name, navigation_rail, employee_name)
                    )
                )
        else:
            search_results.controls.append(
                ft.Text("Клиентне знайдений")
            )

        page.update()

    def on_client_click(e, client_id, client_name, navigation_rail, employee_name):
        page.client_id = client_id
        page.client_name = client_name
        update_current_client_button(page, navigation_rail, client_name)
        page.clean()
        page.add(
            AppBar(title=Text("Інформація про клієнта")),
            ft.Row([
                navigation_rail,
                ft.VerticalDivider(width=1),
                client_info_page(page, client_id, navigation_rail, employee_name)
            ], expand=True)
        )
        page.update()


    first_name_field = TextField(label="Ім'я", width=300)
    last_name_field = TextField(label="Прізвище", width=300)
    middle_name_field = TextField(label="По Батькові", width=300)
    passport_number_field = TextField(label="Номер паспорту", width=300)
    phone_number_field = TextField(label="Номер телефону", width=300)
    search_button = ElevatedButton("Пошук", on_click=search_clients)

    search_form = ft.Column(
        [
            first_name_field,
            last_name_field,
            middle_name_field,
            passport_number_field,
            phone_number_field,
            search_button,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
    )

    search_results = ft.Column()

    return ft.Column(
        [
            search_form,
            search_results,
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=20,
    )

def client_info_page(page: Page, client_id, navigation_rail, employee_name):

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM client_data WHERE id=?", (client_id,))
    client_data = cursor.fetchone()

    conn.close()

    if client_data:
        label_width = 150
        field_height = 40
        field_width = 200

        first_name_label = ft.Container(content=ft.Text("Ім'я:", text_align=ft.TextAlign.RIGHT), width=label_width)
        first_name = ft.TextField(value=client_data[1], read_only=True, width=field_width, height=field_height)

        last_name_label = ft.Container(content=ft.Text("Прізвище:", text_align=ft.TextAlign.RIGHT), width=label_width)
        last_name = ft.TextField(value=client_data[2], read_only=True, width=field_width, height=field_height)

        middle_name_label = ft.Container(content=ft.Text("По-батькові:", text_align=ft.TextAlign.RIGHT), width=label_width)
        middle_name = ft.TextField(value=client_data[3], read_only=True, width=field_width, height=field_height)

        birth_date_label = ft.Container(content=ft.Text("Дата народження:", text_align=ft.TextAlign.RIGHT), width=label_width)
        birth_date = ft.TextField(value=client_data[4], read_only=True, width=field_width, height=field_height)

        inn_label = ft.Container(content=ft.Text("ІПН:", text_align=ft.TextAlign.RIGHT), width=label_width)
        inn = ft.TextField(value=client_data[6], read_only=True, width=field_width, height=field_height)

        passport_number_label = ft.Container(content=ft.Text("Номер паспорту:", text_align=ft.TextAlign.RIGHT), width=label_width)
        passport_number = ft.TextField(value=client_data[5], read_only=True, width=field_width, height=field_height)

        phone_number_label = ft.Container(content=ft.Text("Номер телефону:", text_align=ft.TextAlign.RIGHT), width=label_width)
        phone_number = ft.TextField(value=client_data[7], read_only=True, width=field_width, height=field_height)

        registration_date_label = ft.Container(content=ft.Text("Дата реестрації:", text_align=ft.TextAlign.RIGHT), width=label_width)
        registration_date = ft.TextField(value=client_data[8], read_only=True, width=field_width, height=field_height)

        birth_place_label = ft.Container(content=ft.Text("Місце народження:", text_align=ft.TextAlign.RIGHT), width=label_width)
        birth_place = ft.TextField(value=client_data[11], read_only=True, width=field_width, height=60)

        living_place_label = ft.Container(content=ft.Text("Місце проживання:", text_align=ft.TextAlign.RIGHT), width=label_width)
        living_place = ft.TextField(value=client_data[10], read_only=True, width=field_width, height=60)

        email_label = ft.Container(content=ft.Text("Email:", text_align=ft.TextAlign.RIGHT), width=label_width)
        email = ft.TextField(value=client_data[12], read_only=True, width=field_width, height=60)

        customer_status_label = ft.Container(content=ft.Text("Категорія клієнтів:", text_align=ft.TextAlign.RIGHT), width=label_width)
        customer_status = ft.TextField(value=client_data[14], read_only=True, width=field_width, height=60)


        cards_button = ft.ElevatedButton("Картки", icon=ft.icons.CREDIT_CARD, on_click=lambda _: open_card_info_page(page, client_id, f"{client_data[1]} {client_data[2]}", navigation_rail))
        deposits_button = ft.ElevatedButton("Депозити", icon=ft.icons.ACCOUNT_BALANCE, on_click=lambda _: open_deposit_info_page(page, client_id, f"{client_data[1]} {client_data[2]}", navigation_rail))
        credits_button = ft.ElevatedButton("Кредити", icon=ft.icons.MONETIZATION_ON, on_click=lambda _: open_credit_info_page(page, client_id, f"{client_data[1]} {client_data[2]}", navigation_rail))
        inqueri_button = ft.ElevatedButton("Звернення", icon=ft.icons.CHAT, on_click=lambda _: show_client_inquiries(page, client_id))

        create_inquiry_button = ft.ElevatedButton("Створити звернення", icon=ft.icons.ADD, on_click=lambda _: create_inquiry_page(page, client_id, employee_name))
        edit_button = ft.ElevatedButton("Редагувати данні", icon=ft.icons.EDIT_NOTE_SHARP, on_click=lambda _: enable_editing())
        save_button = ft.ElevatedButton("Зберегти", icon=ft.icons.SAVE, on_click=lambda _: save_changes(), visible=False)
        cancel_button = ft.ElevatedButton("Відмінити", icon=ft.icons.CANCEL, on_click=lambda _: disable_editing(), visible=False)

        def enable_editing():
            first_name.read_only = False
            last_name.read_only = False
            middle_name.read_only = False
            birth_date.read_only = False

            passport_number.read_only = False
            phone_number.read_only = False
            birth_place.read_only = False
            living_place.read_only = False

            edit_button.visible = False
            save_button.visible = True
            cancel_button.visible = True

            page.update()

        def disable_editing():
            first_name.read_only = True
            last_name.read_only = True
            middle_name.read_only = True
            birth_date.read_only = True

            passport_number.read_only = True
            phone_number.read_only = True
            birth_place.read_only = True
            living_place.read_only = True

            edit_button.visible = True
            save_button.visible = False
            cancel_button.visible = False

            page.update()

        def save_changes():
            conn = sqlite3.connect('bank.db')
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE client_data
                SET first_name = ?, last_name = ?, middle_name = ?, birth_date = ?, 
                    passport_number = ?, phone_number = ?, addres_real = ?, birzday_city = ?
                WHERE id = ?
            """, (
                first_name.value, last_name.value, middle_name.value, birth_date.value, 
                passport_number.value, phone_number.value, living_place.value, birth_place.value, client_id
            ))

            conn.commit()
            conn.close()

            disable_editing()
            page.snack_bar = ft.SnackBar(ft.Text("Зміни збережено"))
            page.snack_bar.open = True
            page.update()




        return ft.Column(
            [
                ft.Row([first_name_label, first_name, inn_label, inn, birth_place_label, birth_place]),
                ft.Row([last_name_label, last_name, passport_number_label, passport_number, living_place_label, living_place]),
                ft.Row([middle_name_label, middle_name, phone_number_label, phone_number,email_label, email]),
                ft.Row([birth_date_label, birth_date, registration_date_label, registration_date,customer_status_label,customer_status]),
                ft.Row([ cards_button, deposits_button, credits_button,  inqueri_button, create_inquiry_button, edit_button, save_button, cancel_button,], alignment=ft.MainAxisAlignment.CENTER),
                
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=20,
        )
    else:
        return ft.Text("Кліент не знайден")

def show_client_inquiries(page, client_id):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM client_inquiries WHERE inquiry_client_special_number = (SELECT special_number FROM client_data WHERE id = ?)", (client_id,))
    inquiries = cursor.fetchall()

    conn.close()

    if inquiries:
        inquiry_table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Номер звернення")),
                ft.DataColumn(label=ft.Text("Дата звернення")),
                ft.DataColumn(label=ft.Text("Тема звернення")),
                ft.DataColumn(label=ft.Text("Продукт")),
                ft.DataColumn(label=ft.Text("Підтема")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(inquiry[1])),  # Номер обращения
                        ft.DataCell(ft.Text(inquiry[7])),  # Дата обращения
                        ft.DataCell(ft.Text(inquiry[8])),  # Тема обращения
                        ft.DataCell(ft.Text(inquiry[9])),  # Продукт
                        ft.DataCell(ft.Text(inquiry[10])),  # Подтема
                    ]
                )
                for inquiry in inquiries
            ],
        )

        inquiry_dialog = ft.AlertDialog(
            title=ft.Text("Звернення"),
            content=inquiry_table,
            actions=[
                ft.TextButton("Закрити", on_click=lambda _: close_inquiry_dialog(page))
            ],
        )

        def close_inquiry_dialog(page):
            page.dialog.open = False
            page.update()

        page.dialog = inquiry_dialog
        page.dialog.open = True
        page.update()
    else:
        page.snack_bar = ft.SnackBar(ft.Text("Зверненнь не знайдено"))
        page.snack_bar.open = True
        page.update()
    
def create_inquiry_page(page: ft.Page, client_id, employee_name):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    # Получение данных клиента
    cursor.execute("SELECT first_name, last_name, middle_name, special_number FROM client_data WHERE id=?", (client_id,))
    client_data = cursor.fetchone()

    # Получение данных сотрудника
    cursor.execute("SELECT internal_number FROM employee_data WHERE first_name || ' ' || last_name = ?", (employee_name,))
    employee_number = cursor.fetchone()[0]

    conn.close()

    def generate_inquiry_number():
        random_number = ''.join(random.choices('0123456789', k=8))
        return f"1-4{random_number}"

    inquiry_number = ft.TextField(label="Номер звернення", read_only=True, value=generate_inquiry_number())
    inquiry_date = ft.TextField(label="Дата звернення", read_only=True, value=datetime.now().strftime("%d.%m.%Y"))
    inquiry_employee = ft.TextField(label="ВН Співробітника", read_only=True, value=employee_number)

    inquiry_topic = ft.Dropdown(
        label="Тема обращения",
        options=[
            ft.dropdown.Option("Кредит"),
            ft.dropdown.Option("Депозит"),
            ft.dropdown.Option("Дебетова картка"),
            ft.dropdown.Option("Кредитна картка"),
        ],
        on_change=lambda _: update_sub_topics(page, inquiry_topic, inquiry_sub_topic, inquiry_product, client_id),
        width=400
    )

    inquiry_sub_topic = ft.Dropdown(label="Подтема", options=[])

    def update_sub_topics(page, inquiry_topic, inquiry_sub_topic, inquiry_product, client_id):
        topic = inquiry_topic.value
        sub_topics = []

        if topic == "Кредит":
            sub_topics = [ft.dropdown.Option("Рух по рахунку"), ]
        elif topic == "Депозит":
            sub_topics = [ft.dropdown.Option("Статус депозиту"), ]
        elif topic == "Дебетова картка":
            sub_topics = [ft.dropdown.Option("Баланс по карті"), ]
        elif topic == "Кредитна картка":
            sub_topics = [ft.dropdown.Option("Загальна сума боргу"), ]

        inquiry_sub_topic.options = sub_topics
        inquiry_sub_topic.value = None  # Сбросить выбранное значение
        inquiry_sub_topic.update()
        page.update()  # Обновить страницу после обновления опций

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        inquiry_product.options.clear()  # Очистить текущие опции

        if topic == "Кредит":
            cursor.execute("SELECT loan_number FROM credits WHERE client_id=?", (client_id,))
            products = [ft.dropdown.Option(loan_number[0]) for loan_number in cursor.fetchall()]
            inquiry_product.options = products
        elif topic == "Депозит":
            cursor.execute("SELECT deposit_number FROM deposits WHERE id=?", (client_id,))
            products = [ft.dropdown.Option(deposit_number[0]) for deposit_number in cursor.fetchall()]
            inquiry_product.options = products
        elif topic == "Дебетова картка":
            cursor.execute("SELECT card_number FROM card_accounts WHERE id=? AND account_type='Debit'", (client_id,))
            products = [ft.dropdown.Option(card_number[0]) for card_number in cursor.fetchall()]
            inquiry_product.options = products
        elif topic == "Кредитна картка":
            cursor.execute("SELECT card_number FROM card_accounts WHERE id=? AND account_type='Credit'", (client_id,))
            products = [ft.dropdown.Option(card_number[0]) for card_number in cursor.fetchall()]
            inquiry_product.options = products

        inquiry_product.update()
        page.update()

        conn.close()

        inquiry_topic.on_change = lambda e: update_products(e, page, client_id)

    def update_products(e):
        topic = e.control.value

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        if topic == "Кредит":
            cursor.execute("SELECT loan_number FROM credits WHERE client_id=?", (client_id,))
            products = [ft.dropdown.Option(loan_number[0]) for loan_number in cursor.fetchall()]
            inquiry_product.options = products
        elif topic == "Депозит":
            cursor.execute("SELECT deposit_number FROM deposits WHERE id=?", (client_id,))
            products = [ft.dropdown.Option(deposit_number[0]) for deposit_number in cursor.fetchall()]
            inquiry_product.options = products

        inquiry_product.update()

        inquiry_product.value = inquiry_product.value
        inquiry_product.update()
        page.update()

        conn.close()

    inquiry_product = ft.Dropdown(label="Продукт", options=[], on_change=update_products, width=400)  # Увеличение ширины




    def create_inquiry(e):
        inquiry_number_value = inquiry_number.value
        inquiry_date_value = inquiry_date.value
        inquiry_employee_value = inquiry_employee.value
        inquiry_topic_value = inquiry_topic.value
        inquiry_sub_topic_value = inquiry_sub_topic.value
        inquiry_product_value = inquiry_product.value

        print("inquiry_number_value:", inquiry_number_value)
        print("inquiry_date_value:", inquiry_date_value)
        print("inquiry_employee_value:", inquiry_employee_value)
        print("inquiry_topic_value:", inquiry_topic_value)
        print("inquiry_sub_topic_value:", inquiry_sub_topic_value)
        print("inquiry_product_value:", inquiry_product_value)


        client_first_name, client_last_name, client_middle_name, client_special_number = client_data

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        
        if inquiry_product_value is None:
            inquiry_product_value = ""

        cursor.execute(
            "INSERT INTO client_inquiries (inquiry_current_nummber, inquiry_client_name, inquiry_client_last_name, inquiry_client_middle_name, inquiry_client_special_number, inquiry_employee_login, inquiry_datetime, inquiry_topic, inquiry_product, inquiry_topic_deteils) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (inquiry_number_value, client_first_name, client_last_name, client_middle_name, client_special_number, inquiry_employee_value, inquiry_date_value, inquiry_topic_value, inquiry_product_value, inquiry_sub_topic_value)
        )
        conn.commit()
        conn.close()

        page.snack_bar = ft.SnackBar(ft.Text("Звернення успішно створенно"))
        page.snack_bar.open = True
        page.update()

    def close_dialog(page: ft.Page):
        page.dialog.open = False
        page.update()

    create_inquiry_button = ft.ElevatedButton("Створити звернення", on_click=create_inquiry)
    cancel_button = ft.OutlinedButton("Закрити", on_click=lambda _: close_dialog(page))

    content = ft.Column([
        inquiry_number,
        inquiry_date,
        inquiry_employee,
        inquiry_topic,
        inquiry_sub_topic,
        inquiry_product,

        ft.Row([create_inquiry_button, cancel_button], alignment=ft.MainAxisAlignment.CENTER),
    ], spacing=10)

    page.dialog = ft.AlertDialog(
        title=ft.Text("Створення звернення"),
        content=content,
    )
    page.dialog.open = True
    page.update()

def employee_interface(page: Page, employee_name):
    page.clean()

    page.title = f"Інтерфейс співробітника - {employee_name}"

    navigation_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.HOME_OUTLINED,
                selected_icon=ft.icons.HOME_ROUNDED,
                label="Головна",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SEARCH_OUTLINED,
                selected_icon=ft.icons.SEARCH,
                label="Пошук клієнтів",
            ),

        ]
    )

    def on_navigation_change(e, navigation_rail):
        selected_route = e.control.destinations[e.control.selected_index].label.lower().replace(" ", "_")
        if selected_route == "головна":
            page.clean()
            page.add(
                AppBar(title=Text("АБС Б3 - Сотрудник")),
                ft.Row([
                    navigation_rail,
                    ft.VerticalDivider(width=1),
                    main_page(page, employee_name)
                ], expand=True)
            )
        elif selected_route == "пошук_клієнтів":
            page.clean()
            page.add(
                AppBar(title=Text("Пошук клієнтів")),
                ft.Row([
                    navigation_rail,
                    ft.VerticalDivider(width=1),
                    search_page(page, navigation_rail, employee_name)  # Pass employee_name here
                ], expand=True)
            )

        elif selected_route.startswith("поточний_клієнт"):
            client_id = page.client_id
            page.clean()
            page.add(
                AppBar(title=Text("Інформація про клієнта")),
                ft.Row([
                    navigation_rail,
                    ft.VerticalDivider(width=1),
                    client_info_page(page, client_id, navigation_rail, employee_name)
                ], expand=True)
            )
        page.update()

    navigation_rail.on_change = lambda e: on_navigation_change(e, navigation_rail)

    page.on_resize = lambda _: None

    page.add(
        AppBar(title=Text("АБС Б3 - Співробітник")),
        ft.Row([
            navigation_rail,
            ft.VerticalDivider(width=1),
            main_page(page, employee_name)
        ], expand=True)
    )

    page.update()

