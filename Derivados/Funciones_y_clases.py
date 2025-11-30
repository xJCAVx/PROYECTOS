# PROYECTO DERIVADOS

import math
from scipy.stats import norm
import plotly.graph_objects as go


# ------------------------------------------- FUNCIONES -----------------------------------------------

# Funcion para traer a Valor Presente 
def B( r, delta, tiempo):

    if tiempo == "discreto":
        return (1 + r) ** (-delta)
    else:
        return math.exp( -r * delta)

def grafica_arbol(arbol, tipo):
    niveles = arbol.niveles

    nodes = []
    node_id_map = {}
    contador_nombres = 0   # Para S0, S1, S2, ...

    for t, nivel in enumerate(niveles):
        row = []
        for j, precio in enumerate(nivel):
            node_id = f"{t}-{j}"
            nombre_nodo = f"S{contador_nombres}"
            contador_nombres += 1

            node = {
                "id": node_id,
                "x": t,
                "y": float(precio),
                "label": str(round(precio, 3)),   # precio arriba
                "name": nombre_nodo              # nombre abajo
            }
            row.append(node)
            node_id_map[node_id] = node
        nodes.append(row)

    # ------------------------------
    # Construcción de conexiones según el tipo
    # ------------------------------
    edges = []

    for t in range(len(nodes) - 1):
        nivel_actual = nodes[t]
        nivel_siguiente = nodes[t+1]

        for j, parent in enumerate(nivel_actual):

            if tipo == "General":
                hijo1 = 2*j
                hijo2 = 2*j + 1
                if hijo1 < len(nivel_siguiente):
                    edges.append((parent, nivel_siguiente[hijo1]))
                if hijo2 < len(nivel_siguiente):
                    edges.append((parent, nivel_siguiente[hijo2]))

            else:
                if j < len(nivel_siguiente):
                    edges.append((parent, nivel_siguiente[j]))
                if j + 1 < len(nivel_siguiente):
                    edges.append((parent, nivel_siguiente[j+1]))

    # ------------------------------
    # GRAFICAR
    # ------------------------------

    fig = go.Figure()

    # Líneas
    for parent, child in edges:
        fig.add_trace(go.Scatter(
            x=[parent["x"], child["x"]],
            y=[parent["y"], child["y"]],
            mode="lines",
            line=dict(color="gray", width=1),
            hoverinfo="skip",
            showlegend=False
        ))

    # Nodos
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



# -------------------------------------------- CLASES -------------------------------------------------


# Clase del activo subyacente sin dividendos
class Subyacente:

    def __init__(self,S0, tipo_subyacente = None, monto_dividendo = None, tasa_dividendo = None, periodicidad = None):
        self.S0 = S0                                                    # Precio inicial del subyacente
        self.tipo_subyacente = tipo_subyacente                          # Sin dividendos / Con dividendos discretos / Con dividendos continuos
        self.monto_dividendo = monto_dividendo                          # Monto dividendos discretos
        self.tasa_dividendo = tasa_dividendo                            # Tasa dividendos continuos
        self.periodicidad = periodicidad                                # Cada cuanto se pagan los dividendos 


# Clase de los atributos generales de un derivado
class Derivado:

    def __init__(self, subyacente, strike, vencimiento, periodos, interes, tipo, posicion):

        self.subyacente = subyacente                                    # Subyacente
        self.K = strike                                                 # Precio strike
        self.T = vencimiento                                            # Tiempo de maduración
        self.N = periodos                                               # Numero de periodos
        self.r = interes                                                # Tasa de interes
        self.tipo = tipo                                                # Europea / Americana
        self.posicion = posicion                                        # Long / Short


# ------------------------------------------- FORDWARD ------------------------------------------------


# Subclase del derivado Fordward
class Fordward(Derivado):
    
    # Precio teorico del fordward en t = 0
    def precio_fordward(self,tiempo):
        return self.subyacente.S0 * B( self.r, self.T, tiempo) ** -1

    # Valor del fordward en el tiempo t dado que el subyacente tomo el precio St
    def pay_off(self, t, St, tiempo):
        delta = self.T - t
        if self.posicion == "largo":
            return St - self.K * B(self.r, delta, tiempo)
        else:
            return self.K * B(self.r, delta, tiempo) - St


# ------------------------------------------- OPCIONES ------------------------------------------------

# Subclase del derivado Call
class Call(Derivado):
    
    # Pay off de una opcion call
    def pay_off(self, ST):
        if self.posicion == "largo":    
            return max(ST - self.K, 0)
        else:
            return - max(ST - self.K, 0)


# Subclase del derivado Put
class Put(Derivado):

    # Pay off de una opcion put
    def pay_off(self, ST):
        if self.posicion == "largo":
            return max(self.K - ST,0)
        else:
            return -max(self.K - ST,0)


# Subclase Call Digital Europea
class Call_Digital(Derivado):
    
    def pay_off(self, ST, subtipo, M = None):
     
        if subtipo == "cash or nothing":                                 # Cash or nothing europeo
            if ST > self.K:
                if self.posicion == "largo":
                    return M
                else:
                    return -M
            else:
                return 0

        if subtipo == "asset or nothing":                                # Asset or nothing europeo                                                        
            if ST > self.K:
                if self.posicion == "largo":
                    return ST
                else:
                    return -ST
            else:
                return 0
            

# Subclase Put Digital Europea 
class Put_Digital(Derivado):

    def pay_off(self, ST, subtipo, M = None):
     
        if subtipo == "cash or nothing":                                # Cash or nothing europeo
            if ST < self.K:
                if self.posicion == "largo":
                    return M
                else:
                    return -M
            else:
                return 0

        if subtipo == "asset or nothing":                                # Asset or nothing europeo    
            if ST < self.K:
                if self.posicion == "largo":                
                    return ST
                else:
                    return -ST
            else:
                return 0


# ----------------------------------------- ARBOLES BINOMIALES ----------------------------------------


class Arbol_Binomial:
        
    def __init__(self, Subyacente, T, N, r, tipo, u = None, d = None):
        self.Subyacente = Subyacente                                    # Subyacente
        self.T = T                                                      # Vencimiento
        self.N = N                                                      # Periodos
        self.delta = T/N if T != 0 and N != 0 else 0                    # Delta
        self.r = r                                                      # Tasa de interes     
        self.tipo = tipo                                                # General / Recombinante / Multiplicativo
        self.u = u                                                      # Tasa de subida (multiplicativo)
        self.d = d                                                      # Tasa de bajada (mulitplicativo)
        self.niveles = [[Subyacente.S0]]                                           # Nodos
        self.Q = []                                                     # Probabilidades neutras al riesgo

    # Construccion del arbol multiplicativo
    def construir_arbol_multiplicativo(self):
        self.niveles = [[self.Subyacente.S0]]  
        for i in range(1,self.N + 1): # i es el tiempo (1,N)
            nivel = []
            for j in range(i+1): # j es el nodo en el tiempo i 
                nodo = self.Subyacente.S0 * (self.u ** j) * (self.d ** (i - j))
                nivel.append(nodo)
            self.niveles.append(nivel)


    def nombres_nodos(self):
        lista_ids = []
        indice = 0
        for t, fila in enumerate(self.niveles):
            for j, precio in enumerate(fila):
                etiqueta = f"S{indice}"
                lista_ids.append(etiqueta)
                indice += 1
        return lista_ids

    def obtener_posicion(self, nombre_nodo):

        k = int(nombre_nodo[1:])   # extrae el número
        contador = 0

        for t, fila in enumerate(self.niveles):
            for j, _ in enumerate(fila):
                if contador == k:
                    return t, j
                contador += 1


    # Construccion de arbol General o Recombinante (se le deben pasar una lista con los nodos para cada tiempo)
    def agregar_nivel(self,nodos):
        self.niveles.append(nodos)

    # Para 
    def cambiar_nodo(self, tiempo, nodo_anterior, nodo_nuevo):
        self.niveles[tiempo][nodo_anterior]  = nodo_nuevo


    def arbol_temporal(self):
        if self.tipo == "General":
            self.niveles = [[self.Subyacente.S0]]   
            paso = 0.5  # ajustable

            for t in range(1, self.N + 1):
                nivel_prev = self.niveles[-1]
                delta_t = paso / (2 ** (t - 1))   # decrementa con la profundidad
                nivel = []
                for p in nivel_prev:
                    nivel.append(round(p - delta_t, 6))
                    nivel.append(round(p + delta_t, 6))
                nivel.sort()
                self.agregar_nivel(nivel)

        elif self.tipo == "Recombinante":
            u_temporal = 1.2
            d_temporal = 1/1.2
            self.niveles = [[self.Subyacente.S0]]    
        
            for t in range(1, self.N + 1):
                nivel = [round(self.Subyacente.S0 * (u_temporal**j) * (d_temporal**(t-j)), 6) for j in range(t+1)]
                nivel.sort()  # ordenado
                self.agregar_nivel(nivel)

        
        else:   # Multiplicativo         
            u_temporal = 1.2
            d_temporal = 1/1.2
            self.niveles = [[self.Subyacente.S0]]    
            for t in range(1, self.N + 1):
                nivel = [round(self.Subyacente.S0 * (u_temporal**j) * (d_temporal**(t-j)), 6) for j in range(t+1)]
                nivel.sort()  # ordenado
                self.agregar_nivel(nivel)


    # Calculo de Q
    def probabilidades_neutras_al_riesgo(self, tiempo):
        
        # Caso Multiplicativo
        if self.tipo == "multiplicativo":
            for i in range(self.N): # i es el tiempo (0,N-1)
                Q_t = []
                for j in range(i + 1): # Proba j en el tiempo i (0,i)
                    q_j = ( B( self.r, self.delta, tiempo)**-1 - self.d ) / ( self.u - self.d ) 
                    Q_t.append(q_j)
                self.Q.append(Q_t)
            return self.Q

        # Caso General / Recombinante
        else:
            for i in range(self.N): # i es el tiempo (0,N-1)
                Q_t = []
                for j in range(len(self.niveles[i])): # Proba j en el tiempo i 
                    Sn = self.niveles[i][j]
                    Sd = self.niveles[i+1][j]     # Nodo "down"
                    Su = self.niveles[i+1][j+1]   # Nodo "up"
                    q_j = (Sn * B( self.r, self.delta, tiempo)**-1  - Sd) / (Su - Sd)
                    Q_t.append(q_j)
                self.Q.append(Q_t)
            return self.Q


# --------------------------------------------- COBERTURAS --------------------------------------------


class Cobertura:
    
    def __init__(self, derivado, arbol):
        self.derivado = derivado                                         # Call / Put
        self.arbol = arbol                                               # Árbol binomial ya construido
        self.valores = []                                                # Valor de la cobertura / derivado en cada nodo
        self.alphas = []                                                 # Cantidad de subyacente a mantener en cada nodo
        self.betas = []                                                  # Cantidad invertida en el activo libre de riesgo en cada nodo
        self.optimos = []                                                # Nodos optimos de ejercicio en opciones americanas (1 si es optimo, 0 si no)

    # Calculo del valor del derivado, sus alphas y betas en cada tiempo para cualquier tipo de árbol
    def calcular_cobertura(self, tiempo, subtipo = None, M = None):

        if self.derivado.tipo == "europea":

            STs = self.arbol.niveles[-1]
            if isinstance(self.derivado, (Call_Digital,Put_Digital)):
                Pay_offs = [self.derivado.pay_off(ST,subtipo, M) for ST in STs]
            else:
                Pay_offs = [self.derivado.pay_off(ST) for ST in STs]
            self.valores.append(Pay_offs)
            
            for i in reversed(range(self.arbol.N)): # Se recorre el arbol hacia atras (N-1, 0)
                valores_t = []
                alphas_t = []
                betas_t = []

                for j in range(len(self.arbol.niveles[i])): # Nodo j en el tiempo i 
                    Sd = self.arbol.niveles[i + 1][j]
                    Su = self.arbol.niveles[i + 1][j + 1]
                    Vd = self.valores[0][j]
                    Vu = self.valores[0][j + 1]
                    
                    # Calculo del valor del derivado en en nodo ij
                    Vj = B( self.arbol.r, self.arbol.delta, tiempo) * ( Vu * self.arbol.Q[i][j] + Vd * (1 - self.arbol.Q[i][j]) )
                    valores_t.append(Vj)
                    
                    # Calculo de la alpha en el nodo ij
                    alpha = (Vu - Vd) / (Su - Sd)
                    alphas_t.append(alpha)

                    # Caluclo de la beta en el nodo ij
                    beta = B( self.arbol.r, self.arbol.delta, tiempo) * ( Vu - alpha * Su)
                    betas_t.append(beta)

                self.valores.insert(0, valores_t)
                self.alphas.insert(0, alphas_t)
                self.betas.insert(0, betas_t)

        else:
            STs = self.arbol.niveles[-1]
            Pay_offs = [self.derivado.pay_off(ST) for ST in STs]
            self.valores.append(Pay_offs)

            for i in reversed(range(self.arbol.N)): # Se recorre el arbol hacia atras (N-1, 0)
                valores_t = []
                alphas_t = []
                betas_t = []
                optimos_t = []

                for j in range(len(self.arbol.niveles[i])): # Nodo j en el tiempo i 
                    Sd = self.arbol.niveles[i + 1][j]
                    Su = self.arbol.niveles[i + 1][j + 1]
                    Vd = self.valores[0][j]
                    Vu = self.valores[0][j + 1]

                    # Calculo del valor del derivado en en nodo ij si se deja vivir un periodo más
                    V_teorico = B( self.arbol.r, self.arbol.delta, tiempo) * ( Vu * self.arbol.Q[i][j] + Vd * (1 - self.arbol.Q[i][j]) )

                    # Calculo del valor del derivado en el nodo ij si se ejerce en ese momento
                    ST_actual = self.arbol.niveles[i][j]
                    V_actual = self.derivado.pay_off(ST_actual)
                    
                    # Maximo entre ambos
                    Vj = max(V_actual, V_teorico)
                    valores_t.append(Vj)

                    # Creacion de nodos optimos
                    if max(V_actual, V_teorico) == V_actual:
                        optimos_t.append(1)
                    else:
                        optimos_t.append(0)

                    # Calculo de la alpha en el nodo ij
                    alpha = (Vu - Vd) / (Su - Sd)
                    alphas_t.append(alpha)
                    
                    # Caluclo de la beta en el nodo ij
                    beta = B( self.arbol.r, self.arbol.delta, tiempo) * ( Vu - alpha * Su)
                    betas_t.append(beta)

                self.valores.insert(0, valores_t)
                self.alphas.insert(0, alphas_t)
                self.betas.insert(0, betas_t)
                self.optimos.insert(0,optimos_t)


# -------------------------------------------- BLACK SCHOLES ------------------------------------------


# Precio de opciones call y put europeas
def Black_Scholes(derivado, sigma): 

    d1 = ( 1 / (sigma * math.sqrt(derivado.T)) ) * ( math.log(derivado.subyacente.S0/derivado.K) + (derivado.r + 1/2 * sigma**2) * derivado.T)

    d2 = d1 - sigma * math.sqrt(derivado.T)

    if isinstance(derivado, Call):
        precio = derivado.subyacente.S0 * norm.cdf(d1) - derivado.K * math.exp(-derivado.r * derivado.T) * norm.cdf(d2)
        if derivado.posicion == "largo":
            return precio
        else:
            return -precio

    if isinstance(derivado, Put):
        precio = derivado.K * math.exp(-derivado.r * derivado.T) * norm.cdf(-d2) - derivado.subyacente.S0 * norm.cdf(-d1)
        if derivado.posicion == "largo":
            return precio
        else:
            return -precio

