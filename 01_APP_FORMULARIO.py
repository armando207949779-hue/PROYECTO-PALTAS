import csv
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import gspread
from flask import Flask, redirect, render_template_string, request, session, url_for
from google.oauth2.service_account import Credentials


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cambia-esta-clave-en-railway")


INDEX_TEMPLATE = r"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#14532d">
  <title>Solicitud Pedido Paltas</title>

  <style>
    :root {
      --green-950: #052e16;
      --green-900: #14532d;
      --green-800: #166534;
      --green-700: #15803d;
      --green-600: #16a34a;
      --green-100: #dcfce7;
      --green-50: #f0fdf4;
      --lime-100: #ecfccb;
      --text: #111827;
      --muted: #4b5563;
      --line: #e5e7eb;
      --white: #ffffff;
      --shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
      --soft-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
      --radius-xl: 28px;
      --radius-lg: 22px;
    }

    * {
      box-sizing: border-box;
      -webkit-tap-highlight-color: transparent;
    }

    body {
      margin: 0;
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(187, 247, 208, 0.75), transparent 34rem),
        linear-gradient(180deg, #f8fff9 0%, #ffffff 45%, #f8fafc 100%);
      min-height: 100dvh;
    }

    button,
    input,
    select {
      font: inherit;
    }

    .app-shell {
      width: 100%;
      max-width: 560px;
      margin: 0 auto;
      padding: max(14px, env(safe-area-inset-top)) 14px calc(24px + env(safe-area-inset-bottom));
    }

    .hero {
      position: sticky;
      top: 0;
      z-index: 20;
      background: linear-gradient(180deg, rgba(248, 255, 249, 0.98) 0%, rgba(248, 255, 249, 0.88) 72%, rgba(248, 255, 249, 0) 100%);
      backdrop-filter: blur(10px);
      padding: 10px 0 8px;
    }

    .brand-card {
      background: rgba(255, 255, 255, 0.88);
      border: 1px solid rgba(187, 247, 208, 0.95);
      border-radius: 30px;
      padding: 14px 14px 12px;
      box-shadow: var(--soft-shadow);
    }

    .brand-row {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .logo-box {
      width: 72px;
      height: 72px;
      display: grid;
      place-items: center;
      border-radius: 24px;
      background: linear-gradient(135deg, #dcfce7, #fef9c3);
      border: 1px solid rgba(22, 101, 52, 0.14);
      overflow: hidden;
      flex: 0 0 auto;
    }

    .logo-box img {
      width: 66px;
      height: 66px;
      object-fit: contain;
      display: block;
    }

    .eyebrow {
      color: var(--green-800);
      font-size: 0.78rem;
      font-weight: 900;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      margin-bottom: 2px;
    }

    .main-title {
      color: var(--green-950);
      font-size: clamp(1.45rem, 7vw, 2.15rem);
      font-weight: 950;
      letter-spacing: -0.06em;
      line-height: 0.98;
      margin: 0;
    }

    .step-pill {
      width: fit-content;
      margin-top: 9px;
      color: var(--green-900);
      background: var(--green-100);
      border: 1px solid #bbf7d0;
      border-radius: 999px;
      padding: 7px 11px;
      font-weight: 950;
      font-size: 0.83rem;
    }

    .progress-wrap {
      margin-top: 12px;
    }

    .progress-track {
      height: 9px;
      border-radius: 999px;
      overflow: hidden;
      background: #e5e7eb;
    }

    .progress-fill {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--green-700), #84cc16);
    }

    .stepper {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
      margin-top: 9px;
    }

    .stepper-item {
      border-radius: 999px;
      padding: 7px 4px;
      text-align: center;
      font-size: 0.68rem;
      font-weight: 950;
      color: #64748b;
      background: #ffffff;
      border: 1px solid var(--line);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .stepper-item.active {
      color: var(--green-950);
      background: var(--lime-100);
      border-color: #bef264;
    }

    .stepper-item.done {
      color: #ffffff;
      background: var(--green-700);
      border-color: var(--green-700);
    }

    .main-card {
      margin-top: 14px;
      background: rgba(255, 255, 255, 0.94);
      border: 1px solid rgba(226, 232, 240, 0.95);
      border-radius: var(--radius-xl);
      box-shadow: var(--shadow);
      padding: 18px;
      overflow: hidden;
    }

    .screen-title {
      font-size: clamp(1.55rem, 7vw, 2.2rem);
      line-height: 1.04;
      font-weight: 950;
      letter-spacing: -0.06em;
      margin: 0 0 14px;
      color: var(--green-950);
    }

    .screen-subtitle {
      margin: -8px 0 15px;
      color: var(--muted);
      font-size: 0.94rem;
      line-height: 1.35;
    }

    .field-label,
    .radio-title {
      display: block;
      color: #1f2937;
      font-size: 0.92rem;
      font-weight: 950;
      margin: 14px 0 8px;
    }

    input[type="text"],
    input[type="tel"],
    input[type="number"],
    select {
      width: 100%;
      min-height: 54px;
      border-radius: 18px;
      border: 1px solid #d1d5db;
      background: #ffffff;
      color: var(--text);
      padding: 13px 14px;
      outline: none;
      font-size: 1.02rem;
      box-shadow: 0 1px 0 rgba(15, 23, 42, 0.03);
    }

    input:focus,
    select:focus {
      border-color: var(--green-700);
      box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.16);
    }

    .radio-horizontal,
    .radio-vertical {
      display: grid;
      gap: 10px;
      margin: 8px 0 14px;
    }

    .radio-horizontal {
      grid-template-columns: 1fr 1fr;
    }

    .choice-card {
      position: relative;
      display: flex;
      align-items: center;
      gap: 10px;
      min-height: 58px;
      cursor: pointer;
      border: 1px solid #dbe3ea;
      border-radius: 20px;
      padding: 13px 14px;
      background: linear-gradient(180deg, #ffffff, #fbfdff);
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
      font-weight: 950;
      color: #111827;
    }

    .choice-card input {
      position: absolute;
      opacity: 0;
      pointer-events: none;
    }

    .choice-dot {
      width: 21px;
      height: 21px;
      border-radius: 999px;
      border: 2px solid #cbd5e1;
      display: inline-grid;
      place-items: center;
      flex: 0 0 auto;
      background: #ffffff;
    }

    .choice-dot::after {
      content: "";
      width: 9px;
      height: 9px;
      border-radius: 999px;
      background: transparent;
    }

    .choice-card:has(input:checked) {
      border-color: #22c55e;
      background: linear-gradient(180deg, #f0fdf4, #ffffff);
      box-shadow: 0 10px 25px rgba(22, 163, 74, 0.12);
    }

    .choice-card:has(input:checked) .choice-dot {
      border-color: var(--green-700);
      background: var(--green-700);
    }

    .choice-card:has(input:checked) .choice-dot::after {
      background: #ffffff;
    }

    .choice-title {
      display: block;
      font-size: 1rem;
      line-height: 1.15;
    }

    .choice-hint {
      display: block;
      color: #64748b;
      font-size: 0.78rem;
      font-weight: 750;
      margin-top: 2px;
      line-height: 1.15;
    }

    .total-card {
      background:
        radial-gradient(circle at top left, rgba(187, 247, 208, 0.95), transparent 13rem),
        linear-gradient(135deg, #ecfdf5, #fefce8);
      border: 1px solid #86efac;
      border-radius: 26px;
      padding: 18px 16px;
      text-align: center;
      margin: 16px 0 4px;
      box-shadow: 0 14px 32px rgba(22, 101, 52, 0.12);
    }

    .total-label {
      color: var(--green-800);
      font-size: 0.9rem;
      font-weight: 950;
    }

    .total-value {
      color: var(--green-950);
      font-size: clamp(2.25rem, 13vw, 3.6rem);
      font-weight: 1000;
      letter-spacing: -0.07em;
      line-height: 1;
      margin-top: 4px;
    }

    .soft-note {
      color: var(--muted);
      font-size: 0.88rem;
      line-height: 1.32;
      margin-top: 8px;
      font-weight: 650;
    }

    .info-card,
    .summary-card,
    .clean-card {
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: var(--radius-lg);
      padding: 15px;
      margin: 14px 0;
      box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
    }

    .summary-card {
      background: linear-gradient(180deg, #f0fdf4, #ffffff);
      border-color: #bbf7d0;
    }

    .mini-title {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--green-800);
      font-size: 0.92rem;
      font-weight: 1000;
      margin-bottom: 8px;
    }

    .mini-title::before {
      content: "";
      width: 9px;
      height: 9px;
      border-radius: 999px;
      background: var(--green-600);
      box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.12);
    }

    .summary-row {
      display: flex;
      justify-content: space-between;
      gap: 14px;
      border-bottom: 1px solid #eef2f7;
      padding: 11px 0;
      font-size: 0.96rem;
    }

    .summary-row:last-child {
      border-bottom: 0;
    }

    .summary-key {
      color: var(--muted);
      font-weight: 800;
    }

    .summary-value {
      color: var(--text);
      text-align: right;
      font-weight: 950;
      word-break: break-word;
    }

    .button-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-top: 18px;
    }

    .button-row.single {
      grid-template-columns: 1fr;
    }

    button,
    .button {
      width: 100%;
      min-height: 56px;
      border-radius: 18px;
      border: 1px solid #d1d5db;
      background: #ffffff;
      color: var(--text);
      font-weight: 1000;
      font-size: 1rem;
      cursor: pointer;
      text-decoration: none;
      display: grid;
      place-items: center;
      padding: 12px 14px;
      text-align: center;
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
    }

    button.primary,
    .button.primary {
      background: linear-gradient(135deg, var(--green-700), var(--green-900));
      color: #ffffff;
      border-color: var(--green-800);
      box-shadow: 0 14px 30px rgba(21, 128, 61, 0.24);
    }

    button:active,
    .button:active,
    .choice-card:active {
      transform: scale(0.985);
    }

    .whatsapp-btn {
      display: block;
      width: 100%;
      text-align: center;
      background: linear-gradient(135deg, #16a34a, #15803d);
      color: white !important;
      padding: 15px 16px;
      border-radius: 18px;
      font-weight: 1000;
      text-decoration: none !important;
      margin: 14px 0;
      box-shadow: 0 14px 30px rgba(22, 163, 74, 0.24);
    }

    .notice {
      border-radius: 18px;
      padding: 13px 14px;
      margin: 14px 0;
      font-weight: 900;
      line-height: 1.35;
    }

    .success {
      background: #dcfce7;
      color: #14532d;
      border: 1px solid #86efac;
    }

    .warning {
      background: #fff7ed;
      color: #9a3412;
      border: 1px solid #fed7aa;
    }

    .error {
      background: #fef2f2;
      color: #991b1b;
      border: 1px solid #fecaca;
    }

    .hidden {
      display: none;
    }

    .checkbox-row {
      display: flex;
      gap: 10px;
      align-items: flex-start;
      margin: 15px 0 4px;
      font-weight: 900;
      line-height: 1.3;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: #ffffff;
    }

    .checkbox-row input {
      width: 20px;
      height: 20px;
      accent-color: var(--green-700);
      margin-top: 1px;
      flex: 0 0 auto;
    }

    .footer-version {
      text-align: center;
      color: #94a3b8;
      font-size: 0.72rem;
      margin-top: 18px;
      font-weight: 700;
    }

    @media (max-width: 420px) {
      .app-shell {
        padding-left: 10px;
        padding-right: 10px;
      }

      .brand-card,
      .main-card {
        border-radius: 24px;
      }

      .brand-row {
        gap: 10px;
      }

      .logo-box {
        width: 64px;
        height: 64px;
        border-radius: 21px;
      }

      .logo-box img {
        width: 60px;
        height: 60px;
      }

      .button-row {
        grid-template-columns: 1fr;
      }

      .radio-horizontal {
        grid-template-columns: 1fr 1fr;
        gap: 9px;
      }

      .choice-card {
        min-height: 56px;
        padding: 12px;
      }

      .stepper-item {
        font-size: 0.62rem;
        padding: 7px 2px;
      }

      .summary-row {
        align-items: flex-start;
      }
    }
  </style>
</head>

<body>
  <main class="app-shell">
    <header class="hero">
      <div class="brand-card">
        <div class="brand-row">
          <div class="logo-box">
            <img src="{{ url_for('static', filename='LOGO-PALTA.png') }}" alt="Logo paltas" onerror="this.style.display='none'">
          </div>
          <div class="brand-text">
            <div class="eyebrow">Pedido online</div>
            <h1 class="main-title">Solicitud Pedido<br>Paltas</h1>
            {% set nombres = {1: "Pedido", 2: "Entrega", 3: "Contacto", 4: "Confirmación"} %}
            <div class="step-pill">Paso {{ paso }} de 4 · {{ nombres[paso] }}</div>
          </div>
        </div>

        <div class="progress-wrap">
          <div class="progress-track">
            <div class="progress-fill" style="width: {{ paso * 25 }}%;"></div>
          </div>
          <div class="stepper">
            {% for n in [1, 2, 3, 4] %}
              <div class="stepper-item {% if n == paso %}active{% elif n < paso %}done{% endif %}">
                {{ n }}. {{ nombres[n] }}
              </div>
            {% endfor %}
          </div>
        </div>
      </div>
    </header>

    <section class="main-card">
      {% for error in errores %}
        <div class="notice error">{{ error }}</div>
      {% endfor %}

      {% if resultado %}
        <div class="notice success">Pedido registrado.</div>

        {% if resultado.google_ok %}
          <div class="notice success">Guardado en Google Sheets.</div>
        {% else %}
          <div class="notice warning">
            El pedido quedó como respaldo local. Google Sheets requiere revisión.<br>
            <small>{{ resultado.google_msg }}</small>
          </div>
        {% endif %}

        <div class="clean-card">
          <div class="mini-title">Registro</div>
          <div class="summary-row"><span class="summary-key">Folio</span><span class="summary-value">{{ resultado.folio }}</span></div>
          <div class="summary-row"><span class="summary-key">Total</span><span class="summary-value">{{ resultado.total }}</span></div>
        </div>

        <a class="whatsapp-btn" href="{{ resultado.whatsapp_url }}" target="_blank">Enviar pedido por WhatsApp</a>

        <form method="post" action="{{ url_for('nuevo') }}">
          <button class="primary" type="submit">Nuevo pedido</button>
        </form>

      {% elif paso == 1 %}
        <form method="post" action="{{ url_for('paso_1') }}">
          <h2 class="screen-title">¿Cuántos kilos quieres?</h2>
          <p class="screen-subtitle">Selecciona el tipo de palta y la cantidad. El total se actualiza al instante.</p>

          <div class="radio-title">Tipo de palta</div>
          <div class="radio-horizontal">
            {% for tipo, precio in precios.items() %}
              <label class="choice-card">
                <input type="radio" name="tipo_palta" value="{{ tipo }}" data-precio="{{ precio }}" {% if datos.tipo_palta == tipo %}checked{% endif %}>
                <span class="choice-dot"></span>
                <span>
                  <span class="choice-title">{{ tipo }}</span>
                  <span class="choice-hint">{{ formato_pesos(precio) }} / kg</span>
                </span>
              </label>
            {% endfor %}
          </div>

          <label class="field-label" for="kilos">Kilos</label>
          <input id="kilos" name="kilos" type="number" inputmode="decimal" min="1" step="0.5" value="{{ datos.kilos }}">

          <div class="total-card">
            <div class="total-label" id="precioKgLabel">{{ datos.tipo_palta }} · {{ formato_pesos(datos.precio_kg) }} por kg</div>
            <div class="total-value" id="totalVisual">{{ formato_pesos(datos.total_paltas) }}</div>
            <div class="soft-note">Este es el valor total de las paltas por la cantidad seleccionada.</div>
          </div>

          <div class="button-row single">
            <button class="primary" type="submit">Continuar</button>
          </div>
        </form>

      {% elif paso == 2 %}
        <form method="post" action="{{ url_for('paso_2') }}">
          <h2 class="screen-title">Entrega</h2>
          <p class="screen-subtitle">Elige cómo quieres recibir el pedido. Solo se mostrarán los datos necesarios.</p>

          <div class="radio-title">Selecciona una opción</div>
          <div class="radio-vertical">
            {% for opcion in ["Retiro sin costo", "Despacho zona cercana", "Cotizar otra comuna o región"] %}
              <label class="choice-card">
                <input type="radio" name="modalidad_entrega" value="{{ opcion }}" {% if datos.modalidad_entrega == opcion %}checked{% endif %}>
                <span class="choice-dot"></span>
                <span>
                  <span class="choice-title">{{ opcion }}</span>
                  {% if opcion == "Retiro sin costo" %}
                    <span class="choice-hint">Punto a coordinar por WhatsApp</span>
                  {% elif opcion == "Despacho zona cercana" %}
                    <span class="choice-hint">La Calera, Quillota, La Cruz o Hijuelas</span>
                  {% else %}
                    <span class="choice-hint">Revisamos disponibilidad de envío</span>
                  {% endif %}
                </span>
              </label>
            {% endfor %}
          </div>

          <div id="bloqueRetiro">
            <label class="field-label" for="comuna_retiro">Localidad de retiro</label>
            <select id="comuna_retiro" name="comuna_retiro">
              {% for comuna in localidades %}
                <option value="{{ comuna }}" {% if datos.comuna == comuna %}selected{% endif %}>{{ comuna }}</option>
              {% endfor %}
            </select>

            <div class="info-card">
              <div class="mini-title">Retiro</div>
              Sin costo de despacho. El punto exacto se confirma por WhatsApp.
            </div>
          </div>

          <div id="bloqueLocal" class="hidden">
            <label class="field-label" for="comuna_local">Comuna</label>
            <select id="comuna_local" name="comuna_local">
              {% for comuna in localidades %}
                <option value="{{ comuna }}" {% if datos.comuna == comuna %}selected{% endif %}>{{ comuna }}</option>
              {% endfor %}
            </select>
          </div>

          <div id="bloqueOtra" class="hidden">
            <label class="field-label" for="region">Región</label>
            <select id="region" name="region">
              {% for region in regiones_comunas.keys() %}
                <option value="{{ region }}" {% if datos.region == region %}selected{% endif %}>{{ region }}</option>
              {% endfor %}
            </select>

            <label class="field-label" for="comuna_otra">Comuna</label>
            <select id="comuna_otra" name="comuna_otra"></select>
          </div>

          <div id="bloqueDireccion" class="hidden">
            <div class="info-card">
              <div class="mini-title">Dirección de entrega</div>
              Completa los datos principales para coordinar rápido.
            </div>

            <label class="field-label" for="poblacion">Población / sector</label>
            <input id="poblacion" name="poblacion" value="{{ datos.poblacion }}" placeholder="Ej: Artificio, Boco, Pocochay">

            <label class="field-label" for="calle">Calle</label>
            <input id="calle" name="calle" value="{{ datos.calle }}" placeholder="Ej: Los Aromos">

            <label class="field-label" for="numero">Número</label>
            <input id="numero" name="numero" value="{{ datos.numero }}" placeholder="Ej: 123">
          </div>

          <div class="button-row">
            <button type="submit" formaction="{{ url_for('volver', paso=1) }}">Volver</button>
            <button class="primary" type="submit">Continuar</button>
          </div>
        </form>

      {% elif paso == 3 %}
        <form method="post" action="{{ url_for('paso_3') }}">
          <h2 class="screen-title">Datos de contacto</h2>
          <p class="screen-subtitle">Usaremos estos datos para confirmar el pedido y coordinar la entrega.</p>

          <label class="field-label" for="nombre">Nombre</label>
          <input id="nombre" name="nombre" value="{{ datos.nombre }}" placeholder="Tu nombre" autocomplete="name">

          <label class="field-label" for="whatsapp">WhatsApp</label>
          <input id="whatsapp" name="whatsapp" value="{{ datos.whatsapp }}" placeholder="+56 9 1234 5678" inputmode="tel" autocomplete="tel">

          <div class="summary-card">
            <div class="mini-title">Resumen rápido</div>
            <div class="summary-row"><span class="summary-key">Pedido</span><span class="summary-value">{{ datos.kilos }} kg · {{ datos.tipo_palta }}</span></div>
            <div class="summary-row"><span class="summary-key">Total</span><span class="summary-value">{{ formato_pesos(datos.total_paltas) }}</span></div>
            <div class="summary-row"><span class="summary-key">Entrega</span><span class="summary-value">{{ datos.modalidad_entrega }}</span></div>
          </div>

          <div class="button-row">
            <button type="submit" formaction="{{ url_for('volver', paso=2) }}">Volver</button>
            <button class="primary" type="submit">Ver transferencia</button>
          </div>
        </form>

      {% elif paso == 4 %}
        <h2 class="screen-title">Revisa tu pedido</h2>
        <p class="screen-subtitle">Confirma que todo esté correcto antes de registrar.</p>

        <div class="total-card">
          <div class="total-label">Total paltas</div>
          <div class="total-value">{{ formato_pesos(datos.total_paltas) }}</div>
          <div class="soft-note">El despacho, si corresponde, se coordina aparte.</div>
        </div>

        {% if datos.modalidad_entrega == "Retiro sin costo" %}
          {% set direccion = "Retiro en " ~ datos.comuna %}
        {% else %}
          {% set direccion = [datos.poblacion, datos.calle, datos.numero] | select | join(", ") %}
        {% endif %}

        <div class="clean-card">
          <div class="mini-title">Resumen</div>
          <div class="summary-row"><span class="summary-key">Pedido</span><span class="summary-value">{{ datos.kilos }} kg · {{ datos.tipo_palta }}</span></div>
          <div class="summary-row"><span class="summary-key">Precio kg</span><span class="summary-value">{{ formato_pesos(datos.precio_kg) }}</span></div>
          <div class="summary-row"><span class="summary-key">Entrega</span><span class="summary-value">{{ datos.modalidad_entrega }}</span></div>
          <div class="summary-row"><span class="summary-key">Comuna</span><span class="summary-value">{{ datos.comuna }}</span></div>
          <div class="summary-row"><span class="summary-key">Dirección</span><span class="summary-value">{{ direccion or "Por coordinar" }}</span></div>
          <div class="summary-row"><span class="summary-key">Cliente</span><span class="summary-value">{{ datos.nombre }}</span></div>
          <div class="summary-row"><span class="summary-key">WhatsApp</span><span class="summary-value">{{ datos.whatsapp }}</span></div>
        </div>

        <div class="clean-card">
          <div class="mini-title">Transferencia</div>
          <div class="summary-row"><span class="summary-key">Titular</span><span class="summary-value">{{ titular }}</span></div>
          <div class="summary-row"><span class="summary-key">RUT</span><span class="summary-value">{{ rut }}</span></div>
          <div class="summary-row"><span class="summary-key">Banco</span><span class="summary-value">{{ banco }}</span></div>
          <div class="summary-row"><span class="summary-key">Cuenta</span><span class="summary-value">{{ tipo_cuenta }}</span></div>
          <div class="summary-row"><span class="summary-key">Monto</span><span class="summary-value">{{ formato_pesos(datos.total_paltas) }}</span></div>
        </div>

        <form method="post" action="{{ url_for('registrar') }}">
          <label class="checkbox-row">
            <input type="checkbox" name="confirmar" value="si">
            <span>Confirmo que los datos están correctos.</span>
          </label>

          <div class="button-row">
            <button type="submit" formaction="{{ url_for('volver', paso=3) }}">Volver</button>
            <button class="primary" type="submit">Registrar pedido</button>
          </div>
        </form>
      {% endif %}
    </section>

    <div class="footer-version">{{ app_version or "01_APP_SOLPED_PALTAS · V6 Mobile Premium" }}</div>
  </main>

  <script>
    const regionesComunas = {{ regiones_comunas | tojson }};
    const pesos = (valor) => "$" + Math.round(Number(valor || 0)).toLocaleString("es-CL");

    const kilosInput = document.querySelector("#kilos");
    const totalVisual = document.querySelector("#totalVisual");
    const precioKgLabel = document.querySelector("#precioKgLabel");
    const tipoRadios = document.querySelectorAll("input[name='tipo_palta']");

    function actualizarTotal() {
      if (!kilosInput || !totalVisual) return;

      const seleccionado = document.querySelector("input[name='tipo_palta']:checked");
      const tipo = seleccionado?.value || "Hass";
      const precio = Number(seleccionado?.dataset.precio || 0);
      const kilos = Number(kilosInput.value || 0);
      const total = precio * kilos;

      totalVisual.textContent = pesos(total);
      if (precioKgLabel) {
        precioKgLabel.textContent = `${tipo} · ${pesos(precio)} por kg`;
      }
    }

    tipoRadios.forEach(r => r.addEventListener("change", actualizarTotal));
    kilosInput?.addEventListener("input", actualizarTotal);
    actualizarTotal();

    const bloqueRetiro = document.querySelector("#bloqueRetiro");
    const bloqueLocal = document.querySelector("#bloqueLocal");
    const bloqueOtra = document.querySelector("#bloqueOtra");
    const bloqueDireccion = document.querySelector("#bloqueDireccion");
    const regionSelect = document.querySelector("#region");
    const comunaOtra = document.querySelector("#comuna_otra");

    function modalidadActual() {
      return document.querySelector("input[name='modalidad_entrega']:checked")?.value || "Retiro sin costo";
    }

    function actualizarModalidad() {
      const modalidad = modalidadActual();

      bloqueRetiro?.classList.toggle("hidden", modalidad !== "Retiro sin costo");
      bloqueLocal?.classList.toggle("hidden", modalidad !== "Despacho zona cercana");
      bloqueOtra?.classList.toggle("hidden", modalidad !== "Cotizar otra comuna o región");
      bloqueDireccion?.classList.toggle("hidden", modalidad === "Retiro sin costo");
    }

    function cargarComunas() {
      if (!regionSelect || !comunaOtra) return;

      const region = regionSelect.value;
      const comunas = regionesComunas[region] || [];
      const comunaActual = "{{ datos.comuna }}";

      comunaOtra.innerHTML = "";
      comunas.forEach((comuna) => {
        const option = document.createElement("option");
        option.value = comuna;
        option.textContent = comuna;
        if (comuna === comunaActual) option.selected = true;
        comunaOtra.appendChild(option);
      });
    }

    document.querySelectorAll("input[name='modalidad_entrega']").forEach((radio) => {
      radio.addEventListener("change", actualizarModalidad);
    });

    regionSelect?.addEventListener("change", cargarComunas);

    cargarComunas();
    actualizarModalidad();
  </script>
</body>
</html>

"""


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

WHATSAPP_NEGOCIO = "56963596523"

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1o1zvFzeOsGkDdLQbvEBvMyK6avLiMVMj04Ic0J2bzSw/edit?usp=sharing"
GOOGLE_SHEET_NAME = "Pedidos"

ARCHIVO_RESPALDO = Path("ordenes_paltas.csv")
LOCALIDADES_CERCANAS = ["La Calera", "Quillota", "La Cruz", "Hijuelas"]


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
# UTILIDADES
# ============================================================

def formato_pesos(valor) -> str:
    try:
        numero = int(round(float(valor)))
    except Exception:
        numero = 0
    return "$" + f"{numero:,}".replace(",", ".")


def calcular_total(tipo_palta: str, kilos: float) -> int:
    return int(round(PRECIOS_PALTA[tipo_palta] * kilos))


def normalizar_whatsapp(numero: str) -> str:
    return "".join(c for c in numero if c.isdigit())


def columnas_internas() -> list[str]:
    return [
        "folio", "fecha_registro", "tipo_palta", "kilos", "precio_por_kg",
        "total_paltas", "modalidad_entrega", "region", "comuna", "poblacion",
        "calle", "numero", "nombre", "whatsapp", "estado",
    ]


def encabezados_google_sheets() -> list[str]:
    return [
        "Folio", "Fecha registro", "Tipo de palta", "Kilos", "Precio por kg",
        "Total paltas", "Modalidad de entrega", "Región", "Comuna",
        "Población / sector", "Calle", "Número", "Nombre cliente",
        "WhatsApp cliente", "Estado",
    ]


def obtener_service_account_info() -> dict:
    contenido = os.getenv("GCP_SERVICE_ACCOUNT_JSON", "").strip()
    if not contenido:
        raise RuntimeError("Falta la variable de entorno GCP_SERVICE_ACCOUNT_JSON.")
    return json.loads(contenido)


def obtener_worksheet_google_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(obtener_service_account_info(), scopes=scopes)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_url(GOOGLE_SHEET_URL)

    try:
        worksheet = spreadsheet.worksheet(GOOGLE_SHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=GOOGLE_SHEET_NAME,
            rows=1000,
            cols=len(encabezados_google_sheets()),
        )

    return worksheet


def asegurar_encabezados_google_sheets(worksheet) -> None:
    encabezados = encabezados_google_sheets()
    valores = worksheet.get_all_values()

    if not valores:
        worksheet.append_row(encabezados, value_input_option="USER_ENTERED")
        return

    primera_fila = [str(v).strip() for v in valores[0]]
    if primera_fila[: len(encabezados)] != encabezados:
        worksheet.insert_row(encabezados, index=1, value_input_option="USER_ENTERED")


def guardar_respaldo_csv(datos: dict) -> None:
    existe = ARCHIVO_RESPALDO.exists()
    columnas = columnas_internas()

    with ARCHIVO_RESPALDO.open("a", newline="", encoding="utf-8") as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas)
        if not existe:
            writer.writeheader()
        writer.writerow(datos)


def guardar_google_sheets(datos: dict) -> tuple[bool, str]:
    try:
        worksheet = obtener_worksheet_google_sheets()
        asegurar_encabezados_google_sheets(worksheet)
        fila = [datos.get(clave, "") for clave in columnas_internas()]
        worksheet.append_row(fila, value_input_option="USER_ENTERED")
        return True, "Guardado en Google Sheets."
    except Exception as error:
        guardar_respaldo_csv(datos)
        return False, str(error)


def crear_cuerpo_solicitud(datos: dict) -> str:
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

Estado: {datos["estado"]}
Fecha registro: {datos["fecha_registro"]}
"""


def link_whatsapp(datos: dict) -> str:
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


def datos_actuales() -> dict:
    pedido = session.get("pedido", {})
    return {
        "tipo_palta": pedido.get("tipo_palta", "Hass"),
        "kilos": pedido.get("kilos", KILOS_MINIMOS),
        "precio_kg": pedido.get("precio_kg", PRECIOS_PALTA["Hass"]),
        "total_paltas": pedido.get("total_paltas", PRECIOS_PALTA["Hass"]),
        "modalidad_entrega": pedido.get("modalidad_entrega", "Retiro sin costo"),
        "region": pedido.get("region", "Valparaíso"),
        "comuna": pedido.get("comuna", "La Calera"),
        "poblacion": pedido.get("poblacion", ""),
        "calle": pedido.get("calle", ""),
        "numero": pedido.get("numero", ""),
        "nombre": pedido.get("nombre", ""),
        "whatsapp": pedido.get("whatsapp", ""),
    }


def actualizar_pedido(**kwargs) -> None:
    pedido = session.get("pedido", {})
    pedido.update(kwargs)
    session["pedido"] = pedido


def validar_paso_2(modalidad: str, poblacion: str, calle: str, numero: str) -> list[str]:
    errores = []
    if modalidad != "Retiro sin costo":
        if not poblacion.strip():
            errores.append("Población / sector")
        if not calle.strip():
            errores.append("Calle")
        if not numero.strip():
            errores.append("Número")
    return errores


def construir_datos_finales() -> dict:
    pedido = datos_actuales()
    folio = "PALTA-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    return {
        "folio": folio,
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo_palta": pedido["tipo_palta"],
        "kilos": pedido["kilos"],
        "precio_por_kg": int(pedido["precio_kg"]),
        "total_paltas": int(pedido["total_paltas"]),
        "modalidad_entrega": pedido["modalidad_entrega"],
        "region": pedido["region"],
        "comuna": pedido["comuna"],
        "poblacion": pedido["poblacion"],
        "calle": pedido["calle"],
        "numero": pedido["numero"],
        "nombre": pedido["nombre"],
        "whatsapp": normalizar_whatsapp(pedido["whatsapp"]),
        "estado": "Solicitud recibida",
    }


# ============================================================
# RUTAS
# ============================================================

@app.route("/", methods=["GET"])
def index():
    paso = int(session.get("paso", 1))
    paso = max(1, min(4, paso))
    session["paso"] = paso

    return render_template_string(
        INDEX_TEMPLATE,
        paso=paso,
        datos=datos_actuales(),
        precios=PRECIOS_PALTA,
        localidades=LOCALIDADES_CERCANAS,
        regiones_comunas=REGIONES_COMUNAS,
        formato_pesos=formato_pesos,
        titular=TITULAR,
        rut=RUT,
        banco=BANCO,
        tipo_cuenta=TIPO_CUENTA,
        app_version="01_APP_SOLPED_PALTAS · V6 Mobile Premium",
        resultado=session.pop("resultado", None),
        errores=session.pop("errores", []),
    )


@app.route("/paso/1", methods=["POST"])
def paso_1():
    tipo_palta = request.form.get("tipo_palta", "Hass")
    kilos = float(request.form.get("kilos", KILOS_MINIMOS))
    precio_kg = PRECIOS_PALTA[tipo_palta]
    total = calcular_total(tipo_palta, kilos)

    actualizar_pedido(
        tipo_palta=tipo_palta,
        kilos=kilos,
        precio_kg=precio_kg,
        total_paltas=total,
    )
    session["paso"] = 2
    return redirect(url_for("index"))


@app.route("/paso/2", methods=["POST"])
def paso_2():
    modalidad = request.form.get("modalidad_entrega", "Retiro sin costo")
    region = ""
    comuna = ""
    poblacion = request.form.get("poblacion", "").strip()
    calle = request.form.get("calle", "").strip()
    numero = request.form.get("numero", "").strip()

    if modalidad == "Retiro sin costo":
        region = "Valparaíso"
        comuna = request.form.get("comuna_retiro", "La Calera")
        poblacion = calle = numero = ""
    elif modalidad == "Despacho zona cercana":
        region = "Valparaíso"
        comuna = request.form.get("comuna_local", "La Calera")
    else:
        region = request.form.get("region", "Valparaíso")
        comuna = request.form.get("comuna_otra", "La Calera")

    errores = validar_paso_2(modalidad, poblacion, calle, numero)

    if errores:
        session["errores"] = ["Falta completar: " + ", ".join(errores)]
        session["paso"] = 2
        return redirect(url_for("index"))

    actualizar_pedido(
        modalidad_entrega=modalidad,
        region=region,
        comuna=comuna,
        poblacion=poblacion,
        calle=calle,
        numero=numero,
    )
    session["paso"] = 3
    return redirect(url_for("index"))


@app.route("/paso/3", methods=["POST"])
def paso_3():
    nombre = request.form.get("nombre", "").strip()
    whatsapp = request.form.get("whatsapp", "").strip()

    errores = []
    if not nombre:
        errores.append("Nombre")
    if not whatsapp:
        errores.append("WhatsApp")

    if errores:
        session["errores"] = ["Falta completar: " + ", ".join(errores)]
        session["paso"] = 3
        return redirect(url_for("index"))

    actualizar_pedido(nombre=nombre, whatsapp=whatsapp)
    session["paso"] = 4
    return redirect(url_for("index"))


@app.route("/registrar", methods=["POST"])
def registrar():
    if request.form.get("confirmar") != "si":
        session["errores"] = ["Confirma que los datos están correctos."]
        session["paso"] = 4
        return redirect(url_for("index"))

    datos = construir_datos_finales()
    google_ok, google_msg = guardar_google_sheets(datos)

    session["resultado"] = {
        "google_ok": google_ok,
        "google_msg": google_msg,
        "whatsapp_url": link_whatsapp(datos),
        "folio": datos["folio"],
        "total": formato_pesos(datos["total_paltas"]),
        "texto": crear_cuerpo_solicitud(datos),
    }
    session["paso"] = 4
    return redirect(url_for("index"))


@app.route("/volver/<int:paso>", methods=["POST"])
def volver(paso: int):
    session["paso"] = max(1, min(4, paso))
    return redirect(url_for("index"))


@app.route("/nuevo", methods=["POST"])
def nuevo():
    session.clear()
    session["paso"] = 1
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
