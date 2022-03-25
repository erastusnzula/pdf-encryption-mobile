import os

from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.utils import PdfReadError
from kivy.app import App
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from pdf_settings import settings_json


class MainWidget(BoxLayout):
    label_title = ObjectProperty()
    popup_button = ObjectProperty()
    settings_button = ObjectProperty()
    encrypt_button = ObjectProperty()
    exit_button = ObjectProperty()
    file_selected_label = ObjectProperty()
    encrypted_file_label = ObjectProperty()
    width_size = NumericProperty()
    popup = None
    basename = StringProperty('<Empty>')
    path = None
    password = None
    count = 0
    password_input = ObjectProperty()
    view_encrypted_files_button = ObjectProperty()

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.all_ = [self.label_title, self.popup_button, self.settings_button, self.encrypt_button,
                     self.exit_button, self.encrypted_file_label, self.password_input, self.view_encrypted_files_button]
        try:
            with open('font_name.txt', 'r') as f:
                font_name = f.read()

                for change in self.all_:
                    change.font_name = font_name
        except (AttributeError, OSError):
            pass
        try:
            with open('font_size.txt', 'r') as f:
                font_size = f.read()

                for i in self.all_:
                    i.font_size = font_size
        except (AttributeError, OSError):
            pass
        try:
            with open('color.txt', 'r') as f:
                color = f.read()
                self.change_color(color)
        except (AttributeError, OSError):
            pass

    def change_color(self, color):
        for i in self.all_:
            if color == 'red':
                i.color = 1, 0, 0
            elif color == 'red-green':
                i.color = 1, 1, 0
            elif color == 'green':
                i.color = 0, 1, 0
            elif color == 'white':
                i.color = 1, 1, 1
            elif color == 'black':
                i.color = 0, 0, 0

    def show_select_file_popup(self):
        show = FileChooserListView(filters=['*.pdf', ''])
        self.popup = Popup(title="Select File", content=show, size_hint=(None, None), size=(self.width, self.height))
        self.popup.open()
        show.on_submit = self.get_file_selected

    def get_file_selected(self, instance, *args):
        self.path = ''.join(instance)
        self.basename = os.path.basename(self.path)
        self.check_size()
        self.popup.dismiss()

    def check_size(self):
        if self.width_size < 630 and self.basename != '<Empty>' and self.path != '':
            self.file_selected_label.text = self.basename[:30] + "..."
        else:
            if self.basename != '<Empty>' and self.path != '':
                self.file_selected_label.text = self.basename

    def on_size(self, *args):
        try:
            self.check_size()
        except AttributeError:
            pass

    def encrypt_file(self, instance):
        try:
            if self.password:
                file = PdfFileReader(self.path)
                new_file = PdfFileWriter()
                pages = file.getNumPages()
                for page in range(pages):
                    new_file.addPage(file.getPage(page))
                new_file.encrypt(user_pwd=self.password, use_128bit=True)
                filename = os.path.join(self.path[:-len(self.basename)], 'Encrypted_' + self.basename)
                self.store_encrypted_file(filename)
                with open(filename, 'wb') as f:
                    new_file.write(f)
                    self.count += 1
                    self.encrypted_file_label.text = "Files encrypted : " + str(self.count)
                    self.password_input.text = ''
                    self.path = ''
                    self.file_selected_label.text = '<Empty>'

            else:
                self.error_popup('Password', "Password required!", )

        except PdfReadError:
            self.error_popup('File Encrypted', "File encrypted select another one")
        except (AttributeError, FileNotFoundError):
            self.error_popup('No file selected', "Please select a file")

    def close_popup(self, *args):
        self.popup.dismiss()

    def error_popup(self, title, message):
        box = BoxLayout(orientation='vertical')
        error = Label(text=message)
        close_button = Button(text="Close", on_press=self.close_popup)
        box.add_widget(error)
        box.add_widget(close_button)
        self.popup = Popup(title=title,
                           content=box,
                           size_hint=(None, None), size=(300, 250))
        self.popup.open()

    def store_encrypted_file(self, filename):
        with open('store.txt', 'a') as f:
            basename = os.path.basename(filename)
            if len(basename) > 25:
                f.write(f"\n{basename[:25]}...")
            else:
                f.write(f'\n{basename}')

    def view_encrypted_files(self):
        try:
            with open('store.txt', 'r') as f:
                box = BoxLayout(orientation='vertical')
                btn = BoxLayout()
                error = Label(text=f.read())
                close_button = Button(text="Close", on_press=self.close_popup, size_hint=(1, .2))
                delete_button = Button(text="Delete All", on_press=self.delete_files, size_hint=(1, .2))
                box.add_widget(error)
                btn.add_widget(close_button)
                btn.add_widget(delete_button)
                box.add_widget(btn)
                self.popup = Popup(title='Encrypted Files',
                                   content=box,
                                   size_hint=(None, None), size=(300, 500))
                self.popup.open()
        except FileNotFoundError:
            self.error_popup('Encrypted files', 'No stored encrypted files.')

    def delete_files(self, *args):
        open('store.txt', 'w').close()
        self.close_popup()
        self.error_popup('Delete', 'Files deleted successfully')
        self.count = 0
        self.encrypted_file_label.text = "Files encrypted : " + str(self.count)


class EncryptFilesApp(App):
    change_all = []

    def build(self):
        self.use_kivy_settings = False
        self.icon = 'logo.png'
        return MainWidget()

    def build_config(self, config):
        config.setdefaults('Settings', {
            'font_size': 20,
            'font_name': 'Sackers-Gothic-Std-Light.ttf',
            'color': 'white'
        })

    def build_settings(self, settings):
        settings.add_json_panel('Pdf Encryption', self.config, data=settings_json)

    def on_config_change(self, config, section, key, value):
        self.change_all = [self.root.ids.label_title, self.root.ids.popup_button, self.root.ids.settings_button,
                           self.root.ids.encrypt_button, self.root.ids.exit_button, self.root.ids.encrypted_file_label,
                           self.root.ids.view_encrypted_files_button, self.root.ids.password_input]
        font_name = self.config.get('Settings', 'font_name')
        font_size = self.config.get('Settings', 'font_size')
        color = self.config.get('Settings', 'color')
        self.change_color(color)
        self.change_font(font_name, font_size)

        with open('font_name.txt', 'w') as f:
            f.write(font_name)

        with open('font_size.txt', 'w') as f:
            f.write(font_size)

        with open('color.txt', 'w') as f:
            f.write(color)

    def change_color(self, color):
        for i in self.change_all:
            if color == 'red':
                i.color = 1, 0, 0
            elif color == 'red-green':
                i.color = 1, 1, 0
            elif color == 'green':
                i.color = 0, 1, 0
            elif color == 'white':
                i.color = 1, 1, 1
            elif color == 'black':
                i.color = 0, 0, 0

    def change_font(self, font_name, font_size):
        for i in self.change_all:
            i.font_name = font_name
            i.font_size = font_size


encrypt = EncryptFilesApp()

encrypt.run()
