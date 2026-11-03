# Archivo base para el despliegue del Agente en Streamlit

# ============================================================
# SEMANA 6 - APP DE SEGMENTACIÓN DE CLIENTES RETAIL
# Técnicas: K-means, GMM y K-prototypes
# ============================================================

# 1. IMPORTAR LIBRERÍAS
import streamlit as st
import pandas as pd
import plotly.express as px
import os


# 2. CONFIGURACIÓN GENERAL DE LA APLICACIÓN
st.set_page_config(
    page_title="Segmentación de Clientes Retail",
    page_icon="📊",
    layout="wide"
)

# Título y descripción
st.title("📊 Segmentación de Clientes Retail")
st.write(
    "Aplicación interactiva para explorar y comparar "
    "los segmentos de clientes obtenidos mediante "
    "K-means, GMM y K-prototypes."
)

st.divider()


# 3. CARGAR LOS DATOS
# Se permite cargar el CSV desde la computadora.
# Si no se carga ningún archivo, se busca el CSV
# generado por el notebook en la misma carpeta.

st.sidebar.header("📁 Cargar datos")

archivo = st.sidebar.file_uploader(
    "Selecciona segmentos_notebook.csv",
    type=["csv"]
)

if archivo is not None:
    df = pd.read_csv(archivo)

elif os.path.exists("segmentos_notebook.csv"):
    df = pd.read_csv("segmentos_notebook.csv")

else:
    st.warning(
        "No se encontró el archivo de datos. "
        "Carga el archivo segmentos_notebook.csv "
        "para comenzar."
    )
    st.stop()


# 4. VALIDAR LAS COLUMNAS NECESARIAS
# Estas columnas son generadas en el paso 4 del notebook.

columnas_segmentacion = [
    "seg_kproto",
    "seg_kmeans",
    "seg_gmm",
    "Cluster"
]

faltantes = [
    col for col in columnas_segmentacion
    if col not in df.columns
]

if faltantes:
    st.error(
        f"El archivo no contiene las columnas necesarias: {faltantes}"
    )
    st.stop()

# Comprobar que existan las variables para el análisis
if "gasto_total" not in df.columns:
    st.error("No se encontró la columna gasto_total.")
    st.stop()


# 5. CONFIGURAR LOS FILTROS
st.sidebar.header("⚙️ Filtros")

# Seleccionar la técnica de segmentación
tecnicas = {
    "K-prototypes": "seg_kproto",
    "K-means": "seg_kmeans",
    "GMM": "seg_gmm"
}

tecnica_seleccionada = st.sidebar.selectbox(
    "Selecciona la técnica:",
    list(tecnicas.keys())
)

# Obtener la columna correspondiente a la técnica elegida
col_segmento = tecnicas[tecnica_seleccionada]

# Obtener los segmentos disponibles
segmentos = sorted(
    df[col_segmento].dropna().unique().tolist()
)

# Permitir seleccionar un segmento específico o todos
opciones = ["Todos"] + segmentos

segmento_seleccionado = st.sidebar.selectbox(
    "Filtrar por segmento:",
    opciones
)

# Aplicar el filtro seleccionado
if segmento_seleccionado == "Todos":
    df_filtrado = df.copy()
else:
    df_filtrado = df[
        df[col_segmento] == segmento_seleccionado
    ].copy()


# 6. CREAR LAS PESTAÑAS DE LA APLICACIÓN
tab1, tab2, tab3 = st.tabs([
    "📌 Resumen",
    "📈 Visualización",
    "👥 Datos de clientes"
])


# ============================================================
# PESTAÑA 1: RESUMEN GENERAL
# ============================================================

with tab1:

    st.subheader("Resumen de la segmentación")

    st.write(
        f"Técnica seleccionada: **{tecnica_seleccionada}**"
    )

    # Calcular indicadores generales
    total_clientes = len(df_filtrado)

    total_segmentos = df_filtrado[
        col_segmento
    ].nunique()

    gasto_promedio = df_filtrado[
        "gasto_total"
    ].mean()

    ingreso_promedio = (
        df_filtrado["ingreso_anual"].mean()
        if "ingreso_anual" in df_filtrado.columns
        else 0
    )

    # Mostrar indicadores principales
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Clientes",
        f"{total_clientes:,}"
    )

    col2.metric(
        "Segmentos",
        total_segmentos
    )

    col3.metric(
        "Gasto promedio",
        f"{gasto_promedio:,.1f}"
    )

    col4.metric(
        "Ingreso anual promedio",
        f"{ingreso_promedio:,.1f}"
    )

    st.divider()

    # Calcular las características promedio de cada segmento
    st.subheader("Características por segmento")

    columnas_promedio = [
        col for col in [
            "ingreso_anual",
            "gasto_total",
            "edad",
            "hijos_pequenos",
            "compras_tienda",
            "compras_web",
            "compras_catalogo"
        ]
        if col in df_filtrado.columns
    ]

    resumen = (
        df_filtrado
        .groupby(col_segmento)[columnas_promedio]
        .mean()
        .round(1)
    )

    st.dataframe(
        resumen,
        use_container_width=True
    )

    # Mostrar la cantidad de clientes por segmento
    st.subheader("Distribución de clientes")

    conteo = (
        df_filtrado[col_segmento]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    conteo.columns = ["Segmento", "Clientes"]

    grafico_barras = px.bar(
        conteo,
        x="Segmento",
        y="Clientes",
        color="Segmento",
        title="Cantidad de clientes por segmento",
        text="Clientes"
    )

    st.plotly_chart(
        grafico_barras,
        use_container_width=True
    )


# ============================================================
# PESTAÑA 2: VISUALIZACIÓN INTERACTIVA
# ============================================================

with tab2:

    st.subheader("Exploración visual de los segmentos")

    st.write(
        "Selecciona las variables que deseas comparar "
        "para observar cómo se distribuyen los clientes."
    )

    # Identificar las columnas numéricas disponibles
    variables_numericas = [
        col for col in df_filtrado.select_dtypes(
            include="number"
        ).columns
        if col not in [
            "id_cliente",
            "seg_kproto",
            "seg_kmeans",
            "seg_gmm"
        ]
    ]

    if len(variables_numericas) < 2:
        st.warning(
            "Se necesitan al menos dos variables numéricas."
        )
    else:

        # Permitir seleccionar las variables de los ejes
        colx, coly = st.columns(2)

        variable_x = colx.selectbox(
            "Variable del eje X:",
            variables_numericas,
            index=(
                variables_numericas.index("ingreso_anual")
                if "ingreso_anual" in variables_numericas
                else 0
            )
        )

        variable_y = coly.selectbox(
            "Variable del eje Y:",
            variables_numericas,
            index=(
                variables_numericas.index("gasto_total")
                if "gasto_total" in variables_numericas
                else 1
            )
        )

        # Controlar la cantidad de registros del gráfico
        cantidad = st.slider(
            "Cantidad de clientes a visualizar:",
            min_value=1,
            max_value=len(df_filtrado),
            value=min(1000, len(df_filtrado))
        )

        # Tomar una muestra de clientes para visualizar
        datos_grafico = df_filtrado.sample(
            n=cantidad,
            random_state=0
        )

        # Crear gráfico de dispersión interactivo
        grafico = px.scatter(
            datos_grafico,
            x=variable_x,
            y=variable_y,
            color=col_segmento,
            hover_data=[
                col for col in [
                    "id_cliente",
                    "educacion",
                    "estado_civil"
                ]
                if col in datos_grafico.columns
            ],
            title=f"Segmentación mediante {tecnica_seleccionada}",
            labels={
                variable_x: variable_x.replace("_", " ").title(),
                variable_y: variable_y.replace("_", " ").title(),
                col_segmento: "Segmento"
            },
            opacity=0.7
        )

        st.plotly_chart(
            grafico,
            use_container_width=True
        )


# ============================================================
# PESTAÑA 3: DATOS DE CLIENTES
# ============================================================

with tab3:

    st.subheader("Consulta de clientes")

    st.write(
        "Consulta los registros y sus segmentos asignados "
        "según la técnica seleccionada."
    )

    # Mostrar la cantidad de registros encontrados
    st.info(
        f"Se encontraron {len(df_filtrado):,} clientes "
        f"con los filtros seleccionados."
    )

    # Mostrar la tabla de clientes
    st.dataframe(
        df_filtrado,
        use_container_width=True,
        height=450
    )

    # Preparar archivo CSV para descargar
    csv_descarga = df_filtrado.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 Descargar datos filtrados",
        data=csv_descarga,
        file_name="clientes_segmentados.csv",
        mime="text/csv"
    )


# 7. PIE DE PÁGINA
st.divider()

st.caption(
    "Proyecto académico - Semana 6 | "
    "Segmentación de clientes mediante "
    "K-means, GMM y K-prototypes."
)
