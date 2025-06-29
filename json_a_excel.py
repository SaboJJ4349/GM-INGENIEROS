import json
import pandas as pd

# Cargar el JSON generado previamente
with open("tareas_sin_subtareas.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Lista para almacenar filas planas
filas = []

# Navegar por la estructura anidada
for carpeta, listas in data["Administración y Sistemas"].items():
    for lista, estados in listas.items():
        for estado, tareas in estados.items():
            for tarea in tareas:
                filas.append({
                    "Carpeta": carpeta,
                    "Lista": lista,
                    "Estado": estado,
                    "Nombre de tarea": tarea["nombre"],
                    "Asignados": ", ".join(tarea["asignados"]),
                    "Fecha inicio": tarea.get("fecha_inicio"),
                    "Fecha límite": tarea.get("fecha_limite"),
                    "Prioridad": tarea.get("prioridad")
                })

# Crear DataFrame
df = pd.DataFrame(filas)

# Guardar como Excel
df.to_excel("tareas_clickup.xlsx", index=False)

print("✅ Archivo 'tareas_clickup.xlsx' creado con éxito.")
