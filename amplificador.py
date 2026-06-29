import streamlit as st
import math

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Proyecto Física: Transistor BJT",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚡ Proyecto de Física: Amplificador en Emisor Común")
st.markdown("Análisis riguroso en **Corriente Continua (DC)** y **Corriente Alterna (AC)** para polarización por divisor de tensión.")
st.markdown("---")

# Diccionarios de multiplicadores
res_units = {"Ω": 1.0, "kΩ": 1e3, "MΩ": 1e6}
volt_units = {"V": 1.0, "mV": 1e-3, "µV": 1e-6}
freq_units = {"Hz": 1.0, "kHz": 1e3, "MHz": 1e6}

# Función para alinear perfectamente los inputs
def get_val(label, def_val, def_unit, units_dict, key_id):
    st.markdown(f"<div style='margin-bottom: 5px; font-weight: 600;'>{label}</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    val = col1.number_input(label, value=float(def_val), step=1.0, key=f"num_{key_id}", label_visibility="collapsed")
    unit_list = list(units_dict.keys())
    u_idx = unit_list.index(def_unit)
    unit = col2.selectbox("Unidad", unit_list, index=u_idx, key=f"un_{key_id}", label_visibility="collapsed")
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    return val * units_dict[unit]

# ==========================================
# BARRA LATERAL: INGRESO DE DATOS
# ==========================================
with st.sidebar:
    st.header("⚙️ Parámetros de Entrada")
    
    st.subheader("1. Transistor y Alimentación")
    vcc = get_val("Voltaje Vcc", 10.0, "V", volt_units, "vcc")
    st.markdown("<div style='margin-bottom: 5px; font-weight: 600;'>Ganancia Beta (β)</div>", unsafe_allow_html=True)
    beta = st.number_input("Ganancia Beta (β)", value=100.0, step=10.0, label_visibility="collapsed")
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    
    st.subheader("2. Resistores de Polarización")
    r1 = get_val("Resistor R1", 10.0, "kΩ", res_units, "r1")
    r2 = get_val("Resistor R2", 2.2, "kΩ", res_units, "r2")
    rc = get_val("Resistor Rc", 3.6, "kΩ", res_units, "rc")
    re = get_val("Resistor Re", 1.0, "kΩ", res_units, "re")
    rl = get_val("Resistor RL", 10.0, "kΩ", res_units, "rl")
    
    st.subheader("3. Generador AC (Señal)")
    vg = get_val("Voltaje vg", 2.0, "mV", volt_units, "vg")
    frecuencia = get_val("Frecuencia (f)", 10.0, "kHz", freq_units, "freq")
    rg = get_val("Resist. Interna Rg", 600.0, "Ω", res_units, "rg")

# ==========================================
# CÁLCULOS MATEMÁTICOS (Unidades base: V, A, Ω, W, Hz)
# ==========================================

# --- CONTINUA (DC) ---
vbb = vcc * (r2 / (r1 + r2))
ve = vbb - 0.7
ic = ve / re if ve > 0 else 0.0
ib = ic / beta if beta > 0 else 0.0
vce = vcc - (ic * (rc + re))
pd = vce * ic  # Potencia disipada (Watts)

# --- ALTERNA (AC) ---
if ic > 0 and vce > 0:
    re_prima = 0.025 / ic          # r'e = 25mV / Ic
    rc_ac = (rc * rl) / (rc + rl)  # rc = Rc || RL
    zin_base = beta * re_prima
    zin_etapa = 1.0 / ((1.0/r1) + (1.0/r2) + (1.0/zin_base))
    
    av = rc_ac / re_prima
    vin = vg * (zin_etapa / (rg + zin_etapa))
    vout = av * vin
    
    # --- CÁLCULO DE CONDENSADORES (Regla del 10%) ---
    # C >= 1 / (2 * pi * f * 0.1 * R_asociada)
    c_entrada = 1.0 / (2 * math.pi * frecuencia * 0.1 * zin_etapa)
    c_salida = 1.0 / (2 * math.pi * frecuencia * 0.1 * rl)
    c_emisor = 1.0 / (2 * math.pi * frecuencia * 0.1 * re)
else:
    re_prima = rc_ac = zin_base = zin_etapa = av = vin = vout = 0.0
    c_entrada = c_salida = c_emisor = 0.0

# ==========================================
# PANEL PRINCIPAL
# ==========================================

# Imagen centrada y grande
st.subheader("📐 Circuito de Referencia")
col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
with col_img2:
    try:
        st.image("circuito.png", caption="Esquema del Preamplificador", use_container_width=True)
    except FileNotFoundError:
        st.error("❌ No se encontró 'circuito.png' en la carpeta.")

st.markdown("---")

# Verificación física de operación
if vce <= 0:
    st.error("⚠️ **TRANSISTOR EN SATURACIÓN (Vce ≤ 0V):** La corriente de colector es excesiva. El modelo lineal de pequeña señal queda anulado.")
elif ve <= 0:
    st.error("⚠️ **TRANSISTOR EN CORTE:** El voltaje de base no supera la barrera de 0.7V. No hay conducción de corriente.")
else:
    # SECCIÓN DC
    st.header("1️⃣ Resultados: Corriente Continua (Análisis DC)")
    st.caption("Determina el Punto de Operación estático (Punto Q) del semiconductor.")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Intensidad Colector (Ic)", f"{ic*1e3:.2f} mA")
    m2.metric("Intensidad Base (Ib)", f"{ib*1e6:.2f} µA")
    m3.metric("Voltaje Col.-Emisor (Vce)", f"{vce:.2f} V")
    m4.metric("Ganancia DC (β)", f"{int(beta)}")
    m5.metric("Potencia Disipada (Pd)", f"{pd*1e3:.2f} mW")
    
    st.markdown("---")
    
    # SECCIÓN AC
    st.header("2️⃣ Resultados: Corriente Alterna (Pequeña Señal)")
    st.caption("Cálculo dinámico basado en el modelo de parámetros r'e.")
    
    ac1, ac2, ac3, ac4 = st.columns(4)
    ac1.metric("Resistencia dinámica (r'e)", f"{re_prima:.2f} Ω", delta="25mV / Ic")
    ac2.metric("Resist. Colector AC (rc)", f"{rc_ac*1e-3:.2f} kΩ", delta="Rc || RL")
    ac3.metric("Impedancia Base [Zin(base)]", f"{zin_base*1e-3:.2f} kΩ", delta="β · r'e")
    ac4.metric("Impedancia Etapa [Zin(etapa)]", f"{zin_etapa*1e-3:.2f} kΩ", delta="R1 || R2 || Zin(base)")
    
    st.markdown("### 🎯 Rendimiento de Amplificación")
    r_a, r_b, r_c = st.columns(3)
    r_a.metric("Ganancia de Voltaje (Av)", f"{av:.2f}", help="rc / r'e")
    r_b.metric("Señal real en Base (vin)", f"{vin*1e3:.3f} mV", help="Atenuación por efecto de carga con Rg")
    r_c.metric("Voltaje de Salida (vout)", f"{vout*1e3:.2f} mV", delta=f"{av:.1f}x amplificado")
    
    st.markdown("---")
    
    # SECCIÓN CAPACITORES
    st.header("3️⃣ Diseño Óptimo de Condensadores")
    st.caption(f"Valores mínimos recomendados para operar a una frecuencia de **{frecuencia/1000:.1f} kHz** sin atenuar la señal.")
    
    col_cap1, col_cap2, col_cap3 = st.columns(3)
    col_cap1.info(f"**Condensador Entrada (Cin):**\n\n $\\ge$ {c_entrada * 1e6:.2f} µF")
    col_cap2.info(f"**Condensador Salida (Cout):**\n\n $\\ge$ {c_salida * 1e6:.2f} µF")
    col_cap3.info(f"**Condensador Emisor (Ce):**\n\n $\\ge$ {c_emisor * 1e6:.2f} µF")