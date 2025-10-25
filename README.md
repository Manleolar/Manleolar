# Generador de facturas para Agrícola León Lara S.C.

Hola :)

Bienvenido al GitHub de Manuel León Lara.

Este repositorio contiene una pequeña aplicación de escritorio hecha con Python y Tkinter para generar facturas de Agrícola León Lara S.C. Permite introducir los datos del cliente, las líneas de la factura y exportar el resultado a PDF con el formato corporativo.

## Características destacadas

- Interfaz moderna con cabecera corporativa, tarjetas y campos estilizados para que introducir datos resulte más agradable.
- Panel de totales con tarjetas dinámicas que recalculan automáticamente la base imponible, IVA, retención y total de la factura.
- Exportación profesional a PDF con maquetación optimizada para que los textos largos respeten los márgenes y se distribuyan correctamente.

## Requisitos

- Python 3.10 o superior (solo necesario para preparar el entorno y generar el ejecutable).
- [Pip](https://pip.pypa.io/en/stable/) para instalar dependencias.
- Dependencias Python incluidas en `requirements.txt` (`reportlab`).

## Cómo ejecutar la aplicación en modo desarrollo

1. Crear y activar un entorno virtual (opcional, pero recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows usar: .venv\Scripts\activate
   ```
2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar la aplicación:
   ```bash
   python -m invoice_app.main
   ```

## Cómo generar una factura

1. Introduce los datos de la factura (número, fecha y campaña o concepto).
2. Completa los datos del cliente (nombre, NIF/CIF, dirección, etc.).
3. Añade las líneas de factura rellenando cantidad, descripción y precio unitario. Pulsa **Añadir línea** por cada concepto. Puedes eliminar líneas seleccionándolas y usando **Eliminar seleccionada**.
4. Revisa los tipos de IVA y retención IRPF; la base imponible y los totales se recalculan automáticamente.
5. Pulsa **Exportar a PDF** y elige una carpeta donde guardar el documento.

## Crear un ejecutable para Windows (sin necesidad de tener Python instalado)

1. En un PC con Windows instala Python 3.10+ desde [python.org](https://www.python.org/downloads/). Es necesario solo para preparar el ejecutable.
2. Descarga este repositorio (ZIP o `git clone`).
3. Abre **PowerShell** o **Símbolo del sistema** en la carpeta del proyecto.
4. (Opcional) Crea y activa un entorno virtual:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
5. Instala las dependencias y PyInstaller:
   ```powershell
   pip install -r requirements.txt pyinstaller
   ```
6. Genera el ejecutable:
   ```powershell
   pyinstaller --noconsole --onefile --name "GeneradorFacturasAgricolaLeonLara" invoice_app\main.py
   ```

   - El ejecutable final aparecerá en la carpeta `dist` con el nombre `GeneradorFacturasAgricolaLeonLara.exe`.
   - Puedes copiar ese archivo a cualquier ordenador con Windows (no es necesario tener Python instalado) y ejecutarlo con doble clic.

7. Para facilitar la distribución, copia también la carpeta `dist` completa si deseas incluir ficheros auxiliares generados por PyInstaller.

## Notas importantes

- Si Windows SmartScreen bloquea la ejecución, selecciona **Más información** → **Ejecutar de todas formas**.
- La aplicación genera PDFs con formato A4 utilizando `reportlab`. El diseño está pensado para facturas agrícolas con IVA y retención, pero puedes ajustar los porcentajes desde la propia interfaz antes de exportar.
- Los datos de la empresa Agrícola León Lara S.C. están fijados en el encabezado del PDF. Puedes modificarlos en `invoice_app/main.py` si fuera necesario.

¡Listo! Ahora puedes crear facturas y compartir el ejecutable para que se utilice sin tener Python instalado.
