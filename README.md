# Gestor de Gastos CLI

Aplicación de línea de comandos para registrar tus gastos y ver cuánto llevas gastado en total o en un mes.
Los gastos se guardan en un archivo `expenses.json` en el directorio actual, que se crea automáticamente si no existe.

Hecha solo con la librería estándar de Python (sin dependencias externas), como parte del
[proyecto Expense Tracker de roadmap.sh](https://roadmap.sh/projects/expense-tracker).

## Requisitos

- Python 3 (probado con Python 3.15)

## Uso

```bash
# Agregar un gasto
python expense_tracker.py add --description "Almuerzo" --amount 20

# Actualizar un gasto (la descripción, el monto o ambos)
python expense_tracker.py update --id 1 --amount 22.50

# Eliminar un gasto
python expense_tracker.py delete --id 1

# Listar los gastos
python expense_tracker.py list

# Total de todos los gastos
python expense_tracker.py summary

# Total de un mes del año actual (1-12)
python expense_tracker.py summary --month 8

# Ayuda general o de un comando
python expense_tracker.py --help
python expense_tracker.py add --help
```

Ejemplo:

```
$ python expense_tracker.py list
ID  Fecha       Descripción           Monto
1   2026-10-21  Almuerzo             $22.00
2   2026-10-21  Cena                 $10.50

$ python expense_tracker.py summary --month 10
Total de gastos de octubre: $32.50
```
## Formato de un gasto

```json
{
  "id": 1,
  "date": "2026-10-21",
  "description": "Almuerzo",
  "amount": "22.00"
}
```

El monto se guarda como texto y se calcula con `Decimal`, no con `float`,
para que las sumas de dinero sean exactas (por ejemplo, `0.10 + 0.20` da `0.30`).

## Errores y códigos de salida

| Código | Significado | Ejemplos |
|---|---|---|
| `0` | Todo salió bien | |
| `1` | El comando es válido, pero no se pudo completar | ID inexistente, `update` sin campos, descripción vacía, `expenses.json` dañado |
| `2` | El comando está mal escrito (lo detecta `argparse`) | Falta `--amount`, monto negativo, cero, con más de dos decimales o no numérico, mes fuera de 1-12 |

## Tests

```bash
python -m unittest -v
```

Los tests corren en una carpeta temporal, así que no modifican tu `expenses.json`.

## Estructura del proyecto

```
expense_tracker.py        # Interfaz de línea de comandos con argparse y validación del monto
expenses.py               # Lógica: agregar, actualizar, eliminar, listar y totalizar gastos
storage.py                # Lectura y escritura de expenses.json
test_expense_tracker.py   # Tests de la validación, la lógica y la CLI
```

## Próximas funciones

- [ ] Categorías y filtro por categoría
- [ ] Presupuesto mensual con advertencia al superarlo
- [ ] Exportar los gastos a CSV
