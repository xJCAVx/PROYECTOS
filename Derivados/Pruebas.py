from Funciones_y_clases import B, Black_Scholes
from Funciones_y_clases import Subyacente, Fordward, Call, Put, Call_Digital, Put_Digital, Arbol_Binomial, Cobertura


# --------------------------------------- Pruebas Fordward ---------------------------------------------------


print("FORDWARD")

# Crear subyacente
activo = Subyacente(150)

# Forward largo
forward_largo = Fordward(
    subyacente=activo,
    strike=145,
    vencimiento=2,
    periodos=0,
    interes=0.05,
    tipo=None,
    posicion="largo"
)

# Forward corto
forward_corto = Fordward(
    subyacente=activo,
    strike=145,
    vencimiento=2,
    periodos=0,
    interes=0.05,
    tipo=None,
    posicion="corto"
)

# Precio teórico
print("Forward largo - Precio teórico (discreto):", forward_largo.precio_fordward("discreto"))
print("Forward corto - Precio teórico (discreto):", forward_corto.precio_fordward("discreto"))

# Pay-offs en distintos tiempos
tiempos = [0, 1, 1.5]
precios = [150, 160, 140]

for t, St in zip(tiempos, precios):
    print(f"\nT={t}, St={St}")
    print("Pay-off largo:", forward_largo.pay_off(t, St, "discreto"))
    print("Pay-off corto:", forward_corto.pay_off(t, St, "discreto"))
print()


# --------------------------------------- Pruebas Opciones ---------------------------------------------------


print("CALL Y PUT")

activo = Subyacente(100)

call_largo = Call(subyacente=activo, 
                  strike=105, 
                  vencimiento=1, 
                  periodos=0, 
                  interes=0.05, 
                  tipo=None, 
                  posicion="largo")

call_corto = Call(subyacente=activo, 
                  strike=105, 
                  vencimiento=1, 
                  periodos=0, 
                  interes=0.05, 
                  tipo=None, 
                  posicion="corto")

put_largo = Put(subyacente=activo, 
                strike=105, 
                vencimiento=1, 
                periodos=0, 
                interes=0.05, 
                tipo=None, 
                posicion="largo")

put_corto = Put(subyacente=activo, 
                strike=105, 
                vencimiento=1, 
                periodos=0, 
                interes=0.05, 
                tipo=None, 
                posicion="corto")

# Precios finales a evaluar
precios_ST = [100, 105, 110]

for ST in precios_ST:
    print(f"\nST = {ST}")
    print("Call largo:", call_largo.pay_off(ST))
    print("Call corto:", call_corto.pay_off(ST))
    print("Put largo:", put_largo.pay_off(ST))
    print("Put corto:", put_corto.pay_off(ST))
print()


# ---------------------------------------- Pruebas Arboles ---------------------------------------------------


# Ejercicio 2 de la Sesión 4
print("ARBOL")
subyacente1 = Subyacente(120)
arbol = Arbol_Binomial(subyacente1, 3, 3, r = 0.06, tipo = "multiplicativo", u = 1.7, d = 0.8)
for i in range(len(arbol.niveles)):
    print(arbol.niveles[i]) 
print()

probabilidades = arbol.probabilidades_neutras_al_riesgo("continuo")
for i in range(len(probabilidades)):
    print(probabilidades[i])


# ---------------------------------------- Pruebas Cobertura --------------------------------------------------

# Ejercicio 2 de la Sesión 4

print()
print("COBERTURA")
contrato = Call(subyacente = 120,
                    strike = 115,
                    vencimiento = 3,
                    periodos = 3,
                    interes = 0.06,
                    tipo = "europea",
                    posicion = "largo")

cobertura = Cobertura(contrato, arbol)
cobertura.calcular_cobertura("continuo")

for i in range(len(cobertura.valores)):
    print(cobertura.valores[i])
print()

for i in range(len(cobertura.alphas)):
    print(cobertura.alphas[i])
print()

for i in range(len(cobertura.alphas)):
    print(cobertura.betas[i])
print()


# ----------------------------------- Pruebas Opciones Digitales ----------------------------------------------

print("OPCIONES DIGITALES") # Solo se les paso el precio y funcionaron pero esta mal hay que pasarle un objeto de la clase subyacente

S_T1 = 110
S_T2 = 90
M = 10

#  Cash-or-Nothing Call
call_cash_long = Call_Digital(100, 100, 1, 1, 0.05, "europea", "largo")
call_cash_short = Call_Digital(100, 100, 1, 1, 0.05, "europea", "corto")

print("CALL CASH long:", call_cash_long.pay_off(S_T1, "cash or nothing", M))
print("CALL CASH short:", call_cash_short.pay_off(S_T1, "cash or nothing", M))

#  Asset-or-Nothing Call
call_asset_long = Call_Digital(100, 100, 1, 1, 0.05, "europea", "largo")
call_asset_short = Call_Digital(100, 100, 1, 1, 0.05, "europea", "corto")

print("CALL ASSET long:", call_asset_long.pay_off(S_T1, "asset or nothing"))
print("CALL ASSET short:", call_asset_short.pay_off(S_T1, "asset or nothing"))

# Cash-or-Nothing Put
put_cash_long = Put_Digital(100, 100, 1, 1, 0.05, "europea", "largo")
put_cash_short = Put_Digital(100, 100, 1, 1, 0.05, "europea", "corto")

print("PUT CASH long:", put_cash_long.pay_off(S_T2, "cash or nothing", M))
print("PUT CASH short:", put_cash_short.pay_off(S_T2, "cash or nothing", M))

#  Asset-or-Nothing Put
put_asset_long = Put_Digital(100, 100, 1, 1, 0.05, "europea", "largo")
put_asset_short = Put_Digital(100, 100, 1, 1, 0.05, "europea", "corto")

print("PUT ASSET long:", put_asset_long.pay_off(S_T2, "asset or nothing"))
print("PUT ASSET short:", put_asset_short.pay_off(S_T2, "asset or nothing"))


# Ejercicio 2 de la Sesion 3
print()

subyacente3_2 = Subyacente(100)
Call_3_2 = Call_Digital(subyacente3_2,100,1,3,0,"europea","largo")

arbol_3_2 = Arbol_Binomial(subyacente3_2,1,3,0,"recombinante")

tiempo1 = [80,120]
tiempo2 =[60,100,140]
tiempo3 = [40,80,120,160]

arbol_3_2.agregar_nivel(tiempo1)
arbol_3_2.agregar_nivel(tiempo2)
arbol_3_2.agregar_nivel(tiempo3)

for i in range(len(arbol_3_2.niveles)):
    print(arbol_3_2.niveles[i]) 
print()

probabilidades_3_2 = arbol_3_2.probabilidades_neutras_al_riesgo("continuo")
for i in range(len(probabilidades_3_2)):
    print(probabilidades_3_2[i])
print()

cobertura_3_2 = Cobertura(Call_3_2, arbol_3_2)
cobertura_3_2.calcular_cobertura("continuo", "cash or nothing", 100)

for i in range(len(cobertura_3_2.valores)):
    print(cobertura_3_2.valores[i])
    print()


# -------------------------------------- Pruebas Black Scholes ------------------------------------------------

print("BLACK_SCHOLES")
subyacente_2 = Subyacente(100)
contrato2 = Call(subyacente_2, 95, 1, 0, 0.05, "europeo","largo")

print(Black_Scholes(contrato2,0.2))
print()

subyacente_3 = Subyacente(100)
contrato3 = Call(subyacente_3, 105, 1, 0, 0.05, "europeo","corto")

print(Black_Scholes(contrato3,0.2))
print()



# -------------------------------------- Pruebas Opciones Americanas ------------------------------------------


print("OPCIONES AMERICANAS")

subyacente_4 = Subyacente(4)
contrato4 = Put(subyacente_4,5,1,2,0.25,"americana","largo")

arbol4 = Arbol_Binomial(subyacente_4,1,2,0.5625,"multiplicativo",2,0.5)
for i in range(len(arbol4.niveles)):
    print(arbol4.niveles[i]) 
print()

probabilidades_Arbol = arbol4.probabilidades_neutras_al_riesgo("discreto")
for i in range(len(probabilidades_Arbol)):
    print(probabilidades_Arbol[i])
print()

cobertura4 = Cobertura(contrato4,arbol4)
cobertura4.calcular_cobertura("discreto")

for i in range(len(cobertura4.valores)):
    print(cobertura4.valores[i])
print()

for i in range(len(cobertura4.alphas)):
    print(cobertura4.alphas[i])
print()

for i in range(len(cobertura4.alphas)):
    print(cobertura4.betas[i])
print()

for i in range(len(cobertura4.optimos)):
    print(cobertura4.optimos[i])
print()
