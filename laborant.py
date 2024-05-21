from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.properties import ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp
import psycopg2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm

from config import host, user, password, db_name

class AddPatientPopup(Popup):
    def __init__(self, submit_callback, **kwargs):
        super(AddPatientPopup, self).__init__(**kwargs)
        self.title = 'Добавить нового пациента'
        self.size_hint = (0.8, 0.8)

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.fio_input = TextInput(hint_text='ФИО', multiline=False)
        self.layout.add_widget(self.fio_input)

        self.dob_input = TextInput(hint_text='Дата рождения (ГГГГ-ММ-ДД)', multiline=False)
        self.layout.add_widget(self.dob_input)

        self.passport_input = TextInput(hint_text='Серия и номер паспорта', multiline=False)
        self.layout.add_widget(self.passport_input)

        self.phone_input = TextInput(hint_text='Телефон', multiline=False)
        self.layout.add_widget(self.phone_input)

        self.email_input = TextInput(hint_text='E-mail', multiline=False)
        self.layout.add_widget(self.email_input)

        self.insurance_number_input = TextInput(hint_text='Номер страхового полиса', multiline=False)
        self.layout.add_widget(self.insurance_number_input)

        self.insurance_type_spinner = Spinner(
            text='Тип страхового полиса',
            values=('ОМС', 'ДМС')
        )
        self.layout.add_widget(self.insurance_type_spinner)

        self.insurance_company_spinner = Spinner(
            text='Название страховой компании',
            values=('Росгосстрах', 'СОГАЗ', 'Ингосстрах', 'РЕСО-Гарантия')
        )
        self.layout.add_widget(self.insurance_company_spinner)

        self.submit_button = Button(text='Добавить пациента')
        self.submit_button.bind(on_press=lambda x: self.submit(submit_callback))
        self.layout.add_widget(self.submit_button)

        self.add_widget(self.layout)

    def submit(self, submit_callback):
        patient_data = {
            'fio': self.fio_input.text,
            'dob': self.dob_input.text,
            'passport': self.passport_input.text,
            'phone': self.phone_input.text,
            'email': self.email_input.text,
            'insurance_number': self.insurance_number_input.text,
            'insurance_type': self.insurance_type_spinner.text,
            'insurance_company': self.insurance_company_spinner.text,
        }
        submit_callback(patient_data)
        self.dismiss()

class OrderFormScreen(Screen):
    tube_code_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(OrderFormScreen, self).__init__(**kwargs)
        
        # Создаем AnchorLayout для центрирования по горизонтали и вертикали
        layout = AnchorLayout(anchor_x='center', anchor_y='center')
        self.add_widget(layout)
        
        # Внутри AnchorLayout размещаем BoxLayout с виджетами
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20), size_hint=(None, None))
        self.layout.bind(minimum_size=self.layout.setter('size'))
        layout.add_widget(self.layout)
        
        # Добавляем заголовок
        self.title_label = Label(text='Лаборант', color=(1, 1, 1, 1), font_size=dp(24), size_hint=(None, None), size=(dp(250), dp(50)))
        self.layout.add_widget(self.title_label)

        # Используем свойства size_hint_y и size_hint_x, чтобы виджеты оставались в неизменном размере
        self.tube_code_input = TextInput(hint_text='Введите код пробирки', padding=15,multiline=False, size_hint=(None, None), size=(dp(250), dp(50)))
        self.tube_code_input.bind(on_text_validate=self.check_patient)
        self.layout.add_widget(self.tube_code_input)

        self.patient_name_input = TextInput(hint_text='Введите ФИО пациента', padding=15, multiline=False, size_hint=(None, None), size=(dp(250), dp(50)))
        self.layout.add_widget(self.patient_name_input)

        self.service_input = TextInput(hint_text='Введите услугу', padding=15, multiline=False, size_hint=(None, None), size=(dp(250), dp(50)))
        self.layout.add_widget(self.service_input)

        self.confirm_button = Button(text='Сгенерировать штрих-код', size_hint=(None, None), size=(dp(250), dp(50)))
        self.confirm_button.bind(on_press=self.check_patient)
        self.layout.add_widget(self.confirm_button)

    def check_patient(self, instance):
        fio = self.patient_name_input.text
        if not fio:
            self.show_error_dialog('Пожалуйста, введите\nФИО пациента.')
            return

        connection = None
        cursor = None
        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            cursor = connection.cursor()
            cursor.execute("SELECT patient_id, date_of_birth, insurance_policy_number FROM Patients WHERE full_name=%s", (fio,))
            result = cursor.fetchone()
            
            if result:
                self.patient_id, self.date_of_birth, self.patient_insurance_number = result
                self.generate_order(instance)
            else:
                self.show_add_patient_dialog()
                
        except Exception as _ex:
            print("Error while working with PostgreSQL: ", _ex)
            self.show_error_dialog('Ошибка при работе с базой данных')
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def show_add_patient_dialog(self):
        popup = AddPatientPopup(self.add_patient)
        popup.open()

    def add_patient(self, patient_data):
        connection = None
        cursor = None
        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO Patients (full_name, date_of_birth, passport_number, phone, email, insurance_policy_number, insurance_policy_type, insurance_company_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING patient_id
            """, (patient_data['fio'], patient_data['dob'], patient_data['passport'], patient_data['phone'], 
                  patient_data['email'], patient_data['insurance_number'], patient_data['insurance_type'], 
                  patient_data['insurance_company']))
            self.patient_id = cursor.fetchone()[0]
            self.date_of_birth = patient_data['dob']
            self.patient_insurance_number = patient_data['insurance_number']
            connection.commit()
            self.generate_order(None)
        except Exception as _ex:
            print("Error while working with PostgreSQL: ", _ex)
            self.show_error_dialog('Ошибка при добавлении \nпациента в базу данных')
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def generate_order(self, instance):
        tube_code = self.tube_code_input.text
        service = self.service_input.text
        if not tube_code or not service:
            self.show_error_dialog('Пожалуйста, введите код\nпробирки и услугу.')
            return

        order_date = datetime.datetime.now().strftime('%Y-%m-%d')
        order_number = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.tube_code = tube_code
        self.service = service
        self.cost = self.calculate_cost(service)

        connection = None
        cursor = None
        try:
            connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO Orders (order_date, order_name, patient_id)
                VALUES (%s, %s, %s)
            """, (order_date, order_number,  self.patient_id))
            connection.commit()
            self.generate_barcode(None)
        except Exception as _ex:
            print("Error while working with PostgreSQL: ", _ex)
            self.show_error_dialog('Ошибка при создании заказа')
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def calculate_cost(self, service):
        service_costs = {
            'order-1': 1000,
            'order-2': 2000,
            'order-3': 1500
        }
        return service_costs.get(service, 0)
   
    def generate_barcode(self, instance):
        tube_code = self.tube_code_input.text
        if not tube_code:
            self.show_error_dialog('Please enter the tube code.')
            return

        current_date = datetime.datetime.now().strftime('%Y%m%d')
        unique_id = f"{current_date}{tube_code.zfill(6)}"

        # Create folder for patient
        patient_folder = os.path.join('patients', self.patient_name_input.text)
        os.makedirs(patient_folder, exist_ok=True)

        pdf_filename_barcode = os.path.join(patient_folder, f"{unique_id}_barcode.pdf")
        self.create_pdf_with_barcode(unique_id, pdf_filename_barcode)

        self.create_order_pdf(patient_folder)  # Create PDF with order details

    def create_pdf_with_barcode(self, unique_id, pdf_filename):
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        barcode = code128.Code128(unique_id, barWidth=0.5 * mm, barHeight=20 * mm)
        barcode.drawOn(c, 100, 700)
        c.save()

    def create_order_pdf(self, patient_folder):
        file_name = os.path.join(patient_folder, f"{self.patient_name_input.text}_order.pdf")
        c = canvas.Canvas(file_name, pagesize=letter)
        c.drawString(100, 680, f"Order Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
        c.drawString(100, 660, f"Order Number: {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        c.drawString(100, 640, f"Tube Code: {self.tube_code_input.text}")
        c.drawString(100, 620, f"Insurance Number: {getattr(self, 'patient_insurance_number', '')}")
        c.drawString(100, 600, f"Full Name: {self.patient_name_input.text}")
        c.drawString(100, 580, f"Date of Birth: {getattr(self, 'date_of_birth', '')}")
        c.drawString(100, 560, f"Services: {self.service_input.text}")
        c.drawString(100, 540, f"Cost: {getattr(self, 'cost', '0')} tenge.")
        c.save()
    

    def show_error_dialog(self, message):
        popup = Popup(title='Ошибка',
                      content=Label(text=message),
                      size_hint=(None, None), size=(300, 200))
        popup.open()

