from datetime import date
from decimal import Decimal

import storage

# Precisión de los montos: dos decimales
CENTS = Decimal("0.01")


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
