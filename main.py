from client_interface import client_interface, handle_faq_click, show_change_phone_number, handler_setting_click
from employee_interface import employee_interface, main_page, search_page,client_info_page,create_inquiry_page
from login_register import login_handler, register_handler, apply_phone_mask, forgot_password_handler
from utils import hash_password
import flet as ft
import sqlite3



search_form_added = False
current_client = None
top_menu = None
current_employee = None

def main(page: ft.Page):
    page.title = "ABS B3"
    page.theme_mode = 'dark'
    current_theme = ['dark']
    page.window_width = 1920
    page.window_height = 1080
    page.window_resizable = True

    def switch_theme(e):
        new_theme = 'light' if current_theme[0] == 'dark' else 'dark'
        current_theme[0] = new_theme
        page.theme_mode = new_theme
        theme_button.icon = ft.icons.LIGHT_MODE if new_theme == 'dark' else ft.icons.DARK_MODE
        page.update()

    theme_button = ft.IconButton(
        icon=ft.icons.LIGHT_MODE if page.theme_mode == 'dark' else ft.icons.DARK_MODE,
        on_click=switch_theme,
        tooltip="Switch Theme"
    )

    app_bar = ft.AppBar(
        title=ft.Text("ABS B3"),
        actions=[theme_button],
        bgcolor= None if page.theme_mode == 'dark' else "#b3e5fc",  
    )

    page.app_bar = app_bar

    welcome_text = ft.Text(value="")

    user_login = ft.TextField(label="Login", width=450)     
    user_pass = ft.TextField(label="Password", width=450, password=True)
    
    btn_log = ft.OutlinedButton(text="Log On", width=450, on_click=lambda _: login_handler(page, user_login, user_pass), disabled=True)
    


    def validate_fields(e=None):
        login_value = user_login.value
        password_value = user_pass.value

        if login_value and password_value:
            btn_log.disabled = False
        else:
            btn_log.disabled = True

        page.update()
    
    user_login.on_change = validate_fields
    user_pass.on_change = validate_fields

    validate_fields()
    


    reg_first_name = ft.TextField(label="Ім'я", width=300)
    reg_last_name = ft.TextField(label="По-Батькові", width=300)
    reg_middle_name = ft.TextField(label="Прізвище", width=300)
    reg_birth_date= ft.TextField(label="Дата народження", width=920)
    reg_passport_nummber = ft.TextField(label="Номер паспорту", width=300)
    reg_special_nummber = ft.TextField(label="Ідентифікаційний код", width=300)
    reg_phone_nummber   = ft.TextField(label="Номер телефону", width=300, on_change=apply_phone_mask,)
    reg_real_address = ft.TextField(label="Місце проживання", width=300)
    reg_birth_address = ft.TextField(label="Місце народження", width=300)
    reg_income_amount = ft.TextField(label="Середньо-місячний дохід", width=300)


    
    reg_login = ft.TextField(label="Username", width=455)
    reg_pass = ft.TextField(label="Password", width=455, password=True)
    
    btn_reg = ft.OutlinedButton(text="Sign Up", width=930, on_click=lambda _: register_handler(page, reg_first_name, reg_last_name, reg_middle_name, reg_birth_date, reg_passport_nummber, reg_special_nummber, reg_phone_nummber, reg_real_address, reg_birth_address, reg_income_amount, reg_login, reg_pass))
    
    forgot_password_button = ft.TextButton(text="Я не пам'ятаю пароль", on_click=lambda _: forgot_password_handler(page))

    login_form = ft.Column([ ft.Text('Login', size=20), user_login, user_pass, btn_log, forgot_password_button], alignment=ft.MainAxisAlignment.CENTER)
    register_form = ft.Column([
    ft.Text('Register', size=20),
    ft.Row([reg_first_name, reg_last_name, reg_middle_name], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
    reg_birth_date,  
    ft.Row([reg_passport_nummber, reg_special_nummber, reg_phone_nummber], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
    ft.Row([reg_real_address, reg_birth_address, reg_income_amount], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
    
    ft.Row([reg_login, reg_pass], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
    btn_reg  
    ], alignment=ft.MainAxisAlignment.CENTER)
    
    center_login = ft.Row([login_form], alignment=ft.MainAxisAlignment.CENTER, expand=True)
    center_register = ft.Row([register_form], alignment=ft.MainAxisAlignment.CENTER, expand=True)

    panel_login = ft.Column([center_login], expand=True)
    panel_register = ft.Column([center_register], expand=True)

    def navigate(e):
        page.clean()
        if page.navigation_bar.selected_index == 0:
            page.add(panel_login, app_bar)
        elif page.navigation_bar.selected_index == 1:
            page.add(panel_register, app_bar)

    page.navigation_bar = ft.NavigationBar(destinations=[
        ft.NavigationDestination(icon=ft.icons.LOGIN, label="Login"),
        ft.NavigationDestination(icon=ft.icons.APP_REGISTRATION_OUTLINED, label="Sign in")
    ], on_change=navigate)

    page.add(panel_login, app_bar)  # Default view



ft.app(target=main)