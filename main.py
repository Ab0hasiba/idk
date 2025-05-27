from kivy.lang import Builder
from kivy.properties import ColorProperty
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.scrollview import ScrollView

KV = '''
MDBoxLayout:
    orientation: 'vertical'
    md_bg_color: app.bg_color

    MDTopAppBar:
        title: "GPA/CGPA Calculator"
        right_action_items: [["theme-light-dark", lambda x: app.toggle_theme()]]
        md_bg_color: app.primary_color
        specific_text_color: app.bg_color

    MDTabs:
        id: tabs
        on_tab_switch: app.on_tab_switch(*args)

<GPATab>:
    orientation: "vertical"
    padding: 10
    spacing: 10
    md_bg_color: app.bg_color

    ScrollView:
        MDBoxLayout:
            id: subject_container
            orientation: "vertical"
            adaptive_height: True
            spacing: 10

    MDRaisedButton:
        text: "Add Subject"
        md_bg_color: app.accent_color
        text_color: app.bg_color
        on_release: app.add_subject_fields()

    MDRaisedButton:
        text: "Calculate GPA"
        md_bg_color: app.primary_color
        text_color: app.bg_color
        on_release: app.calculate_gpa()

    MDLabel:
        id: gpa_result
        text: "GPA: "
        halign: "center"
        theme_text_color: "Custom"
        text_color: app.text_color

<CGPATab>:
    orientation: "vertical"
    padding: 10
    spacing: 10
    md_bg_color: app.bg_color

    MDRaisedButton:
        text: "Add GPA"
        md_bg_color: app.accent_color
        text_color: app.bg_color
        on_release: app.add_manual_gpa()

    ScrollView:
        MDLabel:
            id: cgpa_result
            text: "CGPA History:"
            halign: "center"
            theme_text_color: "Custom"
            text_color: app.text_color
            size_hint_y: None
            height: self.texture_size[1]
'''

class GPATab(MDBoxLayout, MDTabsBase):
    pass

class CGPATab(MDBoxLayout, MDTabsBase):
    pass

class GPAApp(MDApp):
    # Theme colors (will update dynamically)
    bg_color = ColorProperty()
    text_color = ColorProperty()
    accent_color = ColorProperty()
    primary_color = ColorProperty()

    # Color palettes
    MOCHA = {
        "bg": "#1e1e2e",
        "text": "#cdd6f4",
        "accent": "#89dceb",
        "primary": "#b4befe"
    }
    LATTE = {
        "bg": "#eff1f5",
        "text": "#4c4f69",
        "accent": "#209fb5",
        "primary": "#1e66f5"
    }

    cgpa_list = []

    def build(self):
        self.theme_mode = "Mocha"
        self.apply_theme(self.MOCHA)
        self.root = Builder.load_string(KV)
        self.gpa_tab = GPATab(title="GPA")
        self.cgpa_tab = CGPATab(title="CGPA")
        self.root.ids.tabs.add_widget(self.gpa_tab)
        self.root.ids.tabs.add_widget(self.cgpa_tab)
        self.add_subject_fields()
        return self.root

    def apply_theme(self, theme_dict):
        self.bg_color = self.hex_to_rgba(theme_dict["bg"])
        self.text_color = self.hex_to_rgba(theme_dict["text"])
        self.accent_color = self.hex_to_rgba(theme_dict["accent"])
        self.primary_color = self.hex_to_rgba(theme_dict["primary"])

    def toggle_theme(self):
        if self.theme_mode == "Mocha":
            self.theme_mode = "Latte"
            self.apply_theme(self.LATTE)
            self.theme_cls.theme_style = "Light"
        else:
            self.theme_mode = "Mocha"
            self.apply_theme(self.MOCHA)
            self.theme_cls.theme_style = "Dark"

    def hex_to_rgba(self, hex_color, alpha=1):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16)/255. for i in (0, 2, 4)] + [alpha]

    def add_subject_fields(self):
        container = self.gpa_tab.ids.subject_container
        subject_layout = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=50)
        grade_input = MDTextField(hint_text="Grade (e.g. 4.0)", input_filter="float", size_hint_x=0.5)
        credit_input = MDTextField(hint_text="Credits", input_filter="int", size_hint_x=0.5)
        subject_layout.add_widget(grade_input)
        subject_layout.add_widget(credit_input)
        container.add_widget(subject_layout)

    def calculate_gpa(self):
        container = self.gpa_tab.ids.subject_container
        total_credits = 0
        total_weighted = 0

        for subject in container.children:
            grade_field, credit_field = subject.children[::-1]
            try:
                grade = float(grade_field.text)
                credits = int(credit_field.text)
                total_weighted += grade * credits
                total_credits += credits
            except (ValueError, AttributeError):
                Snackbar(text="Please enter valid grades and credits.").open()
                return

        try:
            gpa = total_weighted / total_credits
        except ZeroDivisionError:
            Snackbar(text="Total credits cannot be zero.").open()
            return

        self.gpa_tab.ids.gpa_result.text = f"GPA: {gpa:.2f}"

    def add_manual_gpa(self):
        self.manual_gpa_field = MDTextField(hint_text="Enter GPA (e.g. 3.5)", input_filter="float")
        self.manual_gpa_field.text = ""

        self.dialog = MDDialog(
            title="Add GPA",
            type="custom",
            content_cls=self.manual_gpa_field,
            buttons=[
                MDRaisedButton(text="Add", md_bg_color=self.accent_color, on_release=self.save_manual_gpa),
                MDRaisedButton(text="Cancel", md_bg_color=self.primary_color, on_release=lambda x: self.dialog.dismiss())
            ],
        )
        self.dialog.open()

    def save_manual_gpa(self, instance):
        try:
            gpa = float(self.manual_gpa_field.text)
            self.cgpa_list.append(gpa)
            cgpa = sum(self.cgpa_list) / len(self.cgpa_list)
            self.cgpa_tab.ids.cgpa_result.text = (
                f"CGPA History:\n{', '.join(f'{g:.2f}' for g in self.cgpa_list)}\n\nCurrent CGPA: {cgpa:.2f}"
            )
            self.dialog.dismiss()
        except ValueError:
            Snackbar(text="Please enter a valid GPA.").open()

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        pass

if __name__ == '__main__':
    GPAApp().run()
