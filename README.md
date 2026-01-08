BitTorrent Swarm Simulation (P2P Distributed System)
📌 Descripción del Proyecto
Este proyecto es una emulación funcional de una red BitTorrent limitada, desarrollada para la unidad de aprendizaje de Sistemas Distribuidos. Implementa una arquitectura P2P Híbrida que permite la transferencia descentralizada de archivos de gran tamaño (min. 50 MB) mediante fragmentación y validación concurrente.




El sistema utiliza una red Overlay mediante Tailscale para emular un entorno de nube real, superando restricciones de NAT y permitiendo la comunicación entre nodos remotos .

🚀 Características Principales

Arquitectura Multihilo (Threading): Los nodos actúan como Seeder y Leecher de forma simultánea sin bloqueo de interfaz.



Integridad de Datos (SHA-1): Implementación del estándar BEP-0003; cada bloque de 512 KB es validado criptográficamente.



Tolerancia a Fallos (Checkpointing): Persistencia de estado mediante archivos JSON, permitiendo la reanudación de descargas (Resume) tras desconexiones.



Tracker Centralizado: Orquestador encargado del registro de nodos, búsqueda de archivos y monitoreo de la salud del enjambre (Swarm).


🛠️ Stack Tecnológico

Lenguaje: Python 3.x 


Comunicación: Sockets TCP 


Red: Tailscale (Mesh VPN) para emulación de Red Externa 


Serialización: JSON 

📐 Arquitectura del Sistema
El sistema separa estrictamente el Plano de Control (Señalización JSON con el Tracker) del Plano de Datos (Transferencia binaria P2P entre Peers) para optimizar el ancho de banda .

📦 Instalación y Uso
Clonar el repositorio:

Bash

git clone https://github.com/tu-usuario/bittorrent-simulation.git
cd bittorrent-simulation
Configurar Tailscale (Recomendado): Asegúrate de tener Tailscale activo en todos los nodos para obtener las IPs virtuales.

Ejecutar el Tracker:

Bash

python tracker.py
Ejecutar los Peers (mínimo 3):

Bash

python peer.py
📊 Visualización de Pruebas
El proyecto incluye un monitor de red en tiempo real que despliega:

Lista de nodos conectados y sus roles .

Archivos compartidos y en consumo por cada nodo .

Progreso porcentual de las descargas activas.


📜 Licencia
Este proyecto se distribuye bajo la licencia MIT.

🎓 Créditos

Alumno: Isaac Humberto Gámez Gress 


Profesor: Miguel Félix Mata Rivera 


Institución: Instituto Politécnico Nacional - UPIITA
