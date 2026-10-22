import argparse
import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from decimal import Decimal

import expenses
import storage
from expense_tracker import main, parse_amount


# Cada test corre en una carpeta temporal vacía
class TempDirTestCase(unittest.TestCase):
    # Se ejecuta antes de cada test
    def setUp(self):
        self.original_dir = os.getcwd()
        self.temp_dir = tempfile.TemporaryDirectory()
        os.chdir(self.temp_dir.name)

    # Vuelve a la carpeta original y borra la temporal
    def tearDown(self):
        os.chdir(self.original_dir)
        self.temp_dir.cleanup()


class TestParseAmount(unittest.TestCase):
    # Acepta montos positivos con hasta dos decimales
    def test_valid_amounts(self):
        self.assertEqual(parse_amount("20"), Decimal("20"))
        self.assertEqual(parse_amount("10.50"), Decimal("10.50"))

    # Rechaza negativos, cero, texto, NaN, Infinity, más de dos decimales y montos enormes
    def test_invalid_amounts(self):
        for text in ["-5", "0", "abc", "NaN", "Infinity", "1.234", "9999999999"]:
            with self.subTest(text=text):
                with self.assertRaises(argparse.ArgumentTypeError):
                    parse_amount(text)


class TestExpenses(TempDirTestCase):
    # Guarda el gasto con la fecha de hoy y el monto con dos decimales
    def test_add_expense(self):
        expense = expenses.add_expense("Almuerzo", Decimal("20"))

        self.assertEqual(expense, {
            "id": 1,
            "date": date.today().isoformat(),
            "description": "Almuerzo",
            "amount": "20.00",
        })
        self.assertEqual(storage.load_expenses(), [expense])

    # No acepta descripciones vacías
    def test_add_expense_rejects_empty_description(self):
        with self.assertRaises(expenses.ExpenseError):
            expenses.add_expense("   ", Decimal("5"))

    # Suma todo, o solo el mes indicado del año actual
    def test_total_expenses_by_month(self):
        year = date.today().year
        expenses.add_expense("A", Decimal("10.10"), date(year, 3, 1))
        expenses.add_expense("B", Decimal("0.20"), date(year, 3, 31))
        expenses.add_expense("C", Decimal("5"), date(year, 4, 1))
        expenses.add_expense("D", Decimal("100"), date(year - 1, 3, 1))

        self.assertEqual(expenses.total_expenses(), Decimal("115.30"))
        self.assertEqual(expenses.total_expenses(3), Decimal("10.30"))
        self.assertEqual(expenses.total_expenses(12), Decimal("0.00"))

    # Cambia solo los campos indicados
    def test_update_expense(self):
        expenses.add_expense("Almuerzo", Decimal("20"))
        updated = expenses.update_expense(1, amount=Decimal("22.5"))

        self.assertEqual(updated["description"], "Almuerzo")
        self.assertEqual(updated["amount"], "22.50")

    # Exige al menos un campo para actualizar
    def test_update_expense_requires_a_field(self):
        expenses.add_expense("Almuerzo", Decimal("20"))

        with self.assertRaises(expenses.ExpenseError):
            expenses.update_expense(1)

    # Elimina solo el gasto indicado
    def test_delete_expense(self):
        expenses.add_expense("A", Decimal("1"))
        expenses.add_expense("B", Decimal("2"))
        expenses.delete_expense(1)

        self.assertEqual([expense["id"] for expense in expenses.list_expenses()], [2])

    # Update y delete fallan si el id no existe
    def test_missing_id_raises_error(self):
        with self.assertRaises(expenses.ExpenseError):
            expenses.update_expense(99, description="X")
        with self.assertRaises(expenses.ExpenseError):
            expenses.delete_expense(99)


class TestCli(TempDirTestCase):
    # Ejecuta la CLI y devuelve el código de salida y lo que imprimió
    def run_cli(self, *argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()

    # Flujo del enunciado: agregar, listar, resumir y eliminar
    def test_full_flow(self):
        self.assertEqual(self.run_cli("add", "--description", "Almuerzo", "--amount", "20")[0], 0)
        self.assertEqual(self.run_cli("add", "--description", "Cena", "--amount", "10")[0], 0)

        _, out, _ = self.run_cli("list")
        self.assertIn("Almuerzo", out)
        self.assertIn("$10.00", out)

        self.assertIn("Total de gastos: $30.00", self.run_cli("summary")[1])

        self.run_cli("delete", "--id", "2")
        self.assertIn("Total de gastos: $20.00", self.run_cli("summary")[1])

        month = date.today().month
        month_name = expenses.MONTHS[month - 1]
        _, out, _ = self.run_cli("summary", "--month", str(month))
        self.assertIn(f"Total de gastos de {month_name}: $20.00", out)

    # Los errores de uso los detecta argparse y terminan con código 2
    def test_usage_errors_exit_with_code_2(self):
        cases = [
            [],
            ["volar"],
            ["add", "--amount", "5"],
            ["add", "--description", "X", "--amount", "-5"],
            ["summary", "--month", "13"],
            ["delete", "--id", "abc"],
        ]
        for argv in cases:
            with self.subTest(argv=argv):
                # argparse llama a sys.exit(2), que lanza SystemExit
                with self.assertRaises(SystemExit) as context:
                    self.run_cli(*argv)
                self.assertEqual(context.exception.code, 2)

    # Los errores de la lógica y del archivo terminan con código 1
    def test_logic_errors_return_code_1(self):
        self.run_cli("add", "--description", "Almuerzo", "--amount", "20")

        self.assertEqual(self.run_cli("delete", "--id", "99")[0], 1)
        self.assertEqual(self.run_cli("update", "--id", "1")[0], 1)

        storage.EXPENSES_FILE.write_text("basura", encoding="utf-8")
        code, _, err = self.run_cli("list")
        self.assertEqual(code, 1)
        self.assertIn("dañado", err)
