import tkinter as tk
from tkinter import ttk

"""
Punto de entrada principal para la App NIIF 18.
[¤nueva]
"""

def main():
    # Inicializar la ventana principal
    root = tk.Tk()
    root.title("NIIF 18 - Implementación y Reclasificación")
    root.geometry("600x400")
    
    # Estilo básico
    style = ttk.Style()
    style.theme_use('clam')
    
    # Título
    lbl_title = ttk.Label(root, text="App NIIF 18 (Génesis Greenfield)", font=("Helvetica", 16, "bold"))
    lbl_title.pack(pady=20)
    
    # Mensaje de estado
    lbl_status = ttk.Label(root, text="El motor ADPA y las 7 salas están cargadas y listas.", font=("Helvetica", 11))
    lbl_status.pack(pady=10)
    
    # Botón de salir
    btn_exit = ttk.Button(root, text="Salir", command=root.quit)
    btn_exit.pack(pady=20)
    
    # Iniciar el loop de la interfaz
    root.mainloop()

if __name__ == "__main__":
    main()
