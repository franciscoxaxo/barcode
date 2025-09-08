import streamlit as st
import pandas as pd
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import io
import zipfile

# ----------------------------
# Función para generar códigos de barras
# ----------------------------
def generar_codigos_barras(df, col_nombre, col_codigo, tipo_codigo, ancho=2, alto=100, font_size=12, text_distance=5):
    buffer_zip = io.BytesIO()
    with zipfile.ZipFile(buffer_zip, "w") as zf:
        for _, row in df.iterrows():
            nombre = str(row[col_nombre]).strip()
            codigo = str(row[col_codigo]).strip()

            try:
                # Selección de simbología
                if tipo_codigo == "UPC":
                    BarcodeClass = barcode.get_barcode_class("upc")
                elif tipo_codigo == "EAN":
                    BarcodeClass = barcode.get_barcode_class("ean13")
                elif tipo_codigo == "Code39":
                    BarcodeClass = barcode.get_barcode_class("code39")
                elif tipo_codigo == "Code128":
                    BarcodeClass = barcode.get_barcode_class("code128")
                elif tipo_codigo == "Code93":
                    BarcodeClass = barcode.get_barcode_class("code93")
                elif tipo_codigo == "Codabar":
                    BarcodeClass = barcode.get_barcode_class("codabar")
                elif tipo_codigo == "PZN":
                    BarcodeClass = barcode.get_barcode_class("pzn")
                else:
                    st.error(f"❌ Tipo de código no soportado: {tipo_codigo}")
                    continue

                # Generar código de barras en memoria
                barcode_obj = BarcodeClass(codigo, writer=ImageWriter())
                img_bytes = io.BytesIO()
                barcode_obj.write(img_bytes, options={
                    "module_width": ancho,
                    "module_height": alto,
                    "font_size": font_size,
                    "text_distance": text_distance
                })

                # Guardar en el ZIP
                zf.writestr(f"{nombre}_{codigo}.png", img_bytes.getvalue())

            except Exception as e:
                st.error(f"❌ Error generando código {codigo}: {e}")

    buffer_zip.seek(0)
    return buffer_zip

# ----------------------------
# App en Streamlit
# ----------------------------
st.title("📦 Generador de Códigos de Barras")

# Subir archivo
uploaded_file = st.file_uploader("📂 Sube un archivo CSV o Excel", type=["csv", "xls", "xlsx"])

if uploaded_file is not None:
    try:
        # Reiniciar puntero siempre antes de leer
        uploaded_file.seek(0)

        # Intentar leer CSV o Excel
        if uploaded_file.name.endswith(".csv"):
            try:
                df = pd.read_csv(uploaded_file, sep=";")
            except Exception:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=",")
        elif uploaded_file.name.endswith((".xls", ".xlsx")):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("❌ Tipo de archivo no soportado.")
            df = None

        if df is not None:
            st.success(f"✅ Archivo leído correctamente con {len(df)} filas")

            # Selección de columnas
            columnas = df.columns.tolist()
            col_nombre = st.selectbox("📛 Selecciona la columna del nombre del producto", columnas)
            col_codigo = st.selectbox("🔢 Selecciona la columna del código", columnas)

            # Configuración de simbología
            tipo_codigo = st.selectbox(
                "📐 Tipo de código de barras",
                ["UPC", "EAN", "Code39", "Code128", "Code93", "Codabar", "PZN"]
            )

            # Configuración de tamaño
            ancho = st.slider("📏 Ancho del módulo", 1, 5, 2)
            alto = st.slider("📏 Altura del código", 50, 300, 100)
            font_size = st.slider("🔠 Tamaño de la letra", 6, 30, 12)
            text_distance = st.slider("↕️ Separación código-texto", 0, 20, 5)

            # Generar códigos
            if st.button("🚀 Generar códigos de barras"):
                zip_buffer = generar_codigos_barras(
                    df, col_nombre, col_codigo, tipo_codigo,
                    ancho, alto, font_size, text_distance
                )

                # Descargar ZIP
                st.download_button(
                    label="💾 Descargar ZIP con códigos",
                    data=zip_buffer,
                    file_name="codigos_barras.zip",
                    mime="application/zip"
                )

                # Mostrar vista previa del primer código
                try:
                    primera_fila = df.iloc[0]
                    nombre = str(primera_fila[col_nombre]).strip()
                    codigo = str(primera_fila[col_codigo]).strip()

                    if tipo_codigo == "UPC":
                        BarcodeClass = barcode.get_barcode_class("upc")
                    elif tipo_codigo == "EAN":
                        BarcodeClass = barcode.get_barcode_class("ean13")
                    elif tipo_codigo == "Code39":
                        BarcodeClass = barcode.get_barcode_class("code39")
                    elif tipo_codigo == "Code128":
                        BarcodeClass = barcode.get_barcode_class("code128")
                    elif tipo_codigo == "Code93":
                        BarcodeClass = barcode.get_barcode_class("code93")
                    elif tipo_codigo == "Codabar":
                        BarcodeClass = barcode.get_barcode_class("codabar")
                    elif tipo_codigo == "PZN":
                        BarcodeClass = barcode.get_barcode_class("pzn")
                    else:
                        BarcodeClass = None

                    if BarcodeClass:
                        barcode_obj = BarcodeClass(codigo, writer=ImageWriter())
                        img_bytes = io.BytesIO()
                        barcode_obj.write(img_bytes, options={
                            "module_width": ancho,
                            "module_height": alto,
                            "font_size": font_size,
                            "text_distance": text_distance
                        })
                        img_bytes.seek(0)
                        img = Image.open(img_bytes)
                        st.image(img, caption=f"Vista previa: {nombre} ({codigo})")
                except Exception as e:
                    st.warning(f"No se pudo generar la vista previa: {e}")

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
