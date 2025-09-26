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
PORT = 56749  # 9559

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
    Lanza el script de imitación en Python 3 en un proceso separado.
    """
    bm = ALProxy("ALBehaviorManager", ROBOT_IP, PORT)
    tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)
    
    global proceso_imitacion
    python3_path = r"C:\Users\sover\anaconda3\envs\mi_entorno_310"
    script_path = r"C:\Users\sover\Desktop\SeminarioII\vision_computacional_NAO\Vision_comp.py"
    try:
        proceso_imitacion = subprocess.Popen([python3_path, script_path])
        # === INICIAR IMITACIÓN ===
        threading.Thread(target=ejecutar_programa_imitacion).start()
        # === INSTRUCCIONES DE IMITACIÓN ===
        imitacion_instrucciones = basicos[1]  # segundo behavior
        if bm.isBehaviorInstalled(imitacion_instrucciones):
            if bm.isBehaviorRunning(imitacion_instrucciones):
                bm.stopBehavior(imitacion_instrucciones)
            bm.runBehavior(imitacion_instrucciones)  # bloqueante, pero dentro del hilo
            while bm.isBehaviorRunning(imitacion_instrucciones):
                    time.sleep(0.5)
    except Exception as e:
        tkMessageBox.showerror("Error", "No se pudo iniciar el script:\n{}".format(e))


def detener_programa_imitacion():
    """
    Termina el script de imitación si sigue activo (versión Python 2.7).
    """
    global proceso_imitacion
    if proceso_imitacion and proceso_imitacion.poll() is None:
        try:
            proceso_imitacion.terminate()
            print("Script de imitación terminado con terminate().")
            
            #=== FIN DE LA SESIÓN ===
            bm = ALProxy("ALBehaviorManager", ROBOT_IP, PORT)
            despedida = basicos[2]  # tercer behavior
            if bm.isBehaviorInstalled(despedida):
                if bm.isBehaviorRunning(despedida):
                    bm.stopBehavior(despedida)
                bm.runBehavior(despedida)  # bloqueante, pero dentro del hilo
            while bm.isBehaviorRunning(despedida):
                    time.sleep(0.5)
    
        except Exception as e:
            print("No se pudo cerrar el script de imitación:", e)
    proceso_imitacion = None

##Este inicia todo el flujo del programa
def ejecutar_sesion(tiempo_total_min, rutina,nombre=""):
    """
    Maneja la sesión: saludo, ejercicios e inicia imitación.
    La despedida se ejecuta al terminar el temporizador.
    """
    if not rutina:
        tkMessageBox.showinfo("Info", "No hay ejercicios en la rutina para ejecutar.")
        return

    try:
        bm = ALProxy("ALBehaviorManager", ROBOT_IP, PORT)
        tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)
        posture = ALProxy("ALRobotPosture", ROBOT_IP, PORT)
        if nombre:
            tts.say("Hola {}, bienvenido a tu sesión de pausa activa".format(nombre))
        else:
            tts.say("Hola, bienvenido a tu sesión de pausa activa")

        # === SALUDO ===
        saludo = basicos[0]  # primer behavior
        if bm.isBehaviorInstalled(saludo):
            if bm.isBehaviorRunning(saludo):
                    bm.stopBehavior(saludo)
            bm.runBehavior(saludo)  # bloqueante, pero dentro del hilo
            while bm.isBehaviorRunning(saludo):
                    time.sleep(0.5)

        # === EJECUTAR RUTINA DE EJERCICIOS ===
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
                print("Repeticion {}".format(i + 1))
                #tts.say(str(i + 1))
                time.sleep(0.5)

            posture.goToPosture("StandInit", 0.5)
            tts.say("Has terminado {}".format(nombre))
            time.sleep(1)

    except Exception as e:
        tkMessageBox.showerror("Error", "No se pudo ejecutar la sesión:\n{}".format(e))
        detener_programa_imitacion()
        
