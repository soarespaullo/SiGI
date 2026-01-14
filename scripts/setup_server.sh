#!/bin/bash
# setup-server.sh
# Script para configurações iniciais do Ubuntu Server
# - Desativa suspensão e hibernação
# - Define fuso horário para America/Fortaleza

echo ">> Editando /etc/systemd/logind.conf..."
sudo sed -i 's/^#HandleSuspendKey=.*/HandleSuspendKey=ignore/' /etc/systemd/logind.conf
sudo sed -i 's/^#HandleHibernateKey=.*/HandleHibernateKey=ignore/' /etc/systemd/logind.conf
sudo sed -i 's/^#HandleLidSwitch=.*/HandleLidSwitch=ignore/' /etc/systemd/logind.conf

echo ">> Mascarando targets de suspensão/hibernação..."
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

echo ">> Reiniciando systemd-logind..."
sudo systemctl restart systemd-logind

echo ">> Configurando fuso horário para America/Fortaleza..."
sudo timedatectl set-timezone America/Fortaleza

echo ">> Concluído! Configurações iniciais aplicadas com sucesso."
