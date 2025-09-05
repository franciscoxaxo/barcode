import streamlit as st
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from datetime import datetime, timedelta
import re
import zipfile
import os

st.title("Generador de Códigos de Barras")

# --- Parámetros del usuario ---
nombre_col_producto = st.text_input("Nombre columna producto", "Nombre producto")
nombre_col_codigo = st.text_input("Nombre columna código", "Codigo")
module_width = st.slider("Ancho de barras", 0.1, 2.0, 0.5)
module_height = st.slider("Alto de barras", 10, 100, 30)
font_size = st.slider("Tamaño del texto", 6, 24, 12)
text_distance = st.slider("Separación texto-barras", 0, 20, 5)
quiet_zone = st.slider("Margen alrededor del código", 0, 20, 6)

# --- Subir CSV ---
uploaded_file = st.file_uploader("Sube tu CSV", type=["csv"])
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, sep=";", encoding="latin-1")
    except Exception as e:
        st.error(f"Error al leer CSV: {e}")
        st.stop()

    # Verificar columnas
    if nombre_col_producto not in df.columns or nombre_col_codigo not in df.columns:
        st.error("No se encontraron las columnas especificadas en el CSV.")
        st.stop()

    # Carpeta temporal
    carpeta = "codigos_barras"
    os.makedirs(carpeta, exist_ok=True)

    archivos_generados = []

    # Generar códigos
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

    if archivos_generados:
        st.success(f"{len(archivos_generados)} códigos generados correctamente.")

        # Crear ZIP
        now = datetime.now() + timedelta(hours=-3)
        now = now.strftime("%d-%m-%Y_Hora_%H-%M-%S")
        zip_filename = f"codigos_barras_{now}.zip"

        with zipfile.ZipFile(zip_filename, "w") as zipf:
            for file in archivos_generados:
                zipf.write(file)

        # Botón de descarga
        with open(zip_filename, "rb") as f:
            st.download_button("📦 Descargar ZIP con códigos de barras", data=f, file_name=zip_filename)

        # --- Mostrar primer código de barras ---
        st.subheader("Vista previa del primer código de barras")
        st.image(archivos_generados[0], width=400)

        # --- Botón recargar ---
        if st.button("🔄 Recargar"):
            st.experimental_rerun()

    else:
        st.warning("No se generaron códigos de barras.")
