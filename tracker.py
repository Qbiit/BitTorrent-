import socket
import threading
import json
import os
import time

# Configuracion del Tracker
TRACKER_IP = "0.0.0.0" 
TRACKER_PORT = 5000
network_nodes = {} 
NODE_TIMEOUT = 15 # Segundos antes de considerar a un nodo "desconectado" [cite: 81]

def handle_peer(conn, addr):
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
        
        # NUEVA ACCION: Cierre explicito del nodo
        elif action == "DISCONNECT":
            if peer_id in network_nodes:
                del network_nodes[peer_id]
                print(f"\n[!] AVISO: Nodo {peer_id} se ha desconectado formalmente.")
                time.sleep(1) # Breve pausa para que se vea el mensaje antes de limpiar pantalla
        
        elif action == "GET_PEERS":
            target_file = request.get("file")
            potential_sources = [
                p for p, info in network_nodes.items() 
                if target_file in info["files_shared"] or target_file in info["files_downloading"]
            ]
            conn.send(json.dumps({"peers": potential_sources}).encode('utf-8'))
            return

        conn.send(json.dumps({"status": "OK"}).encode('utf-8'))
    except: pass
    finally:
        conn.close()
        display_network_status()

def display_network_status():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "="*85)
    print("SISTEMA DISTRIBUIDO BITTORRENT - MONITOR DE RED (TRACKER) [Capa Monitoreo]")
    print(f"Instrucción: Presione Ctrl+C o cierre la ventana para salir")
    print("-" * 85)
    print(f"{'NODO (IP:PORT)':<20} | {'ROL':<10} | {'COMPARTIENDO':<20} | {'DESCARGANDO (%)'}")
    print("-" * 85)
    
    if not network_nodes:
        print(f"{' ':^30}ESPERANDO CONEXIONES...")
    
    for peer, info in network_nodes.items():
        shared = ", ".join(info["files_shared"]) if info["files_shared"] else "Ninguno"
        downloads = [f"{f} ({p}%)" for f, p in info["files_downloading"].items()]
        consuming = ", ".join(downloads) if downloads else "Completado"
        role = info["status"].upper()
        
        print(f"{peer:<20} | {role:<10} | {shared:<20} | {consuming}")
    print("="*85 + "\n")

def start_tracker():
    # Uso de Sockets e Hilos para concurrencia segun rubrica
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Evita error de socket ocupado
    server.bind((TRACKER_IP, TRACKER_PORT))
    server.listen(30) # Capacidad de hasta 30 conexiones simultaneas
    
        
    print(f"[*] Capa de Monitoreo activa en puerto {TRACKER_PORT}...")
    while True:
        try:
            conn, addr = server.accept()
            # Genera hilos por cada conexión para evitar colapsos
            threading.Thread(target=handle_peer, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\nCerrando Tracker...")
            break

if __name__ == "__main__":
    start_tracker()