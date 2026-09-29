# 📚 Biblioteca Personal (CLI)

Aplicación de línea de comandos en Python para administrar una biblioteca personal. Los libros se guardan en una base de datos **SQLite**, por lo que la información persiste entre ejecuciones.

## Descripción

Permite registrar libros con su **título, autor, género y estado de lectura** (leído / no leído) y realizar las operaciones básicas de una base de datos (CRUD):

| Opción | Funcionalidad |
|--------|---------------|
| 1 | Agregar nuevo libro |
| 2 | Actualizar cualquier campo de un libro (incluido el estado de lectura) |
| 3 | Eliminar un libro (con confirmación) |
| 4 | Ver el listado completo de libros |
| 5 | Buscar por título, autor o género (coincidencia parcial) |
| 6 | Salir |

## Requisitos

- Python 3.7 o superior
- No requiere instalar librerías externas (`sqlite3` viene incluida con Python)

## Instrucciones de ejecución

```bash
# 1. Clona el repositorio
git clone <url-de-tu-repositorio>
cd <carpeta-del-repositorio>

# 2. Ejecuta la aplicación
python biblioteca.py
```

La primera vez que se ejecute se creará automáticamente el archivo `biblioteca.db` con la tabla `libros`.

## Estructura del proyecto

```
.
├── biblioteca.py   # Código de la aplicación
├── biblioteca.db   # Base de datos (se genera al ejecutar)
└── README.md
```

### Diseño del código

- **Capa de datos**: `crear_tabla`, `agregar_libro`, `listar_libros`, `actualizar_libro`, `eliminar_libro`, `buscar_libros`. Usan consultas parametrizadas (`?`) para evitar inyección SQL.
- **Capa de interfaz**: funciones `opcion_*` y `mostrar_menu`, que piden datos al usuario y validan la entrada.

### Esquema de la tabla

```sql
CREATE TABLE libros (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor  TEXT NOT NULL,
    genero TEXT NOT NULL,
    leido  INTEGER NOT NULL DEFAULT 0   -- 0 = no leído, 1 = leído
);
```

## Captura del programa en uso

*(Opcional: agrega aquí una captura de pantalla)*

```
==================================
   📚 BIBLIOTECA PERSONAL
==================================
  1. Agregar nuevo libro
  2. Actualizar un libro
  3. Eliminar un libro
  4. Ver listado de libros
  5. Buscar libros
  6. Salir
Elige una opción:
```
