from Funciones_y_clases import B, Subyacente, Derivado, Fordward

# --------------------------------------- Pruebas Fordward ---------------------------------------------------


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
    exotico=None,
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
    exotico=None,
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


# --------------------------------------- Pruebas Opciones ---------------------------------------------------


