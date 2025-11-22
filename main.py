from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
import sqlite3
import os
import hashlib
import matplotlib.pyplot as plt
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

Window.size = (400, 700)

class Database:
    def __init__(self, path="student.db"):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                password_hash TEXT,
                name TEXT,
                roll TEXT,
                sem TEXT,
                section TEXT,
                branch TEXT
            )
        """)
        self.conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_login(self, email, password):
        if not email or password is None:
            return None
        self.cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
        row = self.cursor.fetchone()
        if row and row["password_hash"] == self.hash_password(password):
            return dict(row)
        return None

    def verify_session(self, email, stored_hash):
        if not email or not stored_hash:
            return None
        self.cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
        row = self.cursor.fetchone()
        if row and row["password_hash"] == stored_hash:
            return dict(row)
        return None

    def get_student_by_email(self, email):
        if not email:
            return None
        self.cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None

    def save_details(self, data):
        email = data.get("email")
        if not email:
            return
        raw_pw = data.get("password", "")
        pw_hash = self.hash_password(raw_pw) if raw_pw is not None else ""
        existing = self.get_student_by_email(email)
        if existing:
            self.cursor.execute("""
                UPDATE students SET name = ?, roll = ?, sem = ?, section = ?, branch = ?, password_hash = ?
                WHERE email = ?
            """, (data.get("name",""), data.get("roll",""), data.get("sem",""), data.get("section",""), data.get("branch",""), pw_hash, email))
        else:
            self.cursor.execute("""
                INSERT INTO students (email, password_hash, name, roll, sem, section, branch)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (email, pw_hash, data.get("name",""), data.get("roll",""), data.get("sem",""), data.get("section",""), data.get("branch","")))
        self.conn.commit()

KV = '''
#:import MDDropdownMenu kivymd.uix.menu.MDDropdownMenu

MDNavigationLayout:
    id: nav_layout

    ScreenManager:
        id: screen_manager

        LoginScreen:
            name: "login"

        DetailsScreen:
            name: "details"

        HomeScreen:
            name: "home"

        LearningScreen:
            name: "learning"

        AssignmentScreen:
            name: "assignments"


    MDNavigationDrawer:
        id: nav_drawer
        MDBoxLayout:
            orientation: "vertical"
            padding: "20dp"
            spacing: "15dp"

            MDLabel:
                text: "MENU"
                font_style: "H5"
                bold: True
                size_hint_y: None
                height: "35dp"

            MDRectangleFlatButton:
                text: "Home"
                on_release:
                    app.root.ids.screen_manager.current = "home"
                    app.root.ids.nav_drawer.set_state("close")

            MDRectangleFlatButton:
                text: "My Learning"
                on_release:
                    app.root.ids.screen_manager.current = "learning"
                    app.root.ids.nav_drawer.set_state("close")

            MDRectangleFlatButton:
                text: "My Assignments"
                on_release:
                    app.root.ids.screen_manager.current = "assignments"
                    app.root.ids.nav_drawer.set_state("close")

            Widget:

            MDRectangleFlatButton:
                text: "Logout"
                on_release: app.logout()


<LoginScreen>:
    MDBoxLayout:
        orientation: "vertical"
        padding: "30dp"
        spacing: "18dp"

        MDTopAppBar:
            title: "Student Login"
            left_action_items: [['menu', lambda x: app.root.ids.nav_drawer.set_state("open")]]

        MDCard:
            orientation: "vertical"
            padding: "18dp"
            size_hint_y: None
            height: "360dp"
            radius: [16,16,16,16]
            elevation: 8

            MDLabel:
                text: "WELCOME TO MYCAMU"
                halign: "center"
                font_style: "H6"
                bold: True
                size_hint_y: None
                height: self.texture_size[1] + dp(8)

            MDTextField:
                id: college_name
                hint_text: "Select College"
                text: root.college
                on_focus: if self.focus: root.open_menu()

            MDTextField:
                id: email
                hint_text: "College Email"
                helper_text_mode: "on_focus"
                helper_text: "Enter your college email"

            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: "48dp"
                spacing: "8dp"

                MDTextField:
                    id: password
                    hint_text: "Password"
                    password: True
                    multiline: False
                    size_hint_x: 0.88

                MDIconButton:
                    id: pw_icon
                    icon: "eye-off"
                    pos_hint: {"center_y": 0.5}
                    on_release: root.toggle_password()

            Label:
                id: login_msg
                text: ""
                color: 1,0,0,1
                size_hint_y: None
                height: self.texture_size[1] + dp(6)

        MDRaisedButton:
            text: "Login"
            pos_hint: {"center_x": 0.5}
            md_bg_color: 0, 0.45, 1, 1
            on_release: root.do_login()


<DetailsScreen>:
    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "12dp"

        MDTopAppBar:
            title: "Enter Student Details"
            left_action_items: [['menu', lambda x: app.root.ids.nav_drawer.set_state("open")]]

        MDCard:
            orientation: "vertical"
            padding: "18dp"
            size_hint_y: None
            height: "420dp"
            radius: [12,12,12,12]
            elevation: 8

            MDLabel:
                text: "ENTER STUDENT DETAILS"
                font_style: "H6"
                halign: "center"
                bold: True

            MDTextField:
                id: name
                hint_text: "Name"
            MDTextField:
                id: roll
                hint_text: "Roll Number"
            MDTextField:
                id: sem
                hint_text: "Semester"
                text: "B"
            MDTextField:
                id: section
                hint_text: "Section"
            MDTextField:
                id: branch
                hint_text: "Branch"

        MDRaisedButton:
            text: "Continue"
            pos_hint: {"center_x": 0.5}
            md_bg_color: 0, 0.45, 1, 1
            on_release: root.go_home()


<HomeScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Home"
            left_action_items: [['menu', lambda x: app.root.ids.nav_drawer.set_state("open")]]

        MDScrollView:
            MDBoxLayout:
                id: content_box
                orientation: "vertical"
                spacing: "50dp"
                padding: "50dp"
                size_hint_y: None
                height: self.minimum_height

                MDLabel:
                    text: "Student Details"
                    font_style: "H6"
                    halign: "center"
                    bold: True
                    size_hint_y: None
                    height: self.texture_size[1] + dp(6)

                MDCard:
                    padding: "50dp"
                    elevation: 8
                    radius: [12,12,12,12]
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: "vertical"
                    spacing: "30dp"

                    MDLabel:
                        id: name_lbl
                        text: "Name: "
                        halign: "left"
                    MDLabel:
                        id: roll_lbl
                        text: "Roll No: "
                        halign: "left"
                    MDLabel:
                        id: sem_lbl
                        text: "Semester: "
                        halign: "left"
                    MDLabel:
                        id: section_lbl
                        text: "Section: "
                        halign: "left"
                    MDLabel:
                        id: branch_lbl
                        text: "Branch: "
                        halign: "left"

                MDLabel:
                    text: "Attendance Report"
                    font_style: "H6"
                    halign: "center"
                    bold: True

                MDCard:
                    radius: [12,12,12,12]
                    elevation: 8
                    size_hint_y: None
                    height: "320dp"
                    padding: "20dp"

                    BoxLayout:
                        id: graph_container
                        padding: "8dp"
                        size_hint: 1, 1


<LearningScreen>:
    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        MDTopAppBar:
            title: "My Learning"
            left_action_items: [['menu', lambda x: app.root.ids.nav_drawer.set_state("open")]]
        MDLabel:
            text: "No current courses"
            halign: "center"
            font_style: "H6"


<AssignmentScreen>:
    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        MDTopAppBar:
            title: "My Assignments"
            left_action_items: [['menu', lambda x: app.root.ids.nav_drawer.set_state("open")]]
        MDLabel:
            text: "No assignments"
            halign: "center"
            font_style: "H6"
'''

class LoginScreen(Screen):
    college = "Model Institute of Engineering and Technology, Jammu"
    def __init__(self, **kw):
        super().__init__(**kw)
        self.menu = None
        self.pw_visible = False

    def open_menu(self):
        if not self.menu:
            self.menu = MDDropdownMenu(
                caller=self.ids.college_name,
                items=[{"text": self.college, "on_release": self.set_college}],
                width_mult=4)
        self.menu.open()

    def set_college(self, *args):
        self.ids.college_name.text = self.college
        self.menu.dismiss()

    def toggle_password(self):
        self.pw_visible = not self.pw_visible
        self.ids.password.password = not self.pw_visible
        self.ids.pw_icon.icon = "eye" if self.pw_visible else "eye-off"

    def do_login(self):
        app = MDApp.get_running_app()
        db = app.db
        self.ids.login_msg.text = ""
        email = (self.ids.email.text or "").strip()
        password = (self.ids.password.text or "")
        if not email or not password:
            self.ids.login_msg.text = "Enter email and password."
            return
        student = db.verify_login(email, password)
        if student:
            app.student_data = student
            with open("session.txt", "w") as f:
                f.write(email + "|" + student.get("password_hash",""))
            app.root.ids.screen_manager.current = "home"
        else:
            existing = db.get_student_by_email(email)
            if existing:
                self.ids.login_msg.text = "Incorrect password."
            else:
                app.student_data = {"email": email, "password": password}
                app.root.ids.screen_manager.current = "details"

class DetailsScreen(Screen):
    def go_home(self):
        app = MDApp.get_running_app()
        db = app.db
        email = app.student_data.get("email", "")
        data = {
            "email": email,
            "password": app.student_data.get("password", ""),
            "name": self.ids.name.text or "",
            "roll": self.ids.roll.text or "",
            "sem": self.ids.sem.text or "B",
            "section": self.ids.section.text or "",
            "branch": self.ids.branch.text or ""
        }
        db.save_details(data)
        app.student_data = db.get_student_by_email(email)
        if app.student_data:
            with open("session.txt", "w") as f:
                f.write(email + "|" + app.student_data.get("password_hash",""))
        app.root.ids.screen_manager.current = "home"

class HomeScreen(Screen):
    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        data = app.student_data or {}
        self.ids.name_lbl.text = "Name: " + data.get("name", "")
        self.ids.roll_lbl.text = "Roll No: " + data.get("roll", "")
        self.ids.sem_lbl.text = "Semester: " + str(data.get("sem", ""))
        self.ids.section_lbl.text = "Section: " + data.get("section", "")
        self.ids.branch_lbl.text = "Branch: " + data.get("branch", "")
        self.load_chart()

    def load_chart(self):
        subjects = ["Maths", "Physics", "DSA", "Python", "EVS"]
        attendance = [95, 88, 92, 75, 82]
        if self.ids.graph_container.children:
            self.ids.graph_container.clear_widgets()
        fig, ax = plt.subplots(figsize=(4.8, 3.2))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        ax.bar(subjects, attendance)
        ax.set_ylim([0, 100])
        ax.set_ylabel("Attendance %")
        ax.set_title("Attendance Chart")
        canvas = FigureCanvasKivyAgg(fig)
        canvas.size_hint = (1, 1)
        self.ids.graph_container.add_widget(canvas)

class LearningScreen(Screen):
    pass

class AssignmentScreen(Screen):
    pass

class StudentApp(MDApp):
    student_data = {}
    db = None

    def build(self):
        self.db = Database()
        root = Builder.load_string(KV)
        if os.path.exists("session.txt"):
            try:
                with open("session.txt", "r") as f:
                    saved = f.read().strip().split("|")
                if len(saved) == 2:
                    email, pw_hash = saved
                    student = self.db.verify_session(email, pw_hash)
                    if student:
                        self.student_data = student
                        root.ids.screen_manager.current = "home"
            except Exception:
                pass
        return root

    def logout(self):
        if os.path.exists("session.txt"):
            try:
                os.remove("session.txt")
            except Exception:
                pass
        self.student_data = {}
        self.root.ids.screen_manager.current = "login"

if __name__ == "__main__":
    StudentApp().run()