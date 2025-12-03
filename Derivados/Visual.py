import streamlit as st
import pandas as pd
from Funciones_y_clases import Subyacente, Call, Put, Call_Digital, Put_Digital, Arbol_Binomial, Cobertura, grafica_arbol, grafica_cobertura

# ---------------------------------------- INICIALIZACION, CREACION Y ACTUALIZACION DE CLASES --------------------------------------------


# Función para iniciar todas las clases y para definir 
def iniciar_sesion():
    if "arboles" not in st.session_state:
        st.session_state["arboles"] = {}                                # Tipo de arbol -> Objeto Arbol_Binomial

    if "Subyacente" not in st.session_state:
        st.session_state["Subyacente"] = Subyacente(1)                  # Objeto Suyacente

    if "Derivado" not in st.session_state:
        st.session_state["Derivado"] = None                             # Objeto Derivado 

    if "tipo_derivado" not in st.session_state:
        st.session_state["tipo_derivado"] = None                        # Cadena de la seleccion actual de derivado

    if "tipo_arbol_seleccionado" not in st.session_state:
        st.session_state["tipo_arbol_seleccionado"] = None              # Cadena de la seleccion actual de arbol


# Función para crear un Derivado
def crear_derivado(opciones, seleccion):

    # Para distinguir entre americanas y europeas
    tipo = "americana" if seleccion in ["Call americano", "Put americano"] else "europea"

    # Creamos el objeto Derivado (sin guardarlo aquí; se guardará en la lógica de UI)
    Derivado = opciones[seleccion](subyacente = st.session_state["Subyacente"],
                                    strike = None,
                                    vencimiento = None,
                                    periodos = None,
                                    interes = None,
                                    tipo = tipo,
                                    posicion = None)
    return Derivado


# Funcion para crear o modificar el Subyacente 
def crear_modicar_subyacente(S0):

    # Si no existe el subyacente en la app, lo creamos
    if st.session_state["Subyacente"] is None:
        st.session_state["Subyacente"] = Subyacente(S0)

    # Si ya existe, lo actualizamos in-place
    else:
        st.session_state["Subyacente"].S0 = S0
    return st.session_state["Subyacente"]

# Funcion para crear o modificar el arbol
def crear_modificar_arbol(tipo_arbol, Derivado):

    # Si no existe el tipo de arbol en la app, lo creamos
    if tipo_arbol not in st.session_state["arboles"]:

        subyacente_del_arbol = st.session_state["Subyacente"]

        # Evitar valores None
        T_temporal = Derivado.T if getattr(Derivado, "T", None) is not None else 1
        N_temporal = Derivado.N if getattr(Derivado, "N", None) is not None else 1
        r_temporal = Derivado.r if getattr(Derivado, "r", None) is not None else 0.0

        # Creamos el árbol
        arbol = Arbol_Binomial(subyacente_del_arbol, T_temporal, N_temporal, r_temporal, tipo_arbol)

        # Construcción inicial
        if tipo_arbol == "Multiplicativo":
            if arbol.u is not None and arbol.d is not None:
                arbol.construir_arbol_multiplicativo()
            else:
                arbol.arbol_temporal()
        else:
            arbol.arbol_temporal()

        # Flag que indica si el usuario ya modificó un nodo manualmente
        arbol.editado = False

        st.session_state["arboles"][tipo_arbol] = arbol

    # --- El árbol YA EXISTE ---
    else:
        arbol = st.session_state["arboles"][tipo_arbol]

        # mantener referencia al subyacente
        arbol.Subyacente = st.session_state["Subyacente"]

        # actualizar parámetros básicos
        if getattr(Derivado, "T", None) is not None:
            arbol.T = Derivado.T
            arbol.delta = arbol.T / arbol.N if arbol.N != 0 else 0

        if getattr(Derivado, "N", None) is not None:
            arbol.N = Derivado.N
            arbol.delta = arbol.T / arbol.N if arbol.N != 0 else 0

        if getattr(Derivado, "r", None) is not None:
            arbol.r = Derivado.r

        # SOLO reconstruir el árbol si NO ha sido editado manualmente
        if not hasattr(arbol, "editado") or arbol.editado is False:

            if arbol.tipo == "General":
                arbol.arbol_temporal()

            elif arbol.tipo == "Multiplicativo":
                if arbol.u is not None and arbol.d is not None:
                    arbol.construir_arbol_multiplicativo()
                else:
                    arbol.arbol_temporal()

            else:  # Recombinante
                arbol.arbol_temporal()

    return st.session_state["arboles"][tipo_arbol]



# Funcion para actualizar atributos del subyacente, derivado o del arbol (utilidad)
def actualizar_parametro(clase, parametro, nuevo_valor):

    if clase == "Subyacente":
        setattr(st.session_state["Subyacente"], parametro, nuevo_valor)
        for arbol in st.session_state["arboles"].values():
            arbol.Subyacente = st.session_state["Subyacente"]

    elif clase == "Derivado":
        setattr(st.session_state["Derivado"], parametro, nuevo_valor)

    else:
        for arbol in st.session_state["arboles"].values():
            setattr(arbol, parametro, nuevo_valor)

        if parametro in ("S0", "T", "N", "r"):
            for arbol in st.session_state["arboles"].values():
                if arbol.tipo == "General" or arbol.tipo == "Recombinante":
                    arbol.arbol_temporal()
                elif arbol.tipo == "Multiplicativo":
                    if arbol.u is not None and arbol.d is not None:
                        arbol.construir_arbol_multiplicativo()
                    else:
                        arbol.arbol_temporal()

# ------------------------------------------------------ TITULO Y CONFIGURACIÓN ------------------------------------------------------------

# Para ocupar toda la pantalla
st.set_page_config(layout="wide")

# Iniciamos las variables y clases en session_state
iniciar_sesion()

# Titulo
st.markdown("""
            <h1 style="
                text-align:center; 
                font-size:60px; 
                margin-top:0px; 
                padding-top:0px;
                font-family: 'Segoe UI';
                col_or: #000000;
            ">
            CALCULADORA DE DERIVADOS
            </h1>
            """, unsafe_allow_html=True)

# Nota y linea de división
#st.caption("By Josué Carlos Abad Villegas (JCAV)")
st.markdown( "<hr style='margin:0; padding:0; border: none; border-top: 1px solid #ccc;'>",unsafe_allow_html=True)

# ------------------------------------------------------- SELECCION DE  DERIVADO -----------------------------------------------------------

# Subtitulo
st.subheader("Selecciona un derivado")

# Opciones disponibles
opciones = {
    "Call europeo" : Call, 
    "Put europeo": Put,
    "Call americano" : Call, 
    "Put americano" : Put,
    "Call digital" : Call_Digital,  
    "Put digital" : Put_Digital
}

# Selección de derivado
seleccion = st.pills(
            label = "Opciones disponibles",
            options = opciones.keys(),
            selection_mode = "single"
        )

# Creamos / recuperamos la clase del derivado seleccionado
if seleccion:
    # Si cambió el tipo de derivado, crear uno nuevo y guardarlo en session_state
    if st.session_state["tipo_derivado"] != seleccion:
        st.session_state["tipo_derivado"] = seleccion
        st.session_state["Derivado"] = crear_derivado(opciones, seleccion)
    # Creamos el derivado
    Derivado = st.session_state["Derivado"]

# Linea de division
st.markdown("<hr style='margin:0; padding:0; border: none; border-top: 1px solid #ccc;'>",unsafe_allow_html=True)

# ------------------------------------------------------ INPUTS  ----------------------------------------------------------------------

# Una vez que se haya elegido el derivado
if seleccion:

    # ---------------------------------------------- PRIMERA PARTE - CARACTERISTICAS ----------------------------------------------------
    st.markdown("#### Caraterísticas:")
    col_11, col_12, col_13, col_14, col_15 = st.columns(5)

    # Determinamos posicion del derivado
    with col_11:
        posicion = st.radio("Posicion",["largo", "corto"])
        Derivado.posicion = posicion

    # Determinamos strike del derivado
    with col_12:
        K = st.number_input("Strike K", min_value=1.0, step=1.0)
        Derivado.K = K

    # Determinamos vencimiento T
    with col_13:
        T = st.number_input("Vencimiento T", min_value=0.0, value=1.0, step=0.1)
        Derivado.T = T

        # sincronizar árbol seleccionado si existe 
        if st.session_state["tipo_arbol_seleccionado"]:
            crear_modificar_arbol(st.session_state["tipo_arbol_seleccionado"], Derivado)

    # Determinamos la cantidad de periodos
    with col_14:
        N = st.number_input("Periodos N", min_value=1, value=1, step=1)
        Derivado.N = N
        if st.session_state["tipo_arbol_seleccionado"]:
            crear_modificar_arbol(st.session_state["tipo_arbol_seleccionado"], Derivado)

    # ----------------------------------------------------- SEGUNDA PARTE - MERCADO -------------------------------------------------------
    st.markdown("#### Mercado:")
    col_21, col_22, col_23, col_24, col_25 = st.columns(5)

    # Determinamos el tipo de la tasa libre de riesgo
    with col_21:
        tasa = st.radio("Tipo de tasa",["Discreta","Continua"])

    # Determinamos la tasa libre de riesgo
    with col_22:
        r = st.number_input("Tasa libre de riesgo r", min_value = 0.0, max_value = 1.0,step=0.01)
        Derivado.r = r
        if st.session_state["tipo_arbol_seleccionado"]:
            crear_modificar_arbol(st.session_state["tipo_arbol_seleccionado"], Derivado)

    # --------------------------------------------------- TERCERA PARTE - SUBYACENTE ------------------------------------------------------
    st.markdown("#### Subyacente:")
    col_31, col_32, col_33, col_34, col_35 = st.columns(5)

    # Determinamos el precio inicial del subyacente
    with col_31:
        S0 = st.number_input("Precio Inicial So",min_value=1)
        Subyacente_del_Derivado = crear_modicar_subyacente(S0)

        # sincronizar árboles si ya hay alguno seleccionado
        if st.session_state["tipo_arbol_seleccionado"]:
            crear_modificar_arbol(st.session_state["tipo_arbol_seleccionado"], Derivado)

    # Creamos la clase del arbol de precios del derivado 
    with col_32:
        arbol = st.radio("Tipo de arbol",["General","Recombinante","Multiplicativo"])

        st.session_state["tipo_arbol_seleccionado"] = arbol
        arbol_del_subyacente = crear_modificar_arbol(arbol, st.session_state["Derivado"])

    # Determinamos el tipo de subyacente
    with col_33:
        dividendo = st.radio("Tipo de Subyacente",["Sin dividendos", "Con dividendos discretos", "Con dividendos continuos"])
        Subyacente_del_Derivado.tipo_subyacente = dividendo

        if dividendo == "Con dividendos discretos":
            with col_34:
                monto = st.number_input("Dividendo",min_value=0.0,step=1.0)
                Subyacente_del_Derivado.monto_dividendo = monto

            with col_35:
                periodicidad =st.radio("Periodicidad",["Anual", "Semestral", "Mensual","Por periodo"], horizontal=False)
                Subyacente_del_Derivado.periodicidad = periodicidad

        elif dividendo == "Con dividendos continuos":
            with col_34:
                tasa_div = st.number_input("Dividendo",min_value=0.0, step=0.01)
                Subyacente_del_Derivado.tasa_dividendo = tasa_div

            with col_35:
                periodicidad =st.radio("Periodicidad",["Anual", "Semestral", "Mensual","Por periodo"], horizontal=False)
                Subyacente_del_Derivado.periodicidad = periodicidad

    st.markdown("<hr style='margin:0; padding:0; border: none; border-top: 1px solid #ccc;'>",unsafe_allow_html=True)

# ------------------------------------------------ CUARTA PARTE - ARBOL DEL SUBYACENTE ------------------------------------------------

    col_41, col_42 = st.columns([1, 3])

    with col_41:
        st.markdown(f"#### Arbol de precios ({arbol})")

        if arbol == "General":
            lista_nombres = arbol_del_subyacente.nombres_nodos()[1:]
            seleccion_nodo = st.selectbox("Selecciona un nodo", lista_nombres)
            t, j = arbol_del_subyacente.obtener_posicion(seleccion_nodo)
            nuevo_precio = st.number_input("Nuevo precio del nodo",min_value=1.0,step=1.0)

            Boton_precio = st.button("Actualizar precio")
            if Boton_precio:
                arbol_del_subyacente.cambiar_nodo(t, j, nuevo_precio)
                arbol_del_subyacente.editado = True
                st.session_state["arboles"][arbol] = arbol_del_subyacente
                st.rerun() 

                
        elif arbol == "Recombinante":

            lista_nombres = arbol_del_subyacente.nombres_nodos()[1:]
            seleccion_nodo = st.selectbox("Selecciona un nodo", lista_nombres)
            t, j = arbol_del_subyacente.obtener_posicion(seleccion_nodo)
            nuevo_precio = st.number_input("Nuevo precio del nodo",min_value=1.0,step=1.0)

            Boton_precio = st.button("Actualizar precio")
            
            if Boton_precio:
                arbol_del_subyacente.cambiar_nodo(t, j, nuevo_precio)
                arbol_del_subyacente.editado = True
                st.session_state["arboles"][arbol] = arbol_del_subyacente
                st.rerun()   

        else:   # Multiplicativo
            u_nuevo = st.number_input("Valor de u", min_value = 0.0, value=arbol_del_subyacente.u if arbol_del_subyacente.u is not None else 0.0)
            d_nuevo = st.number_input("Valor de d", min_value = 0.0, value=arbol_del_subyacente.d if arbol_del_subyacente.d is not None else 0.0)

            Boton_arbol =  st.button("Actualizar valores de u y d",type = "secondary")

            if Boton_arbol:
               # actualizar directamente el arbol persistente
               st.session_state["arboles"][arbol].u = u_nuevo
               st.session_state["arboles"][arbol].d = d_nuevo

               # reconstruir el árbol multiplicativo en session_state (solo si ambos existen)
               if st.session_state["arboles"][arbol].u is not None and st.session_state["arboles"][arbol].d is not None:
                   st.session_state["arboles"][arbol].construir_arbol_multiplicativo()

               # sincronizar la variable local
               arbol_del_subyacente = st.session_state["arboles"][arbol]

        for i in range(12):
            st.write("")
        Boton =  st.button("Calcular precio y cobertura del derivado",type = "primary")

    with col_42:
        fig = grafica_arbol(arbol_del_subyacente, arbol)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr style='margin:0; padding:0; border: none; border-top: 1px solid #ccc;'>",unsafe_allow_html=True)

# ----------------------------------------- QUINTA PARTE - PRECIO Y COBERTURA DEL DERIVADO --------------------------------------------

    if Boton:
        st.markdown(f"#### Precio y cobertura del Derivado ")

        # tomar los objetos persistentes
        Derivado = st.session_state["Derivado"]
        tipo_arbol = st.session_state["tipo_arbol_seleccionado"]
        arbol_del_subyacente = st.session_state["arboles"][tipo_arbol]

        # recalcular probabilidades y cobertura con los objetos persistentes
        arbol_del_subyacente.probabilidades_neutras_al_riesgo("continuo")

        Cobertura_del_Derivado  = Cobertura(Derivado, arbol_del_subyacente)
        Cobertura_del_Derivado.calcular_cobertura("continuo")

        fig_cobertura = grafica_cobertura(arbol_del_subyacente, Cobertura_del_Derivado)
        st.plotly_chart(fig_cobertura, use_container_width=True)


        tabla_valores = []
        tabla_alphas = []
        tabla_betas = []
        tabla_optimos = []

        # ---- VALORES ----
        numero = 0
        for tiempo in Cobertura_del_Derivado.valores:
            for nodo in tiempo:
                tabla_valores.append({"Nodo": f"V{numero}", "Valor": nodo})
                numero += 1

        # ---- ALPHAS ----
        numero = 0
        for tiempo in Cobertura_del_Derivado.alphas:
            for nodo in tiempo:
                tabla_alphas.append({"Nodo": f"ALPHA {numero}", "Valor": nodo})
                numero += 1

        # ---- BETAS ----
        numero = 0
        for tiempo in Cobertura_del_Derivado.betas:
            for nodo in tiempo:
                tabla_betas.append({"Nodo": f"BETA {numero}", "Valor": nodo})
                numero += 1

        # Convertir a DataFrame
        df_valores = pd.DataFrame(tabla_valores)
        df_alphas  = pd.DataFrame(tabla_alphas)
        df_betas   = pd.DataFrame(tabla_betas)

        col_51, col_52, col_53, col_54 = st.columns(4)

        # Mostrar tablas en Streamlit
        with col_51:
            st.markdown(f"##### Valores del derivado")
            st.dataframe(df_valores,hide_index=True)

        with col_52:
            st.markdown("##### Alphas")
            st.dataframe(df_alphas,hide_index=True)

        with col_53:
            st.markdown("##### Betas")
            st.dataframe(df_betas,hide_index=True)

        if seleccion in ["Call americano", "Put americano"]:

            # ---- OPTIMO ----
            numero = 0
            for tiempo in Cobertura_del_Derivado.optimos:
                for nodo in tiempo:
                    tabla_optimos.append({"Nodo": f"NODO {numero}", "Valor": "Optimo" if  nodo == 1 else "No Optimo"})
                    numero += 1

            with col_54:
                st.markdown("##### Nodos optimos")
                st.dataframe(tabla_optimos,hide_index=True)
        