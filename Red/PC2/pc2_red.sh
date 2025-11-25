#!/bin/bash
# ===========================================================
# PC2 - VXLAN + BATMAN ADV - CONFIGURACIÓN ESTABLE
# ===========================================================

# AJUSTA SOLO ESTAS VARIABLES
WIFI_IFACE="wlp2s0"           # interfaz WiFi real del PC2
MY_WIFI_IP="172.25.10.100"    # IP física del WiFi de PC2
MY_MESH_IP="10.10.0.2"        # IP Mesh (bat0) del nodo 2

PEER_PC1="172.25.6.40"        # PC1
PEER_PC3="172.25.6.148"       # PC3
PEER_PC4="172.25.6.83"        # PC4

echo "==============================================="
echo "     PC2 - Configurando VXLAN + BATMAN"
echo "==============================================="
echo "[INFO] WIFI_IFACE = $WIFI_IFACE"
echo "[INFO] MY_WIFI_IP = $MY_WIFI_IP"
echo "[INFO] MY_MESH_IP = $MY_MESH_IP"

### Comprobar interfaz WiFi
if ! ip link show "$WIFI_IFACE" &>/dev/null; then
  echo "[ERROR] La interfaz $WIFI_IFACE no existe."
  exit 1
fi

echo "[+] Cargando módulo batman_adv..."
sudo modprobe batman_adv

### Reiniciar bat0 si existe
if ip link show bat0 &>/dev/null; then
  echo "[i] Eliminando bat0 anterior..."
  sudo ip link set bat0 down 2>/dev/null
  sudo ip link delete bat0 2>/dev/null
fi

### Crear bat0 limpio
echo "[+] Creando bat0..."
sudo ip link add bat0 type batadv
sudo ip link set bat0 up


# -----------------------------------------------------------
# VXLAN PC2 ↔ PC1 (ID 101)
# -----------------------------------------------------------
echo "[+] Creando VXLAN1 PC2 <-> PC1..."

if ip link show vxlan1 &>/dev/null; then
  sudo ip link delete vxlan1 2>/dev/null
fi

sudo ip link add vxlan1 type vxlan id 101 \
     local "$MY_WIFI_IP" remote "$PEER_PC1" \
     dev "$WIFI_IFACE" dstport 4789

sudo ip link set vxlan1 up
sudo batctl if add vxlan1


# -----------------------------------------------------------
# VXLAN PC2 ↔ PC3 (ID 104)
# -----------------------------------------------------------
echo "[+] Creando VXLAN2 PC2 <-> PC3..."

if ip link show vxlan2 &>/dev/null; then
  sudo ip link delete vxlan2 2>/dev/null
fi

sudo ip link add vxlan2 type vxlan id 104 \
     local "$MY_WIFI_IP" remote "$PEER_PC3" \
     dev "$WIFI_IFACE" dstport 4789

sudo ip link set vxlan2 up
sudo batctl if add vxlan2


# -----------------------------------------------------------
# VXLAN PC2 ↔ PC4 (ID 105)
# -----------------------------------------------------------
echo "[+] Creando VXLAN3 PC2 <-> PC4..."

if ip link show vxlan3 &>/dev/null; then
  sudo ip link delete vxlan3 2>/dev/null
fi

sudo ip link add vxlan3 type vxlan id 105 \
     local "$MY_WIFI_IP" remote "$PEER_PC4" \
     dev "$WIFI_IFACE" dstport 4789

sudo ip link set vxlan3 up
sudo batctl if add vxlan3


# -----------------------------------------------------------
# Asignar IP a la malla
# -----------------------------------------------------------
echo "[+] Asignando IP mesh $MY_MESH_IP a bat0..."

sudo ip addr flush dev bat0
sudo ip addr add "$MY_MESH_IP"/24 dev bat0

echo "==============================================="
echo " PC2 LISTO — bat0 con IP $MY_MESH_IP"
echo "==============================================="
