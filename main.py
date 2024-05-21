# main.py

import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.properties import StringProperty
import psycopg2

from config import host, user, password, db_name
from login import LoginScreen
from laborant import OrderFormScreen

# Установим размеры окна для разработки
Window.size = (320, 540)

class MainScreen(Screen):
    user_photo = StringProperty('user-icon.png')
    user_full_name = StringProperty('John Doe')
    user_role = StringProperty('Lab Technician')

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.user_photo_widget = Image(source=self.user_photo)
        self.layout.add_widget(self.user_photo_widget)
        
        self.user_full_name_label = Label(text=self.user_full_name, halign='center')
        self.layout.add_widget(self.user_full_name_label)
        
        self.user_role_label = Label(text=self.user_role, halign='center')
        self.layout.add_widget(self.user_role_label)
        
        self.add_widget(self.layout)

class WindowManager(ScreenManager):
    pass

class MyApp(App):
    def build(self):
        self.title = "Login App"
        self.sm = WindowManager()

        self.login_screen = LoginScreen(name='login')
        self.sm.add_widget(self.login_screen)

        self.main_screen = MainScreen(name='main')
        self.sm.add_widget(self.main_screen)

        self.order_form_screen = OrderFormScreen(name='order_form')
        self.sm.add_widget(self.order_form_screen)

        return self.sm

    def login(self, user_login, user_password):
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
            cursor.execute("SELECT staff_id, full_name, role FROM LaboratoryStaff WHERE username=%s AND password=%s", (user_login, user_password))
            result = cursor.fetchone()
            
            if result:
                staff_id, full_name, role = result
                if role == 'Lab Technician':
                    self.sm.current = 'order_form'
                else:
                    self.sm.current = 'main'
                self.main_screen.user_photo = 'user-icon.png'
                self.main_screen.user_full_name = full_name
                self.main_screen.user_role = role
                self.main_screen.user_photo_widget.source = self.main_screen.user_photo
                self.main_screen.user_full_name_label.text = self.main_screen.user_full_name
                self.main_screen.user_role_label.text = self.main_screen.user_role
            else:
                self.show_error_dialog()
                
        except Exception as _ex:
            print("Error while working with PostgreSQL: ", _ex)
            self.show_error_dialog()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def show_error_dialog(self):
        popup = Popup(title='Error',
                      content=Label(text='Invalid login or password.'),
                      size_hint=(None, None), size=(300, 200))
        popup.open()

if __name__ == '__main__':
    MyApp().run()
