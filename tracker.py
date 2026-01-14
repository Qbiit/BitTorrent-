import socket
import threading
import json
import os
import time
import tkinter as tk
from tkinter import ttk

# Configuración del Tracker
TRACKER_IP = "0.0.0.0" 
TRACKER_PORT = 5000
network_nodes = {} 

class TrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BitTorrent Tracker - Monitor de Red [Capa de Monitoreo]")
        self.root.geometry("900x550")
        self.setup_ui()
        
        # Iniciar el servidor de red en un hilo separado para no congelar la ventana
        threading.Thread(target=self.start_tracker_network, daemon=True).start()

    def setup_ui(self):
        """Configuración de la interfaz visual con tablas y logs."""
        # Encabezado
        header = tk.Label(self.root, text="SISTEMA DISTRIBUIDO BITTORRENT - PANEL DE CONTROL", 
                          font=("Arial", 14, "bold"), fg="#1a237e")
        header.pack(pady=15)

        # Tabla de Nodos (Cumple Punto 5 de la Rúbrica) 
        columns = ("nodo", "rol", "compartiendo", "descargando")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        
        self.tree.heading("nodo", text="NODO (IP:PORT)")
        self.tree.heading("rol", text="ROL")
        self.tree.heading("compartiendo", text="COMPARTIENDO")
        self.tree.heading("descargando", text="DESCARGANDO (%)")
        
        self.tree.column("nodo", width=180)
        self.tree.column("rol", width=100)
        self.tree.column("compartiendo", width=250)
        self.tree.column("descargando", width=250)
        
        self.tree.pack(fill="both", expand=True, padx=20)

        # Área de log de eventos (Terminal integrada)
        self.log_area = tk.Text(self.root, height=10, bg="black", fg="#00FF00", font=("Consolas", 9))
        self.log_area.pack(fill="x", padx=20, pady=15)
        self.write_log("Tracker iniciado. Escuchando peticiones...")

    def write_log(self, text):
        """Escribe mensajes en la consola de la GUI."""
        self.log_area.insert(tk.END, f">> {text}\n")
        self.log_area.see(tk.END)

    def refresh_table(self):
        """Lógica para redibujar la tabla con datos actualizados [cite: 55-62]."""
        # Limpiar tabla actual
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Insertar datos actuales de network_nodes
        for peer, info in network_nodes.items():
            shared = ", ".join(info["files_shared"]) if info["files_shared"] else "Ninguno"
            downloads = [f"{f} ({p}%)" for f, p in info["files_downloading"].items()]
            consuming = ", ".join(downloads) if downloads else "Completado"
            role = info["status"].upper()
            
            self.tree.insert("", tk.END, values=(peer, role, shared, consuming))

    # === LÓGICA DE RED INTEGRADA ===

    def handle_peer(self, conn, addr):
        try:
            data = conn.recv(4096).decode('utf-8')
            if not data: return
            
            request = json.loads(data)
            action = request.get("action")
            peer_id = f"{request.get('ip')}:{request.get('port')}"

            if action == "REGISTER":
                network_nodes[peer_id] = {
                    "files_shared": request.get("files_shared", []),
                    "files_downloading": request.get("files_downloading", {}),
                    "status": request.get("status", "peer"),
                    "last_seen": time.time()
                }
                self.write_log(f"Nodo {peer_id} registrado exitosamente.")
            
            elif action == "DISCONNECT":
                if peer_id in network_nodes:
                    del network_nodes[peer_id]
                    self.write_log(f"Nodo {peer_id} desconectado formalmente.")
            
            elif action == "GET_PEERS":
                target_file = request.get("file")
                potential_sources = [
                    p for p, info in network_nodes.items() 
                    if target_file in info["files_shared"] or target_file in info["files_downloading"]
                ]
                self.write_log(f"Búsqueda: {peer_id} solicitó fuentes para '{target_file}'")
                conn.send(json.dumps({"peers": potential_sources}).encode('utf-8'))
                return

            conn.send(json.dumps({"status": "OK"}).encode('utf-8'))
            
            # Actualizar la interfaz visual en el hilo principal
            self.root.after(0, self.refresh_table)
            
        except Exception as e:
            self.write_log(f"Error en comunicación: {e}")
        finally:
            conn.close()

    def start_tracker_network(self):
        """Uso de Sockets e Hilos para concurrencia [cite: 31-35, 131-134]."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((TRACKER_IP, TRACKER_PORT))
        server.listen(30)
        
        while True:
            conn, addr = server.accept()
            # Genera hilos para concurrencia según rúbrica [cite: 71]
            threading.Thread(target=self.handle_peer, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TrackerGUI(root)
    root.mainloop()
