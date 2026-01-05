#!/bin/bash
# Script para instalar e configurar mod_security e mod_evasive no Apache

set -e

echo "🔒 Instalando módulos de segurança..."
sudo apt update
sudo apt install -y libapache2-mod-security2 libapache2-mod-evasive

echo "✅ Ativando módulos..."
sudo a2enmod security2 evasive

echo "⚙️ Configurando mod_evasive..."
cat <<EOF | sudo tee /etc/apache2/mods-available/evasive.conf > /dev/null
<IfModule mod_evasive20.c>
    DOSHashTableSize    3097
    DOSPageCount        5
    DOSSiteCount        50
    DOSPageInterval     1
    DOSSiteInterval     1
    DOSBlockingPeriod   10
    DOSEmailNotify      admin@localhost
    DOSLogDir           "/var/log/mod_evasive"
</IfModule>
EOF

# Criar diretório de logs para mod_evasive
sudo mkdir -p /var/log/mod_evasive
sudo chown www-data:www-data /var/log/mod_evasive

echo "⚙️ Configurando mod_security..."
sudo cp /etc/modsecurity/modsecurity.conf-recommended /etc/modsecurity/modsecurity.conf
sudo sed -i 's/SecRuleEngine DetectionOnly/SecRuleEngine On/' /etc/modsecurity/modsecurity.conf

echo "🔄 Reiniciando Apache..."
sudo systemctl restart apache2

echo "✅ Configuração concluída!"
echo "Logs de ataques serão gravados em /var/log/apache2/error.log e /var/log/mod_evasive/"
