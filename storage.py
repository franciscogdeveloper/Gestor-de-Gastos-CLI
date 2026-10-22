import json

import os

from pathlib import Path

EXPENSES_FILE = Path("expenses.json")


# Guarda la lista de gastos en el archivo JSON
def save_expenses(expenses):
    # Se guarda en un archivo temporal
    temp_file = EXPENSES_FILE.with_suffix(".tmp")

    # Escribe los gastos en el archivo temporal con formato legible y acentos
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=2, ensure_ascii=False)

    # Reemplaza el archivo original por el temporal en un solo paso,
    # evitando que quede corrupto si el programa se interrumpe al escribir
    os.replace(temp_file, EXPENSES_FILE)


# Error al leer el archivo de gastos
class StorageError(Exception):
    pass


# Devuelve la lista de gastos; si el archivo no existe, lo crea vacío
def load_expenses():
    if not EXPENSES_FILE.exists():
        save_expenses([])
        return []

    # Lee el archivo; si el contenido no es JSON válido, lanza StorageError
    try:
        with open(EXPENSES_FILE, "r", encoding="utf-8") as file:
            expenses = json.load(file)
    except json.JSONDecodeError:
        raise StorageError(f"El archivo {EXPENSES_FILE} está dañado o no es un JSON válido.")

    # El archivo debe contener una lista de gastos
    if not isinstance(expenses, list):
        raise StorageError(f"El archivo {EXPENSES_FILE} no contiene una lista de gastos.")

    return expenses
