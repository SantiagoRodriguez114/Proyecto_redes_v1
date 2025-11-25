#!/bin/bash
# ===========================================================
# PC3 - VXLAN + BATMAN ADV - CONFIGURACIÓN ESTABLE
# ===========================================================

WIFI_IFACE="wlo1"
MY_WIFI_IP="172.25.6.148"
MY_MESH_IP="10.10.0.3"

PEER_PC1="172.25.6.40"
PEER_PC2="172.25.10.100"
PEER_PC4="172.25.6.83"

echo "=== PC3 CONFIGURANDO MALLA ==="

sudo modprobe batman_adv

sudo ip link set bat0 down 2>/dev/null
sudo ip link delete bat0 2>/dev/null

sudo ip link add bat0 type batadv
sudo ip link set bat0 up

# PC3 <-> PC1 (101)
sudo ip link delete vxlan1 2>/dev/null
sudo ip link add vxlan1 type vxlan id 101 \
     local "$MY_WIFI_IP" remote "$PEER_PC1" \
     dev "$WIFI_IFACE" dstport 4789
sudo ip link set vxlan1 up
sudo batctl if add vxlan1

# PC3 <-> PC2 (104)
sudo ip link delete vxlan2 2>/dev/null
sudo ip link add vxlan2 type vxlan id 104 \
     local "$MY_WIFI_IP" remote "$PEER_PC2" \
     dev "$WIFI_IFACE" dstport 4789
sudo ip link set vxlan2 up
sudo batctl if add vxlan2

# PC3 <-> PC4 (106)
sudo ip link delete vxlan3 2>/dev/null
sudo ip link add vxlan3 type vxlan id 106 \
     local "$MY_WIFI_IP" remote "$PEER_PC4" \
     dev "$WIFI_IFACE" dstport 4789
sudo ip link set vxlan3 up
sudo batctl if add vxlan3

sudo ip addr flush dev bat0
sudo ip addr add $MY_MESH_IP/24 dev bat0

echo "=== PC3 LISTO ==="
