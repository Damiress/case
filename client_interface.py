from utils import get_usd_eur_rates, hash_password, generate_card_number, generate_cvv, generate_expiry_date
from datetime import datetime, timedelta
from PIL import Image
import flet as ft
import sqlite3
import qrcode
import base64
import random
import bcrypt
import json
import io
import re


global client_name

def client_interface(page: ft.Page, client_name):
    global top_menu, current_client, navigation_bar, welcome_text
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM client_data WHERE first_name || ' ' || last_name = ?", (client_name,))
    result = cursor.fetchone()

    if result:
        current_client = result[0]
    else:
        current_client = None
    
    conn.close()

    page.clean()
    page.add(page.app_bar)
    current_date_for_client = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    welcome_text = ft.Text(f"Добро пожаловать, {client_name}! Сегодня {current_date_for_client}", size=24)

    destinations = [
        ft.NavigationDestination(icon=ft.icons.CREDIT_CARD, label="Твої карти"),
        ft.NavigationDestination(icon=ft.icons.ATTACH_MONEY, label="Твої депозити"),
        ft.NavigationDestination(icon=ft.icons.ACCOUNT_BALANCE_WALLET, label="Твої кредити"),
        ft.NavigationDestination(icon=ft.icons.ACCOUNT_BALANCE, label="Головна"),
        ft.NavigationDestination(icon=ft.icons.QUESTION_ANSWER_OUTLINED, label="Підтримка"),
        ft.NavigationDestination(icon=ft.icons.ACCOUNT_CIRCLE, label="Твій профіль"),
        ft.NavigationDestination(icon=ft.icons.MORE_VERT_SHARP, label="Інше")
    ]

    navigation_bar = ft.NavigationBar(destinations=destinations)
    page.navigation_bar = navigation_bar

    def on_navigation_change(e):
        selected_destination = None
        
        if e.control.selected_index >= 0 and e.control.selected_index < len(destinations):
            selected_destination = destinations[e.control.selected_index]
        
        if selected_destination is not None:
            if selected_destination.label == "Інше":
                show_other_page(page, client_name)
            
            elif selected_destination.label == "Головна":
                show_main_page(page)
            
            elif selected_destination.label == "Твій профіль":
                show_profile_page(page, client_name)
            
            elif selected_destination.label == "Твої карти":
                show_cards_page(page, client_name)
            
            elif selected_destination.label == "Твої депозити":
                show_deposits_page(page)
            
            elif selected_destination.label == "Твої кредити":
                show_credits_page(page)
                
            elif selected_destination.label == "Підтримка":
                support_page(page)

        else:
            print("Invalid selected index")

    navigation_bar.on_change = on_navigation_change
    
    page.add(navigation_bar, welcome_text)
    page.update() 

def support_page(page: ft.Page):
    page.clean()

    # Форма "Ми готові вам допомогти за телефоном"
    phone_support_form = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.icons.PERM_PHONE_MSG_ROUNDED),
                        ft.Text("Ми готові вам допомогти за телефоном", size=18, weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Text("3700", size=36, weight=ft.FontWeight.BOLD)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        width=400,
        height=150,
        bgcolor=ft.colors.BACKGROUND,
        border_radius=10,
        padding=20
    )

    # Форма "Або у будь якому відділенні банку"
    branch_support_form = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.icons.ACCOUNT_BALANCE_OUTLINED),
                        ft.Text("Або у будь якому відділенні банку", size=18, weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.ElevatedButton(
                    "Дізнатись адресу відділень",
                    icon=ft.icons.MAP_OUTLINED,
                    on_click=lambda _: page.launch_url("https://privatbank.ua/map")
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        width=400,
        height=150,
        bgcolor=ft.colors.BACKGROUND,
        border_radius=10,
        padding=20
    )

    # Форма "Ми працюємо цілодобово"
    working_hours_form = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.icons.ACCESS_TIME),
                        ft.Text("Ми працюємо цілодобово", size=18, weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Text("24/7", size=36, weight=ft.FontWeight.BOLD)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        width=400,
        height=150,
        bgcolor=ft.colors.BACKGROUND,
        border_radius=10,
        padding=20
    )

    # Форма "Відділення готові вам допомогти"
    branch_working_hours_form = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.icons.ACCESS_TIME_FILLED_OUTLINED),
                        ft.Text("Відділення готові вам допомогти", size=18, weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    controls=[
                        ft.Icon(ft.icons.DATE_RANGE),
                        ft.Text("Пн-Пт: 09:00-18:00", size=18)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        width=400,
        height=150,
        bgcolor=ft.colors.BACKGROUND,
        border_radius=10,
        padding=20
    )

    # Размещение форм на странице
    support_content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    phone_support_form,
                    ft.Container(width=20),
                    branch_support_form
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Container(height=20),
            ft.Row(
                controls=[
                    working_hours_form,
                    ft.Container(width=20),
                    branch_working_hours_form
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    page.add(support_content, navigation_bar, page.app_bar)
    page.update()

def show_other_page(page: ft.Page, client_name):
    page.clean()
    rates = get_usd_eur_rates()

    currency_rates_view = ft.Column(
        controls=rates,
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    default_avatar = "https://avatars.githubusercontent.com/u/5041459?s=88&v=4"
    avatar_image = ft.Image(src=default_avatar, width=100, height=100)
    client_full_name = ft.Text(client_name, size=20)

    centered_content = ft.Column([
        ft.Row([avatar_image], alignment="center"),
        ft.Row([client_full_name], alignment="center")
    ], spacing=5)

    def show_qr_code_dialog(_):
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=3)
        qr.add_data("https://github.com/Damiress/diplom")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        qr_image = ft.Image(src_base64=base64.b64encode(img_buffer.getvalue()).decode(), width=250, height=250)

        def close_dialog(_):
            qr_dialog.open = False
            page.update()
        
        qr_dialog = ft.AlertDialog(
            title=ft.Text("QR-код для завантаження проекту", size=18),
            content=ft.Column([
                ft.Text("Завантажити проект можно тут", size=16),
                qr_image,
                ft.Text("Або перейти за посиланням", size=16),
                ft.ElevatedButton("Перейти на GitHub", on_click=lambda _: page.launch_url("https://github.com/Damiress/diplom"), width=250, height=40),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
            height=400,
            ),
            
            

            actions=[
                ft.OutlinedButton("Закрити", on_click=close_dialog, width=200, height=50),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,

        )

        page.dialog = qr_dialog
        qr_dialog.open = True
        page.update()
        
    buttons_row = ft.Row([
        ft.ElevatedButton("Зробити переказ", icon=ft.icons.SEND, icon_color="green", width=600, height=100, on_click=lambda _: show_cards_page(page, client_name)),
        ft.ElevatedButton("Адреса відділень", icon=ft.icons.ACCOUNT_BALANCE, icon_color="green", width=600, height=100, on_click=lambda _: page.launch_url("https://privatbank.ua/map")), 
    ], alignment="center")

    buttons_row_1 = ft.Row([
        ft.ElevatedButton("Сканувати QR Code", icon=ft.icons.QR_CODE_SCANNER, icon_color="purple", width=400, height=100, on_click=show_qr_code_dialog),

        ft.ElevatedButton("FAQ", icon=ft.icons.QUIZ_OUTLINED, icon_color="yellow", width=400, height=100, on_click=lambda _: handle_faq_click(page)),
        ft.ElevatedButton("Бізнес",  icon=ft.icons.BUSINESS_CENTER, icon_color="blue", width=400, height=100),
        ft.ElevatedButton("Зміна номеру", icon=ft.icons.PHONELINK_SETUP, icon_color="purple", width=400, height=100, on_click=lambda _: show_change_phone_number(page))
    ], alignment="center")

    def show_exit_dialog(_):
        def exit_app(_):
             page.window_destroy()
        
        def cancel_exit(_):
            page.dialog.open = False
            page.update()

        exit_dialog = ft.AlertDialog(
            title=ft.Text("Підтвердження виходу"),
            content=ft.Text("Ви впевнені, що бажаєте вийти?"),
            actions=[
                ft.ElevatedButton("Так, вийти", on_click=exit_app),
                ft.OutlinedButton("Ні, залишитись", on_click=cancel_exit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.dialog = exit_dialog
        exit_dialog.open = True
        page.update()        

    

    buttons_row_2 = ft.Row([
        ft.ElevatedButton("Налаштування", icon=ft.icons.SETTINGS, icon_color="gray", width=600, height=100, on_click=lambda _: handler_setting_click(page)),
        ft.ElevatedButton("Вийти", icon=ft.icons.POWER_SETTINGS_NEW_SHARP, icon_color="red", width=600, height=100, on_click=show_exit_dialog)
    ], alignment="center")

    buttons_row_3 = ft.Row([
        ft.ElevatedButton("Про розробника", icon=ft.icons.INFO, icon_color="blue", width=1200, height=50),  
    ], alignment="center")

    information_version = ft.Row([
        ft.Text(f"ABS B3 Version 1.0.2 for Client ")
    ], alignment="center")

    content_column = ft.Column([centered_content, buttons_row, buttons_row_1, buttons_row_2, buttons_row_3, information_version], spacing=10)
    
    page.add(currency_rates_view, navigation_bar, content_column, page.app_bar)
    page.update()

def show_main_page(page: ft.Page):
    page.clean()

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    # Получение баланса по картам клиента
    cursor.execute("SELECT SUM(balance) FROM card_accounts WHERE id=?", (current_client,))
    card_balance = cursor.fetchone()[0] or 0

    # Получение баланса по депозиту клиента
    cursor.execute("SELECT SUM(amount) FROM deposits WHERE id=?", (current_client,))
    deposit_balance = cursor.fetchone()[0] or 0

    # Получение остатка по кредиту клиента
    cursor.execute("SELECT SUM(amount) - SUM(monthly_payment) FROM credits WHERE client_id=?", (current_client,))
    credit_balance = cursor.fetchone()[0] or 0

    # Получение минимального платежа по кредиту клиента
    cursor.execute("SELECT SUM(monthly_payment) FROM credits WHERE client_id=?", (current_client,))
    min_payment = cursor.fetchone()[0] or 0

    # Получение последних операций по карте клиента
    cursor.execute("SELECT * FROM card_statement WHERE card_number IN (SELECT card_number FROM card_accounts WHERE id=?) ORDER BY transaction_date DESC LIMIT 5", (current_client,))
    transactions = cursor.fetchall()

    conn.close()

    # Форма "Мої кошти"
    balance_form = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Мої кошти", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(f"Баланс: {card_balance + deposit_balance} грн", size=20),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Баланс карток", icon=ft.icons.CREDIT_CARD_ROUNDED, icon_color = "green", width=220, on_click=lambda _: show_card_balance_dialog(page, card_balance)),
                        ft.ElevatedButton("Баланс депозиту", icon=ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED, icon_color = "purple", width=220, on_click=lambda _: show_deposit_balance_dialog(page, deposit_balance)),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        width=500,
        height=200,
        bgcolor=ft.colors.BACKGROUND,
        border_radius=10,
        padding=20,
    )

    # Форма "Залишок за кредитом"
    credit_form = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Залишок за кредитом", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(f"Залишок: {credit_balance:.2f} грн", size=20),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Залишок за кредитом",icon=ft.icons.BALLOT, icon_color = "red",  width=220, on_click=lambda _: show_credit_balance_dialog(page, credit_balance)),
                        ft.ElevatedButton("Мінімальний платіж", icon=ft.icons.MONEY, icon_color = "yellow", width=220, on_click=lambda _: show_min_payment_dialog(page, min_payment)),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),
                
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        width=500,
        height=200,
        bgcolor=ft.colors.BACKGROUND,
        border_radius=10,
        padding=20,
    )

    # Форма "Останні операції"
    # Форма "Останні операції"
    transactions_form = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Останні операції", size=24, weight=ft.FontWeight.BOLD),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(label=ft.Text("Дата", size=22,)),
                        ft.DataColumn(label=ft.Text("Тип операції", size=22)),
                        ft.DataColumn(label=ft.Text("Сума", size=22)),
                        ft.DataColumn(label=ft.Text("Картка отримувача", size=22)),
                    ],
                    rows=[
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(transaction[4])),
                            ft.DataCell(ft.Text(transaction[2])),
                            ft.DataCell(ft.Text(str(transaction[3]))),
                            ft.DataCell(ft.Text(transaction[5])),
                        ]) for transaction in transactions
                    ],
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),

        width=1020,
        height=300,
        bgcolor=ft.colors.BACKGROUND,
        border_radius=10,
        padding=20,
    )

    # Размещение форм на странице
    main_content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    balance_form,
                    ft.Container(width=20),
                    credit_form,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(height=20),
            ft.Row(
                controls=[
                    ft.Container(expand=True),
                    transactions_form,
                    ft.Container(expand=True),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(main_content, navigation_bar, page.app_bar)
    page.update()

def show_card_balance_dialog(page: ft.Page, card_balance):
    dialog = ft.AlertDialog(
        title=ft.Text("Баланс карток"),
        content=ft.Text(f"Баланс по картам: {card_balance:.2f} грн"),
        actions=[ft.TextButton("OK", on_click=lambda _: close_dialog(page))],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.dialog = dialog
    dialog.open = True
    page.update()

def show_deposit_balance_dialog(page: ft.Page, deposit_balance):
    dialog = ft.AlertDialog(
        title=ft.Text("Баланс депозиту"),
        content=ft.Text(f"Баланс по депозиту: {deposit_balance:.2f} грн"),
        actions=[ft.TextButton("OK", on_click=lambda _: close_dialog(page))],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.dialog = dialog
    dialog.open = True
    page.update()

def show_credit_balance_dialog(page: ft.Page, credit_balance):
    dialog = ft.AlertDialog(
        title=ft.Text("Залишок за кредитом"),
        content=ft.Text(f"Залишок по кредиту: {credit_balance} грн"),
        actions=[ft.TextButton("OK", on_click=lambda _: close_dialog(page))],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.dialog = dialog
    dialog.open = True
    page.update()

def show_min_payment_dialog(page: ft.Page, min_payment):
    dialog = ft.AlertDialog(
        title=ft.Text("Мінімальний платіж"),
        content=ft.Text(f"Мінімальний платіж по кредиту: {min_payment:.2f} грн"),
        actions=[ft.TextButton("OK", on_click=lambda _: close_dialog(page))],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.dialog = dialog
    dialog.open = True
    page.update()

def close_dialog(page: ft.Page):
    page.dialog.open = False
    page.update()

def show_profile_page(page: ft.Page, client_name):
    page.clean()

    # Получение данных пользователя из базы данных
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client_data WHERE id=?", (current_client,))
    user_data = cursor.fetchone()
    conn.close()

    # Создание элементов интерфейса
    photo_url = "https://avatars.githubusercontent.com/u/5041459?s=88&v=4"  # Замените на фактический URL фото пользователя
    user_photo = ft.Image(src=photo_url, width=100, height=100, fit=ft.ImageFit.CONTAIN, border_radius=5)

    first_name_field = ft.TextField(label="Ім'я", value=user_data[1], read_only=True, width=300)
    last_name_field = ft.TextField(label="Прізвище", value=user_data[2], read_only=True, width=300)
    middle_name_field = ft.TextField(label="По батькові", value=user_data[3], read_only=True, width=300)
    birth_date_field = ft.TextField(label="Дата народження", value=user_data[7], read_only=True, width=300)
    inn_field = ft.TextField(label="ІПН", value=user_data[5], read_only=True, width=300)
    passport_field = ft.TextField(label="Номер паспорта", value=user_data[4], read_only=True, width=300)
    living_place_field = ft.TextField(label="Місце проживання", value=user_data[10], read_only=True, width=300)
    birth_place_field = ft.TextField(label="Місце народження", value=user_data[11], read_only=True, width=300)

    edit_button = ft.ElevatedButton(text="Змінити дані", width=300, height=50)
    save_button = ft.ElevatedButton(text="Зберегти зміни", width=300,height=50, visible=False)
    cancel_button = ft.ElevatedButton(text="Відмінити редагування", width=300,height=50, visible=False)

    # Функция для включения/выключения режима редактирования
    def toggle_edit_mode(e):
        first_name_field.read_only = not first_name_field.read_only
        last_name_field.read_only = not last_name_field.read_only
        middle_name_field.read_only = not middle_name_field.read_only
        birth_date_field.read_only = not birth_date_field.read_only
        inn_field.read_only = not inn_field.read_only
        passport_field.read_only = not passport_field.read_only
        living_place_field.read_only = not living_place_field.read_only
        birth_place_field.read_only = not birth_place_field.read_only

        edit_button.visible = not edit_button.visible
        save_button.visible = not save_button.visible
        cancel_button.visible = not cancel_button.visible

        page.update()

    # Функция для сохранения изменений в базе данных
    def save_changes(e):
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE client_data
            SET first_name=?, last_name=?, middle_name=?, birth_date=?, special_number=?, passport_number=?, addres_real=?, birzday_city=?
            WHERE id=?
        """, (
            first_name_field.value,
            last_name_field.value,
            middle_name_field.value,
            birth_date_field.value,
            inn_field.value,
            passport_field.value,
            living_place_field.value,
            birth_place_field.value,
            current_client
        ))
        conn.commit()
        conn.close()

        toggle_edit_mode(None)
        page.snack_bar = ft.SnackBar(content=ft.Text("Зміни збережено"))
        page.snack_bar.open = True
        page.update()

    # Назначение обработчиков событий на кнопки
    edit_button.on_click = toggle_edit_mode
    save_button.on_click = save_changes
    cancel_button.on_click = toggle_edit_mode

    # Размещение элементов на странице
    profile_content = ft.Column(
        [   
            ft.Container(),
            user_photo,
            first_name_field,
            last_name_field,
            middle_name_field,
            birth_date_field,
            inn_field,
            passport_field,
            living_place_field,
            birth_place_field,
            edit_button,
            save_button,
            cancel_button,
            ft.Container(),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
        expand=True,
        

    )

    page.add(profile_content, navigation_bar, page.app_bar)
    page.update()

def reissue_card(page: ft.Page):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    # Генерация нового номера карты, CVV, даты истечения срока действия и номера IBAN
    new_card_number = generate_card_number()
    new_cvv = generate_cvv()
    new_expiry_date = generate_expiry_date()


    # Обновление данных карты в базе данных
    cursor.execute("""
        UPDATE card_accounts
        SET card_number = ?, expiration_date = ?, security_code = ?
        WHERE id = ?
    """, (new_card_number, new_expiry_date, new_cvv, current_client))
    conn.commit()
    conn.close()

    # Отображение сообщения об успешном перевыпуске карты
    page.snack_bar = ft.SnackBar(ft.Text("Картка успішно перевипущена"))
    page.snack_bar.open = True
    page.update()

def show_cards_page(page: ft.Page, client_name):
    page.clean()
    

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM card_accounts WHERE id=?", (current_client,))
    card_data = cursor.fetchone()

    if card_data:
        card_number = card_data[3]
        expiry_date = card_data[4]
        cvv = card_data[5]
        balance = card_data[9]
        status = card_data[6]
        payment_system = card_data[10]
        account_type = card_data[7]  # Получаем тип карты (дебетовая или кредитная)
        credits_balance = card_data[8]

        

        balance_text = f"Баланс: {balance:.2f} грн"
        if account_type == "Credit":
            balance_text += f"\nКредитний ліміт: {credits_balance:.2f}"

        def open_card_settings(_):
            page.clean()

            block_card_button = ft.ElevatedButton(
                "Заблокувати карту/де-активувати",
                on_click=lambda _: block_card(page),
                icon=ft.icons.LOCK_CLOCK_OUTLINED, 
                icon_color="red",
                width=400,
                height=50,
            )

            unblock_card_button = ft.ElevatedButton(
                "Розблокувати карту/активувати",
                on_click=lambda _: unblock_card(page),
                icon=ft.icons.LOCK_OPEN, 
                icon_color="green",
                width=400,
                height=50,
            )

            close_card_button = ft.ElevatedButton(
                "Закрити карту",
                on_click=lambda _: close_card(page),
                icon=ft.icons.BLOCK,
                icon_color="red",
                width=400,
                height=50,
            )

            change_pin_button = ft.ElevatedButton(
                "Змінити/встановити пін-код карти",
                on_click=lambda _: change_pin(page),
                icon=ft.icons.FIBER_PIN_OUTLINED,
                icon_color="purple",
                width=400,
                height=50,
            )
            reissue_card_button = ft.ElevatedButton(
                "Перевипустити картку",
                on_click=lambda _: reissue_card(page),
                icon=ft.icons.REFRESH,
                icon_color="blue",
                width=400,
                height=50,
            )

            card_settings_container = ft.Container(
                content=ft.Column(
                    [
                        card_container,
                        block_card_button,
                        unblock_card_button,
                        change_pin_button,
                        reissue_card_button,
                        close_card_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                alignment=ft.alignment.center,
            )

            page.add(card_settings_container, navigation_bar, page.app_bar)
            page.update()

        def block_card(page: ft.Page):
            def close_block_card_window(e):
                page.dialog.open = False
                page.update()

            def block_card_confirm(e):
                conn = sqlite3.connect('bank.db')
                cursor = conn.cursor()

                cursor.execute("UPDATE card_accounts SET currency='No Active' WHERE id=?", (current_client,))
                conn.commit()

                page.dialog.open = False
                page.snack_bar = ft.SnackBar(ft.Text("Карта успішно заблокована"))
                page.snack_bar.open = True

                conn.close()
                page.update()

            block_card_window = ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Text("Заблокувати/де-активувати карту", size=20, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.icons.CLEAR,
                                on_click=close_block_card_window,
                                tooltip="Закрити вікно",
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(
                            "Увага! Заблокувавши карту, ви не зможете розраховуватись картою, поповнювати карту, знімати готівку з карти. Ви завжди можете розблокувати карту",
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ElevatedButton(
                            "Заблокувати",
                            on_click=block_card_confirm,
                            bgcolor=ft.colors.RED_200,
                            color=ft.colors.BACKGROUND,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                alignment=ft.alignment.center,
                width=400,
                height=250,
                bgcolor=ft.colors.BACKGROUND,
                border_radius=10,
                padding=20,
            )

            page.dialog = ft.AlertDialog(
                title=ft.Text("Блокування картки"),
                content=block_card_window,
                actions=[],
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=lambda e: print("Dialog dismissed!"),
            )

            page.dialog.open = True
            page.update()

        def unblock_card(page: ft.Page):
            conn = sqlite3.connect('bank.db')
            cursor = conn.cursor()

            cursor.execute("SELECT currency FROM card_accounts WHERE id=?", (current_client,))
            card_status = cursor.fetchone()[0]

            if card_status == "No Active":
                open_activation_window(page)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Карта вже активована"))
                page.snack_bar.open = True
            conn.close()
            page.update()

        
        def open_activation_window(page: ft.Page):
            def close_activation_window(e):
                page.dialog.open = False
                page.update()

            activation_window = ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Text("Активувати карту", size=20, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.icons.CLEAR,
                                on_click=close_activation_window,
                                tooltip="Закрити вікно",
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.TextField(
                            label="Введіть пін-код карти",
                            password=True,
                            max_length=4,
                            on_change=lambda _: check_pin_match(page),
                        ),
                        ft.TextField(
                            label="Повторіть пін-код карти",
                            password=True,
                            max_length=4,
                            on_change=lambda _: check_pin_match(page),
                        ),
                        ft.ElevatedButton(
                            "Активувати",
                            on_click=lambda _: activate_card(page),
                        ),
                        ft.TextButton(
                            "Забули пін?",
                            on_click=lambda _: change_pin(page),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                alignment=ft.alignment.center,
                width=400,
                height=300,
                bgcolor=ft.colors.BACKGROUND,
                border_radius=10,
                padding=20,
            )

            page.dialog = ft.AlertDialog(
                title=ft.Text("Активація картки"),
                content=activation_window,
                actions=[],
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=lambda e: print("Dialog dismissed!"),
            )

            page.dialog.open = True
            page.update()

        def check_pin_match(page: ft.Page):
            pin1 = page.dialog.content.controls[1].value
            pin2 = page.dialog.content.controls[2].value

            if len(pin1) == 4 and len(pin2) == 4 and pin1 != pin2:
                page.snack_bar = ft.SnackBar(ft.Text("Введені пін-коди не співпадають"))
                page.snack_bar.open = True

        def activate_card(page: ft.Page):
            pin = page.dialog.content.content.controls[1].value

            conn = sqlite3.connect('bank.db')
            cursor = conn.cursor()

            cursor.execute("SELECT pin_code FROM card_accounts WHERE id=?", (current_client,))
            db_pin = cursor.fetchone()[0]

            if pin == str(db_pin):
                cursor.execute("UPDATE card_accounts SET currency='Active' WHERE id=?", (current_client,))
                conn.commit()
                page.dialog.open = False
                page.snack_bar = ft.SnackBar(ft.Text("Карту успішно активовано"))
                page.snack_bar.open = True
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Невірний пін-код"))
                page.snack_bar.open = True

            conn.close()
            page.update()
                

        def close_card(page: ft.Page):
            pass

        def change_pin(page: ft.Page):
            conn = sqlite3.connect('bank.db')
            cursor = conn.cursor()

            cursor.execute("SELECT pin_code FROM card_accounts WHERE id=?", (current_client,))
            db_pin = cursor.fetchone()[0]

            if db_pin is None:
                open_set_pin_window(page)
            else:
                open_change_pin_window(page)

            conn.close()

        def open_set_pin_window(page: ft.Page):
            def close_set_pin_window(e):
                page.dialog.open = False
                page.update()

            def set_pin(e):
                pin1 = pin1_field.value
                pin2 = pin2_field.value
                password = password_field.value

                if len(pin1) != 4 or len(pin2) != 4:
                    page.snack_bar = ft.SnackBar(ft.Text("Пін-код повинен містити 4 цифри"))
                    page.snack_bar.open = True
                elif pin1 != pin2:
                    page.snack_bar = ft.SnackBar(ft.Text("Введені пін-коди не співпадають"))
                    page.snack_bar.open = True
                else:
                    conn = sqlite3.connect('bank.db')
                    cursor = conn.cursor()

                    cursor.execute("SELECT password_hash FROM login_users WHERE id=?", (current_client,))
                    db_password_hash = cursor.fetchone()[0]

                    if hash_password(password) != db_password_hash:
                        page.snack_bar = ft.SnackBar(ft.Text("Невірний пароль від кабінету"))
                        page.snack_bar.open = True
                    else:
                        cursor.execute("UPDATE card_accounts SET pin_code=? WHERE id=?", (pin1, current_client))
                        conn.commit()
                        page.dialog.open = False
                        page.snack_bar = ft.SnackBar(ft.Text("Пін-код успішно встановлено"))
                        page.snack_bar.open = True

                    conn.close()

                page.update()

            pin1_field = ft.TextField(label="Введіть новий пін-код", password=True, max_length=4)
            pin2_field = ft.TextField(label="Повторіть новий пін-код", password=True, max_length=4)
            password_field = ft.TextField(label="Введіть пароль від кабінету", password=True)

            set_pin_window = ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Text("Встановити пін-код", size=20, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.icons.CLEAR,
                                on_click=close_set_pin_window,
                                tooltip="Закрити вікно",
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        pin1_field,
                        pin2_field,
                        password_field,
                        ft.ElevatedButton(
                            "Встановити пін-код",
                            on_click=set_pin,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                alignment=ft.alignment.center,
                width=400,
                height=600,
                bgcolor=ft.colors.BACKGROUND,
                border_radius=10,
                padding=20,
            )

            page.dialog = ft.AlertDialog(

                content=set_pin_window,
                actions=[],
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=lambda e: print("Dialog dismissed!"),
            )

            page.dialog.open = True
            page.update()

        def open_change_pin_window(page: ft.Page):
            def close_change_pin_window(e):
                page.dialog.open = False
                page.update()

            def change_pin(e):
                old_pin = old_pin_field.value
                new_pin1 = new_pin1_field.value
                new_pin2 = new_pin2_field.value
                password = password_field.value

                conn = sqlite3.connect('bank.db')
                cursor = conn.cursor()

                cursor.execute("SELECT pin_code FROM card_accounts WHERE id=?", (current_client,))
                db_pin = cursor.fetchone()[0]

                if old_pin != str(db_pin):
                    page.snack_bar = ft.SnackBar(ft.Text("Невірний старий пін-код"))
                    page.snack_bar.open = True
                elif len(new_pin1) != 4 or len(new_pin2) != 4:
                    page.snack_bar = ft.SnackBar(ft.Text("Новий пін-код повинен містити 4 цифри"))
                    page.snack_bar.open = True
                elif new_pin1 != new_pin2:
                    page.snack_bar = ft.SnackBar(ft.Text("Введені нові пін-коди не співпадають"))
                    page.snack_bar.open = True
                else:
                    cursor.execute("SELECT password_hash FROM login_users WHERE id=?", (current_client,))
                    db_password_hash = cursor.fetchone()[0]

                    if hash_password(password) != db_password_hash:
                        page.snack_bar = ft.SnackBar(ft.Text("Невірний пароль від кабінету"))
                        page.snack_bar.open = True
                    else:
                        cursor.execute("UPDATE card_accounts SET pin_code=? WHERE id=?", (new_pin1, current_client))
                        conn.commit()
                        page.dialog.open = False
                        page.snack_bar = ft.SnackBar(ft.Text("Пін-код успішно змінено"))
                        page.snack_bar.open = True

                conn.close()
                page.update()

            old_pin_field = ft.TextField(label="Введіть старий пін-код", password=True, max_length=4)
            new_pin1_field = ft.TextField(label="Введіть новий пін-код", password=True, max_length=4)
            new_pin2_field = ft.TextField(label="Повторіть новий пін-код", password=True, max_length=4)
            password_field = ft.TextField(label="Введіть пароль від кабінету", password=True)

            change_pin_window = ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Text("Змінити пін-код", size=20, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.icons.CLEAR,
                                on_click=close_change_pin_window,
                                tooltip="Закрити вікно",
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        old_pin_field,
                        new_pin1_field,
                        new_pin2_field,
                        password_field,
                        ft.ElevatedButton(
                            "Змінити пін-код",
                            on_click=change_pin,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                alignment=ft.alignment.center,
                width=400,
                height=600,
                bgcolor=ft.colors.BACKGROUND,
                border_radius=10,
                padding=20,
            )

            page.dialog = ft.AlertDialog(

                content=change_pin_window,
                actions=[],
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=lambda e: print("Dialog dismissed!"),
            )

            page.dialog.open = True
            page.update()

        card_settings_icon = ft.IconButton(
            icon=ft.icons.SETTINGS,
            on_click=open_card_settings,
            icon_color="black",
        )

        card_header = ft.Row(
            [
                ft.Container(
                    content=ft.Text(
                        balance_text,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLACK,
                    ),

                ),
                card_settings_icon,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        card_container = ft.Container(
            width=400,
            height=250,
            bgcolor=ft.colors.GREY_300,
            border_radius=10,
            padding=20,
            content=ft.Column(
                [
                    card_header,
                    ft.Container(
                        content=ft.Text(
                            card_number,
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLACK,
                        ),
                        alignment=ft.alignment.center,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                f"{expiry_date}",
                                size=16,
                                color=ft.colors.BLACK,
                            ),
                            ft.Text(
                                f"CVV: {cvv}",
                                size=16,
                                color=ft.colors.BLACK,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                f"{payment_system}",
                                size=16,
                                color=ft.colors.BLACK,
                            ),
                            ft.Text(
                                f"{status}",
                                size=16,
                                color=ft.colors.BLACK,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
        )





        def transfer_money(page: ft.Page):
            page.clean()

            recipient_card_number_field = ft.TextField(
                label="Номер карты получателя",
                text_size=24,
                width=400,
                text_align=ft.TextAlign.CENTER,
                color=ft.colors.BLACK,
            )

            recipient_card_container = ft.Container(
                width=400,
                height=250,
                bgcolor=ft.colors.GREY_300,
                border_radius=10,
                padding=20,
                content=ft.Column([
                    recipient_card_number_field,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

            swap_icon = ft.Icon(
                ft.icons.SWAP_HORIZ,
                color=ft.colors.GREEN,
                size=50,
            )

            transfer_button = ft.ElevatedButton(
                "Перевести",
                on_click=lambda _: perform_transfer(page, card_number, recipient_card_number_field.value), icon=ft.icons.UPLOAD_SHARP, icon_color="red",
                width=300,
                height=50,
            )

            transfer_form = ft.Column([
                ft.Row([
                    card_container,
                    swap_icon,
                    recipient_card_container,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [transfer_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
            page.add(transfer_form, navigation_bar, page.app_bar)
            page.update()

        def perform_transfer(page: ft.Page, sender_card_number, recipient_card_number):
            conn = sqlite3.connect('bank.db')
            cursor = conn.cursor()

            # Проверка наличия карты получателя в базе данных
            cursor.execute("SELECT * FROM card_accounts WHERE card_number=?", (recipient_card_number,))
            recipient_card = cursor.fetchone()

            if recipient_card:
                # Добавление поля для ввода суммы перевода
                transfer_amount_field = ft.TextField(label="Введіть суму переказу", width=400, text_align=ft.TextAlign.CENTER)
                page.add(transfer_amount_field)
                page.update()

                def complete_transfer(e):
                    transfer_amount = float(transfer_amount_field.value)

                    # Создание нового соединения с базой данных внутри функции complete_transfer
                    conn = sqlite3.connect('bank.db')
                    cursor = conn.cursor()

                    # Проверка наличия карты отправителя в базе данных
                    cursor.execute("SELECT balance FROM card_accounts WHERE card_number=?", (sender_card_number,))
                    sender_balance_result = cursor.fetchone()

                    if sender_balance_result is not None:
                        sender_balance = sender_balance_result[0]

                        if sender_balance >= transfer_amount:
                            # Обновление баланса карты отправителя
                            cursor.execute("UPDATE card_accounts SET balance=balance-? WHERE card_number=?", (transfer_amount, sender_card_number))

                            # Обновление баланса карты получателя
                            cursor.execute("UPDATE card_accounts SET balance=balance+? WHERE card_number=?", (transfer_amount, recipient_card_number))

                            # Добавление записи в выписку по карте отправителя
                            cursor.execute("INSERT INTO card_statement (card_number, transaction_type, amount, transaction_date, recipient_card_number) VALUES (?, ?, ?, ?, ?)",
                                        (sender_card_number, "Переказ", -transfer_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), recipient_card_number))

                            # Добавление записи в выписку по карте получателя
                            cursor.execute("INSERT INTO card_statement (card_number, transaction_type, amount, transaction_date, recipient_card_number) VALUES (?, ?, ?, ?, ?)",
                                        (recipient_card_number, "Поповнення", transfer_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sender_card_number))

                            conn.commit()
                            page.snack_bar = ft.SnackBar(ft.Text("Переказ успішно виконано"))
                            page.snack_bar.open = True
                        else:
                            page.snack_bar = ft.SnackBar(ft.Text("Недостатньо коштів на рахунку"))
                            page.snack_bar.open = True
                    else:
                        page.snack_bar = ft.SnackBar(ft.Text("Картку відправника не знайдено"))
                        page.snack_bar.open = True

                    conn.close()  # Закрытие соединения с базой данных внутри функции complete_transfer

                    if page.dialog is not None and page.dialog.open:
                        page.dialog.open = False
                    page.update()

                # Изменение обработчика нажатия на кнопку "Перевести"
                transfer_button = ft.ElevatedButton(
                    "Перевести",
                    on_click=complete_transfer,
                    width=300,
                    height=50,
                )
                page.add(transfer_button)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Картку отримувача не знайдено"))
                page.snack_bar.open = True

            conn.close()  # Закрытие соединения с базой данных после выполнения запросов
            page.update()



            conn.close()

        def deposit_money(_):
            # Логика пополнения карты
            pass

        def open_card_form(_):
            pass

        buttons_container = ft.Container(
            content=ft.Row(
                [
                    ft.ElevatedButton(
                        "Перевести",
                        on_click=lambda _: transfer_money(page), icon=ft.icons.UPLOAD_SHARP, icon_color="red", width=200, height=50,
                    ),
                    ft.ElevatedButton(
                        "Пополнить",
                        on_click=deposit_money, icon=ft.icons.FILE_DOWNLOAD_OUTLINED, icon_color="green", width=200, height=50,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            margin=ft.margin.only(top=20),
        )

        card_form = ft.Column(
            [card_container, buttons_container],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

                # Отображение выписки по карте
        cursor.execute("SELECT * FROM card_statement WHERE card_number=?", (card_number,))
        statement_data = cursor.fetchall()

        statement_table = ft.DataTable(
            columns=[
                ft.DataColumn(label=ft.Text("Дата та час")),
                ft.DataColumn(label=ft.Text("Тип операції")),
                ft.DataColumn(label=ft.Text("Сума")),
                ft.DataColumn(label=ft.Text("Картка отримувача")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(data[4])),
                    ft.DataCell(ft.Text(data[2])),
                    ft.DataCell(ft.Text(str(data[3]))),
                    ft.DataCell(ft.Text(data[5])),
                ]) for data in statement_data
            ],
        )

        card_form = ft.Column(
            [card_container, buttons_container, statement_table],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        page.add(card_form,  navigation_bar, page.app_bar)
    else:
        no_card_text = ft.Text("У вас ще немає карти")
        add_card_button = ft.ElevatedButton(
            "Відкрити карту",
            icon=ft.icons.ADD_CIRCLE_OUTLINE,
            icon_color=ft.colors.LIGHT_BLUE_500,
            on_click=lambda _: open_card_form(page),
        )
        page.add(no_card_text, add_card_button, navigation_bar, page.app_bar)

    page.update()

    conn.close()

def deposit_to_deposit(page: ft.Page, deposit_id):
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT card_number, balance FROM card_accounts WHERE id=?", (current_client,))
    cards = cursor.fetchall()

    conn.close()

    if not cards:
        page.snack_bar = ft.SnackBar(ft.Text("У вас нет доступных карт для пополнения депозита"))
        page.snack_bar.open = True
        return

    card_dropdown = ft.Dropdown(
        label="Выберите карту",
        options=[ft.dropdown.Option(key=card[0], text=f"Карта {card[0][-4:]}, Баланс: {card[1]} грн") for card in cards],
    )

    deposit_amount_field = ft.TextField(label="Сумма пополнения", keyboard_type=ft.KeyboardType.NUMBER)

    def complete_deposit(e):
        selected_card = card_dropdown.value
        deposit_amount = float(deposit_amount_field.value)

        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        cursor.execute("SELECT balance FROM card_accounts WHERE card_number=?", (selected_card,))
        card_balance = cursor.fetchone()[0]

        if card_balance < deposit_amount:
            conn.close()
            page.snack_bar = ft.SnackBar(ft.Text("Недостаточно средств на карте для пополнения депозита"))
            page.snack_bar.open = True
            return

        # Обновление баланса депозита
        cursor.execute("UPDATE deposits SET amount=amount+? WHERE id=?", (deposit_amount, deposit_id))

        # Обновление баланса карты
        cursor.execute("UPDATE card_accounts SET balance=balance-? WHERE card_number=?", (deposit_amount, selected_card))

        # Добавление записи о пополнении депозита
        cursor.execute("INSERT INTO deposit_transactions (deposit_id, transaction_type, amount, transaction_date, card_number) VALUES (?, ?, ?, ?, ?)",
                       (deposit_id, "Пополнение", deposit_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), selected_card))

        # Добавление записи о списании средств в выписку по карте
        cursor.execute("INSERT INTO card_statement (card_number, transaction_type, amount, transaction_date, recipient_card_number) VALUES (?, ?, ?, ?, ?)",
                       (selected_card, "Пополнение депозита", -deposit_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Депозит"))

        conn.commit()
        conn.close()

        page.snack_bar = ft.SnackBar(ft.Text(f"Депозит успешно пополнен на {deposit_amount} грн с карты {selected_card[-4:]}"))
        page.snack_bar.open = True
        page.dialog.open = False
        page.update()

    def deposit_dialog_close(page):
        page.dialog.open = False
        page.update()

    deposit_dialog = ft.AlertDialog(
        title=ft.Text("Пополнение депозита"),
        content=ft.Column([
            card_dropdown,
            deposit_amount_field
        ]),
        actions=[
            ft.TextButton("Отмена", on_click=lambda _: deposit_dialog_close(page)),
            ft.ElevatedButton("Пополнить", on_click=complete_deposit),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.dialog = deposit_dialog
    page.dialog.open = True
    page.update()
    
def show_deposits_page(page: ft.Page):
    page.clean()

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT account_number FROM card_accounts WHERE id=?", (current_client,))
    client_account_number = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM deposits WHERE client_account_number=?", (client_account_number,))
    deposit_data = cursor.fetchone()

    if deposit_data:
        current_balance = deposit_data[5]  # Получаем текущий баланс депозита из столбца "current_amount"
        open_date = deposit_data[9]
        close_date = deposit_data[10]
        interest_rate = deposit_data[7]
        estimated_profit = deposit_data[8]



        # Расчет прогресса депозита
        start_date = datetime.strptime(open_date, "%d.%m.%Y")
        end_date = datetime.strptime(close_date, "%d.%m.%Y")
        total_days = (end_date - start_date).days
        current_date = datetime.now()
        days_passed = (current_date - start_date).days
        progress = days_passed / total_days

        # Форма депозита
        deposit_shape = ft.Container(
            width=600,
            height=200,
            bgcolor=ft.colors.BACKGROUND,
            border_radius=10,
            padding=20,
            content=ft.Column(
                [
                    ft.Text(
                        f"Твій баланс депозиту"
                        f"\n{current_balance} грн",

                        size=20,
                        weight=ft.FontWeight.BOLD,

                    ),
                    ft.Text(
                        "Залишолось часу",
                        size=14,
                        color=ft.colors.BLUE_GREY_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.ProgressBar(
                        value=progress,
                        color=ft.colors.BLUE,
                        bgcolor=ft.colors.BLUE_GREY_100,
                        width=550,
                        height=10,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                f"{open_date}",
                                size=14,
                            ),
                            ft.Text(
                                f"{close_date}",
                                size=14,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        )

        # Форма ставки депозита
        interest_rate_shape = ft.Container(
            width=290,
            height=100,
            bgcolor=ft.colors.BACKGROUND,
            border_radius=10,
            padding=20,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, color=ft.colors.RED, size=20),
                            ft.Text(
                                f"{interest_rate}%",
                                size=24,
                                weight=ft.FontWeight.BOLD,

                            ),
                        ],

                    ),
                    ft.Text(
                        "Твоя ставка %",
                        size=12,
                        color=ft.colors.BLUE_GREY_400,
                        text_align=ft.TextAlign.CENTER,
                        
                    ),
                ],

            ),
            border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        )

        # Форма примерной суммы прибыли
        profit_shape = ft.Container(
            width=290,
            height=100,
            bgcolor=ft.colors.BACKGROUND,
            border_radius=10,
            padding=20,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET_OUTLINED, color=ft.colors.GREEN, size=16),
                            ft.Text(
                                f"{estimated_profit} грн",
                                size=24,
                                weight=ft.FontWeight.BOLD,

                            ),
                        ],

                    ),
                    ft.Row(
                        [
                            ft.Text(
                                "Твій прибуток",
                                size=12,
                                color=ft.colors.BLUE_GREY_400,

                            ),
                            ft.Tooltip(
                                message="За весь термін депозиту",
                                content=ft.Container(
                                    content=ft.Icon(ft.icons.INFO_OUTLINE, color=ft.colors.BLUE, size=16),
                                    padding=5,
                                ),
                            ),
                        ],

                        spacing=5,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        )

        # Кнопка "Пополнить"
        def deposit_money(_):
            deposit_to_deposit(page, deposit_data[0])


        deposit_button = ft.ElevatedButton(
            "Поповнити",
            icon=ft.icons.ADD_CIRCLE,
            icon_color="green",
            on_click=deposit_money,
            width=600,
            height=50,
        )

        # Размещение элементов на странице
        deposit_info = ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(expand=True),  # Добавляем расширяющийся контейнер слева
                        deposit_shape,
                        ft.Container(expand=True),  # Добавляем расширяющийся контейнер справа
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,  # Выравнивание по центру
                ),
                ft.Row(
                    [
                        
                        interest_rate_shape,
                        profit_shape,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                ft.Container(
                    content=deposit_button,
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=10),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        page.add(deposit_info, navigation_bar, page.app_bar)
    else:
        def open_deposit_form(_):
            conn = sqlite3.connect('bank.db')
            cursor = conn.cursor()

            cursor.execute("SELECT account_number FROM card_accounts WHERE id=?", (current_client,))
            client_account_number = cursor.fetchone()[0]

            cursor.execute("SELECT first_name, last_name, middle_name FROM client_data WHERE id=?", (current_client,))
            client_name_data = cursor.fetchone()
            client_full_name = f"{client_name_data[0]} {client_name_data[1]} {client_name_data[2]}"

            conn.close()

            deposit_amount = ft.TextField(label="Сума депозиту", keyboard_type=ft.KeyboardType.NUMBER, width=300)
            deposit_term = ft.Dropdown(
                label="Срок депозиту",
                options=[
                    ft.dropdown.Option("1 месяц"),
                    ft.dropdown.Option("2 месяца"),
                    ft.dropdown.Option("6 месяцев"),
                    ft.dropdown.Option("12 месяцев"),
                    ft.dropdown.Option("14 месяцев"),
                    ft.dropdown.Option("24 месяца"),
                    ft.dropdown.Option("36 месяцев"),
                    ft.dropdown.Option("60 месяцев"),
                ],
                width=300,
            )
            deposit_currency = ft.TextField(label="Валюта", value="UAH", read_only=True, width=300)
            deposit_open_date = ft.TextField(label="Дата відкриття", value=datetime.now().strftime("%d.%m.%Y"), read_only=True, width=300)
            deposit_close_date = ft.TextField(label="Дата завершення", read_only=True, width=300)
            interest_rate = ft.TextField(label="Відсоткова ставка", value="15%", read_only=True, width=300)
            estimated_profit = ft.TextField(label="Твій прибуток", value="0 грн", read_only=True, width=300)
            prolong_deposit = ft.Checkbox(label="Увімкнути пролонгацію", value=False)

            def generate_deposit_number():
                random_digits = ''.join(random.choices('0123456789', k=8))
                return f"TDRM{random_digits}"

            def generate_account_number(deposit_number):
                base_account = "UA85300522000002909"
                deposit_digits = deposit_number[4:]
                return f"{base_account}{deposit_digits}"

            def calculate_close_date(open_date, term):
                months = int(term.split()[0])
                close_date = open_date + timedelta(days=30 * months)
                return close_date.strftime("%d.%m.%Y")

            def calculate_interest_rate(amount, term):
                base_rate = {
                    "1 месяц": 15,
                    "2 месяца": 15.5,
                    "6 месяцев": 16,
                    "12 месяцев": 17,
                    "14 месяцев": 17.5,
                    "24 месяца": 17.8,
                    "36 месяцев": 18,
                    "60 месяцев": 20,
                }

                additional_rate = 0
                if 100001 <= amount <= 500000:
                    additional_rate = 0.2
                elif 500001 <= amount <= 1000000:
                    additional_rate = 0.5
                elif 1000001 <= amount <= 20000000:
                    additional_rate = 1
                elif 20000001 <= amount <= 50000000:
                    additional_rate = 1.75

                return base_rate[term] + additional_rate

            def calculate_estimated_profit(amount, rate, term):
                months = int(term.split()[0])
                profit = amount * (rate / 100) * (months / 12)
                return round(profit, 2)

            def update_calculations(_):
                try:
                    amount = float(deposit_amount.value)
                    term = deposit_term.value
                    open_date = datetime.strptime(deposit_open_date.value, "%d.%m.%Y")
                    close_date = calculate_close_date(open_date, term)
                    rate = calculate_interest_rate(amount, term)
                    profit = calculate_estimated_profit(amount, rate, term)

                    deposit_close_date.value = close_date
                    interest_rate.value = f"{rate}%"
                    estimated_profit.value = f"{profit} грн"

                    deposit_close_date.update()
                    interest_rate.update()
                    estimated_profit.update()
                except ValueError:
                    pass

            deposit_amount.on_change = update_calculations
            deposit_term.on_change = update_calculations

            def create_deposit(_):
                deposit_number = generate_deposit_number()
                deposit_account_number = generate_account_number(deposit_number)
                amount = float(deposit_amount.value)
                term = deposit_term.value
                currency = deposit_currency.value
                open_date = deposit_open_date.value
                close_date = deposit_close_date.value
                rate = float(interest_rate.value[:-1])
                profit = float(estimated_profit.value.split()[0])
                prolong = prolong_deposit.value

                conn = sqlite3.connect('bank.db')
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO deposits (full_name, client_account_number, deposit_number, account_number, amount, term, interest_rate, estimated_profit, open_date, close_date, prolong) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (client_full_name, client_account_number, deposit_number, deposit_account_number, amount, term, rate, profit, open_date, close_date, prolong),
                )
                conn.commit()
                conn.close()

                page.dialog.open = False
                page.snack_bar = ft.SnackBar(ft.Text("Депозит успішно оформленно"))
                page.snack_bar.open = True
                page.update()

            
            page.update()

            def deposit_dialog_close(page):
                page.dialog.open = False
                page.update()

            deposit_form = ft.AlertDialog(
                title=ft.Text("Відкриття депозиту"),
                content=ft.Column(
                    [
                        deposit_amount,
                        deposit_term,
                        deposit_currency,
                        deposit_open_date,
                        deposit_close_date,
                        interest_rate,
                        estimated_profit,
                        prolong_deposit,

                    ],
                    width=400,
                    height=500,
                ),
                actions=[
                    ft.TextButton("Не оформляти", on_click=deposit_dialog_close),
                    ft.ElevatedButton(text="Оформити депозит", on_click=lambda _: create_deposit(page)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            page.dialog = deposit_form
            deposit_form.open = True
            page.update()

        add_deposit_button = ft.ElevatedButton(
            "Відкрити депозит",
            icon=ft.icons.ADD_CIRCLE_OUTLINE,
            icon_color=ft.colors.LIGHT_BLUE_500,
            on_click=open_deposit_form,
        )

        page.add(add_deposit_button, navigation_bar, page.app_bar)

    page.update()

    conn.close()

def calculate_next_payment_date(current_payment_date):
    next_month = current_payment_date.month + 1
    next_year = current_payment_date.year
    if next_month > 12:
        next_month = 1
        next_year += 1
    next_payment_date = current_payment_date.replace(year=next_year, month=next_month)
    return next_payment_date

def show_credits_page(page: ft.Page):
    page.clean()

    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM credits WHERE client_id=?", (current_client,))
    credit_data = cursor.fetchone()

    current_date = datetime.now().date()

    if credit_data:
        credit_amount = credit_data[3]
        open_date = credit_data[4]
        close_date = credit_data[5]
        term_months = credit_data[6]
        monthly_payment = credit_data[8]
        loan_number = credit_data[9]
        next_payment_date_str = credit_data[10]

        remaining_omp = credit_data[11]
        
        if next_payment_date_str:
            next_payment_date = datetime.strptime(next_payment_date_str, "%d.%m.%Y").date()
        else:

            next_payment_date = None
        # Проверка и обновление даты ОМП
        # Проверка и обновление даты ОМП
        if current_date > next_payment_date:
            while current_date > next_payment_date:
                next_payment_date = calculate_next_payment_date(next_payment_date)
                remaining_omp += monthly_payment  # Увеличиваем остаток ОМП на сумму ежемесячного платежа
            cursor.execute("UPDATE credits SET next_payment_date=?, remaining_omp=? WHERE id=?",
                           (next_payment_date.strftime("%d.%m.%Y"), remaining_omp, credit_data[0]))
            conn.commit()

        cursor.execute("SELECT * FROM credit_transactions WHERE credit_id=?", (credit_data[0],))
        transactions = cursor.fetchall()

        # Рассчитываем прогресс кредита
        start_date = datetime.strptime(open_date, "%d.%m.%Y")
        end_date = datetime.strptime(close_date, "%d.%m.%Y")
        total_days = (end_date - start_date).days
        current_date = datetime.now()
        days_passed = (current_date - start_date).days
        progress = days_passed / total_days

        # Большая форма
        credit_card = ft.Container(
            width=600,
            height=200,
            bgcolor=ft.colors.BACKGROUND,
            border_radius=10,
            padding=20,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "Поточна сума боргу",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Tooltip(
                                message="Стільки залишилось до повного погашення",
                                content=ft.Container(
                                    content=ft.Icon(ft.icons.INFO_OUTLINE, color=ft.colors.BLUE, size=16),
                                    padding=5,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(
                        f"{credit_amount:.2f} грн",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                f"{loan_number}",
                                size=16,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Tooltip(
                                message="Реквізити кредиту (IBAN)",
                                content=ft.Container(
                                    content=ft.Icon(ft.icons.INFO_OUTLINE, color=ft.colors.BLUE, size=16),
                                    padding=5,
                                ),
                            ),
                        ],
                    ),

                    ft.Column(
                        [
                            ft.Text("Залишилось часу"),
                            ft.ProgressBar(
                                value=progress,
                                color=ft.colors.BLUE,
                                bgcolor=ft.colors.BLUE_GREY_100,
                                width=560,
                                height=10,
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        )

        # Маленькая форма слева
        monthly_payment_card = ft.Container(
            width=290,
            height=100,
            bgcolor=ft.colors.BACKGROUND,
            border_radius=10,
            padding=10,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.ATTACH_MONEY, color=ft.colors.GREEN, size=24),
                            ft.Text(
                                f"{remaining_omp:.2f} грн",
                                
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),

                    ft.Text(
                        
                        "Мінімальний платіж",
                        size=12,
                        color=ft.colors.BLUE_GREY_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        )

        # Маленькая форма справа
        next_payment_date_card = ft.Container(
            width=290,
            height=100,
            bgcolor=ft.colors.BACKGROUND,
            border_radius=10,
            padding=10,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.DATE_RANGE, color=ft.colors.PURPLE, size=24),
                            ft.Text(
                                f"{next_payment_date}",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),

                    ft.Text(
                        "Дата мінімального платежу",
                        size=12,
                        color=ft.colors.BLUE_GREY_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        )
        
        credit_amount_card = ft.Container(
            width=290,
            height=100,
            bgcolor=ft.colors.BACKGROUND,
            border_radius=10,
            padding=20,
            content=ft.Column(
                [
                    
                    ft.Row(
                        [
                            ft.Icon(ft.icons.MONEY, color=ft.colors.GREEN, size=24),
                            ft.Text(
                                f"{credit_amount:.2f} грн",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            
                        ],
                    ),

                    ft.Text(
                        "Сума оформлення кредиту",
                        size=12,
                        color=ft.colors.BLUE_GREY_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],

                alignment=ft.MainAxisAlignment.CENTER,
            ),
            border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        )

        # Новая маленькая форма справа (дата завершения кредита)
        credit_close_date_card = ft.Container(
            width=290,
            height=100,
            bgcolor=ft.colors.BACKGROUND,
            border_radius=10,
            padding=20,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.DATE_RANGE_OUTLINED, color=ft.colors.PURPLE, size=24),
                            ft.Text(
                                f"{close_date}",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                    ),

                    ft.Text(
                        "Дата завершення кредиту",
                        size=12,
                        color=ft.colors.BLUE_GREY_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            border=ft.border.all(1, ft.colors.BLUE_GREY_400),
        )

        transactions_table = ft.DataTable(
            columns = [
                ft.DataColumn(label=ft.Text("Дата")),
                ft.DataColumn(label=ft.Text("Тип операції")),
                ft.DataColumn(label=ft.Text("Сума")),
                ft.DataColumn(label=ft.Text("Картка")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(transaction[4])),
                    ft.DataCell(ft.Text(transaction[2])),
                    ft.DataCell(ft.Text(str(transaction[3]))),
                    ft.DataCell(ft.Text(transaction[5])),
                ]) for transaction in transactions
            ]
        )
        
            # Кнопка "Пополнить"
        def deposit_credit_click(_):
            deposit_credit(page, credit_data[0])

        deposit_button = ft.ElevatedButton(
            "Поповнити",
            icon=ft.icons.ADD,
            icon_color="green",
            on_click=deposit_credit_click,
            width=600,
            height=40,
        )





        def deposit_credit(page: ft.Page, credit_id):
            conn = sqlite3.connect('bank.db')
            cursor = conn.cursor()

            cursor.execute("SELECT card_number, balance FROM card_accounts WHERE id=?", (current_client,))
            cards = cursor.fetchall()

            cursor.execute("SELECT remaining_omp FROM credits WHERE id=?", (credit_id,))
            remaining_omp = cursor.fetchone()[0]

            conn.close()

            if not cards:
                page.snack_bar = ft.SnackBar(ft.Text("У вас нет доступных карт для пополнения кредита"))
                page.snack_bar.open = True
                return

            card_dropdown = ft.Dropdown(
                label="Выберите карту",
                options=[ft.dropdown.Option(key=card[0], text=f"Карта {card[0][-4:]}, Баланс: {card[1]} грн") for card in cards],
            )

            deposit_amount_field = ft.TextField(label="Сумма пополнения", keyboard_type=ft.KeyboardType.NUMBER)
            payment_amount_field = ft.TextField(label="Сумма платежа", value=str(remaining_omp), read_only=True)
            
            def add_omp_payment(_):
                payment_amount_field.value = str(remaining_omp)
                payment_amount_field.update()

            omp_payment_button = ft.ElevatedButton("Внести ОМП", on_click=add_omp_payment)

            def complete_deposit(e):
                selected_card = card_dropdown.value
                deposit_amount = float(deposit_amount_field.value)

                conn = sqlite3.connect('bank.db')
                cursor = conn.cursor()

                cursor.execute("SELECT balance FROM card_accounts WHERE card_number=?", (selected_card,))
                card_balance = cursor.fetchone()[0]

                if card_balance < deposit_amount:
                    conn.close()
                    page.snack_bar = ft.SnackBar(ft.Text("Недостаточно средств на карте для пополнения кредита"))
                    page.snack_bar.open = True
                    return

                # Получение текущего остатка по кредиту
                cursor.execute("SELECT amount, monthly_payment FROM credits WHERE id=?", (credit_id,))
                credit_data = cursor.fetchone()
                current_balance = credit_data[0] - credit_data[1]

                # Обновление остатка по кредиту
                new_balance = current_balance - deposit_amount
                cursor.execute("UPDATE credits SET amount=? WHERE id=?", (new_balance, credit_id))

                # Обновление баланса карты
                cursor.execute("UPDATE card_accounts SET balance=balance-? WHERE card_number=?", (deposit_amount, selected_card))

                # Добавление записи о пополнении кредита
                cursor.execute("INSERT INTO credit_transactions (credit_id, transaction_type, amount, transaction_date, card_number) VALUES (?, ?, ?, ?, ?)",
                            (credit_id, "Пополнение", deposit_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), selected_card))

                # Добавление записи о списании средств в выписку по карте
                cursor.execute("INSERT INTO card_statement (card_number, transaction_type, amount, transaction_date, recipient_card_number) VALUES (?, ?, ?, ?, ?)",
                            (selected_card, "Пополнение кредита", -deposit_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Кредит"))

                conn.commit()
                conn.close()

                page.snack_bar = ft.SnackBar(ft.Text(f"Кредит успешно пополнен на {deposit_amount} грн с карты {selected_card[-4:]}"))
                page.snack_bar.open = True
                page.dialog.open = False
                page.update()

            def add_omp_payment(_):
                payment_amount_field.value = str(remaining_omp)
                payment_amount_field.update()


                    
            def complete_payment(e):
                payment_amount = float(payment_amount_field.value)
                payment_date = datetime.now().strftime("%d.%m.%Y")
                selected_card = card_dropdown.value

                conn = sqlite3.connect('bank.db')
                cursor = conn.cursor()

                # Получение текущего остатка по кредиту, ОМП и даты следующего ОМП
                cursor.execute("SELECT amount, monthly_payment, next_payment_date, remaining_omp FROM credits WHERE id=?", (credit_id,))
                credit_data = cursor.fetchone()
                current_balance = credit_data[0]
                monthly_payment = credit_data[1]
                next_payment_date_str = credit_data[2]
                remaining_omp = credit_data[3]


                if next_payment_date_str:
                    next_payment_date = datetime.strptime(next_payment_date_str, "%Y-%m-%d").date()
                else:
                    next_payment_date = None


                current_date = datetime.now().date()

                # Обновление остатка по кредиту и остатка ОМП
                new_balance = current_balance - payment_amount
                new_remaining_omp = remaining_omp - payment_amount
                cursor.execute("UPDATE credits SET amount=?, remaining_omp=? WHERE id=?", (new_balance, new_remaining_omp, credit_id))

                # Обновление баланса карты
                cursor.execute("UPDATE card_accounts SET balance=balance-? WHERE card_number=?", (payment_amount, selected_card))

                # Проверка, если текущая дата больше даты следующего ОМП и остаток ОМП равен 0
                if next_payment_date and current_date > next_payment_date and new_remaining_omp == 0:
                    # Обновление даты следующего ОМП и установка остатка ОМП равным стандартному ОМП
                    next_payment_date = calculate_next_payment_date(next_payment_date)
                    cursor.execute("UPDATE credits SET next_payment_date=?, remaining_omp=? WHERE id=?", (next_payment_date.strftime("%d.%m.%Y"), monthly_payment, credit_id))

                # Добавление записи о платеже в выписку по кредиту
                cursor.execute("INSERT INTO credit_transactions (credit_id, transaction_type, amount, transaction_date) VALUES (?, ?, ?, ?)",
                            (credit_id, "Платеж", payment_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                # Добавление записи о списании средств в выписку по карте
                cursor.execute("INSERT INTO card_statement (card_number, transaction_type, amount, transaction_date, recipient_card_number) VALUES (?, ?, ?, ?, ?)",
                            (selected_card, "Платеж по кредиту", -payment_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Кредит"))

                conn.commit()
                conn.close()

                # Проверка на досрочное погашение кредита
                if new_balance <= 0:
                    # Кредит погашен досрочно
                    page.snack_bar = ft.SnackBar(ft.Text("Кредит успешно погашен досрочно"))
                    page.snack_bar.open = True
                    page.dialog.open = False
                    page.update()
                    show_credits_page(page)  # Обновление страницы кредитов
                else:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Платеж в размере {payment_amount} грн успешно внесен"))
                    page.snack_bar.open = True
                    page.dialog.open = False
                    page.update()
            
            def deposit_dialog_close(page):
                page.dialog.open = False
                page.update()
                
            deposit_dialog = ft.AlertDialog(
                title=ft.Text("Пополнение кредита"),
                content=ft.Column([
                    card_dropdown,
                    deposit_amount_field,
                    payment_amount_field,

                ]),
                actions=[
                    ft.TextButton("Отмена", on_click=lambda _: deposit_dialog_close(page)),
                    ft.ElevatedButton("Пополнить", on_click=complete_deposit),
                    ft.ElevatedButton("Внести платеж", on_click=complete_payment), 
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            page.dialog = deposit_dialog
            page.dialog.open = True
            page.update()


        credit_info = ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(expand=True),
                        credit_card,
                        ft.Container(expand=True),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        monthly_payment_card,
                        ft.Container(width=5),
                        next_payment_date_card,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        credit_amount_card,
                        ft.Container(width=5),
                        credit_close_date_card,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [deposit_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                ft.Row(
                    [transactions_table],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        page.add(credit_info, navigation_bar, page.app_bar)


        page.update()

        conn.close()
    else:
        def open_credit_form(_):
            credit_amount = ft.TextField(label="Сума кредиту", keyboard_type=ft.KeyboardType.NUMBER, width=300)
            
            credit_term_values = [1, 3, 6, 12, 24, 36, 60, 120]

            credit_term = ft.Slider(
                min=0,
                max=len(credit_term_values) - 1,
                divisions=len(credit_term_values) - 1,
                label="{value}",
                value=0,
                width=300,
            )

            def update_credit_term_label(e):
                index = int(e.control.value)
                e.control.label = f"{credit_term_values[index]} міс."
                e.control.update()

            credit_term.on_change = update_credit_term_label

            credit_currency = ft.TextField(label="Валюта", value="UAH", read_only=True, width=300)
            open_date = datetime.now().strftime("%d.%m.%Y")
            credit_open_date = ft.TextField(label="Дата оформлення", value=open_date, read_only=True, width=300)
            interest_rate_field = ft.TextField(label="Ставка кредиту", value="48% річних", read_only=True, width=300)
            monthly_payment_field = ft.TextField(label="Мінімальний платіж", value="0 грн", read_only=True, width=300)

            total_payment_field = ft.TextField(label="Загальна сума кредиту з відсотками", value="0 грн", read_only=True, width=300)
            credit_close_date = ft.TextField(label="Дата закриття", read_only=True, width=300)



            def update_calculations(_):
                try:
                    amount = float(credit_amount.value)
                    term_months = credit_term_values[int(credit_term.value)]
                    monthly_payment = calculate_monthly_payment(amount, term_months, 48.0)
                    total_payment = round(monthly_payment * term_months, 2)
                    close_date = calculate_close_date(credit_open_date.value, term_months)
                    monthly_payment_field.value = f"{monthly_payment:.2f} грн"
                    total_payment_field.value = f"{total_payment:.2f} грн"
                    credit_close_date.value = close_date
                    monthly_payment_field.update()
                    total_payment_field.update()
                    credit_close_date.update()
                except ValueError:
                    pass

            credit_amount.on_change = update_calculations
            credit_term.on_change = update_calculations

            def create_credit(_):
                amount = float(credit_amount.value)
                term_months = credit_term_values[int(credit_term.value)]
                open_date = datetime.strptime(credit_open_date.value, "%Y-%m-%d")  # Преобразование строки в объект datetime
                close_date = credit_close_date.value
                monthly_payment = float(monthly_payment_field.value.split()[0])
                total_payment = float(total_payment_field.value.split()[0])
                next_payment_date = calculate_next_payment_date(open_date)  # Передача объекта datetime
                remaining_omp = monthly_payment

                credit_number = generate_credit_number()
                loan_number = f"UA56300522000002909{credit_number[4:]}"

                if amount < 1000 or amount > 500000:
                    page.snack_bar = ft.SnackBar(ft.Text("Сума кредиту повинна бути від 1000 до 500000 грн"))
                    page.snack_bar.open = True
                    return
                
                if term_months not in credit_term_values:
                    page.snack_bar = ft.SnackBar(ft.Text("Некоректний термін кредиту"))
                    page.snack_bar.open = True
                    return

                conn = sqlite3.connect('bank.db')
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO credits (client_id, credit_number, loan_number, amount, open_date, close_date, term_months, interest_rate, monthly_payment, next_payment_date, remaining_omp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (current_client, credit_number, loan_number, amount, open_date, close_date, term_months, 48.0, monthly_payment, next_payment_date, remaining_omp),
                )

                conn.commit()
                conn.close()

                page.dialog.open = False
                page.snack_bar = ft.SnackBar(ft.Text("Кредит успішно оформлено"))
                page.snack_bar.open = True
                page.update()

            create_credit_button = ft.ElevatedButton(text="Оформити кредит", on_click=create_credit)

            def credit_dialog_close(_):
                page.dialog.open = False
                page.update()

            credit_form = ft.AlertDialog(
                title=ft.Text("Оформлення кредиту"),
                content=ft.Column(
                    [
                        credit_amount,
                        credit_term,
                        credit_currency,
                        credit_open_date,
                        credit_close_date,
                        interest_rate_field,
                        monthly_payment_field,
                        total_payment_field, 
                    ],
                    width=400,
                    height=500,
                ),
                actions=[
                    ft.TextButton("Скасувати", on_click=credit_dialog_close),
                    create_credit_button,
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            page.dialog = credit_form
            credit_form.open = True
            page.update()

        open_credit_button = ft.ElevatedButton(
            "Оформити кредит",
            icon=ft.icons.ADD_CIRCLE_OUTLINE,
            icon_color=ft.colors.LIGHT_BLUE_500,
            on_click=open_credit_form,
        )

        page.add(open_credit_button, navigation_bar, page.app_bar)
    
    def calculate_close_date(open_date, term_months):
        open_date = datetime.strptime(open_date, "%d.%m.%Y")
        close_date = open_date + timedelta(days=30 * term_months)
        return close_date.strftime("%d.%m.%Y")
    
    def calculate_monthly_payment(credit_amount, term_months, interest_rate):
        monthly_rate = interest_rate / 100 / 12
        monthly_payment = credit_amount * (monthly_rate / (1 - (1 + monthly_rate) ** (-term_months)))
        return round(monthly_payment, 2)
    
    def generate_credit_number():
        return f"CR{random.randint(10000000, 99999999)}"


    
    page.update()

    conn.close()

def handle_faq_click(page: ft.Page):
    page.clean()



    panel = ft.ExpansionPanelList(
        expand_icon_color=ft.colors.AMBER,
        elevation=10,
        divider_color=ft.colors.BLACK,

    )

    # Загружаем данные из JSON-файла
    with open('faq_data.json', 'r', encoding='utf-8') as file:
        faq_data = json.load(file)

    for item in faq_data:
        question = item['question']
        answer = item['answer']

        exp_panel = ft.ExpansionPanel(
            header=ft.ListTile(title=ft.Text(question)),
            content=ft.ListTile(
                title=ft.Text(answer),
            )
        )
        panel.controls.append(exp_panel)

    page.add(navigation_bar, page.app_bar, panel)
    page.update()

def handler_setting_click(page: ft.Page):
    page.clean()
    
    btn_setting = ft.Row([

        ft.ElevatedButton(f"Зміна паролю", icon=ft.icons.APP_REGISTRATION, icon_color="purple", width=300, height=100, on_click= lambda _: change_password(page, current_client)),
        ft.ElevatedButton(f"Встанови/змінити Email-адресу", icon=ft.icons.EMAIL, icon_color="blue",width=300, height=100, on_click= lambda _: change_email(page,current_client)),
    ], alignment="center")

    panel_btn_setting = ft.Column([btn_setting], spacing=10)

    page.add(panel_btn_setting, navigation_bar, page.app_bar)
    page.update()


def change_password(page: ft.Page, current_client):
    def update_password(e):
        current_password = current_password_field.value
        new_password = new_password_field.value
        confirm_password = confirm_password_field.value

        # Проверка текущего пароля
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM login_users WHERE id=?", (current_client,))
        stored_password_hash = cursor.fetchone()[0]
        conn.close()

        if bcrypt.checkpw(current_password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            # Текущий пароль верный
            if new_password == confirm_password:
                # Новые пароли совпадают
                hashed_new_password = hash_password(new_password)

                conn = sqlite3.connect('bank.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE login_users SET password_hash=? WHERE id=?", (hashed_new_password, current_client))
                conn.commit()
                conn.close()

                page.snack_bar = ft.SnackBar(ft.Text("Пароль успышно зміненно!"))
                page.snack_bar.open = True
                page.dialog.open = False
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Введенні паролі неспівпадають"))
                page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Ви ввели не вірний поточний пароль"))
            page.snack_bar.open = True

    current_password_field = ft.TextField(label="Поточний пароль", password=True)
    new_password_field = ft.TextField(label="Новий пароль", password=True)
    confirm_password_field = ft.TextField(label="Повторіть новий пароль", password=True)

    change_password_button = ft.ElevatedButton(text="Змінити пароль", on_click=update_password)

    change_password_content = ft.Column([
        current_password_field,
        new_password_field,
        confirm_password_field,
        change_password_button
    ], alignment=ft.MainAxisAlignment.CENTER)

    page.dialog = ft.AlertDialog(
        title=ft.Text("Зміна паролю"),
        content=change_password_content,
        actions=[],
        on_dismiss=lambda e: print("Dialog dismissed!"),
    )

    page.dialog.open = True
    page.update()

def show_change_phone_number(page: ft.Page):
    page.clean()
    

    def save_phone_number(e):
        new_phone_number = phone_number_field.value
        
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()

        try:
            if current_client is not None:
                cursor.execute("UPDATE client_data SET phone_number = ? WHERE id = ?", (new_phone_number, current_client))
                conn.commit()
                page.snack_bar = ft.SnackBar(ft.Text('Номер телефона успешно обновлен'))
                page.snack_bar.open = True
            else:
                page.snack_bar = ft.SnackBar(ft.Text('Клиент не выбран'))
                page.snack_bar.open = True
        except Exception as e:
            print(f"Error: {e}")
            page.snack_bar = ft.SnackBar(ft.Text('Ошибка при обновлении номера телефона'))
            page.snack_bar.open = True        
        finally:
            conn.close()

    phone_number_field = ft.TextField(label="Новый номер телефона", width=300)
    save_button = ft.ElevatedButton(text="Сохранить", on_click=save_phone_number)

    content = ft.Column([
        phone_number_field,
        save_button
    ], alignment="center")

    page.add(content, navigation_bar, page.app_bar)
    page.update()   

def change_email(page: ft.Page, current_client):
    def update_email(e):
        current_password = current_password_field.value
        new_email = new_email_field.value

        # Проверка текущего пароля
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM login_users WHERE id=?", (current_client,))
        stored_password_hash = cursor.fetchone()[0]
        conn.close()

        if bcrypt.checkpw(current_password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            # Текущий пароль верный
            if validate_email(new_email):
                # Email адрес валидный
                conn = sqlite3.connect('bank.db')
                cursor = conn.cursor()

                # Проверка наличия email в базе данных
                cursor.execute("SELECT email_addres FROM client_data WHERE id=?", (current_client,))
                existing_email = cursor.fetchone()[0]

                if existing_email:
                    # Обновление email
                    cursor.execute("UPDATE client_data SET email_addres=? WHERE id=?", (new_email, current_client))
                else:
                    # Добавление email
                    cursor.execute("UPDATE client_data SET email_addres=? WHERE id=?", (new_email, current_client))

                conn.commit()
                conn.close()

                page.snack_bar = ft.SnackBar(ft.Text("Email успешно обновлен"))
                page.snack_bar.open = True
                page.dialog.open = False
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Неверный формат email"))
                page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Неверный текущий пароль"))
            page.snack_bar.open = True

    def validate_email(email):
        # Простая регулярка для проверки валидности email
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    current_password_field = ft.TextField(label="Текущий пароль", password=True)
    new_email_field = ft.TextField(label="Новый email")

    # Получение текущего email адреса из базы данных
    conn = sqlite3.connect('bank.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email_addres FROM client_data WHERE id=?", (current_client,))
    current_email = cursor.fetchone()
    conn.close()

    # Создание нередактируемого поля для отображения текущего email адреса
    if current_email and current_email[0]:
        current_email_field = ft.TextField(label="Текущий email", value=current_email[0], read_only=True)
    else:
        current_email_field = ft.TextField(label="Текущий email", value="Email не установлен", read_only=True)

    change_email_button = ft.ElevatedButton(text="Изменить email", on_click=update_email)

    change_email_content = ft.Column([
        current_email_field,
        current_password_field,
        new_email_field,
        change_email_button
    ], alignment=ft.MainAxisAlignment.CENTER)

    page.dialog = ft.AlertDialog(
        title=ft.Text("Изменение email"),
        content=change_email_content,
        actions=[],
        on_dismiss=lambda e: print("Dialog dismissed!"),
    )

    page.dialog.open = True
    page.update()