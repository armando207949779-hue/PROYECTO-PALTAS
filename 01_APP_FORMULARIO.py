import os
import csv
import base64
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import quote

import streamlit as st


# ============================================================
# CONFIGURACIÓN DEL NEGOCIO
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

# Número de WhatsApp del negocio en formato internacional, sin + ni espacios.
WHATSAPP_NEGOCIO = "56963596523"

# Google Sheets donde se guardarán los pedidos.
# La hoja debe estar compartida con el correo client_email del service account.
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1o1zvFzeOsGkDdLQbvEBvMyK6avLiMVMj04Ic0J2bzSw/edit?usp=sharing"
GOOGLE_SHEET_NAME = "Pedidos"

CORREO_DESTINO = os.getenv("ORDER_NOTIFY_TO", "armando207949779@gmail.com")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

ARCHIVO_ORDENES = Path("ordenes_paltas.csv")
LOGO_PATH = Path("LOGO-PALTA.png")

LOCALIDADES_CERCANAS = ["La Calera", "Quillota", "La Cruz", "Hijuelas"]


# ============================================================
# REGIONES Y COMUNAS
# ============================================================

REGIONES_COMUNAS = {
    "Arica y Parinacota": ["Arica", "Camarones", "General Lagos", "Putre"],
    "Tarapacá": ["Alto Hospicio", "Camiña", "Colchane", "Huara", "Iquique", "Pica", "Pozo Almonte"],
    "Antofagasta": ["Antofagasta", "Calama", "María Elena", "Mejillones", "Ollagüe", "San Pedro de Atacama", "Sierra Gorda", "Taltal", "Tocopilla"],
    "Atacama": ["Alto del Carmen", "Caldera", "Chañaral", "Copiapó", "Diego de Almagro", "Freirina", "Huasco", "Tierra Amarilla", "Vallenar"],
    "Coquimbo": ["Andacollo", "Canela", "Combarbalá", "Coquimbo", "Illapel", "La Higuera", "La Serena", "Los Vilos", "Monte Patria", "Ovalle", "Paihuano", "Punitaqui", "Río Hurtado", "Salamanca", "Vicuña"],
    "Valparaíso": ["Algarrobo", "Cabildo", "Calle Larga", "Cartagena", "Casablanca", "Catemu", "Concón", "El Quisco", "El Tabo", "Hijuelas", "Isla de Pascua", "Juan Fernández", "La Calera", "La Cruz", "La Ligua", "Limache", "Llaillay", "Los Andes", "Nogales", "Olmué", "Panquehue", "Papudo", "Petorca", "Puchuncaví", "Putaendo", "Quillota", "Quilpué", "Quintero", "Rinconada", "San Antonio", "San Esteban", "San Felipe", "Santa María", "Santo Domingo", "Valparaíso", "Villa Alemana", "Viña del Mar", "Zapallar"],
    "Metropolitana de Santiago": ["Alhué", "Buin", "Calera de Tango", "Cerrillos", "Cerro Navia", "Colina", "Conchalí", "Curacaví", "El Bosque", "El Monte", "Estación Central", "Huechuraba", "Independencia", "Isla de Maipo", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Lampa", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "María Pinto", "Melipilla", "Ñuñoa", "Padre Hurtado", "Paine", "Pedro Aguirre Cerda", "Peñaflor", "Peñalolén", "Pirque", "Providencia", "Pudahuel", "Puente Alto", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Bernardo", "San Joaquín", "San José de Maipo", "San Miguel", "San Pedro", "San Ramón", "Santiago", "Talagante", "Tiltil", "Vitacura"],
    "O'Higgins": ["Chépica", "Codegua", "Coinco", "Coltauco", "Doñihue", "Graneros", "La Estrella", "Las Cabras", "Litueche", "Lolol", "Machalí", "Malloa", "Marchihue", "Mostazal", "Nancagua", "Navidad", "Olivar", "Palmilla", "Paredones", "Peralillo", "Peumo", "Pichidegua", "Pichilemu", "Placilla", "Pumanque", "Quinta de Tilcoco", "Rancagua", "Rengo", "Requínoa", "San Fernando", "San Vicente", "Santa Cruz"],
    "Maule": ["Cauquenes", "Chanco", "Colbún", "Constitución", "Curepto", "Curicó", "Empedrado", "Hualañé", "Licantén", "Linares", "Longaví", "Maule", "Molina", "Parral", "Pelarco", "Pelluhue", "Pencahue", "Rauco", "Retiro", "Río Claro", "Romeral", "Sagrada Familia", "San Clemente", "San Javier", "San Rafael", "Talca", "Teno", "Vichuquén", "Villa Alegre", "Yerbas Buenas"],
    "Ñuble": ["Bulnes", "Chillán", "Chillán Viejo", "Cobquecura", "Coelemu", "Coihueco", "El Carmen", "Ninhue", "Ñiquén", "Pemuco", "Pinto", "Portezuelo", "Quillón", "Quirihue", "Ránquil", "San Carlos", "San Fabián", "San Ignacio", "San Nicolás", "Treguaco", "Yungay"],
    "Biobío": ["Alto Biobío", "Antuco", "Arauco", "Cabrero", "Cañete", "Chiguayante", "Concepción", "Contulmo", "Coronel", "Curanilahue", "Florida", "Hualpén", "Hualqui", "Laja", "Lebu", "Los Álamos", "Los Ángeles", "Lota", "Mulchén", "Nacimiento", "Negrete", "Penco", "Quilaco", "Quilleco", "San Pedro de la Paz", "San Rosendo", "Santa Bárbara", "Santa Juana", "Talcahuano", "Tirúa", "Tomé", "Tucapel", "Yumbel"],
    "La Araucanía": ["Angol", "Carahue", "Cholchol", "Collipulli", "Cunco", "Curacautín", "Curarrehue", "Ercilla", "Freire", "Galvarino", "Gorbea", "Lautaro", "Loncoche", "Lonquimay", "Los Sauces", "Lumaco", "Melipeuco", "Nueva Imperial", "Padre Las Casas", "Perquenco", "Pitrufquén", "Pucón", "Purén", "Renaico", "Saavedra", "Temuco", "Teodoro Schmidt", "Toltén", "Traiguén", "Victoria", "Vilcún", "Villarrica"],
    "Los Ríos": ["Corral", "Futrono", "La Unión", "Lago Ranco", "Lanco", "Los Lagos", "Máfil", "Mariquina", "Paillaco", "Panguipulli", "Río Bueno", "Valdivia"],
    "Los Lagos": ["Ancud", "Calbuco", "Castro", "Chaitén", "Chonchi", "Cochamó", "Curaco de Vélez", "Dalcahue", "Fresia", "Frutillar", "Futaleufú", "Hualaihué", "Llanquihue", "Los Muermos", "Maullín", "Osorno", "Palena", "Puerto Montt", "Puerto Octay", "Puerto Varas", "Puqueldón", "Purranque", "Puyehue", "Queilén", "Quellón", "Quemchi", "Quinchao", "Río Negro", "San Juan de la Costa", "San Pablo"],
    "Aysén": ["Aysén", "Chile Chico", "Cisnes", "Cochrane", "Coyhaique", "Guaitecas", "Lago Verde", "O'Higgins", "Río Ibáñez", "Tortel"],
    "Magallanes": ["Antártica", "Cabo de Hornos", "Laguna Blanca", "Natales", "Porvenir", "Primavera", "Punta Arenas", "Río Verde", "San Gregorio", "Timaukel", "Torres del Paine"],
}


# ============================================================
# FUNCIONES
# ============================================================

def formato_pesos(valor: int) -> str:
    return f"${valor:,.0f}".replace(",", ".")


def calcular_total(tipo_palta: str, kilos: float) -> int:
    return int(round(PRECIOS_PALTA[tipo_palta] * kilos))


def mostrar_logo_centrado(path: Path, ancho_px: int = 112) -> None:
    if not path.exists():
        return

    extension = path.suffix.replace(".", "").lower()
    if extension == "jpg":
        extension = "jpeg"

    imagen_base64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    st.markdown(
        f"""
        <div class="logo-wrap">
            <img src="data:image/{extension};base64,{imagen_base64}" width="{ancho_px}" />
        </div>
        """,
        unsafe_allow_html=True,
    )


def cambiar_paso(nuevo_paso: int) -> None:
    st.session_state.paso = max(1, min(4, nuevo_paso))


def guardar_en_estado(**kwargs) -> None:
    for clave, valor in kwargs.items():
        st.session_state[clave] = valor


def columnas_pedidos() -> list[str]:
    return [
        "folio",
        "fecha_registro",
        "tipo_palta",
        "kilos",
        "precio_por_kg",
        "total_paltas",
        "modalidad_entrega",
        "region",
        "comuna",
        "poblacion",
        "calle",
        "numero",
        "nombre",
        "whatsapp",
        "estado",
    ]


def guardar_orden_csv(datos: dict) -> None:
    existe = ARCHIVO_ORDENES.exists()
    columnas = columnas_pedidos()

    with ARCHIVO_ORDENES.open("a", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas)
        if not existe:
            writer.writeheader()
        writer.writerow(datos)


def obtener_worksheet_google_sheets():
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        service_account_info = dict(st.secrets["gcp_service_account"])
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=scopes,
        )

        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_url(GOOGLE_SHEET_URL)

        try:
            worksheet = spreadsheet.worksheet(GOOGLE_SHEET_NAME)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=GOOGLE_SHEET_NAME,
                rows=1000,
                cols=len(columnas_pedidos()),
            )

        return worksheet, None
    except Exception as error:
        return None, str(error)


def guardar_orden_google_sheets(datos: dict) -> tuple[bool, str]:
    worksheet, error = obtener_worksheet_google_sheets()

    if worksheet is None:
        return False, error or "No se pudo conectar con Google Sheets."

    columnas = columnas_pedidos()

    try:
        valores_existentes = worksheet.get_all_values()

        if not valores_existentes:
            worksheet.append_row(columnas)

        fila = [datos.get(columna, "") for columna in columnas]
        worksheet.append_row(fila, value_input_option="USER_ENTERED")

        return True, "Solicitud guardada en Google Sheets."
    except Exception as error:
        return False, str(error)


def guardar_orden(datos: dict) -> tuple[bool, str]:
    google_ok, google_msg = guardar_orden_google_sheets(datos)

    # Respaldo local para no perder pedidos si Google Sheets no está configurado.
    if not google_ok:
        guardar_orden_csv(datos)
        return False, google_msg

    return True, google_msg


def crear_cuerpo_correo(datos: dict) -> str:
    return f"""
Nueva solicitud de pedido de paltas.

FOLIO
{datos["folio"]}

PEDIDO
Tipo de palta: {datos["tipo_palta"]}
Kilos: {datos["kilos"]} kg
Precio por kg: {formato_pesos(datos["precio_por_kg"])}
Total paltas: {formato_pesos(datos["total_paltas"])}

ENTREGA
Modalidad: {datos["modalidad_entrega"]}
Región: {datos["region"] or "No aplica"}
Comuna: {datos["comuna"] or "No aplica"}
Población / sector: {datos["poblacion"] or "No informado"}
Calle: {datos["calle"] or "No informado"}
Número: {datos["numero"] or "No informado"}

CONTACTO
Nombre: {datos["nombre"]}
WhatsApp: {datos["whatsapp"]}

TRANSFERENCIA
Titular: {TITULAR}
RUT: {RUT}
Banco: {BANCO}
Tipo de cuenta: {TIPO_CUENTA}
Monto sugerido: {formato_pesos(datos["total_paltas"])}

IMPORTANTE
El monto corresponde a paltas.
Si corresponde despacho, el valor de despacho se coordina aparte.

Estado: {datos["estado"]}
Fecha registro: {datos["fecha_registro"]}
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
    return f"""Hola {datos["nombre"]}, recibimos tu solicitud de pedido de paltas.

Pedido:
• Tipo: {datos["tipo_palta"]}
• Cantidad: {datos["kilos"]} kg
• Precio por kg: {formato_pesos(datos["precio_por_kg"])}
• Total paltas: {formato_pesos(datos["total_paltas"])}

Entrega:
• Modalidad: {datos["modalidad_entrega"]}
• Región: {datos["region"] or "No aplica"}
• Comuna: {datos["comuna"] or "No aplica"}

Datos de transferencia:
• Titular: {TITULAR}
• RUT: {RUT}
• Banco: {BANCO}
• Tipo de cuenta: {TIPO_CUENTA}
• Monto sugerido: {formato_pesos(datos["total_paltas"])}

Importante: el monto corresponde a paltas. Si corresponde despacho, se coordina aparte por WhatsApp.

Cuando transfieras, envíanos el comprobante por WhatsApp."""


def link_whatsapp_negocio(datos: dict) -> str:
    mensaje = f"""Nueva solicitud de pedido de paltas.

Pedido:
• Tipo: {datos["tipo_palta"]}
• Cantidad: {datos["kilos"]} kg
• Precio por kg: {formato_pesos(datos["precio_por_kg"])}
• Total paltas: {formato_pesos(datos["total_paltas"])}

Entrega:
• Modalidad: {datos["modalidad_entrega"]}
• Región: {datos["region"] or "No aplica"}
• Comuna: {datos["comuna"] or "No aplica"}
• Población / sector: {datos["poblacion"] or "No informado"}
• Calle: {datos["calle"] or "No informado"}
• Número: {datos["numero"] or "No informado"}

Contacto:
• Nombre: {datos["nombre"]}
• WhatsApp: {datos["whatsapp"]}

Folio: {datos["folio"]}

Quiero coordinar la entrega."""
    return f"https://wa.me/{WHATSAPP_NEGOCIO}?text={quote(mensaje)}"



# ============================================================
# CONFIGURACIÓN VISUAL
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
    .block-container {
        max-width: 520px;
        padding-top: 1.85rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 2rem;
    }
    .logo-wrap {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 0.85rem;
        margin-bottom: 0.2rem;
    }
    .main-title {
        text-align: center;
        color: #14532d;
        font-size: 1.75rem;
        font-weight: 950;
        line-height: 1.05;
        margin: 0.15rem 0 0.2rem 0;
    }
    .subtitle {
        text-align: center;
        color: #4b5563;
        font-size: 0.94rem;
        line-height: 1.35;
        margin-bottom: 0.9rem;
    }
    .step-pill {
        text-align: center;
        color: #166534;
        background: #dcfce7;
        border: 1px solid #bbf7d0;
        border-radius: 999px;
        padding: 0.42rem 0.9rem;
        font-weight: 900;
        font-size: 0.88rem;
        margin: 0.25rem auto 0.9rem auto;
        width: fit-content;
    }
    .summary-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 18px;
        padding: 1rem;
        margin: 0.8rem 0;
    }
    .total-card {
        background: #ecfdf5;
        border: 1px solid #86efac;
        border-radius: 18px;
        padding: 1rem;
        text-align: center;
        margin: 0.8rem 0;
    }
    .total-label {
        color: #166534;
        font-size: 0.9rem;
        font-weight: 800;
    }
    .total-value {
        color: #14532d;
        font-size: 2.15rem;
        font-weight: 950;
        line-height: 1.05;
    }
    .soft-note {
        color: #4b5563;
        font-size: 0.88rem;
        line-height: 1.3;
        margin-top: 0.35rem;
    }
    .low-priority {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 0.85rem;
        color: #4b5563;
        font-size: 0.92rem;
    }
    .stButton button, .stDownloadButton button {
        width: 100%;
        min-height: 3rem;
        border-radius: 14px;
        font-weight: 850;
    }
    .whatsapp-btn {
        display: block;
        width: 100%;
        text-align: center;
        background: #16a34a;
        color: white !important;
        padding: 0.9rem 1rem;
        border-radius: 14px;
        font-weight: 900;
        text-decoration: none !important;
        margin: 0.8rem 0 0.8rem 0;
    }
    div[data-baseweb="select"] > div {
        min-height: 3rem;
        border-radius: 12px;
    }
    input, textarea {
        border-radius: 12px !important;
    }
    label {
        font-weight: 800 !important;
    }
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


# ============================================================
# PASO 1: PEDIDO
# ============================================================

if st.session_state.paso == 1:
    st.subheader("¿Cuántos kilos quieres?")

    tipo_palta = st.radio(
        "Tipo de palta",
        list(PRECIOS_PALTA.keys()),
        horizontal=True,
        key="tipo_palta_widget",
    )

    kilos = st.number_input(
        "Kilos",
        min_value=KILOS_MINIMOS,
        value=float(st.session_state.get("kilos", KILOS_MINIMOS)),
        step=0.5,
        key="kilos_widget",
    )

    precio_kg = PRECIOS_PALTA[tipo_palta]
    total = calcular_total(tipo_palta, kilos)

    st.markdown(
        f"""
        <div class="total-card">
            <div class="total-label">{tipo_palta} · {formato_pesos(precio_kg)} por kg</div>
            <div class="total-value">{formato_pesos(total)}</div>
            <div class="soft-note">Este es el valor total de las paltas por la cantidad seleccionada.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Continuar", key="btn_paso1"):
        guardar_en_estado(
            tipo_palta=tipo_palta,
            kilos=kilos,
            precio_kg=precio_kg,
            total_paltas=total,
        )
        cambiar_paso(2)
        st.rerun()


# ============================================================
# PASO 2: UBICACIÓN Y MODALIDAD
# ============================================================

elif st.session_state.paso == 2:
    st.subheader("¿Cómo quieres recibirlas?")

    modalidad_entrega = st.radio(
        "Elige una opción",
        [
            "Retiro sin costo",
            "Envío a domicilio en La Calera, Quillota, La Cruz o Hijuelas",
            "Otra comuna o región - cotizar envío",
        ],
        captions=[
            "Ideal si puedes retirar en punto acordado.",
            "Disponible para zona cercana. El despacho se coordina por WhatsApp.",
            "Opción para pedidos menos frecuentes o al por mayor.",
        ],
        key="modalidad_entrega_widget",
    )

    region = ""
    comuna = ""
    poblacion = ""
    calle = ""
    numero = ""

    if modalidad_entrega == "Retiro sin costo":
        st.info("Retiro sin costo de despacho. Coordinaremos el punto por WhatsApp.")
        region = "Valparaíso"
        comuna = st.selectbox(
            "Localidad de retiro preferida",
            LOCALIDADES_CERCANAS,
            key="comuna_retiro_widget",
        )

    elif modalidad_entrega == "Envío a domicilio en La Calera, Quillota, La Cruz o Hijuelas":
        region = "Valparaíso"
        comuna = st.selectbox(
            "Localidad",
            LOCALIDADES_CERCANAS,
            key="comuna_local_widget",
        )

        poblacion = st.text_input("Población / sector", placeholder="Ej: Artificio, Boco, Pocochay", key="poblacion_local_widget")
        calle = st.text_input("Calle", placeholder="Ej: Los Aromos", key="calle_local_widget")
        numero = st.text_input("Número", placeholder="Ej: 123", key="numero_local_widget")

    else:
        st.markdown(
            """
            <div class="low-priority">
            Para otras comunas o regiones, el envío se cotiza aparte. Esta opción está pensada principalmente para pedidos al por mayor.
            </div>
            """,
            unsafe_allow_html=True,
        )

        regiones = list(REGIONES_COMUNAS.keys())
        region = st.selectbox(
            "Región",
            regiones,
            index=regiones.index("Valparaíso"),
            key="region_otras_widget",
        )

        comuna = st.selectbox(
            "Comuna",
            REGIONES_COMUNAS[region],
            key=f"comuna_otras_widget_{region}",
        )

        poblacion = st.text_input("Población / sector", placeholder="Ej: sector o referencia", key="poblacion_otra_widget")
        calle = st.text_input("Calle", placeholder="Ej: Los Aromos", key="calle_otra_widget")
        numero = st.text_input("Número", placeholder="Ej: 123", key="numero_otra_widget")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Volver", key="btn_volver_paso2"):
            cambiar_paso(1)
            st.rerun()
    with col2:
        if st.button("Continuar", key="btn_paso2"):
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
                guardar_en_estado(
                    modalidad_entrega=modalidad_entrega,
                    region=region,
                    comuna=comuna,
                    poblacion=poblacion.strip(),
                    calle=calle.strip(),
                    numero=numero.strip(),
                )
                cambiar_paso(3)
                st.rerun()


# ============================================================
# PASO 3: CONTACTO
# ============================================================

elif st.session_state.paso == 3:
    st.subheader("Datos de contacto")

    nombre = st.text_input("Nombre", placeholder="Tu nombre", key="nombre_widget")
    whatsapp = st.text_input("WhatsApp", placeholder="+56 9 1234 5678", key="whatsapp_widget")

    st.markdown(
        f"""
        <div class="summary-card">
            <b>Resumen rápido</b><br>
            {st.session_state.get("kilos", KILOS_MINIMOS)} kg de palta {st.session_state.get("tipo_palta", "")}<br>
            Total paltas: <b>{formato_pesos(int(st.session_state.get("total_paltas", 0)))}</b><br>
            Modalidad: {st.session_state.get("modalidad_entrega", "")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Volver", key="btn_volver_paso3"):
            cambiar_paso(2)
            st.rerun()
    with col2:
        if st.button("Ver transferencia", key="btn_paso3"):
            errores = []
            if not nombre.strip():
                errores.append("Nombre")
            if not whatsapp.strip():
                errores.append("WhatsApp")

            if errores:
                st.error("Falta completar: " + ", ".join(errores))
            else:
                guardar_en_estado(nombre=nombre.strip(), whatsapp=whatsapp.strip())
                cambiar_paso(4)
                st.rerun()


# ============================================================
# PASO 4: TRANSFERENCIA Y REGISTRO
# ============================================================

elif st.session_state.paso == 4:
    st.subheader("Transferencia")

    datos_previos_ok = all(
        clave in st.session_state
        for clave in ["tipo_palta", "kilos", "precio_kg", "total_paltas", "modalidad_entrega", "nombre", "whatsapp"]
    )

    if not datos_previos_ok:
        campos_necesarios = {
            "tipo_palta": "Tipo de palta",
            "kilos": "Cantidad de kilos",
            "precio_kg": "Precio por kilo",
            "total_paltas": "Total del pedido",
            "modalidad_entrega": "Modalidad de entrega",
            "nombre": "Nombre",
            "whatsapp": "WhatsApp",
        }
        faltantes = [
            nombre_campo
            for clave, nombre_campo in campos_necesarios.items()
            if clave not in st.session_state
        ]

        st.warning("Faltan datos para terminar la solicitud.")
        st.write("Datos faltantes: **" + ", ".join(faltantes) + "**")
        st.caption("Esto puede pasar si se actualiza la página, se abre directo el paso final o Streamlit reinicia la sesión.")

        if st.button("Completar desde el inicio", key="btn_reiniciar_incompleto"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.paso = 1
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

        confirmar = st.checkbox("Confirmo y quiero registrar esta solicitud.", key="confirmar_registro_widget")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Volver", key="btn_volver_paso4"):
                cambiar_paso(3)
                st.rerun()

        with col2:
            if st.button("Registrar", key="btn_registrar"):
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

                    sheets_ok, sheets_mensaje = guardar_orden(datos)
                    correo_ok, mensaje_estado = enviar_correo(datos)

                    st.success("Solicitud registrada correctamente.")

                    if sheets_ok:
                        st.caption("Pedido guardado en Google Sheets.")
                    else:
                        st.warning("Pedido guardado como respaldo local, pero Google Sheets aún no está configurado correctamente.")
                        st.caption(f"Detalle técnico: {sheets_mensaje}")

                    whatsapp_url = link_whatsapp_negocio(datos)
                    st.markdown(
                        f'<a class="whatsapp-btn" href="{whatsapp_url}" target="_blank">Enviar pedido por WhatsApp</a>',
                        unsafe_allow_html=True,
                    )
                    st.caption("Toca el botón para enviar la solicitud directamente al WhatsApp del negocio.")

                    if correo_ok:
                        st.caption(mensaje_estado)

                    st.download_button(
                        "Descargar solicitud",
                        data=crear_cuerpo_correo(datos),
                        file_name=f"{folio}.txt",
                        mime="text/plain",
                        key="descargar_solicitud_final",
                    )

                    if st.button("Crear nueva solicitud", key="btn_nueva_solicitud"):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.session_state.paso = 1
                        st.rerun()
