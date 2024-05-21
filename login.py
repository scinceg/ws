# login.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.app import App

class GradientBackground(Widget):
    def __init__(self, **kwargs):
        super(GradientBackground, self).__init__(**kwargs)
        with self.canvas:
            Color(0.0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

    def update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.gradient = GradientBackground()
        self.add_widget(self.gradient)

        self.anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        self.inner_layout = GridLayout(cols=1, padding=20, spacing=20, size_hint=(0.7, None))

        self.login_input = TextInput(hint_text="Login", multiline=False, height=30, size_hint_y=None)
        self.inner_layout.add_widget(self.login_input)
        
        self.password_input = TextInput(hint_text="Password", password=True, multiline=False, height=30, size_hint_y=None)
        self.inner_layout.add_widget(self.password_input)
        
        self.button_layout = BoxLayout(orientation='vertical', spacing=20, size_hint_y=None)
        self.button_layout.bind(minimum_height=self.button_layout.setter('height'))

        self.show_password_button = Button(text="Show", height=40, size_hint_y=None)
        self.show_password_button.bind(on_release=self.toggle_password_visibility)
        self.button_layout.add_widget(self.show_password_button)

        self.login_button = Button(text="Login", height=40, size_hint_y=None)
        self.login_button.bind(on_release=self.login)
        self.button_layout.add_widget(self.login_button)

        self.inner_layout.add_widget(self.button_layout)
        self.anchor_layout.add_widget(self.inner_layout)
        self.layout.add_widget(self.anchor_layout)
        self.add_widget(self.layout)

    def toggle_password_visibility(self, instance):
        self.password_input.password = not self.password_input.password
        self.show_password_button.text = 'Show' if self.password_input.password else 'Hide'

    def login(self, instance):
        app = App.get_running_app()
        app.login(self.login_input.text, self.password_input.text)
