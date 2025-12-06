# PROYECTO DERIVADOS

import math
from scipy.stats import norm
import plotly.graph_objects as go


# ------------------------------------------- FUNCIONES -----------------------------------------------

def B(r, delta, tiempo):
    """Factor de descuento para traer a valor presente"""
    if tiempo == "discreto":
        return (1 + r) ** (-delta)
    else:
        return math.exp(-r * delta)


def grafica_arbol(arbol, tipo):
    """Genera gráfica interactiva del árbol de precios del subyacente"""
    niveles = arbol.niveles
    nodes = []
    contador_nombres = 0

    # Crear nodos
    for t, nivel in enumerate(niveles):
        row = []
        for precio in nivel:
            node = {
                "x": t,
                "y": float(precio),
                "label": str(round(precio, 3)),
                "name": f"S{contador_nombres}"
            }
            contador_nombres += 1
            row.append(node)
        nodes.append(row)

    # Crear conexiones
    edges = []
    for t in range(len(nodes) - 1):
        nivel_actual = nodes[t]
        nivel_siguiente = nodes[t + 1]
        
        for j, parent in enumerate(nivel_actual):
            if tipo == "General":
                hijo1, hijo2 = 2 * j, 2 * j + 1
                if hijo1 < len(nivel_siguiente):
                    edges.append((parent, nivel_siguiente[hijo1]))
                if hijo2 < len(nivel_siguiente):
                    edges.append((parent, nivel_siguiente[hijo2]))
            else:  # Recombinante o Multiplicativo
                if j < len(nivel_siguiente):
                    edges.append((parent, nivel_siguiente[j]))
                if j + 1 < len(nivel_siguiente):
                    edges.append((parent, nivel_siguiente[j + 1]))

    # Crear figura
    fig = go.Figure()

    # Dibujar líneas
    for parent, child in edges:
        fig.add_trace(go.Scatter(
            x=[parent["x"], child["x"]],
            y=[parent["y"], child["y"]],
            mode="lines",
            line=dict(color="gray", width=1),
            hoverinfo="skip",
            showlegend=False
        ))

    # Dibujar nodos con precios y nombres
    for row in nodes:

        x = [n["x"] for n in row]
        y = [n["y"] for n in row]

        precios = [n["label"] for n in row]
        nombres = [n["name"] for n in row]

        # Precio arriba
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode="markers+text",
            text=precios,
            textposition="top center",
            hoverinfo="skip",
            marker=dict(
                size=20,
                color="#1f77b4",
                line=dict(width=1.5, color="black")
            ),
            showlegend=False
        ))

        # Nombre debajo
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode="markers+text",
            text=nombres,
            textposition="bottom center",
            showlegend=False,
            hoverinfo="skip",
            marker=dict(
                size=20,
                color="#1f77b4",
                line=dict(width=1.5, color="black")
            ),
        ))

    fig.update_layout(
        dragmode="pan",
        xaxis=dict(showgrid=False, zeroline=False, title="Tiempo"),
        yaxis=dict(showgrid=False, zeroline=False, title="Precio Subyacente"),
        height=650,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    return fig


def grafica_cobertura(arbol, cobertura):
    """Genera gráfica interactiva del árbol de valores del derivado y cobertura"""
    niveles = arbol.niveles
    valores = cobertura.valores
    alphas = cobertura.alphas
    betas  = cobertura.betas
    optimos = cobertura.optimos   

    nodes = []
    contador = 0

    # Crear nodos con información de cobertura
    for t, nivel in enumerate(niveles):
        row = []
        for j, precio_sub in enumerate(nivel):
            valor = valores[t][j] if t < len(valores) and j < len(valores[t]) else None
            alpha = alphas[t][j] if t < len(alphas) and j < len(alphas[t]) else None
            beta = betas[t][j] if t < len(betas) and j < len(betas[t]) else None
            optimo = optimos[t][j] if t < len(optimos) and j < len(optimos[t]) else 0

            node = {
                "id": f"{t}-{j}",
                "x": t,
                "y": float(precio_sub),
                "precio_sub": precio_sub,
                "valor": valor,
                "alpha": alpha,
                "beta": beta,
                "optimo": optimo,
                "name": f"V{contador}"
            }
            contador += 1
            row.append(node)
        nodes.append(row)

    # Crear conexiones
    edges = []
    for t in range(len(nodes) - 1):
        nivel_actual = nodes[t]
        nivel_sig = nodes[t + 1]
        
        for j, parent in enumerate(nivel_actual):
            if j < len(nivel_sig):
                edges.append((parent, nivel_sig[j]))
            if j + 1 < len(nivel_sig):
                edges.append((parent, nivel_sig[j + 1]))

    # Crear figura
    fig = go.Figure()

    # Dibujar líneas
    for parent, child in edges:
        fig.add_trace(go.Scatter(
            x=[parent["x"], child["x"]],
            y=[parent["y"], child["y"]],
            mode="lines",
            line=dict(color="gray", width=1),
            hoverinfo="skip",
            showlegend=False
        ))

    # Dibujar nodos
    for row in nodes:
        x = [n["x"] for n in row]
        y = [n["y"] for n in row]
        labels = [n["name"] for n in row]

        # Hover con información detallada
        hovers = [
            f"<b>{n['name']}</b><br>"
            f"Subyacente: {round(n['precio_sub'], 4)}<br>"
            f"Valor derivado: {round(n['valor'], 4) if n['valor'] is not None else 'N/A'}<br>"
            f"Alpha (Δ): {round(n['alpha'], 4) if n['alpha'] is not None else 'N/A'}<br>"
            f"Beta (B): {round(n['beta'], 4) if n['beta'] is not None else 'N/A'}<br>"
            f"Ejercicio óptimo: {'Sí' if n['optimo'] == 1 else 'No'}"
            for n in row
        ]
        
        # Color: Verde si es óptimo ejercer, naranja si no

        colores = ["#2a670a" if n["optimo"] == 1 else "#32CD32" for n in row]      

        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode="markers+text",
            text=labels,
            textposition="top center",
            hovertext=hovers,
            hoverinfo="text",
            marker=dict(
                size=20,
                color=colores,
                line=dict(width=1.5, color="black")
            ),
            showlegend=False
        ))

    fig.update_layout(
        dragmode="pan",
        xaxis=dict(showgrid=False, zeroline=False, title="Tiempo"),
        yaxis=dict(showgrid=False, zeroline=False, title="Valor del derivado"),
        height=650,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    return fig


# -------------------------------------------- CLASES -------------------------------------------------


class Subyacente:
    """Clase que representa el activo subyacente"""

    def __init__(self,S0, tipo_subyacente = None, monto_dividendo = None, tasa_dividendo = None, periodicidad = None):
        self.S0 = S0                                                    # Precio inicial del subyacente
        self.tipo_subyacente = tipo_subyacente                          # Sin dividendos / Con dividendos discretos / Con dividendos continuos
        self.monto_dividendo = monto_dividendo                          # Monto dividendos discretos
        self.tasa_dividendo = tasa_dividendo                            # Tasa dividendos continuos
        self.periodicidad = periodicidad                                # Cada cuanto se pagan los dividendos 


class Derivado:
    """Clase base para todos los derivados"""

    def __init__(self, subyacente, strike, vencimiento, periodos, interes, tipo, posicion):

        self.subyacente = subyacente                                    # Subyacente
        self.K = strike                                                 # Precio strike
        self.T = vencimiento                                            # Tiempo de maduración
        self.N = periodos                                               # Numero de periodos
        self.r = interes                                                # Tasa de interes
        self.tipo = tipo                                                # Europea / Americana
        self.posicion = posicion                                        # Largo / Corto


# ------------------------------------------- FORDWARD ------------------------------------------------

# Este derivado no esta incluido en el trabajo final
class Fordward(Derivado):
    """Subclase del derivado Fordward"""

    def precio_fordward(self,tiempo):
        """Precio teorico del fordward en t = 0"""
        return self.subyacente.S0 * B( self.r, self.T, tiempo) ** -1


    def pay_off(self, t, St, tiempo):
        """Valor del fordward en el tiempo t dado que el subyacente tomo el precio St"""
        delta = self.T - t
        if self.posicion == "largo":
            return St - self.K * B(self.r, delta, tiempo)
        else:
            return self.K * B(self.r, delta, tiempo) - St


# ------------------------------------------- OPCIONES ------------------------------------------------


class Call(Derivado):
    """Opción Call europea o americana"""
    
    def pay_off(self, ST):
        payoff_base = max(ST - self.K, 0)
        return payoff_base if self.posicion == "largo" else -payoff_base


class Put(Derivado):
    """Opción Put europea o americana"""
    
    def pay_off(self, ST):
        payoff_base = max(self.K - ST, 0)
        return payoff_base if self.posicion == "largo" else -payoff_base


class Call_Digital(Derivado):
    """Opción Call Digital (Cash-or-Nothing o Asset-or-Nothing)"""
    
    def pay_off(self, ST, subtipo="cash or nothing", M=None):
        if subtipo == "cash or nothing":
            if ST > self.K:
                return M if self.posicion == "largo" else -M
            return 0
        elif subtipo == "asset or nothing":
            if ST > self.K:
                return ST if self.posicion == "largo" else -ST
            return 0
        return 0


class Put_Digital(Derivado):
    """Opción Put Digital (Cash-or-Nothing o Asset-or-Nothing)"""
    
    def pay_off(self, ST, subtipo="cash or nothing", M=None):
        if subtipo == "cash or nothing":
            if ST < self.K:
                return M if self.posicion == "largo" else -M
            return 0
        elif subtipo == "asset or nothing":
            if ST < self.K:
                return ST if self.posicion == "largo" else -ST
            return 0
        return 0


# ----------------------------------------- ARBOLES BINOMIALES ----------------------------------------

# Árbol binomial para valoración de derivados (sin dividendos)
class Arbol_Binomial:
        
    def __init__(self, Subyacente, T, N, r, tipo, u = None, d = None):
        """Árbol binomial para valoración de derivados (sin dividendos)"""

        self.Subyacente = Subyacente                                    # Subyacente
        self.T = T                                                      # Vencimiento
        self.N = N                                                      # Periodos
        self.delta = T/N if T != 0 and N != 0 else 0                    # Delta
        self.r = r                                                      # Tasa de interes     
        self.tipo = tipo                                                # General / Recombinante / Multiplicativo
        self.u = u                                                      # Tasa de subida (multiplicativo)
        self.d = d                                                      # Tasa de bajada (mulitplicativo)
        self.niveles = [[Subyacente.S0]]                                # Nodos
        self.Q = []                                                     # Probabilidades neutras al riesgo


    def construir_arbol_multiplicativo(self):
        """Construye árbol multiplicativo: S(t,j) = S0 * u^j * d^(t-j)"""
        self.niveles = [[self.Subyacente.S0]]
        
        for i in range(1, self.N + 1):
            nivel = []
            for j in range(i + 1):
                nodo = self.Subyacente.S0 * (self.u ** j) * (self.d ** (i - j))
                nivel.append(nodo)
            self.niveles.append(nivel)


    def arbol_temporal(self):
        """Construye árbol temporal (placeholder para árboles sin parámetros u/d definidos)"""
        if self.tipo == "General":
            self.niveles = [[self.Subyacente.S0]]
            paso = 0.5

            for t in range(1, self.N + 1):
                nivel_prev = self.niveles[-1]
                delta_t = paso / (2 ** (t - 1))
                nivel = []
                for p in nivel_prev:
                    nivel.extend([round(p - delta_t, 6), round(p + delta_t, 6)])
                nivel.sort()
                self.niveles.append(nivel)

        elif self.tipo == "Recombinante" or self.tipo == "Multiplicativo":
            u_temporal = 1.2
            d_temporal = 1 / 1.2
            self.niveles = [[self.Subyacente.S0]]

            for t in range(1, self.N + 1):
                nivel = [round(self.Subyacente.S0 * (u_temporal ** j) * (d_temporal ** (t - j)), 6) 
                         for j in range(t + 1)]
                nivel.sort()
                self.niveles.append(nivel)


    def nombres_nodos(self):
        """Retorna lista de nombres de nodos (S0, S1, S2, ...)"""
        lista_ids = []
        indice = 0
        for t, fila in enumerate(self.niveles):
            for _ in fila:
                lista_ids.append(f"S{indice}")
                indice += 1
        return lista_ids


    def obtener_posicion(self, nombre_nodo):
        """Obtiene posición (t, j) de un nodo dado su nombre"""
        k = int(nombre_nodo[1:])
        contador = 0
        for t, fila in enumerate(self.niveles):
            for j, _ in enumerate(fila):
                if contador == k:
                    return t, j
                contador += 1
        return None, None


    def agregar_nivel(self, nodos):
        """Agrega un nivel completo al árbol"""
        self.niveles.append(nodos)


    def cambiar_nodo(self, tiempo, indice_nodo, nodo_nuevo):
        """Modifica el precio de un nodo específico"""
        if tiempo < len(self.niveles) and indice_nodo < len(self.niveles[tiempo]):
            self.niveles[tiempo][indice_nodo] = nodo_nuevo


    def probabilidades_neutras_al_riesgo(self, tiempo):
        """Calcula probabilidades neutrales al riesgo Q"""
        self.Q = []

        if self.tipo == "Multiplicativo":
            for i in range(self.N):
                Q_t = []
                for _ in range(i + 1):
                    q_j = (B(self.r, self.delta, tiempo) ** -1 - self.d) / (self.u - self.d)
                    Q_t.append(q_j)
                self.Q.append(Q_t)
        else:  # General o Recombinante
            for i in range(self.N):
                Q_t = []
                for j in range(len(self.niveles[i])):
                    Sn = self.niveles[i][j]
                    Sd = self.niveles[i + 1][j]
                    Su = self.niveles[i + 1][j + 1]
                    q_j = (Sn * B(self.r, self.delta, tiempo) ** -1 - Sd) / (Su - Sd)
                    Q_t.append(q_j)
                self.Q.append(Q_t)

        return self.Q
    

class Arbol_Binomial_Con_Dividendos:
    """Árbol binomial para subyacentes que pagan dividendos discretos o continuos"""
    
    def __init__(self, Subyacente, T, N, r, tipo, u=None, d=None):
        self.Subyacente = Subyacente
        self.T = T
        self.N = N
        self.delta = T / N if T != 0 and N != 0 else 0
        self.r = r
        self.tipo = tipo
        self.u = u
        self.d = d
        self.niveles = [[Subyacente.S0]]
        self.Q = []
        
        # Calcular dividendos por periodo según periodicidad
        self.calcular_dividendos_por_periodo()

    def calcular_dividendos_por_periodo(self):
        """Calcula en qué periodos se pagan dividendos según la periodicidad"""
        self.periodos_con_dividendo = []
        
        if self.Subyacente.tipo_subyacente == "Con dividendos discretos":
            if self.Subyacente.periodicidad == "Por periodo":
                # Dividendo en cada periodo
                self.periodos_con_dividendo = list(range(1, self.N + 1))
            elif self.Subyacente.periodicidad == "Anual":
                periodos_por_año = int(self.N / self.T) if self.T > 0 else self.N
                self.periodos_con_dividendo = [i * periodos_por_año for i in range(1, int(self.T) + 1) 
                                               if i * periodos_por_año <= self.N]
            elif self.Subyacente.periodicidad == "Semestral":
                periodos_por_semestre = int(self.N / (self.T * 2)) if self.T > 0 else self.N
                self.periodos_con_dividendo = [i * periodos_por_semestre for i in range(1, int(self.T * 2) + 1) 
                                               if i * periodos_por_semestre <= self.N]
            elif self.Subyacente.periodicidad == "Mensual":
                periodos_por_mes = int(self.N / (self.T * 12)) if self.T > 0 else self.N
                self.periodos_con_dividendo = [i * periodos_por_mes for i in range(1, int(self.T * 12) + 1) 
                                               if i * periodos_por_mes <= self.N]

    def construir_arbol_multiplicativo(self):
        """Construye árbol multiplicativo considerando dividendos"""
        self.niveles = [[self.Subyacente.S0]]
        
        for i in range(1, self.N + 1):
            nivel = []
            for j in range(i + 1):
                nodo = self.Subyacente.S0 * (self.u ** j) * (self.d ** (i - j))
                
                # Ajustar por dividendos discretos
                if self.Subyacente.tipo_subyacente == "Con dividendos discretos":
                    dividendos_acumulados = sum([self.Subyacente.monto_dividendo 
                                                 for t in self.periodos_con_dividendo if t <= i])
                    nodo = max(nodo - dividendos_acumulados, 0.0001)
                
                # Ajustar por dividendos continuos
                elif self.Subyacente.tipo_subyacente == "Con dividendos continuos":
                    factor_dividendo = math.exp(-self.Subyacente.tasa_dividendo * i * self.delta)
                    nodo = nodo * factor_dividendo
                
                nivel.append(round(nodo, 6))
            self.niveles.append(nivel)

    def arbol_temporal(self):
        """Construye árbol temporal considerando dividendos"""
        if self.tipo == "General":
            self.niveles = [[self.Subyacente.S0]]
            paso = 0.5

            for t in range(1, self.N + 1):
                nivel_prev = self.niveles[-1]
                delta_t = paso / (2 ** (t - 1))
                nivel = []
                
                for p in nivel_prev:
                    down = p - delta_t
                    up = p + delta_t
                    
                    # Aplicar dividendo si corresponde
                    if (self.Subyacente.tipo_subyacente == "Con dividendos discretos" and 
                        t in self.periodos_con_dividendo):
                        down = max(down - self.Subyacente.monto_dividendo, 0.0001)
                        up = max(up - self.Subyacente.monto_dividendo, 0.0001)
                    
                    nivel.extend([round(down, 6), round(up, 6)])
                
                nivel.sort()
                self.niveles.append(nivel)

        elif self.tipo == "Recombinante" or self.tipo == "Multiplicativo":
            u_temporal = 1.2
            d_temporal = 1 / 1.2
            self.niveles = [[self.Subyacente.S0]]

            for t in range(1, self.N + 1):
                nivel = []
                for j in range(t + 1):
                    nodo = self.Subyacente.S0 * (u_temporal ** j) * (d_temporal ** (t - j))
                    
                    # Aplicar dividendos
                    if self.Subyacente.tipo_subyacente == "Con dividendos discretos":
                        dividendos_acumulados = sum([self.Subyacente.monto_dividendo 
                                                     for periodo in self.periodos_con_dividendo if periodo <= t])
                        nodo = max(nodo - dividendos_acumulados, 0.0001)
                    elif self.Subyacente.tipo_subyacente == "Con dividendos continuos":
                        factor_dividendo = math.exp(-self.Subyacente.tasa_dividendo * t * self.delta)
                        nodo = nodo * factor_dividendo
                    
                    nivel.append(round(nodo, 6))
                
                nivel.sort()
                self.niveles.append(nivel)

    # Métodos auxiliares (iguales a Arbol_Binomial)
    def nombres_nodos(self):
        lista_ids = []
        indice = 0
        for t, fila in enumerate(self.niveles):
            for _ in fila:
                lista_ids.append(f"S{indice}")
                indice += 1
        return lista_ids

    def obtener_posicion(self, nombre_nodo):
        k = int(nombre_nodo[1:])
        contador = 0
        for t, fila in enumerate(self.niveles):
            for j, _ in enumerate(fila):
                if contador == k:
                    return t, j
                contador += 1
        return None, None

    def agregar_nivel(self, nodos):
        self.niveles.append(nodos)

    def cambiar_nodo(self, tiempo, indice_nodo, nodo_nuevo):
        if tiempo < len(self.niveles) and indice_nodo < len(self.niveles[tiempo]):
            self.niveles[tiempo][indice_nodo] = nodo_nuevo

    def probabilidades_neutras_al_riesgo(self, tiempo):
        """Calcula probabilidades neutrales al riesgo ajustadas por dividendos"""
        self.Q = []
        
        # Ajustar tasa por dividendos continuos
        r_ajustado = self.r
        if self.Subyacente.tipo_subyacente == "Con dividendos continuos":
            r_ajustado = self.r - self.Subyacente.tasa_dividendo

        if self.tipo == "Multiplicativo":
            for i in range(self.N):
                Q_t = []
                for _ in range(i + 1):
                    q_j = (math.exp(r_ajustado * self.delta) - self.d) / (self.u - self.d)
                    Q_t.append(q_j)
                self.Q.append(Q_t)
        else:  # General o Recombinante
            for i in range(self.N):
                Q_t = []
                for j in range(len(self.niveles[i])):
                    Sn = self.niveles[i][j]
                    Sd = self.niveles[i + 1][j]
                    Su = self.niveles[i + 1][j + 1]
                    q_j = (Sn * math.exp(-r_ajustado * self.delta) - Sd) / (Su - Sd)
                    Q_t.append(q_j)
                self.Q.append(Q_t)

        return self.Q

# --------------------------------------------- COBERTURAS --------------------------------------------


class Cobertura:
    """Calcula la cobertura dinámica y valoración del derivado"""
    
    def __init__(self, derivado, arbol):
        self.derivado = derivado                                         # Call / Put
        self.arbol = arbol                                               # Árbol binomial ya construido
        self.valores = []                                                # Valor de la cobertura / derivado en cada nodo
        self.alphas = []                                                 # Cantidad de subyacente a mantener en cada nodo
        self.betas = []                                                  # Cantidad invertida en el activo libre de riesgo en cada nodo
        self.optimos = []                                                # Nodos optimos de ejercicio en opciones americanas (1 si es optimo, 0 si no)

    def calcular_cobertura(self, tiempo, subtipo=None, M=None):
        """Calcula valores, alphas y betas mediante backward induction"""
        
        # Paso 1: Calcular payoffs en el vencimiento
        STs = self.arbol.niveles[-1]
        
        if isinstance(self.derivado, (Call_Digital, Put_Digital)):
            Pay_offs = [self.derivado.pay_off(ST, subtipo, M) for ST in STs]
        else:
            Pay_offs = [self.derivado.pay_off(ST) for ST in STs]
        
        self.valores.append(Pay_offs)
        
        # Para opciones americanas, inicializar lista de optimos
        if self.derivado.tipo == "americana":
            self.optimos.append([0] * len(Pay_offs))

        # Paso 2: Backward induction
        for i in reversed(range(self.arbol.N)):
            valores_t = []
            alphas_t = []
            betas_t = []
            optimos_t = []

            for j in range(len(self.arbol.niveles[i])):
                Sd = self.arbol.niveles[i + 1][j]
                Su = self.arbol.niveles[i + 1][j + 1]
                Vd = self.valores[0][j]
                Vu = self.valores[0][j + 1]

                # Valor teórico (continuación)
                V_teorico = B(self.arbol.r, self.arbol.delta, tiempo) * \
                           (Vu * self.arbol.Q[i][j] + Vd * (1 - self.arbol.Q[i][j]))

                # Para americanas: comparar con ejercicio inmediato
                if self.derivado.tipo == "americana":
                    ST_actual = self.arbol.niveles[i][j]
                    V_ejercicio = self.derivado.pay_off(ST_actual)
                    
                    if V_ejercicio > V_teorico:
                        Vj = V_ejercicio
                        optimos_t.append(1)
                    else:
                        Vj = V_teorico
                        optimos_t.append(0)
                else:
                    Vj = V_teorico

                valores_t.append(Vj)

                # Calcular cobertura (alpha y beta)
                alpha = (Vu - Vd) / (Su - Sd)
                alphas_t.append(alpha)

                beta = B(self.arbol.r, self.arbol.delta, tiempo) * (Vu - alpha * Su)
                betas_t.append(beta)

            # Insertar al inicio (porque vamos hacia atrás)
            self.valores.insert(0, valores_t)
            self.alphas.insert(0, alphas_t)
            self.betas.insert(0, betas_t)
            
            if self.derivado.tipo == "americana":
                self.optimos.insert(0, optimos_t)


# -------------------------------------------- BLACK SCHOLES ------------------------------------------

# Esta parte no esta incluida en el trabajo final
def Black_Scholes(derivado, sigma):
    """Calcula precio de opciones europeas usando Black-Scholes"""
    
    d1 = (1 / (sigma * math.sqrt(derivado.T))) * \
         (math.log(derivado.subyacente.S0 / derivado.K) + 
          (derivado.r + 0.5 * sigma ** 2) * derivado.T)
    
    d2 = d1 - sigma * math.sqrt(derivado.T)

    if isinstance(derivado, Call):
        precio = (derivado.subyacente.S0 * norm.cdf(d1) - 
                 derivado.K * math.exp(-derivado.r * derivado.T) * norm.cdf(d2))
        return precio if derivado.posicion == "largo" else -precio

    elif isinstance(derivado, Put):
        precio = (derivado.K * math.exp(-derivado.r * derivado.T) * norm.cdf(-d2) - 
                 derivado.subyacente.S0 * norm.cdf(-d1))
        return precio if derivado.posicion == "largo" else -precio
    
    return None

