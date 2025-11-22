from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
import sqlite3
import os
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
                password TEXT,
                name TEXT,
                roll TEXT,
                sem TEXT,
                section TEXT,
                branch TEXT
            )
        """)
        self.conn.commit()

    def verify_login(self, email, password):
        if not email:
            return None
        self.cursor.execute("SELECT * FROM students WHERE email = ? AND password = ?", (email, password))
        row = self.cursor.fetchone()
        if row:
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
        existing = self.get_student_by_email(email)
        if existing:
            self.cursor.execute("""
                UPDATE students SET name = ?, roll = ?, sem = ?, section = ?, branch = ?
                WHERE email = ?
            """, (data.get("name"), data.get("roll"), data.get("sem"), data.get("section"), data.get("branch"), email))
        else:
            self.cursor.execute("""
                INSERT INTO students (email, password, name, roll, sem, section, branch)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (email, data.get("password", ""), data.get("name"), data.get("roll"), data.get("sem"),
                  data.get("section"), data.get("branch")))
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
        padding: "20dp"
        spacing: "10dp"

        MDTopAppBar:
            title: "Student Login"
            left_action_items: [['menu', lambda x: app.root.ids.nav_drawer.set_state("open")]]

        MDCard:
            orientation: "vertical"
            padding: "20dp"
            size_hint_y: None
            height: "300dp"
            radius: [20,20,20,20]
            elevation: 8

            MDLabel:
                text: "WELCOME TO MYCAMU"
                halign: "center"
                font_style: "H6"
                bold: True

            MDTextField:
                id: college_name
                hint_text: "Select College"
                text: root.college
                on_focus: if self.focus: root.open_menu()

            MDTextField:
                id: email
                hint_text: "College Email"

            MDTextField:
                id: password
                hint_text: "Password"
                password: True

        MDRaisedButton:
            text: "Login"
            pos_hint: {"center_x": 0.5}
            md_bg_color: 0, 0.45, 1, 1
            on_release: root.do_login()


<DetailsScreen>:
    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"

        MDTopAppBar:
            title: "Enter Student Details"
            left_action_items: [['menu', lambda x: app.root.ids.nav_drawer.set_state("open")]]

        MDCard:
            orientation: "vertical"
            padding: "20dp"
            size_hint_y: None
            height: "420dp"
            radius: [20,20,20,20]
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
                spacing: "70dp"
                padding: "40dp"
                size_hint_y: None
                height: self.minimum_height

                MDLabel:
                    text: "Student Details"
                    font_style: "H5"
                    halign: "center"
                    bold: True

                MDCard:
                    padding: "100dp"
                    elevation: 40
                    radius: [20,20,20,20]
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: "vertical"
                    spacing: "50dp"

                    MDLabel:
                        id: name_lbl
                        text: "Name:"
                        halign: "left"

                    MDLabel:
                        id: roll_lbl
                        text: "Roll No:"
                        halign: "left"

                    MDLabel:
                        id: sem_lbl
                        text: "Semester:"
                        halign: "left"

                    MDLabel:
                        id: section_lbl
                        text: "Section:"
                        halign: "left"

                    MDLabel:
                        id: branch_lbl
                        text: "Branch:"
                        halign: "left"

                MDLabel:
                    text: "Attendance Report"
                    font_style: "H6"
                    halign: "center"
                    bold: True

                MDCard:
                    radius: [20,20,20,20]
                    elevation: 12
                    size_hint_y: None
                    height: "350dp"
                    padding: "15dp"

                    BoxLayout:
                        id: graph_container
                        padding: "10dp"
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
    def _init_(self, **kw):
        super()._init_(**kw)
        self.menu = None

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

    def do_login(self):
        app = MDApp.get_running_app()
        db = app.db
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()
        student = db.verify_login(email, password)
        if student:
            app.student_data = student
            with open("session.txt", "w") as f:
                f.write(email)
            app.root.ids.screen_manager.current = "home"
        else:
            existing = db.get_student_by_email(email)
            if existing:
                app.student_data = existing
                with open("session.txt", "w") as f:
                    f.write(email)
                app.root.ids.screen_manager.current = "home"
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
            "name": self.ids.name.text,
            "roll": self.ids.roll.text,
            "sem": self.ids.sem.text,
            "section": self.ids.section.text,
            "branch": self.ids.branch.text
        }
        db.save_details(data)
        app.student_data = db.get_student_by_email(email)
        with open("session.txt", "w") as f:
            f.write(email)
        app.root.ids.screen_manager.current = "home"


class HomeScreen(Screen):
    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        data = app.student_data
        self.ids.name_lbl.text = "Name: " + data.get("name", "")
        self.ids.roll_lbl.text = "Roll No: " + data.get("roll", "")
        self.ids.sem_lbl.text = "Semester: " + data.get("sem", "")
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
            with open("session.txt", "r") as f:
                email = f.read().strip()
            if email:
                student = self.db.get_student_by_email(email)
                if student:
                    self.student_data = student
                    root.ids.screen_manager.current = "home"
        return root

    def logout(self):
        if os.path.exists("session.txt"):
            os.remove("session.txt")
        self.student_data = {}
        self.root.ids.screen_manager.current = "login"


if __name__ == "__main__":
    StudentApp().run()