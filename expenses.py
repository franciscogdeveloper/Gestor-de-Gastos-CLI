from datetime import date
from decimal import Decimal

import storage

# Precisión de los montos: dos decimales
CENTS = Decimal("0.01")

# Nombres de los meses para el resumen mensual
MONTHS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


# Error de la lógica de gastos
class ExpenseError(Exception):
    pass


# Crea un gasto, lo guarda y lo devuelve; si no se indica fecha, usa la de hoy
def add_expense(description, amount, expense_date=None):
    description = description.strip()
    if not description:
        raise ExpenseError("La descripción no puede estar vacía.")
    if amount <= 0:
        raise ExpenseError("El monto debe ser mayor que cero.")

    expenses = storage.load_expenses()
    new_id = max((expense["id"] for expense in expenses), default=0) + 1

    expense = {
        "id": new_id,
        "date": (expense_date or date.today()).isoformat(),
        "description": description,
        # Se guarda como texto con dos decimales para no perder precisión
        "amount": str(amount.quantize(CENTS)),
    }

    expenses.append(expense)
    storage.save_expenses(expenses)
    return expense


# Devuelve todos los gastos
def list_expenses():
    return storage.load_expenses()


# Suma los gastos; si se indica un mes, solo los de ese mes del año actual
def total_expenses(month=None):
    if month is not None and not 1 <= month <= 12:
        raise ExpenseError("El mes debe estar entre 1 y 12.")

    current_year = date.today().year
    total = Decimal("0")

    for expense in storage.load_expenses():
        expense_date = date.fromisoformat(expense["date"])
        # Omite los gastos de otros meses o de otros años
        if month is not None and (expense_date.year != current_year or expense_date.month != month):
            continue
        total += Decimal(expense["amount"])

    return total.quantize(CENTS)


# Busca un gasto por id; si no existe, lanza ExpenseError
def find_expense(expenses, expense_id):
    expense = next((expense for expense in expenses if expense["id"] == expense_id), None)
    if expense is None:
        raise ExpenseError(f"No existe un gasto con ID {expense_id}.")
    return expense


# Cambia la descripción, el monto o ambos; al menos uno es obligatorio
def update_expense(expense_id, description=None, amount=None):
    if description is None and amount is None:
        raise ExpenseError("Indica una nueva descripción o un nuevo monto.")

    expenses = storage.load_expenses()
    expense = find_expense(expenses, expense_id)

    if description is not None:
        description = description.strip()
        if not description:
            raise ExpenseError("La descripción no puede estar vacía.")
        expense["description"] = description

    if amount is not None:
        if amount <= 0:
            raise ExpenseError("El monto debe ser mayor que cero.")
        expense["amount"] = str(amount.quantize(CENTS))

    storage.save_expenses(expenses)
    return expense


# Elimina un gasto por id y devuelve el gasto eliminado
def delete_expense(expense_id):
    expenses = storage.load_expenses()
    expense = find_expense(expenses, expense_id)

    expenses.remove(expense)
    storage.save_expenses(expenses)
    return expense
