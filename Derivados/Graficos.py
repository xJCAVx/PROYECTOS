# PROYECTO DERIVADOS V2

import plotly.graph_objects as go

def grafica_arbol(arbol, tipo_arbol, cobertura = None):

    """
    Grafica el árbol de precios del subyacente. 
    O si se le pasa `cobertura` (objeto Cobertura),
    grafica el arbol de la cobertura del derivado
    """

    niveles = arbol.niveles
    filas_nodos = []           # lista de listas de nodos por nivel
    contador_nombres = 0

    # Construir nodos (solo estructura, sin trazas todavia)
    for t, nivel_precios in enumerate(niveles):
        fila = []
        for j, precio in enumerate(nivel_precios):
            nodo = {
                    "t" : t,
                    "j" : j,
                    "x" : float(t),
                    "y" : float(precio),
                    "precio_mostrar" : f"{precio:.2f}",
                    "nombre" : f"S{contador_nombres}",
                    "id" : f"{t}-{j}"
                    }
            
            # Si hay objeto cobertura, se agrega dicha información
            if cobertura is not None:
                nodo["valor"] = cobertura.valores[t][j] if t < len(cobertura.valores) and j < len(cobertura.valores[t]) else None
                nodo["alpha"] = cobertura.alphas[t][j] if t < len(cobertura.alphas) and j < len(cobertura.alphas[t]) else None
                nodo["beta"]  = cobertura.betas[t][j]  if t < len(cobertura.betas)  and j < len(cobertura.betas[t])  else None
                nodo["optimo"] = cobertura.optimos[t][j] if t < len(cobertura.optimos) and j < len(cobertura.optimos[t]) else 0
                nodo["nombre_valor"] = f"V{contador_nombres}"
            
            fila.append(nodo)
            contador_nombres += 1
        filas_nodos.append(fila)

    # Construir listas de segmentos de linea 
    x_segmentos = []
    y_segmentos = []
    for t in range(len(filas_nodos) - 1):
        nivel_actual = filas_nodos[t]
        nivel_siguiente = filas_nodos[t + 1]
        for j, padre in enumerate(nivel_actual):
            if tipo_arbol == "General":
                hijo1, hijo2 = 2 * j, 2 * j + 1
                if hijo1 < len(nivel_siguiente):
                    x_segmentos.extend([padre["x"], nivel_siguiente[hijo1]["x"], None])
                    y_segmentos.extend([padre["y"], nivel_siguiente[hijo1]["y"], None])
                if hijo2 < len(nivel_siguiente):
                    x_segmentos.extend([padre["x"], nivel_siguiente[hijo2]["x"], None])
                    y_segmentos.extend([padre["y"], nivel_siguiente[hijo2]["y"], None])
            else:  # Recombinante o Multiplicativo
                if j < len(nivel_siguiente):
                    x_segmentos.extend([padre["x"], nivel_siguiente[j]["x"], None])
                    y_segmentos.extend([padre["y"], nivel_siguiente[j]["y"], None])
                if j + 1 < len(nivel_siguiente):
                    x_segmentos.extend([padre["x"], nivel_siguiente[j+1]["x"], None])
                    y_segmentos.extend([padre["y"], nivel_siguiente[j+1]["y"], None])

    # Crear figura y agregar la traza de líneas (todas las aristas en una sola traza)
    fig = go.Figure()
    if x_segmentos:
        fig.add_trace(go.Scatter(
            x=x_segmentos,
            y=y_segmentos,
            mode="lines",
            line=dict(color="gray", width=1),
            hoverinfo="skip",
            showlegend=False
        ))

    # Preparar listas planas para nodos (para dibujar en una sola traza por tipo de texto)
    xs = []
    ys = []
    textos_precios = []
    textos_nombres = []
    hover_texts = []
    colores = []

    for fila in filas_nodos:
        for nodo in fila:
            xs.append(nodo["x"])
            ys.append(nodo["y"])
            if cobertura is None:
                textos_precios.append(nodo["precio_mostrar"])
            else:
                textos_precios.append(
                    f"{nodo['valor']:.3f}" if nodo.get("valor") is not None else "N/A"
                )

            textos_nombres.append(nodo["nombre_valor"] if cobertura is not None else nodo["nombre"])

            # Hover: información detallada si hay cobertura, si no, solo nombre y precio
            if cobertura is not None:
                valor = (f"{nodo['valor']:.2f}" if nodo.get("valor") is not None else "N/A")
                alpha = (f"{nodo['alpha']:.2f}" if nodo.get("alpha") is not None else "N/A")
                beta  = (f"{nodo['beta']:.2f}"  if nodo.get("beta")  is not None else "N/A")
                opt   = "Sí" if nodo.get("optimo", 0) == 1 else "No"
                hover_texts.append(
                    f"<b>{nodo.get('nombre_valor', nodo['nombre'])}</b><br>"
                    f"Subyacente: {nodo['precio_mostrar']}<br>"
                    f"Valor derivado: {valor}<br>"
                    f"Alpha (Δ): {alpha}<br>"
                    f"Beta (B): {beta}<br>"
                    f"Ejercicio óptimo: {opt}"
                )
                colores.append("#006400" if nodo.get("optimo", 0) == 1 else "#32CD32")
            else:
                hover_texts.append(f"<b>{nodo['nombre']}</b><br>Precio: {nodo['precio_mostrar']}")
                colores.append("#1f77b4")

    # Trazas de nodos: precios arriba y nombre abajo usando dos trazas
    fig.add_trace(go.Scatter(
        x=xs,
        y=ys,
        mode="markers+text",
        text=textos_precios,
        textposition="top center",
        hovertext=hover_texts,
        hoverinfo="text",
        marker=dict(size=16, color=colores, line=dict(width=1.2, color="black")),
        showlegend=False
    ))

    rango_y = max(ys) - min(ys)
    offset = 0.04 * rango_y

    fig.add_trace(go.Scatter(
        x=xs,
        y=[y - offset for y in ys],
        mode="text",
        text=textos_nombres,
        hoverinfo="skip",
        showlegend=False
    ))

    fig.update_layout(
        dragmode="pan",
        xaxis=dict(showgrid=False, zeroline=False, title="Tiempo"),
        yaxis=dict(showgrid=False, zeroline=False, title="Precio"),
        height=650,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    return fig