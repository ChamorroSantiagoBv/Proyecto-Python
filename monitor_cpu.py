import tkinter as tk
from tkinter import ttk
import psutil
import time
from threading import Thread
import configparser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# Leer archivo de configuración .ini
config = configparser.ConfigParser()
config.read('config.ini')

# Extraer parámetros de configuración
window_size = config['GENERAL']['window_size']
refresh_rate = config.getint('GENERAL', 'refresh_rate')
log_file_path = config['LOGGING']['log_file_path']
theme = config['INTERFACE']['theme']
cpu_monitor_enabled = config.getboolean('MONITORING', 'cpu_monitor_enabled')
cpu_usage_unit = config['MONITORING']['cpu_usage_unit']
graph_save_path = config['GRAPH']['graph_save_path']

# Crear directorios si no existen
if not os.path.exists(os.path.dirname(log_file_path)):
    os.makedirs(os.path.dirname(log_file_path))

if not os.path.exists(graph_save_path):
    os.makedirs(graph_save_path)

# Función para obtener el uso del CPU
def obtener_uso_cpu():
    return psutil.cpu_percent(interval=1)

# Función para actualizar el porcentaje del CPU en la interfaz y el gráfico
def actualizar_cpu():
    while ejecutar_hilo and cpu_monitor_enabled:
        cpu_uso = obtener_uso_cpu()
        cpu_label.config(text=f"Uso del CPU: {cpu_uso}{cpu_usage_unit}")
        guardar_registro(cpu_uso)
        # Añadir el nuevo valor al gráfico
        datos_cpu.append(cpu_uso)
        if len(datos_cpu) > 60:  # Mantener solo los últimos 60 segundos de datos
            datos_cpu.pop(0)
        actualizar_grafico()
        time.sleep(refresh_rate)

# Función para guardar el registro en un archivo de texto
def guardar_registro(cpu_uso):
    with open(log_file_path, "a") as f:
        tiempo_actual = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write(f"{tiempo_actual} - Uso del CPU: {cpu_uso}{cpu_usage_unit}\n")

# Función para actualizar el gráfico
def actualizar_grafico():
    linea.set_ydata(datos_cpu)
    linea.set_xdata(range(len(datos_cpu)))
    ax.relim()
    ax.autoscale_view()
    canvas.draw()

# Función para cerrar la ventana y detener el hilo de forma segura
def cerrar_ventana():
    global ejecutar_hilo
    ejecutar_hilo = False  # Detener el hilo
    ventana.destroy()  # Cerrar la ventana

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Monitoreo de CPU")
ventana.protocol("WM_DELETE_WINDOW", cerrar_ventana)  # Asociar cierre seguro al botón de cerrar

# Configurar tamaño de la ventana
width, height = map(int, window_size.split('x'))
ventana.geometry(f"{width}x{height}")

# Etiqueta para mostrar el porcentaje del CPU
cpu_label = ttk.Label(ventana, text=f"Uso del CPU: 0{cpu_usage_unit}", font=("Arial", 14))
cpu_label.pack(pady=20)

# Lista para almacenar los datos del CPU
datos_cpu = []

# Crear la figura de matplotlib para el gráfico
fig, ax = plt.subplots(figsize=(5, 2))
linea, = ax.plot(datos_cpu, label="Uso del CPU (%)")
ax.set_ylim(0, 100)
ax.set_ylabel(f"CPU ({cpu_usage_unit})")
ax.set_xlabel("Tiempo (s)")
ax.set_title("Uso del CPU en Tiempo Real")
ax.legend()

# Añadir el gráfico a la interfaz de Tkinter
canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas.get_tk_widget().pack()

# Variable global para controlar el hilo
ejecutar_hilo = True

# Iniciar un hilo para actualizar el porcentaje del CPU
hilo = Thread(target=actualizar_cpu)
hilo.daemon = True
hilo.start()

# Ejecutar la ventana
ventana.mainloop()
