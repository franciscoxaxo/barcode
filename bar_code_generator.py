# --- Instalar librerías si no existen ---
import importlib
import sys
import subprocess

def instalar_si_no_existe(paquete, import_name=None):
    if import_name is None:
        import_name = paquete
    try:
        importlib.import_module(import_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", paquete, "-q"])

# Instalar librerías necesarias
instalar_si_no_existe("python-barcode", "barcode")
instalar_si_no_existe("Pillow", "PIL")
instalar_si_no_existe("pandas")
instalar_si_no_existe("streamlit")

# --- Importaciones ---
import streamlit as st
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from datetime import datetime, timedelta
import re
import zipfile
import os
from io import BytesIO

# --- Función adaptada a Streamlit ---
def generar_codigos_barras_streamlit(nombre_col_producto="Nombre producto", nombre_col_codigo="Codigo",
                                     module_width=0.5, module_height=30, font_size=12,
                                     text_distance=5, quiet_zone=6):
    
    st.title("Generador de Códigos de Barras")
    st.write("Sube un CSV con columnas de nombre de producto y código, y descarga un ZIP con los códigos generados.")

    # --- Subir archivo CSV ---
    uploaded_file = st.file_uploader("Selecciona tu archivo CSV", type=["csv"])
    if uploaded_file is None:
        st.info("Espera a que subas un CSV.")
        return

    # --- Leer CSV ---
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, sep=";", encoding="latin-1")
    except Exception as e:
        st.error(f"Error al leer el CSV: {e}")
        return

    # --- Verificar columnas ---
    for col in [nombre_col_producto, nombre_col_codigo]:
        if col not in df.columns:
            st.error(f"La columna '{col}' no se encontró en el CSV.")
            return

    # --- Configuración de tamaño ---
    opciones = {
        "module_width": module_width,
        "module_height": module_height,
        "font_size": font_size,
        "text_distance": text_distance,
        "quiet_zone": quiet_zone
    }

    # --- Crear carpeta temporal para PNGs ---
    carpeta = "codigos_barras"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    archivos_generados = []

    # --- Generar códigos de barras ---
    for i, row in df.iterrows():
        try:
            nombre_producto = str(row[nombre_col_producto])
            codigo = str(row[nombre_col_codigo])
            nombre_archivo = re.sub(r'[^a-zA-Z0-9_-]', "_", nombre_producto)
            ruta_archivo = os.path.join(carpeta, nombre_archivo)

            barra = barcode.get("code128", codigo, writer=ImageWriter())
            archivo = barra.save(ruta_archivo, options=opciones)

            st.success(f"Código de barras generado: {archivo}")
            st.image(archivo, width=300)
            archivos_generados.append(archivo)
        except Exception as e:
            st.error(f"Error al generar el código de barras para '{nombre_producto}': {e}")

    # --- Crear ZIP ---
    if archivos_generados:
        now = datetime.now() + timedelta(hours=-3)
        now = now.strftime('%d-%m-%Y_Hora_%H-%M-%S')
        zip_filename = f"codigos_barras_{now}.zip"
        with zipfile.ZipFile(zip_filename, "w") as zipf:
            for file in archivos_generados:
                zipf.write(file)

        # --- Descargar ZIP ---
        with open(zip_filename, "rb") as f:
            bytes_data = f.read()
        st.download_button("📦 Descargar ZIP con códigos de barras", data=bytes_data, file_name=zip_filename)
    else:
        st.warning("No se generaron códigos de barras, no se creó ZIP.")
