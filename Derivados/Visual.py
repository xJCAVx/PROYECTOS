import streamlit as st
import plotly.graph_objects as go
from pyvis.network import Network
import networkx as nx

st.set_page_config(layout="wide")

# --- Título principal centrado ---
st.markdown("""
    <h1 style="
        text-align:center; 
        font-size:60px; 
        margin-top:0px; 
        padding-top:0px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #1F2937;
    ">
    CALCULADORA DE DERIVADOS
    </h1>
""", unsafe_allow_html=True)

# --- Subtítulo con línea delgada y negra ---
st.markdown("""
<div style="
    display: flex; 
    align-items: center; 
    margin-top: 20px; 
    margin-bottom: 10px;
">
    <h3 style="
        margin: 0; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #111827;
    ">Opción Europea</h3>
    <div style="
        flex-grow: 1; 
        height: 1px; 
        background-color: black; 
        margin-left: 15px;
    "></div>
</div>
""", unsafe_allow_html=True)

# --- Widgets en columnas ---
col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 2])

with col1:
    st.write("")

with col2:
    S0 = st.number_input("Precio inicial S₀", min_value=0.0, step=1.0, format="%.2f")

with col3:
    K = st.number_input("Strike K", min_value=0.0, step=1.0, format="%.2f")

with col4:
    r = st.number_input("Tasa de interés r (%)", min_value=0.0, step=0.1, format="%.2f")

with col5:
    T = st.number_input("Tiempo T (años)", min_value=0.0, step=0.1, format="%.2f")


modo = st.radio(
    "Selecciona el modelo:",
    ["Discreto (Árbol Binomial)", "Continuo (Black–Scholes)"],
    horizontal=True
)

st.markdown("---")

# --- Si elige modo discreto: muestra el árbol ---
if modo == "Discreto (Árbol Binomial)":
    # --- Columnas principales ---
    col_controls, col_graph = st.columns([1, 3])

    with col_controls:
        st.header("Árbol Binomial")

        tree_type = st.selectbox(
            "Selecciona el tipo de árbol",
            ["General", "Recombinante", "Multiplicativo"]
        )
        steps = st.slider("Número de pasos / tiempos", 1, 5, 3)

        # --- Construcción de nodos ---
        if "nodes" not in st.session_state or st.session_state.get("tree_type") != tree_type or st.session_state.get("steps") != steps:
            st.session_state["tree_type"] = tree_type
            st.session_state["steps"] = steps

            nodes = []
            node_id_map = {}
            counter = 1

            if tree_type == "General":
                # Árbol NO recombinante (2^t nodos por paso)
                for i in range(steps + 1):
                    row = []
                    for j in range(2**i):
                        price = 100 - 5 * (i - j) + 5 * j / 2
                        node_id = f"{i}-{j}"
                        node = {
                            "id": node_id,
                            "x": i,
                            "y": float(price),
                            "label": str(round(price, 2)),
                            "name": f"S{counter}"
                        }
                        counter += 1
                        row.append(node)
                        node_id_map[node_id] = node
                    nodes.append(row)

            elif tree_type == "Recombinante":
                # Árbol clásico (t+1 nodos por paso)
                for i in range(steps + 1):
                    row = []
                    for j in range(i + 1):
                        price = 100 - 5 * (i - j) + 5 * j
                        node_id = f"{i}-{j}"
                        node = {
                            "id": node_id,
                            "x": i,
                            "y": float(price),
                            "label": str(round(price, 2)),
                            "name": f"S{counter}"
                        }
                        counter += 1
                        row.append(node)
                        node_id_map[node_id] = node
                    nodes.append(row)

            else:
                # Multiplicativo
                for i in range(steps + 1):
                    row = []
                    for j in range(i + 1):
                        price = 100 * (1.05 ** j) * (0.95 ** (i - j))
                        node_id = f"{i}-{j}"
                        node = {
                            "id": node_id,
                            "x": i,
                            "y": float(price),
                            "label": str(round(price, 2)),
                            "name": f"S{counter}"
                        }
                        counter += 1
                        row.append(node)
                        node_id_map[node_id] = node
                    nodes.append(row)

            st.session_state["nodes"] = nodes
            st.session_state["node_id_map"] = node_id_map

        else:
            nodes = st.session_state["nodes"]
            node_id_map = st.session_state["node_id_map"]

        # --- Edición de nodo ---
        selected_node_id = st.selectbox(
            "Selecciona un nodo",
            [node["id"] for row in nodes for node in row]
        )

        new_price = st.number_input(
            "Nuevo precio del nodo",
            value=float(node_id_map[selected_node_id]["y"]),
            step=1.0
        )

        node_id_map[selected_node_id]["y"] = float(new_price)
        node_id_map[selected_node_id]["label"] = str(round(float(new_price), 2))

    # --- Conexiones ---
    edges = []
    if tree_type == "General":
        # Cada nodo genera dos nuevos, sin recombinar
        for i in range(steps):
            for j in range(len(nodes[i])):
                parent = nodes[i][j]
                left = nodes[i + 1][2 * j]
                right = nodes[i + 1][2 * j + 1]
                edges.append((parent, left))
                edges.append((parent, right))
    else:
        # Recombinante o multiplicativo
        for i in range(steps):
            for j in range(i + 1):
                parent = nodes[i][j]
                edges.append((parent, nodes[i + 1][j]))
                edges.append((parent, nodes[i + 1][j + 1]))

    # --- Gráfico ---
    fig = go.Figure()

    # Conexiones
    for parent, child in edges:
        fig.add_trace(go.Scatter(
            x=[parent["x"], child["x"]],
            y=[parent["y"], child["y"]],
            mode="lines",
            line=dict(color="black"),
            hoverinfo="skip",
            showlegend=False
        ))

    # Nodos
    for row in nodes:
        for node in row:
            # Precio arriba del nodo (desplazado ligeramente)
            fig.add_trace(go.Scatter(
                x=[node["x"]],
                y=[node["y"] + 2],
                text=[node["label"]],
                mode="text",
                textposition="top center",
                hoverinfo="text",
                showlegend=False
            ))

            # Nodo azul
            fig.add_trace(go.Scatter(
                x=[node["x"]],
                y=[node["y"]],
                mode="markers",
                marker=dict(size=20, color="blue"),
                hoverinfo="skip",
                showlegend=False
            ))

            # Nombre abajo del nodo
            fig.add_trace(go.Scatter(
                x=[node["x"]],
                y=[node["y"] - 2],
                text=[node["name"]],
                mode="text",
                textposition="bottom center",
                hoverinfo="skip",
                showlegend=False
            ))

    # Layout
    fig.update_layout(
        dragmode="pan",
        xaxis=dict(title="Tiempo / Step", showgrid=False, zeroline=False),
        yaxis=dict(title="Precio del Subyacente", showgrid=False, zeroline=False),
        height=650
    )

    with col_graph:
        st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown("### ⚫ Modelo de Black–Scholes")