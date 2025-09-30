# -*- coding: utf-8 -*-
import threading
import Tkinter as tk
import tkMessageBox
import json
import time
import subprocess
from naoqi import ALProxy

# Configuración del robot
ROBOT_IP = "localhost"  # Cambiar a la IP real del NAO
PORT = 50281  # 9559

# Cargar ejercicios desde JSON
with open("../actualizar robot/comportamientos.json", "r") as f:
    ejercicios = json.load(f)

rutina = []  # Lista de la rutina seleccionada
basicos = ["saludar-909889/BienvenidaTerapia", "imitacion-f5ffbe/behavior_1", "despedida-afd07c/behavior_1"]

arm_joints = [
    "RShoulderPitch",
    "RShoulderRoll",
    "RElbowYaw",
    "RElbowRoll",
    "RWristYaw"
]

# === Variable global para manejar el proceso de imitación ===
proceso_imitacion = None

def agregar_ejercicio(ejercicio, repeticiones, listbox, rutina):
    for item in rutina:
        if item["id"] == ejercicio["id"].encode('utf-8'):
            tkMessageBox.showinfo("Info", "Este ejercicio ya está en la rutina.")
            return
    item = {
        "id": ejercicio["id"].encode('utf-8'),
        "nombre": ejercicio["nombre"].encode('utf-8'),
        "descripcion": ejercicio["descripcion"].encode('utf-8'),
        "repeticiones": repeticiones
    }
    rutina.append(item)
    listbox.insert(tk.END, "%s (x%d)" % (item["nombre"], repeticiones))
    print("Agregado:", item["nombre"], "x", repeticiones)


def remover_ejercicio(listbox, rutina):
    seleccionado = listbox.curselection()
    if seleccionado:
        idx = seleccionado[0]
        eliminado = rutina.pop(idx)
        listbox.delete(idx)
        print("Eliminado:", eliminado["nombre"])
    else:
        tkMessageBox.showinfo("Info", "Selecciona un ejercicio para remover.")


def mostrar_rutina(rutina):
    if not rutina:
        tkMessageBox.showinfo("Info", "No hay ejercicios en la rutina.")
        return
    resumen = "\n".join(["- %s x%d" % (r["nombre"], r["repeticiones"]) for r in rutina])
    tkMessageBox.showinfo("Rutina Final", resumen)
    print("\n=== Rutina Final ===\n" + resumen)


def ejecutar_programa_imitacion():
    """
    Lanza el script de imitación en Python 3 y, en paralelo, 
    ejecuta las instrucciones en el robot.
    """
    bm = ALProxy("ALBehaviorManager", ROBOT_IP, PORT)
    tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)
    
    global proceso_imitacion
    python3_path = r"C:\Users\sover\anaconda3\envs\mi_entorno_310\python.exe"
    script_path = r"C:\Users\sover\Desktop\SeminarioII\vision_computacional_NAO\Vision_comp.py"
    
    try:
        # Lanza el script en Python 3 (en segundo plano)
        proceso_imitacion = subprocess.Popen([python3_path, script_path])
        
        # Al mismo tiempo corre las instrucciones en un hilo
        hilo_instrucciones = threading.Thread(
            target=ejecutar_instrucciones_imitacion,
            args=(bm,)
        )
        hilo_instrucciones.start()

    except Exception as e:
        print("Error", "No se pudo iniciar el script:\n{}".format(e))


def ejecutar_instrucciones_imitacion(bm):
    """
    Ejecuta el behavior de imitación en paralelo al script de visión.
    """
    imitacion_instrucciones = basicos[1]  # segundo behavior
    
    if bm.isBehaviorInstalled(imitacion_instrucciones):
        if bm.isBehaviorRunning(imitacion_instrucciones):
            bm.stopBehavior(imitacion_instrucciones)
        
        bm.runBehavior(imitacion_instrucciones)  # arranca
        while bm.isBehaviorRunning(imitacion_instrucciones):
            time.sleep(0.5)  # espera hasta que termine


def detener_programa_imitacion():
    """
    Termina el script de imitación si sigue activo (versión Python 2.7).
    Llama a despedida, luego lo sienta y reinicia el temporizador.
    """
    global proceso_imitacion

    def _hilo_finalizacion():
        try:
            if proceso_imitacion and proceso_imitacion.poll() is None:
                proceso_imitacion.terminate()
                print("Script de imitación terminado con terminate().")

            # === FIN DE LA SESIÓN ===
            bm = ALProxy("ALBehaviorManager", ROBOT_IP, PORT)
            pm = ALProxy("ALRobotPosture", ROBOT_IP, PORT)

            despedida = basicos[2]  # tercer behavior en tu lista
            if bm.isBehaviorInstalled(despedida):
                if bm.isBehaviorRunning(despedida):
                    bm.stopBehavior(despedida)
                bm.runBehavior(despedida)

                # Esperar que termine la despedida
                while bm.isBehaviorRunning(despedida):
                    time.sleep(0.5)

            # Pasar a sentado de manera estable
            #pm.goToPosture("Sit", 0.5)


        except Exception as e:
            print("Error en finalizar sesión:", e)

        # Liberar proceso
        proceso_imitacion = None

    # Lanzar en hilo para no bloquear Tkinter
    threading.Thread(target=_hilo_finalizacion, daemon=True).start()


##Este inicia todo el flujo del programa
def ejecutar_sesion(tiempo_total_min, rutina, nombre=""):
    """
    Maneja la sesión: saludo, ejercicios e inicia imitación.
    La despedida se ejecuta al terminar el temporizador.
    """
    try:
        bm = ALProxy("ALBehaviorManager", ROBOT_IP, PORT)
        tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)
        posture = ALProxy("ALRobotPosture", ROBOT_IP, PORT)

        # === SALUDO ===
        if nombre:
            tts.say("Hola {}, bienvenido a tu sesión de pausa activa".format(nombre))
        else:
            tts.say("Hola, bienvenido a tu sesión de pausa activa")

        saludo = basicos[0]  # primer behavior
        if bm.isBehaviorInstalled(saludo):
            if bm.isBehaviorRunning(saludo):
                bm.stopBehavior(saludo)
            bm.runBehavior(saludo)
            while bm.isBehaviorRunning(saludo):
                time.sleep(0.5)

        # === RUTINA DE EJERCICIOS O DIRECTO A IMITACIÓN ===
        if rutina:  # hay ejercicios
            for r in rutina:
                behavior_name = r["id"]
                repeticiones = r.get("repeticiones", 1)
                nombre = r.get("nombre", "ejercicio")

                if not bm.isBehaviorInstalled(behavior_name):
                    print("[!] No está instalado:", behavior_name)
                    continue

                tts.say("Listo. Iniciamos el ejercicio {}".format(nombre))
                time.sleep(0.5)

                for i in range(repeticiones):
                    bm.runBehavior(behavior_name)
                    print("Repetición {}".format(i + 1))
                    time.sleep(0.5)

                #posture.goToPosture("StandInit", 0.5)
                tts.say("Has terminado {}".format(nombre))
                time.sleep(1)
        else:  # no hay ejercicios
            tts.say("Hoy no haremos ejercicios. Vamos directo al juego de imitación.")
        
        # === INICIAR IMITACIÓN ===
        ejecutar_programa_imitacion()

    except Exception as e:
        tkMessageBox.showerror("Error", "No se pudo ejecutar la sesión:\n{}".format(e))
        detener_programa_imitacion()

def generar_rutina_default():
    """
    Genera rutina default:
    - Primer ejercicio 1 vez
    - Los demás con repeticiones fijas
    """
    rutina_default = []
    repeticiones_default = 8

    for idx, ejercicio in enumerate(ejercicios):
        repeticiones = 1 if idx == 0 else repeticiones_default
        rutina_default.append({
            "id": ejercicio["id"].encode('utf-8'),
            "nombre": ejercicio["nombre"].encode('utf-8'),
            "descripcion": ejercicio["descripcion"].encode('utf-8'),
            "repeticiones": repeticiones
        })
    return rutina_default


def iniciar_sesion_configurada(nombre=""):
    """
    Botón: usa la rutina armada por el usuario
    """
    tiempo_total = 10 * 60
    hilo = threading.Thread(
        target=lambda: ejecutar_sesion(tiempo_total, rutina, nombre)
    )
    hilo.setDaemon(True)
    hilo.start()


def iniciar_sesion_default(nombre=""):
    """
    Botón: genera rutina default y la ejecuta
    """
    tiempo_total = 10 * 60
    rutina_default = generar_rutina_default()
    hilo = threading.Thread(
        target=lambda: ejecutar_sesion(tiempo_total, rutina_default, nombre)
    )
    hilo.setDaemon(True)
    hilo.start()


