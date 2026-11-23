
# ==========================================
# POCKET CALCULATOR - KIVY
# ==========================================

# IMPORTS
import ast
import operator
import math

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.graphics import Color, Ellipse


# ==========================================
# COLOURS
# ==========================================

BLACK = (0.02, 0.02, 0.02, 1)
DARK_GREY = (0.32, 0.32, 0.32, 1)
LIGHT_GREY = (0.65, 0.65, 0.65, 1)
ORANGE = (1, 0.62, 0.04, 1)
WHITE = (1, 1, 1, 1)


# ==========================================
# ROUND BUTTON CLASS
# ==========================================

class RoundButton(Button):

    def __init__(self, bg, fg=WHITE, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self.color = fg
        self.font_size = sp(25)
        self.bold = False

        with self.canvas.before:
            Color(*bg)
            self.shape = Ellipse(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.update_shape,
            size=self.update_shape
        )

    def update_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size


# ==========================================
# CALCULATOR CLASS
# ==========================================

class Calculator(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            size_hint=(None, None),
            size=(dp(340), dp(570)),
            padding=dp(16),
            spacing=dp(10),
            **kwargs
        )

        self.expression = ""
        self.just_calculated = False

        # DISPLAY
        self.display = Label(
            text="0",
            color=WHITE,
            font_size=sp(52),
            halign="right",
            valign="center",
            size_hint_y=0.28,
            shorten=True,
            shorten_from="left"
        )

        self.add_widget(self.display)

        # BUTTON ROWS
        rows = [

            [
                ("AC", LIGHT_GREY, BLACK),
                ("+/-", LIGHT_GREY, BLACK),
                ("%", LIGHT_GREY, BLACK),
                ("÷", ORANGE, WHITE)
            ],

            [
                ("7", DARK_GREY, WHITE),
                ("8", DARK_GREY, WHITE),
                ("9", DARK_GREY, WHITE),
                ("×", ORANGE, WHITE)
            ],

            [
                ("4", DARK_GREY, WHITE),
                ("5", DARK_GREY, WHITE),
                ("6", DARK_GREY, WHITE),
                ("−", ORANGE, WHITE)
            ],

            [
                ("1", DARK_GREY, WHITE),
                ("2", DARK_GREY, WHITE),
                ("3", DARK_GREY, WHITE),
                ("+", ORANGE, WHITE)
            ]

        ]

        for row in rows:
            self.add_button_row(row)

        # BOTTOM BUTTON ROW
        bottom = BoxLayout(
            spacing=dp(10),
            size_hint_y=1
        )

        for value, bg, fg in [
            ("0", DARK_GREY, WHITE),
            (".", DARK_GREY, WHITE),
            ("=", ORANGE, WHITE)
        ]:

            button = RoundButton(
                bg,
                fg,
                text=value
            )

            button.bind(on_press=self.button_click)
            bottom.add_widget(button)

        self.add_widget(bottom)

    # ======================================
    # CREATE BUTTON ROWS
    # ======================================

    def add_button_row(self, buttons):

        row = BoxLayout(
            spacing=dp(10),
            size_hint_y=1
        )

        for value, bg, fg in buttons:

            button = RoundButton(
                bg,
                fg,
                text=value
            )

            button.bind(on_press=self.button_click)
            row.add_widget(button)

        self.add_widget(row)

    # ======================================
    # SAFE CALCULATION
    # ======================================

    def calculate(self, expression):

        operations = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv
        }

        def evaluate(node):

            if isinstance(node, ast.Constant):

                if type(node.value) in (int, float):
                    return node.value

            if isinstance(node, ast.BinOp):

                operation = operations.get(type(node.op))

                if operation is None:
                    raise ValueError("Invalid operation")

                return operation(
                    evaluate(node.left),
                    evaluate(node.right)
                )

            if isinstance(node, ast.UnaryOp):

                number = evaluate(node.operand)

                if isinstance(node.op, ast.USub):
                    return -number

                if isinstance(node.op, ast.UAdd):
                    return number

            raise ValueError("Invalid expression")

        tree = ast.parse(expression, mode="eval")
        result = evaluate(tree.body)

        if not math.isfinite(result):
            raise ValueError("Invalid result")

        return result

    # ======================================
    # FORMAT RESULTS
    # ======================================

    def format_number(self, number):

        if isinstance(number, float) and number.is_integer():
            return str(int(number))

        return f"{number:.10g}"

    # ======================================
    # BUTTON CLICK FUNCTION
    # ======================================

    def button_click(self, instance):

        value = instance.text

        # CLEAR
        if value == "AC":

            self.expression = ""
            self.just_calculated = False

        # PLUS OR MINUS
        elif value == "+/-":

            try:

                if self.expression:

                    expression = (
                        self.expression
                        .replace("−", "-")
                        .replace("×", "*")
                        .replace("÷", "/")
                    )

                    result = self.calculate(expression)

                    self.expression = self.format_number(-result)

            except Exception:
                self.expression = "Error"

        # PERCENTAGE
        elif value == "%":

            try:

                if self.expression:

                    expression = (
                        self.expression
                        .replace("−", "-")
                        .replace("×", "*")
                        .replace("÷", "/")
                    )

                    result = self.calculate(expression)

                    self.expression = self.format_number(result / 100)

            except Exception:
                self.expression = "Error"

        # EQUALS
        elif value == "=":

            try:

                expression = (
                    self.expression
                    .replace("−", "-")
                    .replace("×", "*")
                    .replace("÷", "/")
                )

                result = self.calculate(expression)

                self.expression = self.format_number(result)
                self.just_calculated = True

            except Exception:
                self.expression = "Error"

        # OPERATORS
        elif value in ["+", "−", "×", "÷"]:

            if self.expression == "Error":
                self.expression = ""

            if self.expression and self.expression[-1] in "+−×÷":
                self.expression = self.expression[:-1]

            if self.expression:
                self.expression += value

            self.just_calculated = False

        # NUMBERS AND DECIMALS
        else:

            if self.expression == "Error":
                self.expression = ""

            if self.just_calculated:

                self.expression = ""
                self.just_calculated = False

            if value == ".":

                current = self.expression

                for symbol in "+−×÷":
                    current = current.replace(symbol, " ")

                if "." in current.split(" ")[-1]:
                    return

            self.expression += value

        # UPDATE DISPLAY
        self.display.text = self.expression or "0"


# ==========================================
# MAIN APPLICATION
# ==========================================

class CalculatorApp(App):

    def build(self):

        Window.size = (390, 700)
        Window.minimum_width = 360
        Window.minimum_height = 650
        Window.clearcolor = (0.12, 0.12, 0.12, 1)

        screen = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(10)
        )

        screen.add_widget(
            Label(size_hint_y=0.15)
        )

        screen.add_widget(Calculator())

        screen.add_widget(
            Label(size_hint_y=0.15)
        )

        return screen


# ==========================================
# RUN CALCULATOR
# ==========================================

if __name__ == "__main__":
    CalculatorApp().run()
