#!/bin/bash
# ===========================================================
# PC4 - VXLAN + BATMAN ADV - CONFIGURACIÓN ESTABLE
# ===========================================================

WIFI_IFACE="wlp2s0"
MY_WIFI_IP="172.25.6.83"
MY_MESH_IP="10.10.0.4"

PEER_PC1="172.25.6.40"
PEER_PC2="172.25.10.100"
PEER_PC3="172.25.6.148"

echo "=== PC4 CONFIGURANDO MALLA ==="

sudo modprobe batman_adv

sudo ip link set bat0 down 2>/dev/null
sudo ip link delete bat0 2>/dev/null

sudo ip link add bat0 type batadv
sudo ip link set bat0 up

# PC4 <-> PC1 (103)
sudo ip link delete vxlan1 2>/dev/null
sudo ip link add vxlan1 type vxlan id 103 \
     local "$MY_WIFI_IP" remote "$PEER_PC1" \
     dev "$WIFI_IFACE" dstport 4789
sudo ip link set vxlan1 up
sudo batctl if add vxlan1

# PC4 <-> PC2 (105)
sudo ip link delete vxlan2 2>/dev/null
sudo ip link add vxlan2 type vxlan id 105 \
     local "$MY_WIFI_IP" remote "$PEER_PC2" \
     dev "$WIFI_IFACE" dstport 4789
sudo ip link set vxlan2 up
sudo batctl if add vxlan2

# PC4 <-> PC3 (106)
sudo ip link delete vxlan3 2>/dev/null
sudo ip link add vxlan3 type vxlan id 106 \
     local "$MY_WIFI_IP" remote "$PEER_PC3" \
     dev "$WIFI_IFACE" dstport 4789
sudo ip link set vxlan3 up
sudo batctl if add vxlan3

sudo ip addr flush dev bat0
sudo ip addr add $MY_MESH_IP/24 dev bat0

echo "=== PC4 LISTO ==="
