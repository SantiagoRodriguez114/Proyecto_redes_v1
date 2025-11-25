#!/bin/bash
# ===========================================================
# PC1 - VXLAN + BATMAN ADV - CONFIGURACIÓN ESTABLE
# ===========================================================

WIFI_IFACE="wlo1"
MY_WIFI_IP="172.25.6.40"
MY_MESH_IP="10.10.0.1"

PEER_PC2="172.25.10.100"
PEER_PC3="172.25.6.148"
PEER_PC4="172.25.6.83"

echo "=== PC1 CONFIGURANDO MALLA ==="

sudo modprobe batman_adv

# Reiniciar bat0 limpio
sudo ip link set bat0 down 2>/dev/null
sudo ip link delete bat0 2>/dev/null

sudo ip link add bat0 type batadv
sudo ip link set bat0 up

# -------------------------------
# VXLAN 1 <-> PC2  (VNI 101)
# -------------------------------
sudo ip link delete vxlan1 2>/dev/null
sudo ip link add vxlan1 type vxlan id 101 \
     local "$MY_WIFI_IP" remote "$PEER_PC2" \
     dev "$WIFI_IFACE" dstport 4789
sudo ip link set vxlan1 up
sudo batctl if add vxlan1

# -------------------------------
# VXLAN 2 <-> PC3 (VNI 102)
# -------------------------------
sudo ip link delete vxlan2 2>/dev/null
sudo ip link add vxlan2 type vxlan id 102 \
     local "$MY_WIFI_IP" remote "$PEER_PC3" \
     dev "$WIFI_IFACE" dstport 4789
sudo ip link set vxlan2 up
sudo batctl if add vxlan2
