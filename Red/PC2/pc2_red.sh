#!/bin/bash

# PC2 - Configuración de VXLAN + BATMAN-adv

# DECLARAR INTERFAZ DE WIFI MANUALMENTE
WIFI_IFACE="wlan0"
# IP WiFi REAL de este PC
MY_WIFI_IP="10.0.0.2"
# IP de bat0 que tendrá este PC
MY_MESH_IP="10.10.0.2"

PEER_1_IP="10.0.0.1"   # PC1
PEER_2_IP="10.0.0.3"   # PC3
PEER_3_IP="10.0.0.4"   # PC4

# Activar módulo BATMAN
sudo modprobe batman_adv

sudo ip link add bat0 type batadv
sudo ip link set bat0 up

sudo ip link add vxlan1 type vxlan id 101 dev $IFACE local $MY_WIFI_IP remote $PEER_1_IP dstport 4789
sudo ip link set vxlan1 up
sudo batctl if add vxlan1

sudo ip link add vxlan2 type vxlan id 102 dev $IFACE local $MY_WIFI_IP remote $PEER_2_IP dstport 4789
sudo ip link set vxlan2 up
sudo batctl if add vxlan2

sudo ip link add vxlan3 type vxlan id 103 dev $IFACE local $MY_WIFI_IP remote $PEER_3_IP dstport 4789
sudo ip link set vxlan3 up
sudo batctl if add vxlan3

sudo ip addr add $MY_MESH_IP/24 dev bat0

echo "[PC2 LISTO] bat0 configurado con IP $MY_MESH_IP"