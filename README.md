🚀 BitTorrent- Swarm Simulation
Este proyecto es una implementación funcional y robusta del protocolo BitTorrent para sistemas distribuidos, desarrollada como proyecto final para la unidad de Sistemas Distribuidos en la UPIITA-IPN.

El sistema emula un enjambre (swarm) de nodos P2P que permite la transferencia eficiente, segura y resiliente de archivos de gran tamaño (mínimo 50 MB) sobre una red externa simulada.

🛠️ Características Técnicas
Arquitectura P2P Híbrida: Separación de planos; un Tracker central orquestador para señalización (JSON) y una red de Peers para transferencia binaria directa.

Concurrencia Real (Multithreading): Implementación de hilos independientes para permitir que un nodo actúe como Seeder y Leecher simultáneamente sin bloqueos.

Integridad BEP-0003 (SHA-1): Validación pieza por pieza (chunks de 512 KB) mediante hashes criptográficos para asegurar réplicas exactas bit a bit.

Tolerancia a Fallos & Resume: Mecanismo de checkpointing persistente que permite reanudar descargas y procesos de subida tras desconexiones inesperadas.

Red Overlay (Tailscale): Configurado para operar sobre una VPN Mesh, permitiendo comunicación entre nodos a través de redes externas y superando restricciones de NAT.

📂 Estructura del Proyecto
/tracker.py: Servidor de monitoreo y registro de nodos.

/peer.py: Lógica del nodo (Cliente/Servidor) con motor de integridad.

/Shared_X: Directorios de trabajo para simular la dispersión de datos.

/progress.json: Archivo de estado para persistencia y recuperación.

🚀 Cómo empezar
Red: Asegúrate de tener Tailscale activo o estar en la misma red local.

Lanzar el Orquestador:

Bash

python tracker.py
Lanzar los Nodos:

Bash

python peer.py
📊 Visualización
El sistema proporciona una interfaz de consola estructurada que muestra:

Lista de nodos activos y sus roles.

Archivos en consumo y progreso porcentual en tiempo real.

Logs de validación SHA-1 para cada fragmento recibido.

🎓 Créditos
Desarrollador: Isaac Humberto Gámez Gress

Profesor: Miguel Félix Mata Rivera

Institución: UPIITA - Instituto Politécnico Nacional
