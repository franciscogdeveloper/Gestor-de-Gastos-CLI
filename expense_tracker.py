import argparse
import sys
from decimal import Decimal, InvalidOperation

import expenses
import storage

# Monto máximo aceptado por gasto
MAX_AMOUNT = Decimal("1000000000")


# Convierte el texto del monto a Decimal; si no es válido, argparse muestra el error
def parse_amount(text):
    try:
        amount = Decimal(text)
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f"'{text}' no es un monto válido.")

    # Rechaza NaN, Infinity, cero y negativos
    if not amount.is_finite() or amount <= 0:
        raise argparse.ArgumentTypeError("el monto debe ser un número mayor que cero.")
    if amount > MAX_AMOUNT:
        raise argparse.ArgumentTypeError("el monto es demasiado grande.")

    # Quita los ceros finales: 1.230 -> 1.23; el exponente indica los decimales
    if amount.normalize().as_tuple().exponent < -2:
        raise argparse.ArgumentTypeError("el monto no puede tener más de dos decimales.")

    return amount


def cmd_add(args):
    expense = expenses.add_expense(args.description, args.amount)
    print(f"Gasto agregado correctamente (ID: {expense['id']})")


# Define los subcomandos, sus opciones y la función que ejecuta cada uno
def build_parser():
    parser = argparse.ArgumentParser(prog="python expense_tracker.py", description="Gestor de gastos")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Agrega un gasto")
    add_parser.add_argument("--description", required=True, help="Descripción del gasto")
    add_parser.add_argument("--amount", type=parse_amount, required=True, help="Monto del gasto")
    add_parser.set_defaults(handler=cmd_add)

    return parser


def main(argv):
    # Si los argumentos no son válidos, argparse muestra el error y termina con código 2
    args = build_parser().parse_args(argv)

    # Muestra los errores de la lógica y del archivo como un mensaje limpio
    try:
        args.handler(args)
    except (expenses.ExpenseError, storage.StorageError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
