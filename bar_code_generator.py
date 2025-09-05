import streamlit as st
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from datetime import datetime, timedelta
import re
import zipfile
import os

st.set_page_config(page_title="Generador de Códigos de Barras", layout="wide")
st.title("Generador de Códigos de Barras")

# --- Estado ---
if "csv_subido" not in st.session_state:
    st.session_state.csv_subido = False

if st.button("🔄 Recargar"):
    st.session_state.csv_subido = False
    st.session_state.file = None

# --- Parámetros del usuario ---
nombre_col_producto = st.text_input("Nombre columna producto", "Nombre producto")
nombre_col_codigo = st.text_input("Nombre columna código", "Codigo")

# Selector de simbología
symbologia = st.selectbox(
    "Selecciona el tipo de código de barras",
    [
        "ean13",     # EAN-13
        "ean8",      # EAN-8
        "upc",       # UPC-A
        "code39",    # Código 39
        "code128",   # Código 128
        "pzn",       # Código PZN (farmacéutico)
        "isbn13",    # ISBN
        "issn"       # ISSN
    ],
    index=4  # Por defecto: Code128
)

# Parámetros gráficos
module_width = st.slider("Ancho de barras", 0.1, 2.0, 0.5)
module_height = st.slider("Alto de barras", 10, 100, 30)
font_size = st.slider("Tamaño del texto", 6, 24, 12)
text_distance = st.slider("Separación texto-barras", 0, 20, 5)
quiet_zone = st.slider("Margen alrededor del código", 0, 20, 6)

# --- Subir archivo ---
if not st.session_state.csv_subido:
    uploaded_file = st.file_uploader("Sube tu CSV o Excel", type=["csv", "xlsx"])
    if uploaded_file is not None:
        st.session_state.csv_subido = True
        st.session_state.file = uploaded_file

# --- Procesar archivo ---
if st.session_state.csv_subido and st.session_state.file is not None:
    uploaded_file = st.session_state.file

    try:
        if uploaded_file.name.endswith(".csv"):
            try:
                df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
            except Exception:
                try:
                    df = pd.read_csv(uploaded_file, sep=",", encoding="utf-8")
                except UnicodeDecodeError:
                    df = pd.read_csv(uploaded_file, sep=",", encoding="latin-1")
            st.success(f"Archivo CSV leído correctamente. Contiene {len(df)} filas.")
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            st.success(f"Archivo Excel leído correctamente. Contiene {len(df)} filas.")
        else:
            st.error("Formato de archivo no soportado.")
            st.stop()
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()

    # --- Verificar columnas ---
    if nombre_col_producto not in df.columns or nombre_col_codigo not in df.columns:
        st.error("No se encontraron las columnas especificadas en el archivo.")
        st.stop()

    # --- Carpeta temporal ---
    carpeta = "codigos_barras"
    os.makedirs(carpeta, exist_ok=True)
    archivos_generados = []

    # --- Generar códigos de barras ---
    for i, row in df.iterrows():
        try:
            nombre_producto = str(row[nombre_col_producto])
            codigo = str(row[nombre_col_codigo])
            nombre_archivo = re.sub(r'[^a-zA-Z0-9_-]', "_", nombre_producto)
            ruta_archivo = os.path.join(carpeta, nombre_archivo)

            barra = barcode.get(symbologia, codigo, writer=ImageWriter())
            archivo = barra.save(ruta_archivo, options={
                "module_width": module_width,
                "module_height": module_height,
                "font_size": font_size,
                "text_distance": text_distance,
                "quiet_zone": quiet_zone
            })
            archivos_generados.append(archivo)
        except Exception as e:
            st.warning(f"No se pudo generar código para '{nombre_producto}': {e}")

    # --- Mostrar resultados ---
    if archivos_generados:
        st.success(f"{len(archivos_generados)} códigos generados correctamente.")

        # Crear ZIP
        now = datetime.now() + timedelta(hours=-3)
        now_str = now.strftime("%d-%m-%Y_Hora_%H-%M-%S")
        zip_filename = f"codigos_barras_{now_str}.zip"
        with zipfile.ZipFile(zip_filename, "w") as zipf:
            for file in archivos_generados:
                zipf.write(file)

        with open(zip_filename, "rb") as f:
            st.download_button("📦 Descargar ZIP con códigos de barras", data=f, file_name=zip_filename)

        # Vista previa
        st.subheader("Vista previa del primer código de barras")
        st.image(archivos_generados[0], width=400)
    else:
        st.warning("No se generaron códigos de barras.")
# --- Procesar archivo si ya se subió ---
if st.session_state.csv_subido and st.session_state.file is not None:
    uploaded_file = st.session_state.file

    # --- Leer archivo con soporte CSV/Excel y distintos separadores ---
    try:
        if uploaded_file.name.endswith(".csv"):
            # Intentar primero con ';'
            try:
                df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
            except Exception:
                # Si falla, intentar con ','
                try:
                    df = pd.read_csv(uploaded_file, sep=",", encoding="utf-8")
                except UnicodeDecodeError:
                    df = pd.read_csv(uploaded_file, sep=",", encoding="latin-1")
            st.success(f"Archivo CSV leído correctamente. Contiene {len(df)} filas.")
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            st.success(f"Archivo Excel leído correctamente. Contiene {len(df)} filas.")
        else:
            st.error("Formato de archivo no soportado.")
            st.stop()
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()

    # --- Verificar columnas ---
    if nombre_col_producto not in df.columns or nombre_col_codigo not in df.columns:
        st.error("No se encontraron las columnas especificadas en el archivo.")
        st.stop()

    # --- Carpeta temporal ---
    carpeta = "codigos_barras"
    os.makedirs(carpeta, exist_ok=True)
    archivos_generados = []

    # --- Generar códigos de barras ---
    for i, row in df.iterrows():
        try:
            nombre_producto = str(row[nombre_col_producto])
            codigo = str(row[nombre_col_codigo])
            nombre_archivo = re.sub(r'[^a-zA-Z0-9_-]', "_", nombre_producto)
            ruta_archivo = os.path.join(carpeta, nombre_archivo)

            barra = barcode.get("code128", codigo, writer=ImageWriter())
            archivo = barra.save(ruta_archivo, options={
                "module_width": module_width,
                "module_height": module_height,
                "font_size": font_size,
                "text_distance": text_distance,
                "quiet_zone": quiet_zone
            })
            archivos_generados.append(archivo)
        except Exception as e:
            st.warning(f"No se pudo generar código para '{nombre_producto}': {e}")

    # --- Mostrar resultados ---
    if archivos_generados:
        st.success(f"{len(archivos_generados)} códigos generados correctamente.")

        # --- Crear ZIP ---
        now = datetime.now() + timedelta(hours=-3)
        now_str = now.strftime("%d-%m-%Y_Hora_%H-%M-%S")
        zip_filename = f"codigos_barras_{now_str}.zip"
        with zipfile.ZipFile(zip_filename, "w") as zipf:
            for file in archivos_generados:
                zipf.write(file)

        # --- Botón descargar ZIP ---
        with open(zip_filename, "rb") as f:
            st.download_button("📦 Descargar ZIP con códigos de barras", data=f, file_name=zip_filename)

        # --- Vista previa del primer código ---
        st.subheader("Vista previa del primer código de barras")
        st.image(archivos_generados[0], width=400)
    else:
        st.warning("No se generaron códigos de barras.")
