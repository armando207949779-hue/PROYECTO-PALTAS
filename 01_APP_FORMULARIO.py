import os
import csv
import base64
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import streamlit as st


# ============================================================
# CONFIGURACIÓN DEL NEGOCIO
# ============================================================

PRECIO_POR_KG = 2500
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


# ============================================================
# REGIONES Y COMUNAS DE CHILE
# Fuente referencial: BCN / SUBDERE / MMA
# ============================================================

REGIONES_COMUNAS = {
    "Arica y Parinacota": [
        "Arica", "Camarones", "General Lagos", "Putre"
    ],
    "Tarapacá": [
        "Alto Hospicio", "Camiña", "Colchane", "Huara", "Iquique", "Pica",
        "Pozo Almonte"
    ],
    "Antofagasta": [
        "Antofagasta", "Calama", "María Elena", "Mejillones", "Ollagüe",
        "San Pedro de Atacama", "Sierra Gorda", "Taltal", "Tocopilla"
    ],
    "Atacama": [
        "Alto del Carmen", "Caldera", "Chañaral", "Copiapó",
        "Diego de Almagro", "Freirina", "Huasco", "Tierra Amarilla",
        "Vallenar"
    ],
    "Coquimbo": [
        "Andacollo", "Canela", "Combarbalá", "Coquimbo", "Illapel",
        "La Higuera", "La Serena", "Los Vilos", "Monte Patria", "Ovalle",
        "Paihuano", "Punitaqui", "Río Hurtado", "Salamanca", "Vicuña"
    ],
    "Valparaíso": [
        "Algarrobo", "Cabildo", "Calle Larga", "Cartagena", "Casablanca",
        "Catemu", "Concón", "El Quisco", "El Tabo", "Hijuelas",
        "Isla de Pascua", "Juan Fernández", "La Calera", "La Cruz",
        "La Ligua", "Limache", "Llaillay", "Los Andes", "Nogales", "Olmué",
        "Panquehue", "Papudo", "Petorca", "Puchuncaví", "Putaendo",
        "Quillota", "Quilpué", "Quintero", "Rinconada", "San Antonio",
        "San Esteban", "San Felipe", "Santa María", "Santo Domingo",
        "Valparaíso", "Villa Alemana", "Viña del Mar", "Zapallar"
    ],
    "Metropolitana de Santiago": [
        "Alhué", "Buin", "Calera de Tango", "Cerrillos", "Cerro Navia",
        "Colina", "Conchalí", "Curacaví", "El Bosque", "El Monte",
        "Estación Central", "Huechuraba", "Independencia", "Isla de Maipo",
        "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina",
        "Lampa", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado",
        "Macul", "Maipú", "María Pinto", "Melipilla", "Ñuñoa",
        "Padre Hurtado", "Paine", "Pedro Aguirre Cerda", "Peñaflor",
        "Peñalolén", "Pirque", "Providencia", "Pudahuel", "Puente Alto",
        "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Bernardo",
        "San Joaquín", "San José de Maipo", "San Miguel", "San Pedro",
        "San Ramón", "Santiago", "Talagante", "Tiltil", "Vitacura"
    ],
    "O'Higgins": [
        "Chépica", "Codegua", "Coinco", "Coltauco", "Doñihue", "Graneros",
        "La Estrella", "Las Cabras", "Litueche", "Lolol", "Machalí",
        "Malloa", "Marchihue", "Mostazal", "Nancagua", "Navidad", "Olivar",
        "Palmilla", "Paredones", "Peralillo", "Peumo", "Pichidegua",
        "Pichilemu", "Placilla", "Pumanque", "Quinta de Tilcoco",
        "Rancagua", "Rengo", "Requínoa", "San Fernando", "San Vicente",
        "Santa Cruz"
    ],
    "Maule": [
        "Cauquenes", "Chanco", "Colbún", "Constitución", "Curepto",
        "Curicó", "Empedrado", "Hualañé", "Licantén", "Linares", "Longaví",
        "Maule", "Molina", "Parral", "Pelarco", "Pelluhue", "Pencahue",
        "Rauco", "Retiro", "Río Claro", "Romeral", "Sagrada Familia",
        "San Clemente", "San Javier", "San Rafael", "Talca", "Teno",
        "Vichuquén", "Villa Alegre", "Yerbas Buenas"
    ],
    "Ñuble": [
        "Bulnes", "Chillán", "Chillán Viejo", "Cobquecura", "Coelemu",
        "Coihueco", "El Carmen", "Ninhue", "Ñiquén", "Pemuco", "Pinto",
        "Portezuelo", "Quillón", "Quirihue", "Ránquil", "San Carlos",
        "San Fabián", "San Ignacio", "San Nicolás", "Treguaco", "Yungay"
    ],
    "Biobío": [
        "Alto Biobío", "Antuco", "Arauco", "Cabrero", "Cañete",
        "Chiguayante", "Concepción", "Contulmo", "Coronel", "Curanilahue",
        "Florida", "Hualpén", "Hualqui", "Laja", "Lebu", "Los Álamos",
        "Los Ángeles", "Lota", "Mulchén", "Nacimiento", "Negrete", "Penco",
        "Quilaco", "Quilleco", "San Pedro de la Paz", "San Rosendo",
        "Santa Bárbara", "Santa Juana", "Talcahuano", "Tirúa", "Tomé",
        "Tucapel", "Yumbel"
    ],
    "La Araucanía": [
        "Angol", "Carahue", "Cholchol", "Collipulli", "Cunco",
        "Curacautín", "Curarrehue", "Ercilla", "Freire", "Galvarino",
        "Gorbea", "Lautaro", "Loncoche", "Lonquimay", "Los Sauces",
        "Lumaco", "Melipeuco", "Nueva Imperial", "Padre Las Casas",
        "Perquenco", "Pitrufquén", "Pucón", "Purén", "Renaico", "Saavedra",
        "Temuco", "Teodoro Schmidt", "Toltén", "Traiguén", "Victoria",
        "Vilcún", "Villarrica"
    ],
    "Los Ríos": [
        "Corral", "Futrono", "La Unión", "Lago Ranco", "Lanco", "Los Lagos",
        "Máfil", "Mariquina", "Paillaco", "Panguipulli", "Río Bueno",
        "Valdivia"
    ],
    "Los Lagos": [
        "Ancud", "Calbuco", "Castro", "Chaitén", "Chonchi", "Cochamó",
        "Curaco de Vélez", "Dalcahue", "Fresia", "Frutillar", "Futaleufú",
        "Hualaihué", "Llanquihue", "Los Muermos", "Maullín", "Osorno",
        "Palena", "Puerto Montt", "Puerto Octay", "Puerto Varas", "Puqueldón",
        "Purranque", "Puyehue", "Queilén", "Quellón", "Quemchi", "Quinchao",
        "Río Negro", "San Juan de la Costa", "San Pablo"
    ],
    "Aysén": [
        "Aysén", "Chile Chico", "Cisnes", "Cochrane", "Coyhaique",
        "Guaitecas", "Lago Verde", "O'Higgins", "Río Ibáñez", "Tortel"
    ],
    "Magallanes": [
        "Antártica", "Cabo de Hornos", "Laguna Blanca", "Natales",
        "Porvenir", "Primavera", "Punta Arenas", "Río Verde", "San Gregorio",
        "Timaukel", "Torres del Paine"
    ],
}

COMUNAS_RETIRO_GRATIS = ["Quillota", "La Calera"]
REGIONES_DESPACHO_A_SOLICITUD = ["Valparaíso", "Metropolitana de Santiago"]


# ============================================================
# FUNCIONES
# ============================================================

def formato_pesos(valor: int) -> str:
    return f"${valor:,.0f}".replace(",", ".")


def calcular_total(kilos: float) -> int:
    return int(round(kilos * PRECIO_POR_KG))


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


def opciones_entrega(region: str, comuna: str) -> list[str]:
    opciones = []

    if comuna in COMUNAS_RETIRO_GRATIS:
        opciones.append("Retiro en Quillota / La Calera - sin costo de despacho")

    if region in REGIONES_DESPACHO_A_SOLICITUD:
        opciones.append("Despacho a solicitud - Quinta Región / Santiago")

    if region not in REGIONES_DESPACHO_A_SOLICITUD:
        opciones.append("Cotizar envío a otra región - al por mayor")

    if not opciones:
        opciones.append("Coordinar por WhatsApp")

    return opciones


def nota_entrega(region: str, tipo_entrega: str) -> str:
    if tipo_entrega.startswith("Retiro"):
        return "Retiro disponible sin costo de despacho. La coordinación final se realiza por WhatsApp."

    if tipo_entrega.startswith("Despacho"):
        return "El valor mostrado corresponde solo a paltas. El despacho se coordina y confirma por WhatsApp."

    if tipo_entrega.startswith("Cotizar"):
        return "Para otras regiones se cotiza envío al por mayor. El formulario deja registrada la solicitud."

    return "La entrega se coordina después por WhatsApp."


def guardar_orden(datos: dict) -> None:
    existe = ARCHIVO_ORDENES.exists()

    columnas = [
        "folio",
        "fecha_registro",
        "nombre",
        "whatsapp",
        "correo",
        "region",
        "comuna",
        "tipo_entrega",
        "direccion_referencia",
        "kilos",
        "precio_por_kg",
        "total_paltas",
        "fecha_preferida",
        "comentarios",
        "estado",
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
{datos["folio"]}

CLIENTE
Nombre: {datos["nombre"]}
WhatsApp: {datos["whatsapp"]}
Correo: {datos["correo"] or "No informado"}

UBICACIÓN Y ENTREGA
Región: {datos["region"]}
Comuna: {datos["comuna"]}
Modalidad: {datos["tipo_entrega"]}
Dirección o referencia: {datos["direccion_referencia"] or "No informado"}

PEDIDO
Kilos solicitados: {datos["kilos"]} kg
Precio por kg: {formato_pesos(PRECIO_POR_KG)}
Total paltas: {formato_pesos(datos["total_paltas"])}
Fecha preferida: {datos["fecha_preferida"] or "No informada"}

COMENTARIOS
{datos["comentarios"] or "Sin comentarios"}

TRANSFERENCIA PARA CLIENTE
Titular: {TITULAR}
RUT: {RUT}
Banco: {BANCO}
Tipo de cuenta: {TIPO_CUENTA}
Monto sugerido: {formato_pesos(datos["total_paltas"])}

IMPORTANTE
El monto mostrado corresponde a paltas.
Si corresponde despacho, se coordina o cotiza aparte según la zona.

Estado interno: {datos["estado"]}
Fecha registro: {datos["fecha_registro"]}
"""


def enviar_correo(datos: dict) -> tuple[bool, str]:
    if not SMTP_USER or not SMTP_PASSWORD:
        return False, "Solicitud guardada. Correo no enviado porque falta configurar SMTP_USER y SMTP_PASSWORD."

    mensaje = EmailMessage()
    mensaje["Subject"] = f"Solicitud paltas {datos['folio']} - {datos['nombre']} - {formato_pesos(datos['total_paltas'])}"
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

Resumen:
• Cantidad: {datos["kilos"]} kg
• Precio por kg: {formato_pesos(PRECIO_POR_KG)}
• Total paltas: {formato_pesos(datos["total_paltas"])}

Entrega:
• Región: {datos["region"]}
• Comuna: {datos["comuna"]}
• Modalidad: {datos["tipo_entrega"]}

Datos de transferencia:
• Titular: {TITULAR}
• RUT: {RUT}
• Banco: {BANCO}
• Tipo de cuenta: {TIPO_CUENTA}
• Monto sugerido: {formato_pesos(datos["total_paltas"])}

Importante:
El monto corresponde a paltas. Si corresponde despacho, se coordina o cotiza aparte.

Cuando transfieras, envíanos el comprobante por WhatsApp.
Luego coordinamos la logística final."""


# ============================================================
# INTERFAZ OPTIMIZADA PARA TELÉFONO
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
        max-width: 560px;
        padding-top: 0.75rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 2rem;
    }
    .logo-wrap {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 0.15rem;
        margin-bottom: 0.25rem;
    }
    .title-mobile {
        text-align: center;
        font-size: 1.85rem;
        font-weight: 900;
        line-height: 1.05;
        margin: 0.15rem 0 0.25rem 0;
        color: #14532d;
    }
    .subtitle-mobile {
        text-align: center;
        color: #4b5563;
        font-size: 0.96rem;
        line-height: 1.35;
        margin-bottom: 1rem;
    }
    .quick-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.9rem;
        text-align: center;
    }
    .quick-label {
        color: #166534;
        font-size: 0.86rem;
        font-weight: 700;
    }
    .quick-value {
        font-size: 1.5rem;
        color: #14532d;
        font-weight: 900;
    }
    .total-card {
        background: #ecfdf5;
        border: 1px solid #86efac;
        border-radius: 18px;
        padding: 1rem;
        text-align: center;
        margin: 0.75rem 0 0.75rem 0;
    }
    .total-label {
        color: #166534;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .total-value {
        color: #14532d;
        font-size: 2.05rem;
        font-weight: 950;
        line-height: 1.1;
    }
    .soft-note {
        color: #4b5563;
        font-size: 0.88rem;
        line-height: 1.3;
        margin-top: 0.35rem;
    }
    div[data-testid="stForm"] {
        border: 0;
        padding: 0;
    }
    div[data-testid="stForm"] label {
        font-weight: 700;
    }
    .stButton button, .stDownloadButton button {
        width: 100%;
        border-radius: 14px;
        min-height: 3rem;
        font-weight: 800;
    }
    div[data-baseweb="select"] > div {
        border-radius: 12px;
        min-height: 3rem;
    }
    input, textarea {
        border-radius: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

mostrar_logo_centrado(LOGO_PATH, ancho_px=118)

st.markdown(
    """
    <div class="title-mobile">Solicitud Pedido<br>Paltas</div>
    <div class="subtitle-mobile">
        Formulario rápido para registrar tu pedido. La logística se coordina después por WhatsApp.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="quick-card">
        <div class="quick-label">Precio por kilo</div>
        <div class="quick-value">{formato_pesos(PRECIO_POR_KG)}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("solicitud_paltas_v3", clear_on_submit=False):
    st.markdown("### 1. Contacto")

    nombre = st.text_input("Nombre", placeholder="Tu nombre")
    whatsapp = st.text_input("WhatsApp", placeholder="+56 9 1234 5678")
    correo = st.text_input("Correo opcional", placeholder="correo@gmail.com")

    st.markdown("### 2. Ubicación")

    regiones = list(REGIONES_COMUNAS.keys())
    region_default = regiones.index("Valparaíso") if "Valparaíso" in regiones else 0

    region = st.selectbox(
        "Región",
        regiones,
        index=region_default,
        key="region_select",
    )

    comunas_disponibles = REGIONES_COMUNAS[region]

    comuna = st.selectbox(
        "Comuna",
        comunas_disponibles,
        key=f"comuna_select_{region}",
    )

    opciones = opciones_entrega(region, comuna)

    tipo_entrega = st.radio(
        "Modalidad",
        opciones,
        captions=[nota_entrega(region, opcion) for opcion in opciones],
    )

    pedir_direccion = tipo_entrega.startswith("Despacho") or tipo_entrega.startswith("Cotizar")

    direccion_referencia = ""
    if pedir_direccion:
        direccion_referencia = st.text_input(
            "Dirección o referencia",
            placeholder="Calle, sector o referencia para coordinar",
        )

    st.markdown("### 3. Pedido")

    kilos = st.number_input(
        "Kilos",
        min_value=KILOS_MINIMOS,
        value=KILOS_MINIMOS,
        step=0.5,
    )

    fecha_preferida = st.date_input(
        "Fecha preferida opcional",
        value=None,
    )

    comentarios = st.text_area(
        "Comentario opcional",
        placeholder="Ej: paltas más maduras, horario ideal, pedido mayorista, etc.",
        height=80,
    )

    total = calcular_total(kilos)

    st.markdown(
        f"""
        <div class="total-card">
            <div class="total-label">Total paltas</div>
            <div class="total-value">{formato_pesos(total)}</div>
            <div class="soft-note">{nota_entrega(region, tipo_entrega)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    confirmar = st.checkbox("Confirmo que mis datos están correctos.")
    enviar = st.form_submit_button("Enviar solicitud")

if enviar:
    errores = []

    if not nombre.strip():
        errores.append("Nombre")
    if not whatsapp.strip():
        errores.append("WhatsApp")
    if pedir_direccion and not direccion_referencia.strip():
        errores.append("Dirección o referencia")
    if not confirmar:
        errores.append("Confirmación")

    if errores:
        st.error("Falta revisar: " + ", ".join(errores))
    else:
        folio = "PALTA-" + datetime.now().strftime("%Y%m%d-%H%M%S")

        datos = {
            "folio": folio,
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nombre": nombre.strip(),
            "whatsapp": whatsapp.strip(),
            "correo": correo.strip(),
            "region": region,
            "comuna": comuna,
            "tipo_entrega": tipo_entrega,
            "direccion_referencia": direccion_referencia.strip(),
            "kilos": kilos,
            "precio_por_kg": PRECIO_POR_KG,
            "total_paltas": total,
            "fecha_preferida": str(fecha_preferida) if fecha_preferida else "",
            "comentarios": comentarios.strip(),
            "estado": "Solicitud recibida",
        }

        guardar_orden(datos)
        correo_ok, mensaje_estado = enviar_correo(datos)

        st.success("Solicitud enviada.")
        st.caption(mensaje_estado)

        st.markdown("### Transferencia")
        st.write(f"**Titular:** {TITULAR}")
        st.write(f"**RUT:** {RUT}")
        st.write(f"**Banco:** {BANCO}")
        st.write(f"**Tipo de cuenta:** {TIPO_CUENTA}")
        st.write(f"**Monto sugerido:** {formato_pesos(total)}")

        st.markdown("### Mensaje WhatsApp")
        st.text_area(
            "Copia este mensaje para el cliente",
            value=mensaje_para_cliente(datos),
            height=300,
        )

        st.download_button(
            "Descargar solicitud",
            data=crear_cuerpo_correo(datos),
            file_name=f"{folio}.txt",
            mime="text/plain",
        )

with st.expander("Registro interno"):
    if ARCHIVO_ORDENES.exists():
        with ARCHIVO_ORDENES.open("rb") as archivo:
            st.download_button(
                "Descargar solicitudes CSV",
                data=archivo,
                file_name="ordenes_paltas.csv",
                mime="text/csv",
            )
    else:
        st.caption("Aún no hay solicitudes registradas.")
