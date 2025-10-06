from Funciones_y_clases import B, Subyacente, Fordward, Call, Put, Arbol_Binomial, Cobertura

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
                tipo=None, posicion="corto")

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
arbol = Arbol_Binomial(120, 3, 3, r = 0.06, tipo = "multiplicativo", u = 1.7, d = 0.8)
for i in range(len(arbol.niveles)):
    print(arbol.niveles[i]) 
print()

probabilidades = arbol.probabilidades_neutras_al_riesgo("continuo")
for i in range(len(probabilidades)):
    print(probabilidades[i])


# ---------------------------------------- Pruebas Cobertura --------------------------------------------------

# Ejercicio 2 de la Sesión 4

print("COBERTURA")
contrato = Call(subyacente = 120,
                    strike = 115,
                    vencimiento = 3,
                    periodos = 3,
                    interes = 0.06,
                    tipo = "Europea",
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