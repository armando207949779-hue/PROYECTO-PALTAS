import os
import csv
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import streamlit as st


# =========================
# CONFIGURACIÓN DEL NEGOCIO
# =========================

DUENO_NOMBRE = "Enrique Armando Brun Urrutia"
DUENO_RUT = "20.794.977-9"
BANCO = "Banco Estado"
TIPO_CUENTA = "Cuenta RUT"

# Correo donde quieres recibir los pedidos
CORREO_DUENO = os.getenv("ORDER_NOTIFY_TO", "armando207949779@gmail.com")

# Para enviar correos, configura estas variables de entorno:
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=tu_correo@gmail.com
# SMTP_PASSWORD=tu_clave_de_aplicacion
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

ARCHIVO_ORDENES = Path("ordenes_paltas.csv")
LOGO_PATH = Path("LOGO-PALTA.png")


# =========================
# FUNCIONES
# =========================

def formato_pesos(valor: int) -> str:
    return f"${valor:,.0f}".replace(",", ".")


def calcular_total(kilos: float, precio_por_kg: int, costo_despacho: int) -> int:
    return int(round(kilos * precio_por_kg + costo_despacho))


def guardar_orden(datos: dict) -> None:
    existe = ARCHIVO_ORDENES.exists()

    with ARCHIVO_ORDENES.open("a", newline="", encoding="utf-8") as archivo:
        columnas = [
            "fecha_registro",
            "nombre",
            "telefono",
            "correo",
            "kilos",
            "precio_por_kg",
            "costo_despacho",
            "total",
            "comuna",
            "direccion",
            "fecha_entrega",
            "horario",
            "comentarios",
            "estado_transferencia",
        ]

        writer = csv.DictWriter(archivo, fieldnames=columnas)

        if not existe:
            writer.writeheader()

        writer.writerow(datos)


def crear_cuerpo_correo(datos: dict) -> str:
    return f"""
Nuevo pedido de paltas registrado.

DATOS DEL CLIENTE
Nombre: {datos["nombre"]}
Teléfono / WhatsApp: {datos["telefono"]}
Correo: {datos["correo"] or "No informado"}

PEDIDO
Kilos solicitados: {datos["kilos"]} kg
Precio por kg: {formato_pesos(int(datos["precio_por_kg"]))}
Despacho: {formato_pesos(int(datos["costo_despacho"]))}
TOTAL A PAGAR: {formato_pesos(int(datos["total"]))}

ENTREGA
Comuna: {datos["comuna"]}
Dirección: {datos["direccion"]}
Fecha solicitada: {datos["fecha_entrega"]}
Horario: {datos["horario"]}
Comentarios: {datos["comentarios"] or "Sin comentarios"}

TRANSFERENCIA
Titular: {DUENO_NOMBRE}
RUT: {DUENO_RUT}
Banco: {BANCO}
Tipo de cuenta: {TIPO_CUENTA}
Monto: {formato_pesos(int(datos["total"]))}
Estado: {datos["estado_transferencia"]}

Registro creado el: {datos["fecha_registro"]}
"""


def enviar_correo(datos: dict) -> tuple[bool, str]:
    if not SMTP_USER or not SMTP_PASSWORD:
        return False, (
            "No se envió correo porque faltan SMTP_USER y SMTP_PASSWORD. "
            "El pedido sí quedó guardado en el archivo CSV."
        )

    mensaje = EmailMessage()
    mensaje["Subject"] = f"Nuevo pedido de paltas - {datos['nombre']} - {formato_pesos(int(datos['total']))}"
    mensaje["From"] = SMTP_USER
    mensaje["To"] = CORREO_DUENO
    mensaje.set_content(crear_cuerpo_correo(datos))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(mensaje)

        return True, "Correo enviado correctamente."
    except Exception as error:
        return False, f"No se pudo enviar el correo: {error}"


def generar_mensaje_whatsapp(datos: dict) -> str:
    return f"""Hola {datos["nombre"]}, tu pedido quedó registrado ✅

Pedido:
- {datos["kilos"]} kg de paltas
- Precio por kg: {formato_pesos(int(datos["precio_por_kg"]))}
- Despacho: {formato_pesos(int(datos["costo_despacho"]))}
- Total a pagar: {formato_pesos(int(datos["total"]))}

Datos para transferencia:
- Titular: {DUENO_NOMBRE}
- RUT: {DUENO_RUT}
- Banco: {BANCO}
- Tipo de cuenta: {TIPO_CUENTA}
- Monto: {formato_pesos(int(datos["total"]))}

Entrega:
- Comuna: {datos["comuna"]}
- Dirección: {datos["direccion"]}
- Fecha: {datos["fecha_entrega"]}
- Horario: {datos["horario"]}

Por favor envíanos el comprobante de transferencia por WhatsApp."""


# =========================
# INTERFAZ
# =========================

st.set_page_config(
    page_title="Formulario de pedidos de paltas",
    page_icon="🥑",
    layout="centered",
)

if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=170)

st.title("Formulario de pedidos de paltas")
st.write("Completa los datos del cliente, calcula el total y guarda el pedido para seguimiento.")

with st.sidebar:
    st.header("Valores")
    precio_por_kg = st.number_input(
        "Precio por kilo",
        min_value=0,
        value=2500,
        step=100,
    )
    costo_despacho = st.number_input(
        "Costo de despacho",
        min_value=0,
        value=0,
        step=500,
    )
    st.caption("Puedes cambiar estos valores antes de registrar cada pedido.")

with st.form("formulario_pedido"):
    st.subheader("Datos del cliente")

    nombre = st.text_input("Nombre del cliente")
    telefono = st.text_input("Teléfono / WhatsApp")
    correo = st.text_input("Correo del cliente, opcional")

    st.subheader("Pedido")

    kilos = st.number_input(
        "Cantidad de paltas en kilos",
        min_value=0.5,
        value=1.0,
        step=0.5,
    )

    st.subheader("Entrega")

    comuna = st.text_input("Comuna")
    direccion = st.text_area("Dirección de entrega")
    fecha_entrega = st.date_input("Fecha solicitada de entrega")
    horario = st.selectbox(
        "Horario preferido",
        [
            "Mañana",
            "Tarde",
            "Noche",
            "Coordinar por WhatsApp",
        ],
    )
    comentarios = st.text_area("Comentarios o requerimientos especiales")
    estado_transferencia = st.selectbox(
        "Estado de transferencia",
        [
            "Pendiente",
            "Comprobante enviado",
            "Pagado",
        ],
    )

    total = calcular_total(kilos, precio_por_kg, costo_despacho)

    st.info(f"Total a pagar: {formato_pesos(total)}")

    enviar = st.form_submit_button("Registrar pedido")

if enviar:
    campos_obligatorios = {
        "Nombre": nombre,
        "Teléfono / WhatsApp": telefono,
        "Comuna": comuna,
        "Dirección": direccion,
    }

    faltantes = [campo for campo, valor in campos_obligatorios.items() if not str(valor).strip()]

    if faltantes:
        st.error("Faltan estos datos obligatorios: " + ", ".join(faltantes))
    else:
        datos = {
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nombre": nombre.strip(),
            "telefono": telefono.strip(),
            "correo": correo.strip(),
            "kilos": kilos,
            "precio_por_kg": precio_por_kg,
            "costo_despacho": costo_despacho,
            "total": total,
            "comuna": comuna.strip(),
            "direccion": direccion.strip(),
            "fecha_entrega": str(fecha_entrega),
            "horario": horario,
            "comentarios": comentarios.strip(),
            "estado_transferencia": estado_transferencia,
        }

        guardar_orden(datos)
        correo_enviado, mensaje_correo = enviar_correo(datos)

        st.success("Pedido registrado correctamente.")
        st.write(mensaje_correo)

        st.subheader("Resumen para enviar por WhatsApp")
        mensaje_whatsapp = generar_mensaje_whatsapp(datos)
        st.text_area(
            "Copia este mensaje y envíalo al cliente",
            value=mensaje_whatsapp,
            height=330,
        )

        st.subheader("Datos de transferencia")
        st.write(f"**Titular:** {DUENO_NOMBRE}")
        st.write(f"**RUT:** {DUENO_RUT}")
        st.write(f"**Banco:** {BANCO}")
        st.write(f"**Tipo de cuenta:** {TIPO_CUENTA}")
        st.write(f"**Monto:** {formato_pesos(total)}")

st.divider()

st.subheader("Registro de pedidos")
if ARCHIVO_ORDENES.exists():
    with ARCHIVO_ORDENES.open("rb") as archivo:
        st.download_button(
            "Descargar registro CSV",
            data=archivo,
            file_name="ordenes_paltas.csv",
            mime="text/csv",
        )
else:
    st.caption("Aún no hay pedidos registrados.")
