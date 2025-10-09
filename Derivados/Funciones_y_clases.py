# PROYECTO DERIVADOS

import math
from scipy.stats import norm


# ------------------------------------------- FUNCIONES -----------------------------------------------

# Funcion para traer a Valor Presente 
def B( r, delta, tiempo):

    if tiempo == "discreto":
        return (1 + r) ** (-delta)
    else:
        return math.exp( -r * delta)


# -------------------------------------------- CLASES -------------------------------------------------


# Clase del activo subyacente sin dividendos
class Subyacente:

    def __init__(self,S0):
        self.S0 = S0                                                    # Precio inicial del subyacente


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
        self.delta = T/N                                                # Delta
        self.r = r                                                      # Tasa de interes     
        self.tipo = tipo                                                # General / Recombinante / Multiplicativo
        self.u = u                                                      # Tasa de subida (multplicativo)
        self.d = d                                                      # Tasa de bajada (multplicativo)
        self.niveles = [[Subyacente.S0]]                                           # Nodos
        self.Q = []                                                     # Probabilidades neutras al riesgo
        
        # Construccion de un arbol Multiplicativo
        if tipo == "multiplicativo":
            for i in range(1,self.N + 1): # i es el tiempo (1,N)
                nivel = []
                for j in range(i+1): # j es el nodo en el tiempo i 
                    nodo = self.Subyacente.S0 * (self.u ** j) * (self.d ** (i - j))
                    nivel.append(nodo)
                self.niveles.append(nivel)


    # Construccion de arbol General o Recombinante (se le deben pasar una lista con los nodos para cada tiempo)
    def agregar_nivel(self,nodos):
        self.niveles.append(nodos)


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
        precio = derivado.K * math.exp(-derivado.r * derivado.T) * norm.cdf(-d2) + derivado.subyacente.S0 * norm.cdf(-d1)
        if derivado.posicion == "largo":
            return precio
        else:
            return -precio

