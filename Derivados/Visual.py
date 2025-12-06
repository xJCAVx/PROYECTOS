import streamlit as st
import pandas as pd
from Funciones_y_clases import (Subyacente, Call, Put, Call_Digital, 
                                Put_Digital, Arbol_Binomial,
                                Arbol_Binomial_Con_Dividendos,Cobertura, 
                                grafica_arbol, grafica_cobertura)

# ---------------------------------------- INICIALIZACION, CREACION Y ACTUALIZACION DE CLASES --------------------------------------------


def iniciar_sesion():
    """Inicializa las variables de sesión"""

    if "arboles" not in st.session_state:
        st.session_state["arboles"] = {}                                # Tipo de arbol 

    if "Subyacente" not in st.session_state:
        st.session_state["Subyacente"] = Subyacente(1)                  # Objeto Suyacente

    if "Derivado" not in st.session_state:
        st.session_state["Derivado"] = None                             # Objeto Derivado 

    if "tipo_derivado" not in st.session_state:
        st.session_state["tipo_derivado"] = None                        # Cadena de la seleccion actual de derivado

    if "tipo_arbol_seleccionado" not in st.session_state:
        st.session_state["tipo_arbol_seleccionado"] = None              # Cadena de la seleccion actual de arbol


def crear_derivado(opciones, seleccion):
    """Crea un objeto derivado según la selección"""
    tipo = "americana" if seleccion in ["Call americano", "Put americano"] else "europea"
    
    Derivado = opciones[seleccion](
        subyacente=st.session_state["Subyacente"],
        strike=None,
        vencimiento=None,
        periodos=None,
        interes=None,
        tipo=tipo,
        posicion=None
    )
    return Derivado


def crear_modificar_subyacente(S0):
    """Crea o modifica el subyacente"""
    if st.session_state["Subyacente"] is None:
        st.session_state["Subyacente"] = Subyacente(S0)
    else:
        st.session_state["Subyacente"].S0 = S0
    
    return st.session_state["Subyacente"]


def crear_modificar_arbol(tipo_arbol, Derivado):
    """Crea o modifica el árbol binomial (con o sin dividendos)"""
    
    # Determinar si usar árbol con dividendos
    usar_dividendos = (
        st.session_state["Subyacente"].tipo_subyacente in 
        ["Con dividendos discretos", "Con dividendos continuos"]
    )
    
    # Si el árbol no existe, crearlo
    if tipo_arbol not in st.session_state["arboles"]:
        subyacente_del_arbol = st.session_state["Subyacente"]
        
        T_temporal = Derivado.T if getattr(Derivado, "T", None) is not None else 1
        N_temporal = Derivado.N if getattr(Derivado, "N", None) is not None else 1
        r_temporal = Derivado.r if getattr(Derivado, "r", None) is not None else 0.0
        
        # Crear árbol según si tiene dividendos o no
        if usar_dividendos:
            arbol = Arbol_Binomial_Con_Dividendos(
                subyacente_del_arbol, T_temporal, N_temporal, r_temporal, tipo_arbol
            )
        else:
            arbol = Arbol_Binomial(
                subyacente_del_arbol, T_temporal, N_temporal, r_temporal, tipo_arbol
            )
        
        # Construcción inicial
        if tipo_arbol == "Multiplicativo":
            if arbol.u is not None and arbol.d is not None:
                arbol.construir_arbol_multiplicativo()
            else:
                arbol.arbol_temporal()
        else:
            arbol.arbol_temporal()
        
        arbol.editado = False
        st.session_state["arboles"][tipo_arbol] = arbol
    
    # Si el árbol ya existe, actualizarlo
    else:
        arbol = st.session_state["arboles"][tipo_arbol]
        
        # Verificar si cambió el tipo de dividendo y recrear árbol si es necesario
        tipo_arbol_actual = type(arbol).__name__
        tipo_arbol_necesario = "Arbol_Binomial_Con_Dividendos" if usar_dividendos else "Arbol_Binomial"
        
        if tipo_arbol_actual != tipo_arbol_necesario:
            # Recrear árbol con el tipo correcto
            subyacente_del_arbol = st.session_state["Subyacente"]
            T_temporal = Derivado.T if getattr(Derivado, "T", None) is not None else 1
            N_temporal = Derivado.N if getattr(Derivado, "N", None) is not None else 1
            r_temporal = Derivado.r if getattr(Derivado, "r", None) is not None else 0.0
            
            if usar_dividendos:
                arbol = Arbol_Binomial_Con_Dividendos(
                    subyacente_del_arbol, T_temporal, N_temporal, r_temporal, tipo_arbol
                )
            else:
                arbol = Arbol_Binomial(
                    subyacente_del_arbol, T_temporal, N_temporal, r_temporal, tipo_arbol
                )
            
            if tipo_arbol == "Multiplicativo":
                if arbol.u is not None and arbol.d is not None:
                    arbol.construir_arbol_multiplicativo()
                else:
                    arbol.arbol_temporal()
            else:
                arbol.arbol_temporal()
            
            arbol.editado = False
            st.session_state["arboles"][tipo_arbol] = arbol
        else:
            # Actualizar parámetros del árbol existente
            arbol.Subyacente = st.session_state["Subyacente"]
            
            if getattr(Derivado, "T", None) is not None:
                arbol.T = Derivado.T
                arbol.delta = arbol.T / arbol.N if arbol.N != 0 else 0
            
            if getattr(Derivado, "N", None) is not None:
                arbol.N = Derivado.N
                arbol.delta = arbol.T / arbol.N if arbol.N != 0 else 0
                
                # Recalcular periodos con dividendos si tiene dividendos
                if usar_dividendos:
                    arbol.calcular_dividendos_por_periodo()
            
            if getattr(Derivado, "r", None) is not None:
                arbol.r = Derivado.r
            
            # Reconstruir árbol si no ha sido editado manualmente
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

# -------------------------------------------------------- CONFIGURACIÓN DE LA PÁGINA --------------------------------------------------------------


st.set_page_config(layout="wide", page_title="Calculadora de Derivados")
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

st.markdown( "<hr style='margin:0; padding:0; border: none; border-top: 1px solid #ccc;'>",unsafe_allow_html=True)


# ------------------------------------------------------- SELECCION DE  DERIVADO -----------------------------------------------------------


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

if seleccion:
    if st.session_state["tipo_derivado"] != seleccion:
        st.session_state["tipo_derivado"] = seleccion
        st.session_state["Derivado"] = crear_derivado(opciones, seleccion)
    Derivado = st.session_state["Derivado"]

st.markdown("<hr style='margin:0; padding:0; border: none; border-top: 1px solid #ccc;'>",unsafe_allow_html=True)


# ------------------------------------------------------ INPUTS  ----------------------------------------------------------------------


# Una vez que se haya elegido el derivado
if seleccion:

    # ---------------------------------------------- PRIMERA PARTE - CARACTERISTICAS ----------------------------------------------------
    st.markdown("#### Caraterísticas del Derivado")
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
        r = st.number_input("Tasa libre de riesgo r", min_value = 0.0, max_value = 1.0,step=0.0001,format = f"%.5f")
        Derivado.r = r
        if st.session_state["tipo_arbol_seleccionado"]:
            crear_modificar_arbol(st.session_state["tipo_arbol_seleccionado"], Derivado)


    # --------------------------------------------------- TERCERA PARTE - SUBYACENTE ------------------------------------------------------
   
   
    st.markdown("#### Subyacente:")
    col_31, col_32, col_33, col_34, col_35 = st.columns(5)

    # Determinamos el precio inicial del subyacente
    with col_31:
        S0 = st.number_input("Precio Inicial So",min_value=1)
        Subyacente_del_Derivado = crear_modificar_subyacente(S0)
        if st.session_state["tipo_arbol_seleccionado"]:
            crear_modificar_arbol(st.session_state["tipo_arbol_seleccionado"], Derivado)

    # Creamos la clase del arbol de precios del derivado 
    with col_32:
        arbol = st.radio("Tipo de arbol",["General","Recombinante","Multiplicativo"])
        st.session_state["tipo_arbol_seleccionado"] = arbol
        arbol_del_subyacente = crear_modificar_arbol(arbol, st.session_state["Derivado"])

    # Determinamos el tipo de subyacente
    with col_33:
        dividendo = st.radio("Tipo de Subyacente", 
                            ["Sin dividendos", "Con dividendos discretos", "Con dividendos continuos"])
        Subyacente_del_Derivado.tipo_subyacente = dividendo
        
        # Si cambió el tipo de dividendo, recrear el árbol
        if st.session_state["tipo_arbol_seleccionado"]:
            crear_modificar_arbol(st.session_state["tipo_arbol_seleccionado"], Derivado)
        
        if dividendo == "Con dividendos discretos":
            with col_34:
                monto = st.number_input("Monto dividendo", min_value=0.0, step=1.0)
                Subyacente_del_Derivado.monto_dividendo = monto
                
                # Actualizar árbol
                if st.session_state["tipo_arbol_seleccionado"]:
                    arbol_del_subyacente = st.session_state["arboles"][st.session_state["tipo_arbol_seleccionado"]]
                    arbol_del_subyacente.Subyacente.monto_dividendo = monto
                    if not arbol_del_subyacente.editado:
                        arbol_del_subyacente.calcular_dividendos_por_periodo()
                        if arbol == "Multiplicativo" and arbol_del_subyacente.u and arbol_del_subyacente.d:
                            arbol_del_subyacente.construir_arbol_multiplicativo()
                        else:
                            arbol_del_subyacente.arbol_temporal()
            
            with col_35:
                periodicidad = st.radio("Periodicidad", 
                                       ["Anual", "Semestral", "Mensual", "Por periodo"])
                Subyacente_del_Derivado.periodicidad = periodicidad
                
                # Actualizar árbol
                if st.session_state["tipo_arbol_seleccionado"]:
                    arbol_del_subyacente = st.session_state["arboles"][st.session_state["tipo_arbol_seleccionado"]]
                    arbol_del_subyacente.Subyacente.periodicidad = periodicidad
                    if not arbol_del_subyacente.editado:
                        arbol_del_subyacente.calcular_dividendos_por_periodo()
                        if arbol == "Multiplicativo" and arbol_del_subyacente.u and arbol_del_subyacente.d:
                            arbol_del_subyacente.construir_arbol_multiplicativo()
                        else:
                            arbol_del_subyacente.arbol_temporal()
        
        elif dividendo == "Con dividendos continuos":
            with col_34:
                tasa_div = st.number_input("Tasa dividendo", min_value=0.0, step=0.01)
                Subyacente_del_Derivado.tasa_dividendo = tasa_div
                
                # Actualizar árbol
                if st.session_state["tipo_arbol_seleccionado"]:
                    arbol_del_subyacente = st.session_state["arboles"][st.session_state["tipo_arbol_seleccionado"]]
                    arbol_del_subyacente.Subyacente.tasa_dividendo = tasa_div
                    if not arbol_del_subyacente.editado:
                        if arbol == "Multiplicativo" and arbol_del_subyacente.u and arbol_del_subyacente.d:
                            arbol_del_subyacente.construir_arbol_multiplicativo()
                        else:
                            arbol_del_subyacente.arbol_temporal()
            
            with col_35:
                periodicidad = st.radio("Periodicidad", 
                                       ["Anual", "Semestral", "Mensual", "Por periodo"])
                Subyacente_del_Derivado.periodicidad = periodicidad

    st.markdown("<hr style='margin:0; padding:0; border: none; border-top: 1px solid #ccc;'>",unsafe_allow_html=True)

# ------------------------------------------------ CUARTA PARTE - ARBOL DEL SUBYACENTE ------------------------------------------------

    col_41, col_42 = st.columns([1, 3])
    
    with col_41:
        st.markdown(f"####  Árbol de precios ({arbol})")
        
        if arbol in ["General", "Recombinante"]:
            lista_nombres = arbol_del_subyacente.nombres_nodos()[1:]
            seleccion_nodo = st.selectbox("Selecciona un nodo", lista_nombres)
            t, j = arbol_del_subyacente.obtener_posicion(seleccion_nodo)
            nuevo_precio = st.number_input("Nuevo precio del nodo", min_value=1.0, step=1.0)
            
            Boton_precio = st.button("Actualizar precio", type="secondary")
            if Boton_precio:
                arbol_del_subyacente.cambiar_nodo(t, j, nuevo_precio)
                arbol_del_subyacente.editado = True
                st.session_state["arboles"][arbol] = arbol_del_subyacente
                st.rerun()
        
        else:  # Multiplicativo
            u_nuevo = st.number_input("Valor de u", min_value=0.0, 
                                     value=arbol_del_subyacente.u if arbol_del_subyacente.u else 1.2,
                                     step=0.01)
            d_nuevo = st.number_input("Valor de d", min_value=0.0, 
                                     value=arbol_del_subyacente.d if arbol_del_subyacente.d else 0.833,
                                     step=0.01)
            
            Boton_arbol = st.button("Actualizar valores de u y d", type="secondary")
            
            if Boton_arbol:
                st.session_state["arboles"][arbol].u = u_nuevo
                st.session_state["arboles"][arbol].d = d_nuevo
                
                if st.session_state["arboles"][arbol].u and st.session_state["arboles"][arbol].d:
                    st.session_state["arboles"][arbol].construir_arbol_multiplicativo()
                
                arbol_del_subyacente = st.session_state["arboles"][arbol]
                st.rerun()
        
        # Espaciado
        for _ in range(10):
            st.write("")

        Boton = st.button(" Calcular precio y cobertura del derivado", type="primary")

    with col_42:
        fig = grafica_arbol(arbol_del_subyacente, arbol)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr style='margin:0; padding:0; border: none; border-top: 1px solid #ccc;'>",unsafe_allow_html=True)

# ----------------------------------------- QUINTA PARTE - PRECIO Y COBERTURA DEL DERIVADO --------------------------------------------

    if Boton:
        
        st.markdown("####  Precio y Cobertura del Derivado")
        col_51, col_52 = st.columns([1, 3])
        
        Derivado = st.session_state["Derivado"]
        tipo_arbol = st.session_state["tipo_arbol_seleccionado"]
        arbol_del_subyacente = st.session_state["arboles"][tipo_arbol]
        
        # Calcular probabilidades y cobertura
        tipo_tiempo = "continua" if tasa == "Continua" else "discreto"
        arbol_del_subyacente.probabilidades_neutras_al_riesgo(tipo_tiempo)
        
        Cobertura_del_Derivado = Cobertura(Derivado, arbol_del_subyacente)
        Cobertura_del_Derivado.calcular_cobertura(tipo_tiempo)
        
        
        with col_51:
            tab_1, tab_2, tab_3 = st.tabs([" Valores", " Alphas (Δ)", " Betas (B)"])
            
            # Preparar datos para tablas
            tabla_valores = []
            tabla_alphas = []
            tabla_betas = []
            
            # Valores
            numero = 0
            for tiempo in Cobertura_del_Derivado.valores:
                for nodo in tiempo:
                    tabla_valores.append({"Nodo": f"V{numero}", "Valor": round(nodo, 6)})
                    numero += 1
            
            # Alphas
            numero = 0
            for tiempo in Cobertura_del_Derivado.alphas:
                for nodo in tiempo:
                    tabla_alphas.append({"Nodo": f"α{numero}", "Valor": round(nodo, 6)})
                    numero += 1
            
            # Betas
            numero = 0
            for tiempo in Cobertura_del_Derivado.betas:
                for nodo in tiempo:
                    tabla_betas.append({"Nodo": f"β{numero}", "Valor": round(nodo, 6)})
                    numero += 1
            
            # Mostrar DataFrames
            with tab_1:
                st.markdown("##### Valores del derivado en cada nodo")
                df_valores = pd.DataFrame(tabla_valores)
                st.dataframe(df_valores, hide_index=True, use_container_width=True)
                
                st.markdown(f"**Precio del derivado en t = 0:** `{round(tabla_valores[0]['Valor'], 6)}`")
            
            with tab_2:
                st.markdown("##### Posición en el subyacente (Δ)")
                df_alphas = pd.DataFrame(tabla_alphas)
                st.dataframe(df_alphas, hide_index=True, use_container_width=True)
            
            with tab_3:
                st.markdown("##### Posición en el bono (B)")
                df_betas = pd.DataFrame(tabla_betas)
                st.dataframe(df_betas, hide_index=True, use_container_width=True)
                
        
        with col_52:
            fig_cobertura = grafica_cobertura(arbol_del_subyacente, Cobertura_del_Derivado)
            st.plotly_chart(fig_cobertura, use_container_width=True)
            
            # Información adicional para opciones americanas
            if seleccion in ["Call americano", "Put americano"]:
                nodos_optimos = sum([sum(tiempo) for tiempo in Cobertura_del_Derivado.optimos])
                st.info(f"🎯 **Nodos con ejercicio óptimo temprano:** {nodos_optimos}")