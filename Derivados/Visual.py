import pandas as pd
import streamlit as st
from Graficos import grafica_arbol
from Funciones_y_Clases import (Call, Put, Call_Digital, Put_Digital, 
                                Arbol_Binomial, Cobertura)
from Funcionamiento_Streamlit import (iniciar_sesion, crear_derivado, 
                                        crear_modificar_subyacente,
                                        crear_modificar_arbol, 
                                        reconstruir_arbol_por_dividendos)

# -------------------------------------------------------- CONFIGURACIÓN DE LA PÁGINA --------------------------------------------------------------

iniciar_sesion()
st.set_page_config(layout="wide", page_title="Calculadora de Derivados")
# Iniciamos las variables y clases en session_state

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

col_01, col_02 = st.columns([2, 1])

with col_01:
    # Selección de derivado
    seleccion = st.pills(
                label = "Derivados disponibles",
                options = opciones.keys(),
                selection_mode = "single"
            )

if seleccion:

    # Detectar cambio de derivado y resetear estado dependiente
    if st.session_state["tipo_derivado_seleccionado"] != seleccion:
        st.session_state["tipo_derivado_seleccionado"] = seleccion
        st.session_state["subtipo_derivado"] = None
        st.session_state["Derivado"] = crear_derivado(opciones, seleccion)
    Derivado = st.session_state["Derivado"]

    if seleccion in ["Call digital", "Put digital"]:
        with col_02:
            st.session_state["subtipo_derivado"] = st.radio(
                                                            "Tipo de digital",
                                                            ["Cash-or-Nothing", "Asset-or-Nothing"],
                                                            horizontal=True
                                                            )

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
        N = st.number_input("Periodos N", min_value=1, max_value=5,value=1, step=1)
        Derivado.N = N
        if st.session_state["tipo_arbol_seleccionado"]:
            crear_modificar_arbol(st.session_state["tipo_arbol_seleccionado"], Derivado)

    # Determinamos el monto del derivado digital "cash or nothing"
    if seleccion in ["Call digital","Put digital"] and st.session_state["subtipo_derivado"] == "Cash-or-Nothing":
        with col_15:
            M = st.number_input("Cantidad M", min_value=1.0, value=1.0, step = 0.1)
    else:
        M = None


    # ----------------------------------------------------- SEGUNDA PARTE - MERCADO -------------------------------------------------------
   
   
    st.markdown("#### Mercado:")
    col_21, col_22, col_23, col_24, col_25 = st.columns(5)

    # Determinamos el tipo de la tasa libre de riesgo
    with col_21:
        tasa = st.radio("Tipo de tasa",["Discreta","Continua"])

    # Determinamos la tasa libre de riesgo
    with col_22:
        r = st.number_input("Tasa libre de riesgo r", min_value = 0.0, max_value = 1.0,step=0.0001,format = f"%.4f")
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
        reconstruir_arbol_por_dividendos()

        # Si cambió el tipo de dividendo, recrear el árbol
        if st.session_state["tipo_arbol_seleccionado"]:
            crear_modificar_arbol(st.session_state["tipo_arbol_seleccionado"], Derivado)
    

        if dividendo == "Con dividendos discretos":

            with col_34:
                monto = st.number_input("Monto dividendo", min_value=0.0, step=1.0)
                Subyacente_del_Derivado.monto_dividendo = monto
                reconstruir_arbol_por_dividendos()
                            
            with col_35:
                periodicidad = st.radio("Periodicidad", 
                                       ["Anual", "Semestral", "Mensual", "Por periodo"])
                Subyacente_del_Derivado.periodicidad = periodicidad
                reconstruir_arbol_por_dividendos()

        elif dividendo == "Con dividendos continuos":
            with col_34:
                tasa_div = st.number_input("Tasa dividendo",min_value=0.0,max_value=1.0,step=0.0001,format="%.4f")
                Subyacente_del_Derivado.tasa_dividendo = tasa_div
                reconstruir_arbol_por_dividendos()


    st.markdown("<hr style='margin:0; padding:0; border: none; border-top: 1px solid #ccc;'>",unsafe_allow_html=True)

# ------------------------------------------------ CUARTA PARTE - ARBOL DEL SUBYACENTE ------------------------------------------------

    col_41, col_42 = st.columns([1, 3])
    
    with col_41:
        st.markdown(f"####  Árbol de precios ({arbol})")
        
        if arbol in ["General", "Recombinante"]:
            arbol_del_subyacente.nombre_posicion_nodos()
            lista_nombres = list(arbol_del_subyacente.nombres_posicion.keys())
            seleccion_nodo = st.selectbox("Selecciona un nodo", lista_nombres)
            t, j = arbol_del_subyacente.nombres_posicion[seleccion_nodo]
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
        tipo_tiempo = "Continua" if tasa == "Continua" else "Discreto"
        arbol_del_subyacente.probabilidades_neutras_al_riesgo(tipo_tiempo)
        Cobertura_del_Derivado = Cobertura(Derivado, arbol_del_subyacente)

        if type(Derivado).__name__ in ("Call_Digital", "Put_Digital"):
            Cobertura_del_Derivado.calcular_cobertura(tipo_tiempo, st.session_state["subtipo_derivado"], M)
        else:
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
            fig_cobertura = grafica_arbol(arbol_del_subyacente,arbol, Cobertura_del_Derivado)
            st.plotly_chart(fig_cobertura, use_container_width=True)
            
            # Información adicional para opciones americanas
            if seleccion in ["Call americano", "Put americano"]:
                nodos_optimos = sum([sum(tiempo) for tiempo in Cobertura_del_Derivado.optimos])
                st.info(f"🎯 **Nodos con ejercicio óptimo temprano:** {nodos_optimos}")