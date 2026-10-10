def media(valores):
    if not valores:
        raise ValueError("La lista no puede estar vacía")
    return sum(valores) / len(valores)