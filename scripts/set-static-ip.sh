#!/bin/bash
# set-static-ip.sh
# Script para configurar IP fixo no Ubuntu Server usando Netplan

# === CONFIGURAÇÕES ===
INTERFACE="ens33"              # Nome da interface de rede (use `ip a` para descobrir)
STATIC_IP="192.168.1.100/24"   # IP fixo com máscara
GATEWAY="192.168.1.1"          # Gateway padrão
DNS="8.8.8.8,8.8.4.4"          # Servidores DNS

# === GERAR ARQUIVO NETPLAN ===
NETPLAN_FILE="/etc/netplan/static-network.yaml"

echo ">> Criando configuração Netplan em $NETPLAN_FILE..."
sudo tee $NETPLAN_FILE > /dev/null <<EOL
network:
  version: 2
  renderer: networkd
  ethernets:
    $INTERFACE:
      dhcp4: no
      addresses: [$STATIC_IP]
      gateway4: $GATEWAY
      nameservers:
        addresses: [$DNS]
EOL

# === APLICAR CONFIGURAÇÃO ===
echo ">> Aplicando configuração Netplan..."
sudo netplan apply

echo ">> Concluído! IP fixo configurado em $INTERFACE como $STATIC_IP"
