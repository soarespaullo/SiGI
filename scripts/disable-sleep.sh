#!/bin/bash
# disable-sleep.sh
# Script para desativar suspensão e hibernação no Ubuntu Server

echo ">> Editando /etc/systemd/logind.conf..."
sudo sed -i 's/^#HandleSuspendKey=.*/HandleSuspendKey=ignore/' /etc/systemd/logind.conf
sudo sed -i 's/^#HandleHibernateKey=.*/HandleHibernateKey=ignore/' /etc/systemd/logind.conf
sudo sed -i 's/^#HandleLidSwitch=.*/HandleLidSwitch=ignore/' /etc/systemd/logind.conf

echo ">> Mascarando targets de suspensão/hibernação..."
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

echo ">> Reiniciando systemd-logind..."
sudo systemctl restart systemd-logind

echo ">> Concluído! Suspensão e hibernação foram desativadas."
