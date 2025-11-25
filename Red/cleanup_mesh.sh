#!/bin/bash

echo "==============================================="
echo "     LIMPIEZA COMPLETA DE RED MESH VXLAN + BATMAN"
echo "==============================================="


### ---------------------------------------------
### FUNCIONES DE APOYO
### ---------------------------------------------

delete_interface() {
    IFACE_NAME=$1
    if ip link show $IFACE_NAME > /dev/null 2>&1; then
        echo "[+] Eliminando interfaz $IFACE_NAME..."
        sudo ip link set $IFACE_NAME down 2>/dev/null
        sudo ip link delete $IFACE_NAME 2>/dev/null
    else
        echo "[i] $IFACE_NAME no existe, se omite."
    fi
}


### ---------------------------------------------
### ELIMINAR VXLANs (vxlan1, vxlan2, vxlan3)
### ---------------------------------------------

delete_interface vxlan1
delete_interface vxlan2
delete_interface vxlan3


### ---------------------------------------------
### ELIMINAR bat0
### ---------------------------------------------
if ip link show bat0 > /dev/null 2>&1; then
    echo "[+] Removiendo bat0…"
    sudo ip link set bat0 down 2>/dev/null

    # Intentar remover interfaces asociadas
    sudo batctl if del vxlan1 2>/dev/null
    sudo batctl if del vxlan2 2>/dev/null
    sudo batctl if del vxlan3 2>/dev/null

    sudo ip link delete bat0 type batadv 2>/dev/null
else
    echo "[i] bat0 no existe, se omite."
fi


### ---------------------------------------------
### LIMPIAR IPs (por si quedaron asignadas)
### ---------------------------------------------
echo "[+] Limpiando IPs residuales..."

sudo ip addr flush dev bat0 2>/dev/null
sudo ip addr flush dev vxlan1 2>/dev/null
sudo ip addr flush dev vxlan2 2>/dev/null
sudo ip addr flush dev vxlan3 2>/dev/null


echo ""
echo "==============================================="
echo "   LIMPIEZA FINALIZADA — SISTEMA RESTAURADO"
echo "==============================================="
echo "Ahora puedes volver a ejecutar tu script pcX_mesh.sh"
echo ""
