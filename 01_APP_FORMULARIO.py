import os
import csv
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import streamlit as st


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

# Deja el precio fijo en el código.
# Cambia este valor cuando quieras actualizar el precio por kilo.
PRECIO_POR_KG = 2500

# Pedido mínimo sugerido.
KILOS_MINIMOS = 1.0

# Datos de transferencia.
TITULAR = "Enrique Armando Brun Urrutia"
RUT = "20.794.977-9"
BANCO = "Banco Estado"
TIPO_CUENTA = "Cuenta RUT"

# Correo donde quieres recibir aviso del pedido.
CORREO_DESTINO = os.getenv("ORDER_NOTIFY_TO", "armando207949779@gmail.com")

# Configuración de correo.
# Para Gmail usa una clave de aplicación, no tu contraseña normal.
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

ARCHIVO_ORDENES = Path("ordenes_paltas.csv")
LOGO_PATH = Path("LOGO-PALTA.png")


# ============================================================
# DICCIONARIO REGIONES Y COMUNAS
# ============================================================

REGIONES_COMUNAS = {
    "Arica y Parinacota": [
        "Arica", "Camarones", "Putre", "General Lagos"
    ],
    "Tarapacá": [
        "Iquique", "Alto Hospicio", "Pozo Almonte", "Camiña", "Colchane",
        "Huara", "Pica"
    ],
    "Antofagasta": [
        "Antofagasta", "Mejillones", "Sierra Gorda", "Taltal", "Calama",
        "Ollagüe", "San Pedro de Atacama", "Tocopilla", "María Elena"
    ],
    "Atacama": [
        "Copiapó", "Caldera", "Tierra Amarilla", "Chañaral", "Diego de Almagro",
        "Vallenar", "Alto del Carmen", "Freirina", "Huasco"
    ],
    "Coquimbo": [
        "La Serena", "Coquimbo", "Andacollo", "La Higuera", "Paihuano",
        "Vicuña", "Illapel", "Canela", "Los Vilos", "Salamanca", "Ovalle",
        "Combarbalá", "Monte Patria", "Punitaqui", "Río Hurtado"
    ],
    "Valparaíso": [
        "Valparaíso", "Casablanca", "Concón", "Juan Fernández", "Puchuncaví",
        "Quintero", "Viña del Mar", "Isla de Pascua", "Los Andes", "Calle Larga",
        "Rinconada", "San Esteban", "La Ligua", "Cabildo", "Papudo", "Petorca",
        "Zapallar", "Quillota", "Calera", "Hijuelas", "La Cruz", "Nogales",
        "San Antonio", "Algarrobo", "Cartagena", "El Quisco", "El Tabo",
        "Santo Domingo", "San Felipe", "Catemu", "Llaillay", "Panquehue",
        "Putaendo", "Santa María", "Quilpué", "Limache", "Olmué", "Villa Alemana"
    ],
    "Metropolitana de Santiago": [
        "Cerrillos", "Cerro Navia", "Conchalí", "El Bosque", "Estación Central",
        "Huechuraba", "Independencia", "La Cisterna", "La Florida", "La Granja",
        "La Pintana", "La Reina", "Las Condes", "Lo Barnechea", "Lo Espejo",
        "Lo Prado", "Macul", "Maipú", "Ñuñoa", "Pedro Aguirre Cerda",
        "Peñalolén", "Providencia", "Pudahuel", "Quilicura", "Quinta Normal",
        "Recoleta", "Renca", "San Joaquín", "San Miguel", "San Ramón",
        "Santiago", "Vitacura", "Puente Alto", "Pirque", "San José de Maipo",
        "Colina", "Lampa", "Tiltil", "San Bernardo", "Buin", "Calera de Tango",
        "Paine", "Melipilla", "Alhué", "Curacaví", "María Pinto", "San Pedro",
        "Talagante", "El Monte", "Isla de Maipo", "Padre Hurtado", "Peñaflor"
    ],
    "O'Higgins": [
        "Rancagua", "Codegua", "Coinco", "Coltauco", "Doñihue", "Graneros",
        "Las Cabras", "Machalí", "Malloa", "Mostazal", "Olivar", "Peumo",
        "Pichidegua", "Quinta de Tilcoco", "Rengo", "Requínoa", "San Vicente",
        "Pichilemu", "La Estrella", "Litueche", "Marchihue", "Navidad",
        "Paredones", "San Fernando", "Chépica", "Chimbarongo", "Lolol",
        "Nancagua", "Palmilla", "Peralillo", "Placilla", "Pumanque",
        "Santa Cruz"
    ],
    "Maule": [
        "Talca", "Constitución", "Curepto", "Empedrado", "Maule", "Pelarco",
        "Pencahue", "Río Claro", "San Clemente", "San Rafael", "Cauquenes",
        "Chanco", "Pelluhue", "Curicó", "Hualañé", "Licantén", "Molina",
        "Rauco", "Romeral", "Sagrada Familia", "Teno", "Vichuquén", "Linares",
        "Colbún", "Longaví", "Parral", "Retiro", "San Javier", "Villa Alegre",
        "Yerbas Buenas"
    ],
    "Ñuble": [
        "Chillán", "Bulnes", "Chillán Viejo", "El Carmen", "Pemuco", "Pinto",
        "Quillón", "San Ignacio", "Yungay", "Quirihue", "Cobquecura", "Coelemu",
        "Ninhue", "Portezuelo", "Ránquil", "Treguaco", "San Carlos", "Coihueco",
        "Ñiquén", "San Fabián", "San Nicolás"
    ],
    "Biobío": [
        "Concepción", "Coronel", "Chiguayante", "Florida", "Hualqui", "Lota",
        "Penco", "San Pedro de la Paz", "Santa Juana", "Talcahuano", "Tomé",
        "Hualpén", "Lebu", "Arauco", "Cañete", "Contulmo", "Curanilahue",
        "Los Álamos", "Tirúa", "Los Ángeles", "Antuco", "Cabrero", "Laja",
        "Mulchén", "Nacimiento", "Negrete", "Quilaco", "Quilleco",
        "San Rosendo", "Santa Bárbara", "Tucapel", "Yumbel", "Alto Biobío"
    ],
    "La Araucanía": [
        "Temuco", "Carahue", "Cunco", "Curarrehue", "Freire", "Galvarino",
        "Gorbea", "Lautaro", "Loncoche", "Melipeuco", "Nueva Imperial",
        "Padre Las Casas", "Perquenco", "Pitrufquén", "Pucón", "Saavedra",
        "Teodoro Schmidt", "Toltén", "Vilcún", "Villarrica", "Cholchol",
        "Angol", "Collipulli", "Curacautín", "Ercilla", "Lonquimay",
        "Los Sauces", "Lumaco", "Purén", "Renaico", "Traiguén", "Victoria"
    ],
    "Los Ríos": [
        "Valdivia", "Corral", "Lanco", "Los Lagos", "Máfil", "Mariquina",
        "Paillaco", "Panguipulli", "La Unión", "Futrono", "Lago Ranco",
        "Río Bueno"
    ],
    "Los Lagos": [
        "Puerto Montt", "Calbuco", "Cochamó", "Fresia", "Frutillar",
        "Los Muermos", "Llanquihue", "Maullín", "Puerto Varas", "Castro",
        "Ancud", "Chonchi", "Curaco de Vélez", "Dalcahue", "Puqueldón",
        "Queilén", "Quellón", "Quemchi", "Quinchao", "Osorno", "Puerto Octay",
        "Purranque", "Puyehue", "Río Negro", "San Juan de la Costa",
        "San Pablo", "Chaitén", "Futaleufú", "Hualaihué", "Palena"
    ],
    "Aysén": [
        "Coyhaique", "Lago Verde", "Aysén", "Cisnes", "Guaitecas",
        "Cochrane", "O'Higgins", "Tortel", "Chile Chico", "Río Ibáñez"
    ],
    "Magallanes": [
        "Punta Arenas", "Laguna Blanca", "Río Verde", "San Gregorio",
        "Cabo de Hornos", "Antártica", "Porvenir", "Primavera", "Timaukel",
        "Natales", "Torres del Paine"
    ],
}


# ============================================================
# FUNCIONES
# ============================================================

def formato_pesos(valor: int) -> str:
    return f"${valor:,.0f}".replace(",", ".")


def calcular_total(kilos: float) -> int:
    return int(round(kilos * PRECIO_POR_KG))


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
        "direccion_referencia",
        "kilos",
        "precio_por_kg",
        "total",
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

UBICACIÓN
Región: {datos["region"]}
Comuna: {datos["comuna"]}
Dirección o referencia: {datos["direccion_referencia"] or "No informado"}

PEDIDO
Kilos solicitados: {datos["kilos"]} kg
Precio por kg: {formato_pesos(PRECIO_POR_KG)}
Total paltas: {formato_pesos(datos["total"])}
Fecha preferida: {datos["fecha_preferida"] or "No informada"}

COMENTARIOS
{datos["comentarios"] or "Sin comentarios"}

TRANSFERENCIA PARA CLIENTE
Titular: {TITULAR}
RUT: {RUT}
Banco: {BANCO}
Tipo de cuenta: {TIPO_CUENTA}
Monto: {formato_pesos(datos["total"])}

Estado interno: {datos["estado"]}
Fecha registro: {datos["fecha_registro"]}
"""


def enviar_correo(datos: dict) -> tuple[bool, str]:
    if not SMTP_USER or not SMTP_PASSWORD:
        return False, "Pedido guardado. Correo no enviado porque falta configurar SMTP_USER y SMTP_PASSWORD."

    mensaje = EmailMessage()
    mensaje["Subject"] = f"Solicitud paltas {datos['folio']} - {datos['nombre']} - {formato_pesos(datos['total'])}"
    mensaje["From"] = SMTP_USER
    mensaje["To"] = CORREO_DESTINO
    mensaje.set_content(crear_cuerpo_correo(datos))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(mensaje)
        return True, "Pedido guardado y correo enviado."
    except Exception as error:
        return False, f"Pedido guardado. No se pudo enviar el correo: {error}"


def mensaje_para_cliente(datos: dict) -> str:
    return f"""Hola {datos["nombre"]}, recibimos tu solicitud de pedido de paltas.

Resumen:
• Cantidad: {datos["kilos"]} kg
• Precio por kg: {formato_pesos(PRECIO_POR_KG)}
• Total a transferir: {formato_pesos(datos["total"])}

Datos de transferencia:
• Titular: {TITULAR}
• RUT: {RUT}
• Banco: {BANCO}
• Tipo de cuenta: {TIPO_CUENTA}
• Monto: {formato_pesos(datos["total"])}

Ubicación informada:
• Región: {datos["region"]}
• Comuna: {datos["comuna"]}

Cuando transfieras, envíanos el comprobante por WhatsApp.
Luego coordinamos la logística y entrega."""


# ============================================================
# INTERFAZ
# ============================================================

st.set_page_config(
    page_title="Solicitud Pedido Paltas",
    page_icon="🥑",
    layout="centered",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 760px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .logo-box {
        display: flex;
        justify-content: center;
        margin-bottom: 0.4rem;
    }
    .titulo-principal {
        text-align: center;
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1.05;
        margin-bottom: 0.2rem;
    }
    .subtitulo {
        text-align: center;
        color: #4b5563;
        font-size: 1rem;
        margin-bottom: 1.3rem;
    }
    .precio-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 16px;
        text-align: center;
    }
    .precio-grande {
        font-size: 1.4rem;
        font-weight: 800;
        color: #166534;
    }
    .total-box {
        background: #ecfdf5;
        border: 1px solid #86efac;
        border-radius: 16px;
        padding: 18px;
        margin-top: 8px;
        margin-bottom: 12px;
        text-align: center;
    }
    .total-numero {
        font-size: 2rem;
        font-weight: 900;
        color: #14532d;
    }
    .nota {
        color: #6b7280;
        font-size: 0.92rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if LOGO_PATH.exists():
    st.markdown('<div class="logo-box">', unsafe_allow_html=True)
    st.image(str(LOGO_PATH), width=150)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="titulo-principal">Solicitud Pedido<br>Paltas</div>
    <div class="subtitulo">Completa tus datos en menos de un minuto. Luego coordinamos logística y entrega por WhatsApp.</div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="precio-box">
        <div>Precio actual por kilo</div>
        <div class="precio-grande">{formato_pesos(PRECIO_POR_KG)}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("solicitud_paltas", clear_on_submit=False):
    st.subheader("1. Tus datos")

    nombre = st.text_input("Nombre", placeholder="Ej: Juan Pérez")
    whatsapp = st.text_input("WhatsApp", placeholder="Ej: +56 9 1234 5678")
    correo = st.text_input("Correo opcional", placeholder="Ej: correo@gmail.com")

    st.subheader("2. Ubicación")

    region = st.selectbox(
        "Región",
        list(REGIONES_COMUNAS.keys()),
        index=list(REGIONES_COMUNAS.keys()).index("Metropolitana de Santiago"),
    )

    comuna = st.selectbox(
        "Comuna",
        REGIONES_COMUNAS[region],
    )

    direccion_referencia = st.text_input(
        "Dirección o referencia opcional",
        placeholder="Ej: sector, villa, calle principal, referencia de entrega",
    )

    st.subheader("3. Pedido")

    kilos = st.number_input(
        "Kilos de paltas",
        min_value=KILOS_MINIMOS,
        value=KILOS_MINIMOS,
        step=0.5,
        help="Puedes ajustar la cantidad en medios kilos.",
    )

    fecha_preferida = st.date_input("Fecha preferida, opcional", value=None)

    comentarios = st.text_area(
        "Comentario opcional",
        placeholder="Ej: prefiero paltas más maduras, coordinar horario, etc.",
        height=90,
    )

    total = calcular_total(kilos)

    st.markdown(
        f"""
        <div class="total-box">
            <div>Total a transferir</div>
            <div class="total-numero">{formato_pesos(total)}</div>
            <div class="nota">No incluye despacho si aplica. La logística se coordina después.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    aceptar = st.checkbox("Confirmo que los datos están correctos.")
    enviar = st.form_submit_button("Enviar solicitud")

if enviar:
    errores = []

    if not nombre.strip():
        errores.append("Nombre")
    if not whatsapp.strip():
        errores.append("WhatsApp")
    if kilos < KILOS_MINIMOS:
        errores.append("Kilos")

    if not aceptar:
        errores.append("Confirmación")

    if errores:
        st.error("Revisa estos campos: " + ", ".join(errores))
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
            "direccion_referencia": direccion_referencia.strip(),
            "kilos": kilos,
            "precio_por_kg": PRECIO_POR_KG,
            "total": total,
            "fecha_preferida": str(fecha_preferida) if fecha_preferida else "",
            "comentarios": comentarios.strip(),
            "estado": "Solicitud recibida",
        }

        guardar_orden(datos)
        correo_ok, mensaje_estado = enviar_correo(datos)

        st.success("Solicitud enviada correctamente.")
        st.caption(mensaje_estado)

        st.subheader("Datos de transferencia")
        st.write(f"**Titular:** {TITULAR}")
        st.write(f"**RUT:** {RUT}")
        st.write(f"**Banco:** {BANCO}")
        st.write(f"**Tipo de cuenta:** {TIPO_CUENTA}")
        st.write(f"**Monto:** {formato_pesos(total)}")

        st.subheader("Mensaje para WhatsApp")
        st.text_area(
            "Copia y pega este mensaje al cliente",
            value=mensaje_para_cliente(datos),
            height=280,
        )

        st.download_button(
            "Descargar esta solicitud",
            data=crear_cuerpo_correo(datos),
            file_name=f"{folio}.txt",
            mime="text/plain",
        )

st.divider()

with st.expander("Ver registro interno"):
    if ARCHIVO_ORDENES.exists():
        with ARCHIVO_ORDENES.open("rb") as archivo:
            st.download_button(
                "Descargar todas las solicitudes CSV",
                data=archivo,
                file_name="ordenes_paltas.csv",
                mime="text/csv",
            )
    else:
        st.caption("Todavía no hay solicitudes registradas.")
