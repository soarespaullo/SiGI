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
