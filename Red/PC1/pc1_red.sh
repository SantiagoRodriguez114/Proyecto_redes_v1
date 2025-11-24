#!/bin/bash
# ---------------------------------------------------------
#   PC1 - Configuración de VXLAN + BATMAN-adv
# ---------------------------------------------------------

# DECLARAR INTERFAZ DE WIFI MANUALMENTE
WIFI_IFACE="wlan0"

# Activar módulo BATMAN
sudo modprobe batman_adv

# Crear interfaz BATMAN
sudo ip link add bat0 type batadv
sudo ip link set bat0 up

# VXLAN hacia PC2
sudo ip link add vxlan101 type vxlan id 101 remote 10.0.0.2 dev $WIFI_IFACE dstport 4789
sudo ip link set vxlan101 up
sudo batctl if add vxlan101

# VXLAN hacia PC3
sudo ip link add vxlan102 type vxlan id 102 remote 10.0.0.3 dev $WIFI_IFACE dstport 4789
sudo ip link set vxlan102 up
sudo batctl if add vxlan102

# VXLAN hacia PC4
sudo ip link add vxlan103 type vxlan id 103 remote 10.0.0.4 dev $WIFI_IFACE dstport 4789
sudo ip link set vxlan103 up
sudo batctl if add vxlan103

# IP mesh
sudo ip addr add 10.10.0.1/24 dev bat0

echo "[DONE] PC1 configurado."

