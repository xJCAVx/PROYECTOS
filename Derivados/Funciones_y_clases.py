# PROYECTO DERIVADOS

import math


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
    def __init__(self, subyacente, strike, vencimiento, periodos, interes, tipo, exotico, posicion):

        self.subyacente = subyacente                                    # Subyacente
        self.K = strike                                                 # Precio strike
        self.T = vencimiento                                            # Tiempo de maduración
        self.N = periodos                                               # Numero de periodos
        self.r = interes                                                # Tasa de interes
        self.tipo = tipo                                                # Europea / Americana
        self.exotico = exotico                                          # Si / No
        self.posicion = posicion                                        # Long / Short


#------------------------------------------- FORDWARD -----------------------------------------------

# Subclase del derivado fordward
class Fordward(Derivado):
    
    # Precio teorico del fordward en t = 0
    def precio_fordward(self,tiempo):
        return self.subyacente.S0 * B( self.r, self.T, tiempo) ** -1


    # Valor del fordward en el tiempo t dado St
    def pay_off(self, t, St, tiempo):
        delta = self.T - t
        if self.posicion == "largo":
            return St - self.K * B(self.r, delta, tiempo)
        else:
            return self.K * B(self.r, delta, tiempo) - St







































