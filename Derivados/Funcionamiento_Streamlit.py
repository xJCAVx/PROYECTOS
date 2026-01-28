# PROYECTO DERIVADOS V2

import streamlit as st
from Funciones_y_Clases import (Subyacente, Derivado, Call, Put, Call_Digital, Put_Digital, 
                                Arbol_Binomial, Cobertura)

def iniciar_sesion():
    """Iniciliza las variables de la sesion"""

    if "Subyacente" not in st.session_state:
        st.session_state["Subyacente"] = None                     # Objeto Suyacente

    if "Derivado" not in st.session_state:
        st.session_state["Derivado"] = None                       # Objeto Derivado 

    if "arboles" not in st.session_state:
        st.session_state["arboles"] = {}                          # Diccionario para los arboles 

    if "tipo_derivado_seleccionado" not in st.session_state:
        st.session_state["tipo_derivado_seleccionado"] = None     # Cadena de la seleccion actual de derivado

    if "subtipo_derivado" not in st.session_state:
        st.session_state["subtipo_derivado"] = None               # Subtipo de derivado para opciones digitales

    if "tipo_arbol_seleccionado" not in st.session_state:
        st.session_state["tipo_arbol_seleccionado"] = None        # Cadena de la seleccion actual de arbol


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


def construir_arbol(arbol):
    """Construye el árbol según su tipo"""

    if arbol.tipo == "Multiplicativo":
        if arbol.u is not None and arbol.d is not None:
            arbol.construir_arbol_multiplicativo()
        else:
            arbol.arbol_temporal()
    else:
        arbol.arbol_temporal()

    arbol.Q = []
    arbol.S0_actual = arbol.Subyacente.S0


def crear_modificar_arbol(tipo_arbol, derivado):
    """Crea o actualiza un árbol binomial sin dividendos"""

    arboles = st.session_state["arboles"]
    subyacente = st.session_state["Subyacente"]

    # Parámetros del derivado (con valores por defecto)
    T = derivado.T if getattr(derivado, "T", None) is not None else 1
    N = derivado.N if getattr(derivado, "N", None) is not None else 1
    r = derivado.r if getattr(derivado, "r", None) is not None else 0.0

    # Si el árbol NO existe, crearlo
    if tipo_arbol not in arboles:

        arbol = Arbol_Binomial(
            Subyacente=subyacente,
            T=T,
            N=N,
            r=r,
            tipo=tipo_arbol
        )

        construir_arbol(arbol)
        arbol.editado = False
        arboles[tipo_arbol] = arbol
        return arbol

    # Si el árbol YA existe, actualizarlo
    arbol = arboles[tipo_arbol]

    S0_viejo = getattr(arbol, "S0_actual", None)

    # Detecta cambio estructural con el valor anterior
    cambio_estructural = (
        arbol.N != N or
        arbol.T != T or
        arbol.tipo != tipo_arbol or
        S0_viejo != subyacente.S0
    )

    arbol.Subyacente = subyacente
    arbol.T = T
    arbol.N = N
    arbol.r = r
    arbol.delta = T / N if N != 0 else 0

    if cambio_estructural:
        construir_arbol(arbol)
        arbol.Q = None
        arbol.editado = False

    return arbol

def reconstruir_arbol_por_dividendos():
    if st.session_state["tipo_arbol_seleccionado"]:
        arbol = st.session_state["arboles"][st.session_state["tipo_arbol_seleccionado"]]
        arbol.editado = False
        construir_arbol(arbol)