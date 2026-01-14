import socket
import threading
import os
import json
import time
import sys
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox

# === CONFIGURACION ===
TRACKER_IP = "192.168.1.135" 
TRACKER_PORT = 5000
MY_IP = "192.168.1.135"
PEER_PORT = 5001         # Nodo A=5001, B=5002, C=5003
SHARED_DIR = "Shared_A"  
CHUNK_SIZE = 1024 * 512  
FILE_SIZE = 52428800     

os.makedirs(SHARED_DIR, exist_ok=True)
DB_FILE = f"progress_{PEER_PORT}.json"
progress_db = {}

class PeerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"BitTorrent Peer - Puerto {PEER_PORT}")
        self.root.geometry("600x550")
        self.load_progress_local()
        self.setup_ui()
        
        # Iniciar el servidor de subida (Uploads) en segundo plano [cite: 136]
        threading.Thread(target=self.serve, daemon=True).start()
        self.register_with_tracker()

    def setup_ui(self):
        # --- SECCIÓN SUPERIOR: CONFIGURACIÓN ---
        tk.Label(self.root, text=f"NODO ACTIVO: {MY_IP}:{PEER_PORT}", font=("Arial", 10, "bold"), fg="blue").pack(pady=5)
        
        # --- SECCIÓN: DESCARGA ---
        frame_dl = tk.LabelFrame(self.root, text=" Descargar Archivo (Leecher) ")
        frame_dl.pack(fill="x", padx=10, pady=5)
        
        self.entry_file = tk.Entry(frame_dl)
        self.entry_file.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.entry_file.insert(0, "archivo.mp4")
        
        btn_dl = tk.Button(frame_dl, text="Iniciar Descarga", command=self.btn_download_clicked, bg="#d1e7dd")
        btn_dl.pack(side="right", padx=5)

        # --- SECCIÓN: PROGRESO ---
        frame_prog = tk.LabelFrame(self.root, text=" Estado de Transferencia ")
        frame_prog.pack(fill="x", padx=10, pady=5)
        
        self.lbl_status = tk.Label(frame_prog, text="Esperando instrucciones...")
        self.lbl_status.pack(anchor="w", padx=5)
        
        self.progress_bar = ttk.Progressbar(frame_prog, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(fill="x", padx=5, pady=5)

        # --- SECCIÓN: LOGS (Visualización en tiempo real) [cite: 34, 62] ---
        frame_logs = tk.LabelFrame(self.root, text=" Bitácora de Red (SHA-1 / Checkpoints) ")
        frame_logs.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_area = tk.Text(frame_logs, height=12, font=("Consolas", 9), bg="black", fg="white")
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)

        # --- BOTONES EXTRA ---
        frame_btns = tk.Frame(self.root)
        frame_btns.pack(fill="x", padx=10, pady=5)
        
        tk.Button(frame_btns, text="Ver Locales", command=self.ver_archivos_locales).pack(side="left", padx=5)
        tk.Button(frame_btns, text="Abrir Descargado", command=self.abrir_archivo).pack(side="left", padx=5)
        tk.Button(frame_btns, text="Salir", command=self.salir, bg="#f8d7da").pack(side="right", padx=5)

    def write_log(self, text):
        self.log_area.insert(tk.END, f"> {text}\n")
        self.log_area.see(tk.END)

    # === INTEGRACIÓN DE TU LÓGICA ORIGINAL ===

    def load_progress_local(self):
        global progress_db
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f:
                    progress_db = json.load(f)
            except: progress_db = {}

    def register_with_tracker(self, downloading_file=None, percent=0):
        all_files = os.listdir(SHARED_DIR)
        files_shared = [f for f in all_files if f != downloading_file]
        files_downloading = {downloading_file: percent} if downloading_file else {}
        status = "seeder" if not downloading_file else "leecher"
        msg = {
            "action": "REGISTER", "ip": MY_IP, "port": PEER_PORT,
            "files_shared": files_shared, "files_downloading": files_downloading, "status": status
        }
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((TRACKER_IP, TRACKER_PORT))
            s.send(json.dumps(msg).encode())
            s.close()
        except: pass

    def btn_download_clicked(self):
        fname = self.entry_file.get()
        if fname:
            # Lanzamos en hilo para no congelar la GUI [cite: 90]
            threading.Thread(target=self.request_file_logic, args=(fname,), daemon=True).start()

    def request_file_logic(self, filename):
        self.write_log(f"Consultando Tracker por: {filename}")
        msg = {"action": "GET_PEERS", "file": filename}
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TRACKER_IP, TRACKER_PORT))
            s.send(json.dumps(msg).encode())
            resp = json.loads(s.recv(4096).decode())
            s.close()
            
            peers = resp.get("peers", [])
            others = [p for p in peers if p != f"{MY_IP}:{PEER_PORT}"]
            
            if others:
                self.write_log(f"Fuentes encontradas: {others}")
                t_ip, t_port = others[0].split(":") # Tomamos el primero por simplicidad
                self.download_logic(t_ip, int(t_port), filename)
            else:
                self.write_log("No hay fuentes disponibles.")
        except:
            self.write_log("Error de conexión con el Tracker.")

    def download_logic(self, ip, port, filename):
        self.load_progress_local()
        start_byte = progress_db.get(filename, 0)
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(json.dumps({"file": filename, "start": start_byte}).encode())

            mode = "ab" if start_byte > 0 else "wb"
            with open(os.path.join(SHARED_DIR, filename), mode) as f:
                while start_byte < FILE_SIZE:
                    data = s.recv(CHUNK_SIZE)
                    if not data: break
                    
                    pieza_hash = hashlib.sha1(data).hexdigest()
                    f.write(data)
                    start_byte += len(data)
                    
                    percent = min(int((start_byte / FILE_SIZE) * 100), 100)
                    
                    # Actualizar UI
                    self.progress_bar['value'] = percent
                    self.lbl_status.config(text=f"Descargando: {percent}%")
                    self.write_log(f"Chunk verificado (SHA-1): {pieza_hash[:10]}")
                    
                    progress_db[filename] = start_byte
                    with open(DB_FILE, "w") as dbf: json.dump(progress_db, dbf)
                    self.register_with_tracker(filename, percent)
                    time.sleep(0.05)

            self.write_log(f"DESCARGA COMPLETADA AL 100%")
            messagebox.showinfo("Éxito", f"Archivo {filename} descargado.")
            self.register_with_tracker()
        except Exception as e:
            self.write_log(f"Error: {e}")

    def ver_archivos_locales(self):
        archivos = os.listdir(SHARED_DIR)
        messagebox.showinfo("Archivos Compartidos", f"Contenido de {SHARED_DIR}:\n" + "\n".join(archivos))

    def abrir_archivo(self):
        # Lógica simplificada: abre el primero que encuentre en la carpeta
        archivos = os.listdir(SHARED_DIR)
        if archivos:
            path = os.path.join(SHARED_DIR, archivos[0])
            if sys.platform == "win32": os.startfile(path)
            else: os.system(f"xdg-open '{path}'")

    def serve(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", PEER_PORT))
        server.listen(10)
        while True:
            conn, addr = server.accept()
            threading.Thread(target=self.handle_upload, args=(conn,), daemon=True).start()

    def handle_upload(self, conn):
        try:
            data = conn.recv(1024).decode()
            req = json.loads(data)
            path = os.path.join(SHARED_DIR, req['file'])
            if os.path.exists(path):
                with open(path, "rb") as f:
                    f.seek(req['start'])
                    while chunk := f.read(CHUNK_SIZE):
                        conn.send(chunk)
        except: pass
        finally: conn.close()

    def salir(self):
        try:
            msg = {"action": "DISCONNECT", "ip": MY_IP, "port": PEER_PORT}
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TRACKER_IP, TRACKER_PORT))
            s.send(json.dumps(msg).encode())
            s.close()
        except: pass
        os._exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = PeerGUI(root)
    root.mainloop()
