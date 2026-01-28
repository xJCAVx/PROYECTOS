# PROYECTO DERIVADOS V2

import math
from scipy.stats import norm

# FUNCIONES ---------------------------------------------------------------------------------------------


def Factor_de_Descuento(tasa : float, delta : float, tiempo : str) -> float:
    """ 
    Calcula el factor de descuento para traer un flujo a Valor presente

    Parameters
    ----------
    tasa (Tasa de interés) : float
    delta (Tiempo en años) : float
    tiempo (Tipo de capitalización, discreta o continua) : str

    Returns
    -------
    Factor de descuento : float
    """
    if tiempo == "Discreto":
        return (1.0 + tasa)**(-delta)
    else:
        return math.exp(-tasa*delta)


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


# SUBYACENTE ---------------------------------------------------------------------------------------------


class Subyacente:
    """Clase que representa el activo subyacente"""
    def __init__(self, S0, tipo_subyacente = None, monto_dividendo = None, tasa_dividendo = None, periodicidad = None):
        
        self.S0 = S0                                                                           # Precio inicial del subyacente
        self.tipo_subyacente = tipo_subyacente                                                 # Sin dividendos / Con dividendos discretos / Con dividendos continuos
        self.monto_dividendo = monto_dividendo                                                 # Monto dividendos discretos
        self.tasa_dividendo = tasa_dividendo if tasa_dividendo is not None else 0              # Tasa dividendos continuos
        self.periodicidad = periodicidad                                                       # Cada cuanto se pagan los dividendos 


# DERIVADOS ----------------------------------------------------------------------------------------------


class Derivado:
    """Clase base para todos los derivados"""
    def __init__(self, subyacente, strike, vencimiento, periodos, interes, tipo, posicion):

        self.subyacente = subyacente                        # Subyacente
        self.K = strike                                     # Precio strike
        self.T = vencimiento                                # Tiempo de maduración
        self.N = periodos                                   # Numero de periodos
        self.r = interes                                    # Tasa de interes
        self.tipo = tipo                                    # Europea / Americana
        self.posicion = posicion                            # Largo / Corto


class Fordward(Derivado):
    """Subclase del derivado Fordward"""
    def precio_fordward(self,tiempo):
        """Precio teorico del fordward en t = 0"""
        return self.subyacente.S0 * Factor_de_Descuento( self.r, self.T, tiempo) ** -1

    def pay_off(self, t, St, tiempo):
        """Valor del fordward en el tiempo t dado que el subyacente tomo el precio St"""
        delta = self.T - t
        payoff_base = St - self.K * Factor_de_Descuento(self.r, delta, tiempo)
        return payoff_base if self.posicion == "largo" else -payoff_base

class Call(Derivado):
    """Opción Call europea o americana"""
    def pay_off(self, ST):
        """Payoff del Call a vencimiento"""
        payoff_base = max(ST - self.K, 0)
        return payoff_base if self.posicion == "largo" else -payoff_base

class Put(Derivado):
    """Opción Put europea o americana"""
    def pay_off(self, ST):
        """Payoff del Put a vencimiento"""
        payoff_base = max(self.K - ST, 0)
        return payoff_base if self.posicion == "largo" else -payoff_base


class Call_Digital(Derivado):
    """Opción Call Digital (Cash-or-Nothing o Asset-or-Nothing)"""
    def pay_off(self, ST, subtipo="Cash-or-Nothing", M=None):
        """Payoff de la opción digital dependiendo el tipo"""
        if subtipo == "Cash-or-Nothing":
            cantidad = M
        elif subtipo == "Asset-or-Nothing":
            cantidad = ST
        if ST > self.K:
            return cantidad if self.posicion == "largo" else -cantidad
        return 0

class Put_Digital(Derivado):
    """Opción Put Digital (Cash-or-Nothing o Asset-or-Nothing)"""
    def pay_off(self, ST, subtipo="Cash-or-Nothing", M=None):
        """Payoff de la opción digital dependiendo el tipo"""
        if subtipo == "Cash-or-Nothing":
            cantidad = M
        elif subtipo == "Asset-or-Nothing":
            cantidad = ST
        if ST < self.K:
            return cantidad if self.posicion == "largo" else -cantidad
        return 0
    

# ARBOLES BINOMIALES -------------------------------------------------------------------------------------


class Arbol_Binomial:
    """Árbol binomial del precio del subyacente""" 
    def __init__(self, Subyacente, T, N, r, tipo, u = None, d = None):
        self.Subyacente = Subyacente                        # Subyacente
        self.T = T                                          # Vencimiento
        self.N = N                                          # Periodos
        self.delta = T/N                                    # Delta
        self.r = r                                          # Tasa de interes     
        self.tipo = tipo                                    # General / Recombinante / Multiplicativo
        self.u = u if (u is not None) else 1.2              # Tasa de subida (multiplicativo, valor default)
        self.d = d if (d is not None) else (1.0 / self.u)   # Tasa de bajada (mulitplicativo, valor default)
        self.niveles = [[Subyacente.S0]]                    # Nodos
        self.Q = None                                       # Probabilidades neutras al riesgo
        self.nombres_posicion = {}                          # Nombres y posicion de cada nodo

    def nombre_posicion_nodos(self):
        """Ingresa en un diccionario el nombre de los nodos y una lista con su posición """
        self.nombres_posicion = {}
        indice = 0
        for t, fila in enumerate(self.niveles):
            for j, _ in enumerate(fila):
                self.nombres_posicion[f"S{indice}"] = (t,j)
                indice += 1

    def agregar_nivel(self, nodos):
        """Agrega un nivel completo (una lista) a los arboles generales y recombinantes"""
        self.niveles.append(nodos)
        self.nombres_posicion = {}
        self.nombre_posicion_nodos()

    def cambiar_nodo(self, tiempo, indice_nodo, nodo_nuevo):
        """Modifica el precio de un nodo específico"""
        self.niveles[tiempo][indice_nodo] = nodo_nuevo


    def calcular_dividendos_por_periodo(self):
        """Calculamos los pagos de dividendos discretos"""
        self.periodos_con_dividendo = []
        self.dividendos_por_periodo = {}

        tipo = getattr(self.Subyacente, "tipo_subyacente", None)
        monto = getattr(self.Subyacente, "monto_dividendo", None)
        periodicidad = getattr(self.Subyacente, "periodicidad", None)

        if tipo != "Con dividendos discretos" or monto in (None,0):
            return
        
        pagos_por_año = {
                        "Anual" : 1,
                        "Semestral" : 2,
                        "Mensual": 12,
                        "Por periodo" : None
                        }
        
        if periodicidad == "Por periodo":
            self.periodos_con_dividendo = list(range(1,self.N+1))
        else:
            pagos = pagos_por_año.get(periodicidad,1)
            # Cantidad de pagos hasta el vencimiento T
            if pagos is None:
                self.periodos_con_dividendo = []
            else:
                max_pagos = int(self.T * pagos) 
                for k in range(1, max_pagos + 1):
                    pago_t = k /pagos # tiempo en años
                    idx = int(round(pago_t * self.N / self.T))
                    idx = max(1,min(self.N, idx))
                    if idx not in self.periodos_con_dividendo:
                        self.periodos_con_dividendo.append(idx)
            
        for periodo in self.periodos_con_dividendo:
            self.dividendos_por_periodo[periodo] = monto


    def construir_arbol_multiplicativo(self):
        """
        Construye árbol multiplicativo: S(t,j) = S0 * u^j * d^(t-j)
        """
        self.niveles = [[self.Subyacente.S0]]

        if getattr(self.Subyacente, "tipo_subyacente", None) == "Con dividendos discretos":
            if not hasattr(self, "periodos_con_dividendo"):
                self.calcular_dividendos_por_periodo()

        # Por que cada i es un periodo
        for i in range(1, self.N + 1): 
            nivel = []
            # Cada j es un nodo en el tiempo i
            for j in range(i + 1):
                nodo = self.Subyacente.S0 * (self.u ** j) * (self.d ** (i - j))

                # Si hay dividendos discretos, restar suma de dividendos pagados hasta periodo i
                if getattr(self.Subyacente, "tipo_subyacente", None) == "Con dividendos discretos":
                    dividendos_acumulados = 0.0
                    for periodo, monto in self.dividendos_por_periodo.items():
                        if periodo <=i:
                            dividendos_acumulados += monto
                    nodo = nodo - dividendos_acumulados

                if getattr(self.Subyacente, "tipo_subyacente", None) == "Con dividendos continuos":
                    q = getattr(self.Subyacente, "tasa_dividendo",0.0)
                    nodo = nodo * math.exp(-q * i * self.delta)
                    
                nivel.append(nodo)
            self.niveles.append(nivel)


    def arbol_temporal(self):
        """Construye un árbol general correctamente,
        con dividendos discretos y continuos arbitrage-free"""
        
        if self.tipo == "General":
            self.niveles = [[self.Subyacente.S0]]
            paso = 0.5

            for t in range(1, self.N + 1):
                nivel_prev = self.niveles[-1]
                delta_t = paso / (2 ** (t - 1))
                nivel = []

                for p in nivel_prev:
                    abajo = p - delta_t
                    arriba = p + delta_t
                    nivel.extend([abajo, arriba])

                # Dividendo discreto
                if getattr(self.Subyacente, "tipo_subyacente", None) == "Con dividendos discretos":
                    if not hasattr(self, "periodos_con_dividendo"):
                        self.calcular_dividendos_por_periodo()

                    if t in self.periodos_con_dividendo and t < self.N:
                        nivel = [s - self.Subyacente.monto_dividendo for s in nivel]

                # Dividendo continuo
                elif getattr(self.Subyacente, "tipo_subyacente", None) == "Con dividendos continuos":
                    q = getattr(self.Subyacente, "tasa_dividendo", None) or 0.0
                    factor = math.exp(-q * self.delta)
                    nivel = [s * factor for s in nivel]

                nivel = sorted(round(s, 6) for s in nivel)
                self.niveles.append(nivel)

        else:
            self.construir_arbol_multiplicativo()


    def probabilidades_neutras_al_riesgo(self, tiempo):
        """Calcula probabilidades neutrales al riesgo Q"""
        self.Q = []
        if self.tipo == "Multiplicativo":
            for i in range(self.N):
                Q_t = []
                for _ in range(i + 1):
                    q_j = (Factor_de_Descuento(self.r, self.delta, tiempo) ** -1 - self.d) / (self.u - self.d)
                    Q_t.append(q_j)
                self.Q.append(Q_t)
        else:  # General o Recombinante
            for i in range(self.N):
                Q_t = []
                for j in range(len(self.niveles[i])):
                    Sn = self.niveles[i][j]
                    Sd = self.niveles[i + 1][j]
                    Su = self.niveles[i + 1][j + 1]
                    q_j = (Sn * Factor_de_Descuento(self.r, self.delta, tiempo) ** -1 - Sd) / (Su - Sd)
                    Q_t.append(q_j)
                self.Q.append(Q_t)
        return self.Q


# COBERTURA ----------------------------------------------------------------------------------------------


class Cobertura:
    """Calcula la cobertura dinámica y valoración del derivado"""
    
    def __init__(self, derivado, arbol):
        self.derivado = derivado                            # Call / Put
        self.arbol = arbol                                  # Árbol binomial ya construido
        self.valores = []                                   # Valor de la cobertura / derivado en cada nodo
        self.alphas = []                                    # Cantidad de subyacente a mantener en cada nodo
        self.betas = []                                     # Cantidad invertida en el activo libre de riesgo en cada nodo
        self.optimos = []                                   # Nodos optimos de ejercicio en opciones americanas (1 si es optimo, 0 si no)

    def calcular_cobertura(self, tiempo, subtipo=None, M=None):
        """Calcula valores, alphas y betas mediante backward induction"""

        if self.arbol.Q is None:
            self.arbol.probabilidades_neutras_al_riesgo(tiempo)
        
        # Paso 1: Calcular payoffs en el vencimiento
        STs = self.arbol.niveles[-1]
        if type(self.derivado).__name__ in ("Call_Digital", "Put_Digital"):
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
                V_teorico = Factor_de_Descuento(self.arbol.r, self.arbol.delta, tiempo) * \
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

                beta = Factor_de_Descuento(self.arbol.r, self.arbol.delta, tiempo) * (Vu - alpha * Su)
                betas_t.append(beta)

            # Insertar al inicio (porque vamos hacia atrás)
            self.valores.insert(0, valores_t)
            self.alphas.insert(0, alphas_t)
            self.betas.insert(0, betas_t)
            if self.derivado.tipo == "americana":
                self.optimos.insert(0, optimos_t)


