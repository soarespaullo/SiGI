# ✝️ SiGI – Sistema de Gestão Integrada para Igrejas

O **SiGI** é uma aplicação web desenvolvida em **Flask** com o objetivo de apoiar **igrejas evangélicas** na administração de suas atividades.  
Ele nasceu do desejo de ajudar congregações que não têm condições de adquirir sistemas pagos, oferecendo uma solução gratuita, simples e eficiente para organizar a vida administrativa da igreja.

---

## 🎯 Propósito
- Facilitar a gestão de igrejas evangélicas.  
- Oferecer uma ferramenta acessível para comunidades com poucos recursos.  
- Centralizar informações administrativas em um único sistema.  

---

## 🚀 Recursos principais
- 🔒 **Autenticação e segurança** com controle de acesso por papéis.  
- 👥 **Gestão de membros**: cadastro e acompanhamento de fiéis.  
- 📅 **Eventos**: criação e gerenciamento de atividades da igreja.  
- 💰 **Financeiro**: controle de entradas e saídas, relatórios básicos.  
- 🏠 **Patrimônio**: registro e acompanhamento dos bens da igreja.  
- 📊 **Dashboard**: visão geral com indicadores e atalhos.  
- 📧 **Integração com e-mail**: envio de notificações e comunicados.  
- 📂 **Uploads**: armazenamento de documentos e arquivos.  

---

## 🛠️ Tecnologias utilizadas
- **Backend:** Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Mail, Flask-WTF  
- **Banco de Dados:** MySQL (produção) / SQLite (desenvolvimento)  
- **Configuração:** Variáveis de ambiente com `python-dotenv`  
- **Servidor:** Apache + mod_wsgi (produção)  
- **Frontend:** Jinja2 templates + Bootstrap  

---

## ⚙️ Diferenciais
- Estrutura modular com **Blueprints** (auth, dashboard, eventos, financeiro, membros, patrimônio).  
- Segurança integrada (CSRF, senhas com hash).  
- Migrações de banco com **Flask-Migrate**.  
- Deploy simplificado em **Ubuntu Server**.  

---

## 🤝 Como contribuir
O **SiGI** nasceu com o propósito de ajudar igrejas evangélicas que não têm condições de investir em sistemas pagos.  
Se você deseja apoiar esse projeto, existem várias formas de contribuir:

- Reportar problemas abrindo uma **issue**.  
- Sugerir melhorias e novos módulos (ex.: escola bíblica, ministérios, relatórios).  
- Contribuir com código via **pull requests**.  
- Melhorar a documentação e tutoriais.  
- Divulgar o projeto para outras igrejas que possam se beneficiar.  

---

## 📜 Código de conduta
Este projeto segue princípios de respeito e colaboração.  
Todas as contribuições devem ser feitas com espírito de serviço, lembrando que o objetivo é **abençoar igrejas e comunidades**.


# 🚀 Guia de Deploy – SiGI (Flask + Apache + MySQL)

---

## 1. Instalar dependências

```
sudo apt update
sudo apt install apache2 libapache2-mod-wsgi-py3 python3-venv python3-pip mysql-server -y
sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info -y
```

- Clonar repositório:

```
sudo git clone https://github.com/soarespaullo/SiGI.git /var/www/sigi ; cd /var/www/sigi
```

## 2. Configurar MySQL

```
sudo mysql -u root -p
CREATE DATABASE sigi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sigi_user'@'localhost' IDENTIFIED BY 'sigi_password';
GRANT ALL PRIVILEGES ON sigi_db.* TO 'sigi_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

- Testar conexão:

```
mysql -u sigi_user -p sigi_db
```

> ⚠️ utf8mb4 garante suporte a acentos e emojis.


## 3. Ajustar .env

```
 sudo mv .env.example .env
```

- No arquivo /var/www/sigi/.env:

```
DATABASE_URL="mysql+pymysql://sigi_user:sigi_password@localhost:3306/sigi_db"
```

## 4. Configurar SECRET_KEY

- Gerar chave:

```
python3 -c "import secrets; print(secrets.token_hex(32))"
```

- Adicionar no .env:

```
env
SECRET_KEY="sua_chave_gerada"
```

## 5. Configurar ambiente virtual

- No diretório do projeto:

```
sudo chown $USER:$USER /var/www/sigi

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Permissões:

```
sudo mkdir -p /var/www/sigi/app/static/uploads
sudo chown -R www-data:www-data /var/www/sigi/app/static/uploads
sudo chmod -R 775 /var/www/sigi/app/static/uploads
```

## 6. Configurar Apache

- Mova o arquivo de configuração:

```
sudo mv sigi.conf /etc/apache2/sites-available/sigi.conf
```

- Ativar site e módulos:

```
sudo a2ensite sigi.conf
sudo a2dissite 000-default.conf 
sudo a2enmod wsgi
sudo systemctl restart apache2
```

## 7. Habilitar HTTPS (Certbot)

```
sudo apt install certbot python3-certbot-apache -y
sudo certbot --apache -d sigi.seudominio.com
```

> 🔒 Configura automaticamente HTTPS com Let’s Encrypt.


## Proteger .env:

```
sudo chown www-data:www-data /var/www/sigi/.env
sudo chmod 600 /var/www/sigi/.env
```

## 8. Criar e aplicar as migrations

- Inicializar o diretório de migrations (se ainda não existir):

```
flask db init
```

- Isso cria a pasta migrations/ no projeto.

- Criar as migrations a partir dos modelos definidos:

```
flask db migrate -m "Inicializando tabelas"
```

- Aplicar as migrations no banco de dados:

```
flask db upgrade
```

 - Reiniciar Apache:
 
```
sudo systemctl restart apache2
```

## 9. Testar aplicação

- Acesse:

```
http://sigi.seudominio.com
```
# ou

```
http://localhost
```

- Ver logs:

```
sudo tail -f /var/log/apache2/sigi_error.log
```

## 🔄 Rollback de migrations (se necessário)

- Voltar uma migration:

```
flask db downgrade -1
```

- Voltar para uma versão específica:

```
flask db downgrade <id_da_migration>
```

- Resetar completamente (estado inicial, sem tabelas):

```
flask db downgrade base
```

- Reaplicar depois de corrigir:

```
flask db migrate -m "Correção de tabelas"
```

```
flask db upgrade
```
