import os
import csv
import base64
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import streamlit as st

# ============================================================
# CONFIGURACION DEL NEGOCIO
# ============================================================

PRECIOS_PALTA = {
    "Hass": 2500,
    "Fuerte": 2500,
}

KILOS_MINIMOS = 1.0

TITULAR = "Enrique Armando Brun Urrutia"
RUT = "20.794.977-9"
BANCO = "Banco Estado"
TIPO_CUENTA = "Cuenta RUT"

CORREO_DESTINO = os.getenv("ORDER_NOTIFY_TO", "armando207949779@gmail.com")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

ARCHIVO_ORDENES = Path("ordenes_paltas.csv")
LOGO_PATH = Path("LOGO-PALTA.png")

LOCALIDADES_CERCANAS = ["La Calera", "Quillota", "La Cruz", "Hijuelas"]

REGIONES_COMUNAS = {
    "Arica y Parinacota": ["Arica", "Camarones", "Putre", "General Lagos"],
    "Tarapacá": ["Iquique", "Alto Hospicio", "Pozo Almonte", "Camiña", "Colchane", "Huara", "Pica"],
    "Antofagasta": ["Antofagasta", "Calama", "Tocopilla", "Mejillones", "Taltal", "Sierra Gorda", "San Pedro de Atacama", "María Elena"],
    "Atacama": ["Copiapó", "Caldera", "Tierra Amarilla", "Chañaral", "Diego de Almagro", "Vallenar", "Huasco", "Freirina"],
    "Coquimbo": ["La Serena", "Coquimbo", "Ovalle", "Illapel", "Los Vilos", "Salamanca", "Vicuña", "Monte Patria"],
    "Valparaíso": ["La Calera", "Quillota", "La Cruz", "Hijuelas", "Valparaíso", "Viña del Mar", "Concón", "Quilpué", "Villa Alemana", "Limache", "Olmué", "San Antonio", "Los Andes", "San Felipe", "La Ligua", "Cabildo", "Quintero", "Puchuncaví", "Casablanca", "Nogales"],
    "Metropolitana de Santiago": ["Santiago", "Providencia", "Las Condes", "Vitacura", "Ñuñoa", "La Florida", "Puente Alto", "Maipú", "Pudahuel", "Quilicura", "Renca", "Recoleta", "Independencia", "San Miguel", "La Cisterna", "San Bernardo", "Buin", "Paine", "Colina", "Lampa", "Melipilla", "Talagante", "Peñaflor"],
    "O'Higgins": ["Rancagua", "Machalí", "Graneros", "Rengo", "San Vicente", "San Fernando", "Santa Cruz", "Pichilemu"],
    "Maule": ["Talca", "Curicó", "Linares", "Cauquenes", "Constitución", "Molina", "Parral", "San Javier"],
    "Ñuble": ["Chillán", "Chillán Viejo", "San Carlos", "Bulnes", "Quillón", "Yungay"],
    "Biobío": ["Concepción", "Talcahuano", "San Pedro de la Paz", "Chiguayante", "Coronel", "Los Ángeles", "Lota", "Tomé"],
    "La Araucanía": ["Temuco", "Padre Las Casas", "Villarrica", "Pucón", "Angol", "Victoria", "Lautaro"],
    "Los Ríos": ["Valdivia", "La Unión", "Río Bueno", "Panguipulli", "Los Lagos"],
    "Los Lagos": ["Puerto Montt", "Puerto Varas", "Osorno", "Castro", "Ancud", "Quellón", "Frutillar"],
    "Aysén": ["Coyhaique", "Aysén", "Chile Chico", "Cochrane"],
    "Magallanes": ["Punta Arenas", "Natales", "Porvenir", "Cabo de Hornos"],
}


def formato_pesos(valor: int) -> str:
    return f"${valor:,.0f}".replace(",", ".")


def calcular_total(tipo_palta: str, kilos: float) -> int:
    return int(round(PRECIOS_PALTA[tipo_palta] * kilos))


def mostrar_logo_centrado(path: Path, ancho_px: int = 110) -> None:
    if not path.exists():
        return
    extension = path.suffix.replace(".", "").lower()
    if extension == "jpg":
        extension = "jpeg"
    imagen_base64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    st.markdown(
        f'<div class="logo-wrap"><img src="data:image/{extension};base64,{imagen_base64}" width="{ancho_px}" /></div>',
        unsafe_allow_html=True,
    )


def cambiar_paso(paso: int) -> None:
    st.session_state.paso = max(1, min(4, paso))


def guardar_orden(datos: dict) -> None:
    existe = ARCHIVO_ORDENES.exists()
    columnas = [
        "folio", "fecha_registro", "tipo_palta", "kilos", "precio_por_kg", "total_paltas",
        "modalidad_entrega", "region", "comuna", "poblacion", "calle", "numero",
        "nombre", "whatsapp", "estado"
    ]
    with ARCHIVO_ORDENES.open("a", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas)
        if not existe:
            writer.writeheader()
        writer.writerow(datos)


def crear_cuerpo_correo(datos: dict) -> str:
    return f"""
Nueva solicitud de pedido de paltas.

FOLIO
{datos['folio']}

PEDIDO
Tipo de palta: {datos['tipo_palta']}
Kilos: {datos['kilos']} kg
Precio por kg: {formato_pesos(datos['precio_por_kg'])}
Total paltas: {formato_pesos(datos['total_paltas'])}

ENTREGA
Modalidad: {datos['modalidad_entrega']}
Región: {datos['region'] or 'No aplica'}
Comuna: {datos['comuna'] or 'No aplica'}
Población / sector: {datos['poblacion'] or 'No informado'}
Calle: {datos['calle'] or 'No informado'}
Número: {datos['numero'] or 'No informado'}

CONTACTO
Nombre: {datos['nombre']}
WhatsApp: {datos['whatsapp']}

TRANSFERENCIA
Titular: {TITULAR}
RUT: {RUT}
Banco: {BANCO}
Tipo de cuenta: {TIPO_CUENTA}
Monto sugerido: {formato_pesos(datos['total_paltas'])}

IMPORTANTE
El monto corresponde a paltas. Si corresponde despacho, se coordina aparte.

Estado: {datos['estado']}
Fecha registro: {datos['fecha_registro']}
"""


def enviar_correo(datos: dict) -> tuple[bool, str]:
    if not SMTP_USER or not SMTP_PASSWORD:
        return False, "Solicitud guardada. Correo no enviado porque falta configurar SMTP_USER y SMTP_PASSWORD."

    mensaje = EmailMessage()
    mensaje["Subject"] = f"Pedido paltas {datos['folio']} - {datos['nombre']} - {formato_pesos(datos['total_paltas'])}"
    mensaje["From"] = SMTP_USER
    mensaje["To"] = CORREO_DESTINO
    mensaje.set_content(crear_cuerpo_correo(datos))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(mensaje)
        return True, "Solicitud guardada y correo enviado."
    except Exception as error:
        return False, f"Solicitud guardada. No se pudo enviar el correo: {error}"


def mensaje_para_cliente(datos: dict) -> str:
    return f"""Hola {datos['nombre']}, recibimos tu solicitud de pedido de paltas.

Pedido:
• Tipo: {datos['tipo_palta']}
• Cantidad: {datos['kilos']} kg
• Precio por kg: {formato_pesos(datos['precio_por_kg'])}
• Total paltas: {formato_pesos(datos['total_paltas'])}

Entrega:
• Modalidad: {datos['modalidad_entrega']}
• Comuna: {datos['comuna'] or 'No aplica'}

Datos de transferencia:
• Titular: {TITULAR}
• RUT: {RUT}
• Banco: {BANCO}
• Tipo de cuenta: {TIPO_CUENTA}
• Monto sugerido: {formato_pesos(datos['total_paltas'])}

Importante: el monto corresponde a paltas. Si corresponde despacho, se coordina aparte por WhatsApp.

Cuando transfieras, envíanos el comprobante por WhatsApp."""


# ============================================================
# INTERFAZ
# ============================================================

st.set_page_config(
    page_title="Solicitud Pedido Paltas",
    page_icon="🥑",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {max-width: 520px; padding-top: .65rem; padding-left: 1rem; padding-right: 1rem; padding-bottom: 2rem;}
    .logo-wrap {display: flex; justify-content: center; align-items: center; margin-top: .1rem; margin-bottom: .2rem;}
    .main-title {text-align: center; color: #14532d; font-size: 1.75rem; font-weight: 950; line-height: 1.05; margin: .15rem 0 .2rem 0;}
    .subtitle {text-align: center; color: #4b5563; font-size: .94rem; line-height: 1.35; margin-bottom: .9rem;}
    .step-pill {text-align: center; color: #166534; background: #dcfce7; border: 1px solid #bbf7d0; border-radius: 999px; padding: .42rem .9rem; font-weight: 900; font-size: .88rem; margin: .25rem auto .9rem auto; width: fit-content;}
    .summary-card {background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 18px; padding: 1rem; margin: .8rem 0;}
    .total-card {background: #ecfdf5; border: 1px solid #86efac; border-radius: 18px; padding: 1rem; text-align: center; margin: .8rem 0;}
    .total-label {color: #166534; font-size: .9rem; font-weight: 800;}
    .total-value {color: #14532d; font-size: 2.15rem; font-weight: 950; line-height: 1.05;}
    .soft-note {color: #4b5563; font-size: .88rem; line-height: 1.3; margin-top: .35rem;}
    .low-priority {background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 16px; padding: .85rem; color: #4b5563; font-size: .92rem;}
    .stButton button, .stDownloadButton button {width: 100%; min-height: 3rem; border-radius: 14px; font-weight: 850;}
    div[data-baseweb="select"] > div {min-height: 3rem; border-radius: 12px;}
    input, textarea {border-radius: 12px !important;}
    label {font-weight: 800 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "paso" not in st.session_state:
    st.session_state.paso = 1

mostrar_logo_centrado(LOGO_PATH, 112)

st.markdown(
    """
    <div class="main-title">Solicitud Pedido<br>Paltas</div>
    <div class="subtitle">Completa tu pedido por pasos. Es rápido y pensado para WhatsApp.</div>
    """,
    unsafe_allow_html=True,
)

st.markdown(f'<div class="step-pill">Paso {st.session_state.paso} de 4</div>', unsafe_allow_html=True)

if st.session_state.paso == 1:
    st.subheader("¿Cuántos kilos quieres?")

    tipo_palta = st.radio("Tipo de palta", list(PRECIOS_PALTA.keys()), horizontal=True, key="tipo_palta")
    kilos = st.number_input("Kilos", min_value=KILOS_MINIMOS, value=float(st.session_state.get("kilos", KILOS_MINIMOS)), step=0.5, key="kilos_input")

    precio_kg = PRECIOS_PALTA[tipo_palta]
    total = calcular_total(tipo_palta, kilos)

    st.markdown(
        f"""
        <div class="total-card">
            <div class="total-label">{tipo_palta} · {formato_pesos(precio_kg)} por kg</div>
            <div class="total-value">{formato_pesos(total)}</div>
            <div class="soft-note">Este es el valor total por la cantidad seleccionada.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Continuar"):
        st.session_state.tipo_palta = tipo_palta
        st.session_state.kilos = kilos
        st.session_state.precio_kg = precio_kg
        st.session_state.total_paltas = total
        cambiar_paso(2)
        st.rerun()

elif st.session_state.paso == 2:
    st.subheader("¿Dónde quieres recibirlas?")

    modalidad_entrega = st.radio(
        "Elige una opción",
        [
            "Retiro sin costo",
            "Envío a domicilio en La Calera, Quillota, La Cruz o Hijuelas",
            "Otra comuna o región - cotizar envío",
        ],
        captions=[
            "Retiro en punto acordado por WhatsApp.",
            "Disponible para zona cercana. El despacho se coordina por WhatsApp.",
            "Opción menos frecuente, pensada principalmente para pedidos al por mayor.",
        ],
        key="modalidad_entrega",
    )

    region = ""
    comuna = ""
    poblacion = ""
    calle = ""
    numero = ""

    if modalidad_entrega == "Retiro sin costo":
        st.info("Retiro sin costo de despacho. Coordinaremos el punto por WhatsApp.")
        region = "Valparaíso"
        comuna = st.selectbox("Localidad de retiro preferida", LOCALIDADES_CERCANAS, key="comuna_retiro")

    elif modalidad_entrega == "Envío a domicilio en La Calera, Quillota, La Cruz o Hijuelas":
        region = "Valparaíso"
        comuna = st.selectbox("Localidad", LOCALIDADES_CERCANAS, key="comuna_local")
        poblacion = st.text_input("Población / sector", placeholder="Ej: Artificio, Boco, Pocochay", key="poblacion_local")
        calle = st.text_input("Calle", placeholder="Ej: Los Aromos", key="calle_local")
        numero = st.text_input("Número", placeholder="Ej: 123", key="numero_local")

    else:
        st.markdown('<div class="low-priority">Para otras comunas o regiones, el envío se cotiza aparte. Esta opción está pensada principalmente para pedidos al por mayor.</div>', unsafe_allow_html=True)
        regiones = list(REGIONES_COMUNAS.keys())
        region = st.selectbox("Región", regiones, index=regiones.index("Valparaíso"), key="region_otras")
        comuna = st.selectbox("Comuna", REGIONES_COMUNAS[region], key=f"comuna_otras_{region}")
        poblacion = st.text_input("Población / sector", placeholder="Ej: sector o referencia", key="poblacion_otra")
        calle = st.text_input("Calle", placeholder="Ej: Los Aromos", key="calle_otra")
        numero = st.text_input("Número", placeholder="Ej: 123", key="numero_otra")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Volver"):
            cambiar_paso(1)
            st.rerun()
    with col2:
        if st.button("Continuar"):
            errores = []
            if modalidad_entrega != "Retiro sin costo":
                if not poblacion.strip():
                    errores.append("Población / sector")
                if not calle.strip():
                    errores.append("Calle")
                if not numero.strip():
                    errores.append("Número")
            if errores:
                st.error("Falta completar: " + ", ".join(errores))
            else:
                st.session_state.modalidad_entrega = modalidad_entrega
                st.session_state.region = region
                st.session_state.comuna = comuna
                st.session_state.poblacion = poblacion.strip()
                st.session_state.calle = calle.strip()
                st.session_state.numero = numero.strip()
                cambiar_paso(3)
                st.rerun()

elif st.session_state.paso == 3:
    st.subheader("Datos de contacto")
    nombre = st.text_input("Nombre", placeholder="Tu nombre", key="nombre")
    whatsapp = st.text_input("WhatsApp", placeholder="+56 9 1234 5678", key="whatsapp")

    st.markdown(
        f"""
        <div class="summary-card">
            <b>Resumen rápido</b><br>
            {st.session_state.get('kilos', KILOS_MINIMOS)} kg de palta {st.session_state.get('tipo_palta', '')}<br>
            Total paltas: <b>{formato_pesos(int(st.session_state.get('total_paltas', 0)))}</b><br>
            Modalidad: {st.session_state.get('modalidad_entrega', '')}
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Volver"):
            cambiar_paso(2)
            st.rerun()
    with col2:
        if st.button("Ver transferencia"):
            errores = []
            if not nombre.strip():
                errores.append("Nombre")
            if not whatsapp.strip():
                errores.append("WhatsApp")
            if errores:
                st.error("Falta completar: " + ", ".join(errores))
            else:
                st.session_state.nombre = nombre.strip()
                st.session_state.whatsapp = whatsapp.strip()
                cambiar_paso(4)
                st.rerun()

elif st.session_state.paso == 4:
    st.subheader("Transferencia")

    datos_previos_ok = all(clave in st.session_state for clave in ["tipo_palta", "kilos", "precio_kg", "total_paltas", "modalidad_entrega", "nombre", "whatsapp"])

    if not datos_previos_ok:
        st.warning("Faltan datos del pedido. Vuelve al inicio para completar la solicitud.")
        if st.button("Volver al paso 1"):
            cambiar_paso(1)
            st.rerun()
    else:
        st.markdown(
            f"""
            <div class="total-card">
                <div class="total-label">Monto sugerido a transferir</div>
                <div class="total-value">{formato_pesos(int(st.session_state.total_paltas))}</div>
                <div class="soft-note">Corresponde solo a las paltas. El despacho, si aplica, se coordina aparte.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write(f"**Titular:** {TITULAR}")
        st.write(f"**RUT:** {RUT}")
        st.write(f"**Banco:** {BANCO}")
        st.write(f"**Tipo de cuenta:** {TIPO_CUENTA}")

        st.markdown("### Resumen")
        st.write(f"**Pedido:** {st.session_state.kilos} kg de palta {st.session_state.tipo_palta}")
        st.write(f"**Entrega:** {st.session_state.modalidad_entrega}")
        st.write(f"**Comuna:** {st.session_state.get('comuna', '')}")
        st.write(f"**Cliente:** {st.session_state.nombre}")
        st.write(f"**WhatsApp:** {st.session_state.whatsapp}")

        confirmar = st.checkbox("Confirmo y quiero registrar esta solicitud.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Volver"):
                cambiar_paso(3)
                st.rerun()

        with col2:
            if st.button("Registrar"):
                if not confirmar:
                    st.error("Debes confirmar para registrar la solicitud.")
                else:
                    folio = "PALTA-" + datetime.now().strftime("%Y%m%d-%H%M%S")
                    datos = {
                        "folio": folio,
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "tipo_palta": st.session_state.tipo_palta,
                        "kilos": st.session_state.kilos,
                        "precio_por_kg": int(st.session_state.precio_kg),
                        "total_paltas": int(st.session_state.total_paltas),
                        "modalidad_entrega": st.session_state.modalidad_entrega,
                        "region": st.session_state.get("region", ""),
                        "comuna": st.session_state.get("comuna", ""),
                        "poblacion": st.session_state.get("poblacion", ""),
                        "calle": st.session_state.get("calle", ""),
                        "numero": st.session_state.get("numero", ""),
                        "nombre": st.session_state.nombre,
                        "whatsapp": st.session_state.whatsapp,
                        "estado": "Solicitud recibida",
                    }
                    guardar_orden(datos)
                    correo_ok, mensaje_estado = enviar_correo(datos)
                    st.success("Solicitud registrada correctamente.")
                    st.caption(mensaje_estado)
                    st.text_area("Mensaje para WhatsApp", value=mensaje_para_cliente(datos), height=285)
                    st.download_button("Descargar solicitud", data=crear_cuerpo_correo(datos), file_name=f"{folio}.txt", mime="text/plain")

with st.expander("Registro interno"):
    if ARCHIVO_ORDENES.exists():
        with ARCHIVO_ORDENES.open("rb") as archivo:
            st.download_button("Descargar solicitudes CSV", data=archivo, file_name="ordenes_paltas.csv", mime="text/csv")
    else:
        st.caption("Aún no hay solicitudes registradas.")
