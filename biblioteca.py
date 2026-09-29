#!/usr/bin/env python3
"""
Biblioteca Personal - Aplicación de consola para administrar libros.

Los datos se almacenan en una base de datos SQLite (biblioteca.db).
El programa está dividido en dos capas:
  1. Capa de datos: funciones que hablan con SQLite (crear, leer, actualizar, borrar).
  2. Capa de interfaz: funciones que muestran el menú y piden datos al usuario.
"""

import sqlite3

DB_NOMBRE = "biblioteca.db"

# Campos que el usuario puede editar o usar para buscar.
# Se usa una lista blanca para evitar inyección SQL en nombres de columna.
CAMPOS = {
    "1": ("titulo", "Título"),
    "2": ("autor", "Autor"),
    "3": ("genero", "Género"),
    "4": ("leido", "Estado de lectura"),
}


# ---------------------------------------------------------------------------
# CAPA DE DATOS
# ---------------------------------------------------------------------------

def conectar():
    """Abre una conexión a la base de datos."""
    return sqlite3.connect(DB_NOMBRE)


def crear_tabla():
    """Crea la tabla 'libros' si todavía no existe."""
    with conectar() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS libros (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor  TEXT NOT NULL,
                genero TEXT NOT NULL,
                leido  INTEGER NOT NULL DEFAULT 0  -- 0 = no leído, 1 = leído
            )
            """
        )


def agregar_libro(titulo, autor, genero, leido):
    """Inserta un libro nuevo y devuelve su id."""
    with conectar() as conn:
        cursor = conn.execute(
            "INSERT INTO libros (titulo, autor, genero, leido) VALUES (?, ?, ?, ?)",
            (titulo, autor, genero, leido),
        )
        return cursor.lastrowid


def obtener_libro(id_libro):
    """Devuelve la fila del libro con ese id, o None si no existe."""
    with conectar() as conn:
        return conn.execute(
            "SELECT id, titulo, autor, genero, leido FROM libros WHERE id = ?",
            (id_libro,),
        ).fetchone()


def listar_libros():
    """Devuelve todos los libros ordenados por título."""
    with conectar() as conn:
        return conn.execute(
            "SELECT id, titulo, autor, genero, leido FROM libros ORDER BY titulo COLLATE NOCASE"
        ).fetchall()


def actualizar_libro(id_libro, campo, valor):
    """Actualiza un campo del libro. Devuelve True si se modificó alguna fila."""
    columnas_validas = {c for c, _ in CAMPOS.values()}
    if campo not in columnas_validas:
        raise ValueError(f"Campo no válido: {campo}")
    with conectar() as conn:
        cursor = conn.execute(
            f"UPDATE libros SET {campo} = ? WHERE id = ?", (valor, id_libro)
        )
        return cursor.rowcount > 0


def eliminar_libro(id_libro):
    """Elimina un libro por id. Devuelve True si se eliminó."""
    with conectar() as conn:
        cursor = conn.execute("DELETE FROM libros WHERE id = ?", (id_libro,))
        return cursor.rowcount > 0


def buscar_libros(campo, texto):
    """Busca libros cuyo campo (titulo/autor/genero) contenga el texto dado."""
    if campo not in ("titulo", "autor", "genero"):
        raise ValueError(f"Campo de búsqueda no válido: {campo}")
    with conectar() as conn:
        return conn.execute(
            f"SELECT id, titulo, autor, genero, leido FROM libros "
            f"WHERE {campo} LIKE ? ORDER BY titulo COLLATE NOCASE",
            (f"%{texto}%",),
        ).fetchall()


# ---------------------------------------------------------------------------
# CAPA DE INTERFAZ (consola)
# ---------------------------------------------------------------------------

def pedir_texto(mensaje):
    """Pide un texto al usuario y repite hasta que no esté vacío."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("  ⚠ Este campo no puede estar vacío.")


def pedir_entero(mensaje):
    """Pide un número entero; devuelve None si el usuario no escribe un número."""
    try:
        return int(input(mensaje).strip())
    except ValueError:
        print("  ⚠ Debes escribir un número válido.")
        return None


def pedir_estado():
    """Pide el estado de lectura y lo devuelve como 1 (leído) o 0 (no leído)."""
    while True:
        r = input("¿Ya lo leíste? (s/n): ").strip().lower()
        if r in ("s", "si", "sí"):
            return 1
        if r in ("n", "no"):
            return 0
        print("  ⚠ Responde 's' o 'n'.")


def texto_estado(leido):
    """Convierte 0/1 en texto legible."""
    return "Leído" if leido else "No leído"


def mostrar_libros(libros):
    """Imprime una lista de libros en forma de tabla."""
    if not libros:
        print("\n  (No se encontraron libros)")
        return
    encabezado = f"{'ID':<4} {'Título':<30} {'Autor':<22} {'Género':<15} {'Estado':<9}"
    print("\n" + encabezado)
    print("-" * len(encabezado))
    for id_, titulo, autor, genero, leido in libros:
        print(f"{id_:<4} {titulo[:29]:<30} {autor[:21]:<22} {genero[:14]:<15} {texto_estado(leido):<9}")
    print(f"\nTotal: {len(libros)} libro(s)")


def opcion_agregar():
    """Opción 1: agregar un libro nuevo."""
    print("\n--- Agregar nuevo libro ---")
    titulo = pedir_texto("Título: ")
    autor = pedir_texto("Autor: ")
    genero = pedir_texto("Género: ")
    leido = pedir_estado()
    id_nuevo = agregar_libro(titulo, autor, genero, leido)
    print(f"✔ Libro agregado con ID {id_nuevo}.")


def opcion_actualizar():
    """Opción 2: modificar un campo de un libro existente."""
    print("\n--- Actualizar libro ---")
    mostrar_libros(listar_libros())
    id_libro = pedir_entero("\nID del libro a actualizar: ")
    if id_libro is None:
        return
    if obtener_libro(id_libro) is None:
        print("✘ No existe un libro con ese ID.")
        return

    print("\n¿Qué campo deseas modificar?")
    for clave, (_, etiqueta) in CAMPOS.items():
        print(f"  {clave}. {etiqueta}")
    eleccion = input("Opción: ").strip()
    if eleccion not in CAMPOS:
        print("✘ Opción no válida.")
        return

    columna, etiqueta = CAMPOS[eleccion]
    nuevo_valor = pedir_estado() if columna == "leido" else pedir_texto(f"Nuevo valor para {etiqueta}: ")
    if actualizar_libro(id_libro, columna, nuevo_valor):
        print("✔ Libro actualizado correctamente.")


def opcion_eliminar():
    """Opción 3: eliminar un libro (con confirmación)."""
    print("\n--- Eliminar libro ---")
    mostrar_libros(listar_libros())
    id_libro = pedir_entero("\nID del libro a eliminar: ")
    if id_libro is None:
        return
    libro = obtener_libro(id_libro)
    if libro is None:
        print("✘ No existe un libro con ese ID.")
        return
    confirmar = input(f"¿Seguro que deseas eliminar '{libro[1]}'? (s/n): ").strip().lower()
    if confirmar in ("s", "si", "sí"):
        eliminar_libro(id_libro)
        print("✔ Libro eliminado.")
    else:
        print("Operación cancelada.")


def opcion_listar():
    """Opción 4: mostrar todos los libros."""
    print("\n--- Listado de libros ---")
    mostrar_libros(listar_libros())


def opcion_buscar():
    """Opción 5: buscar por título, autor o género."""
    print("\n--- Buscar libros ---")
    print("  1. Título\n  2. Autor\n  3. Género")
    eleccion = input("Buscar por: ").strip()
    if eleccion not in ("1", "2", "3"):
        print("✘ Opción no válida.")
        return
    columna, etiqueta = CAMPOS[eleccion]
    texto = pedir_texto(f"{etiqueta} a buscar: ")
    mostrar_libros(buscar_libros(columna, texto))


def mostrar_menu():
    """Imprime el menú principal."""
    print("\n" + "=" * 34)
    print("   📚 BIBLIOTECA PERSONAL")
    print("=" * 34)
    print("  1. Agregar nuevo libro")
    print("  2. Actualizar un libro")
    print("  3. Eliminar un libro")
    print("  4. Ver listado de libros")
    print("  5. Buscar libros")
    print("  6. Salir")


def main():
    """Punto de entrada: prepara la base de datos y ejecuta el bucle del menú."""
    crear_tabla()
    acciones = {
        "1": opcion_agregar,
        "2": opcion_actualizar,
        "3": opcion_eliminar,
        "4": opcion_listar,
        "5": opcion_buscar,
    }
    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()
        if opcion == "6":
            print("\n¡Hasta pronto! 👋")
            break
        accion = acciones.get(opcion)
        if accion:
            accion()
        else:
            print("✘ Opción no válida. Elige un número del 1 al 6.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nPrograma terminado.")
