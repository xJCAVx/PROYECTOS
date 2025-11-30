import streamlit as st
from Funciones_y_clases import Subyacente, Call, Put, Call_Digital, Put_Digital, Arbol_Binomial, Cobertura, grafica_arbol


# ------------------------------------------------------ TITULO Y CONFIGURACIÓN ------------------------------------------------------------

# Para ocupar toda la pantalla
st.set_page_config(layout="wide")

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
st.caption("By Josué Carlos Abad Villegas (JCAV)")
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

# Creamos la clase del derivado seleccionado
if seleccion:
    derivado_seleccionado = opciones[seleccion]
    Derivado = derivado_seleccionado(subyacente = None, 
                                    strike = None, 
                                    vencimiento = None, 
                                    periodos = None,
                                    interes = None, 
                                    tipo = "americana" if seleccion in ["Call americano", "Put americano"] else "europea",
                                    posicion = None
                                    )

# Linea de division
st.markdown("<hr style='margin:0; padding:0; border: none; border-top: 1px solid #ccc;'>",unsafe_allow_html=True)

# --------------------------------------------------- INPUTS  -------------------------------------------------------------------------

# Una vez que se haya elegido el derivado
if seleccion:

    # Primera parte - Caracteristicas -------------------------------------------------------------------------------------------------
    
    st.markdown("#### Caraterísticas:")
    col_11, col_12, col_13, col_14, col_15 = st.columns(5)

    # Determinamos posicion del derivado
    with col_11:
        posicion = st.radio("Posicion",["Long", "Short"])
        Derivado.posicion = posicion

    # Determinamos strike del derivado
    with col_12:
        K = st.number_input("Strike K", min_value=1.0, step=1.0)
        Derivado.K = K

    # Determinamos vencimiento T
    with col_13:
        T = st.number_input("Vencimiento T", min_value=1, value=1, step=1)
        Derivado.T = T

    # Determinamos la cantidad de periodos
    with col_14:
        N = st.number_input("Periodos N", min_value=1, value=1, step=1)
        Derivado.N = N

    # Segunda parte - Mercado ---------------------------------------------------------------------------------------------------------
    
    st.markdown("#### Mercado:")
    col_21, col_22, col_23, col_24, col_25 = st.columns(5)

    # Determinamos el tipo de la tasa libre de riesgo
    with col_21:
        tasa = st.radio("Tipo de tasa",["Discreta","Continua"])

    # Determinamos la tasa libre de riesgo
    with col_22:
        r = st.number_input("Tasa libre de riesgo r", min_value = 0.0, max_value = 1.0,step=0.1)
        Derivado.r = r

    # Tercera parte - Subyacente ------------------------------------------------------------------------------------------------------

    st.markdown("#### Subyacente:")
    col_31, col_32, col_33, col_34, col_35 = st.columns(5)

    # Determinamos el precio inicial del subyacente
    with col_31:
        S0 = st.number_input("Precio Inicial So",min_value=1)
        Subyacente_del_Derivado = Subyacente(S0)
                                             
    # Creamos la clase del arbol de precios del derivado
    with col_32:
        if "arboles" not in st.session_state:
            st.session_state.arboles = {}

        arbol = st.radio("Tipo de arbol",["General","Recombinante","Multiplicativo"])

        if arbol not in st.session_state.arboles:
            arbol_del_subyacente = Arbol_Binomial(Subyacente_del_Derivado,
                                                T = Derivado.T,
                                                N = Derivado.N,
                                                r = Derivado.r,
                                                tipo = arbol)
            # Construir el árbol solo una vez
            arbol_del_subyacente.arbol_temporal()

            st.session_state.arboles[arbol] = arbol_del_subyacente

        arbol_del_subyacente = st.session_state.arboles[arbol]

    # Determinamos el tipo de subyacente
    with col_33:
        dividendo = st.radio("Tipo de Subyacente",["Sin dividendos", "Con dividendos discretos", "Con dividendos continuos"])
        Subyacente_del_Derivado.tipo_subyacente = dividendo

        if dividendo == "Con dividendos discretos":

            # Determinamos el monto de dividendo
            with col_34:
                monto = st.number_input("Dividendo",min_value=0.0,step=1.0)
                Subyacente_del_Derivado.monto_dividendo = monto
                
            # Determinamos la periodicidad del dividendo
            with col_35:
                periodicidad =st.radio("Periodicidad",["Anual", "Semestral", "Mensual","Por periodo"], horizontal=False)
                Subyacente_del_Derivado.periodicidad = periodicidad

        elif dividendo == "Con dividendos continuos":

            # Determinamos la tasa del dividendo
            with col_34:
                tasa = st.number_input("Dividendo",min_value=0.0, step=1.0)
                Subyacente_del_Derivado.tasa_dividendo = tasa

            # Determinamos la periodicidad del dividendo
            with col_35:
                periodicidad =st.radio("Periodicidad",["Anual", "Semestral", "Mensual","Por periodo"], horizontal=False)
                Subyacente_del_Derivado.periodicidad = periodicidad

    st.markdown("<hr style='margin:0; padding:0; border: none; border-top: 1px solid #ccc;'>",unsafe_allow_html=True)

    # Cuarta parte - Arbol del subyacente ---------------------------------------------------------------------------------------------

    col_41, col_42 = st.columns([1, 3])

    with col_41:
        st.markdown(f"#### Arbol de precios ({arbol})")

        if arbol == "General":
            lista_nombres = arbol_del_subyacente.nombres_nodos()[1:]
            seleccion_nodo = st.selectbox("Selecciona un nodo", lista_nombres)

            t, j = arbol_del_subyacente.obtener_posicion(seleccion_nodo)

            nuevo_precio = st.number_input("Nuevo precio del nodo",min_value=1.0,step=1.0)

            # 5. Actualizar
            Boton_precio = st.button("Actualizar precio")
            if Boton_precio:
                arbol_del_subyacente.cambiar_nodo(t, j, nuevo_precio)

        elif arbol == "Recombinante":
            pass

        else:   # Multiplicativo         

            u_nuevo = st.number_input("Valor de u", min_value = 0.0)
            d_nuevo = st.number_input("Valor de d", min_value = 0.0)

            Boton_arbol =  st.button("Actualizar valores de u y d",type = "secondary")
            if Boton_arbol:
               arbol_del_subyacente.u = u_nuevo 
               arbol_del_subyacente.d = d_nuevo
               arbol_del_subyacente.construir_arbol_multiplicativo()

        for i in range(12):
            st.write("")
        Boton =  st.button("Calcular precio y cobertura del derivado",type = "primary")

    with col_42:
        fig = grafica_arbol(arbol_del_subyacente, arbol)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr style='margin:0; padding:0; border: none; border-top: 1px solid #ccc;'>",unsafe_allow_html=True)


# Quinta Parte - Precio y cobertura ---------------------------------------------------------------------------------------------------
    if Boton:
        st.write("Se ejecutó")
        tab1, tab2, tab3 = st.tabs(["Cat", "Dog", "Owl"])
        with tab1:
            st.header("A cat")
            st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
        with tab2:
            st.header("A dog")
            st.image("https://static.streamlit.io/examples/dog.jpg", width=200)
        with tab3:
            st.header("An owl")
            st.image("https://static.streamlit.io/examples/owl.jpg", width=200)



        