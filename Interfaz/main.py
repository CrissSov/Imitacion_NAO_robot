# -*- coding: utf-8 -*-
import Tkinter as tk
import json
import threading
from Interfaz import agregar_ejercicio, remover_ejercicio, mostrar_rutina, ejecutar_sesion, ejecutar_programa_imitacion,detener_programa_imitacion



root = tk.Tk()
root.title("Configurar Rutina de Pausa Activa")
root.geometry("600x500")
root.configure(bg="#f9f9f9")

# === Lista donde se guarda la rutina seleccionada ===
rutina = []

# Cargar ejercicios desde JSON
with open("../actualizar robot/comportamientos.json", "r") as f:
    ejercicios = json.load(f)

# --- Frame inicio ---
frame_inicio = tk.Frame(root, bg="#f9f9f9")
frame_inicio.pack(fill="both", expand=True)

tk.Label(frame_inicio, text="Bienvenido", font=("Arial", 16, "bold"), bg="#f9f9f9").pack(pady=20)
tk.Label(frame_inicio, text="Ingresa tu nombre:", font=("Arial", 12), bg="#f9f9f9").pack()

nombre_var = tk.StringVar()
tk.Entry(frame_inicio, textvariable=nombre_var, font=("Arial", 12), width=30).pack(pady=10)

tk.Label(frame_inicio, text="Tiempo total de rutina (minutos):", font=("Arial", 12), bg="#f9f9f9").pack()
tiempo_total_var = tk.IntVar(value=5)
tk.Spinbox(frame_inicio, from_=1, to=120, textvariable=tiempo_total_var, font=("Arial", 12), width=5).pack(pady=5)

def mostrar_rutina_frame():
    frame_inicio.pack_forget()
    titulo_label.config(text="Hola, {}. Configura tu rutina personalizada:".format(nombre_var.get()))
    frame_rutina.pack(fill="both", expand=True)

# === NUEVA FUNCIÓN PARA EL TEMPORIZADOR ===
def actualizar_temporizador(segundos_restantes):
    if segundos_restantes >= 0:
        minutos = segundos_restantes // 60
        segundos = segundos_restantes % 60
        temporizador_label.config(text="Tiempo restante: {:02}:{:02}".format(minutos, segundos))
        root.after(1000, actualizar_temporizador, segundos_restantes - 1)
    else:
        temporizador_label.config(text="¡Tiempo terminado!")
        detener_programa_imitacion()


def iniciar_sesion():
    tiempo_total = tiempo_total_var.get() * 60  # minutos → segundos
    actualizar_temporizador(tiempo_total)       # inicia contador visual
    hilo = threading.Thread(target=lambda: ejecutar_sesion(tiempo_total_var.get(), rutina,nombre_var.get()))
    hilo.setDaemon(True)  
    hilo.start()


tk.Button(frame_inicio, text="Continuar", command=mostrar_rutina_frame,
          font=("Arial", 12, "bold"), bg="#2d89ef", fg="white").pack(pady=20)

# --- Frame rutina ---
frame_rutina = tk.Frame(root, bg="#f9f9f9")

titulo_label = tk.Label(frame_rutina, text="Configura tu  rutina de hoy", font=("Arial", 14, "bold"), bg="#f9f9f9")
titulo_label.pack(pady=10)

# Lista ejercicios
for ejercicio in ejercicios:
    frame = tk.Frame(frame_rutina, bd=2, relief="groove", padx=10, pady=10, bg="#e6e6e6")
    frame.pack(fill="x", padx=10, pady=5)

    tk.Label(frame, text=ejercicio["nombre"], font=("Arial", 10, "bold"), bg="#e6e6e6").grid(row=0, column=0, sticky="w")
    tk.Label(frame, text=ejercicio["descripcion"], width=40, anchor="w", bg="white", relief="solid").grid(row=0, column=1, padx=5, sticky="w")

    spin = tk.Spinbox(frame, from_=1, to=20, width=5)
    spin.grid(row=1, column=0, sticky="w")

    tk.Button(frame, text="Agregar", bg="#2d89ef", fg="white",
              command=lambda e=ejercicio, s=spin: agregar_ejercicio(e, int(s.get()), listbox, rutina)).grid(row=1, column=2, padx=10)

# Lista seleccionados
frame_lista = tk.Frame(frame_rutina, bd=2, relief="ridge", padx=10, pady=10, bg="#f0f0f0")
frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

tk.Label(frame_lista, text="Rutina seleccionada:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w")

listbox = tk.Listbox(frame_lista, width=50, height=8)
listbox.pack(pady=5)

btns = tk.Frame(frame_lista, bg="#f0f0f0")
btns.pack()

# Label temporizador
temporizador_label = tk.Label(frame_rutina, text="Tiempo restante: 00:00", 
                              font=("Arial", 14, "bold"), bg="#f9f9f9", fg="black")
temporizador_label.pack(pady=10)

tk.Button(btns, text="Remover", command=lambda: remover_ejercicio(listbox, rutina),
          bg="red", fg="white").grid(row=0, column=0, padx=5)

tk.Button(btns, text="Mostrar", command=lambda: mostrar_rutina(rutina),
          bg="black", fg="white").grid(row=0, column=1, padx=5)

tk.Button(btns, text="Ejecutar en Robot",
          command=iniciar_sesion,
          bg="blue", fg="white").grid(row=0, column=2, padx=5)


tk.Button(btns, text="Iniciar Imitación",
          command=ejecutar_programa_imitacion,
          bg="green", fg="white").grid(row=0, column=3, padx=5)

root.mainloop()
