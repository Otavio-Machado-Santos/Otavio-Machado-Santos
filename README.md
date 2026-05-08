<div align="center">

# Otávio Machado Santos

### Analista de Observabilidade Pleno · DevOps & Automação · AI-Augmented Monitoring

📍 Araraquara/SP — Brasil &nbsp;|&nbsp; 💼 [Flowbix](https://flowbix.com.br) &nbsp;|&nbsp; 📧 otaviomachado2003@gmail.com

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/otávio-machado-santos)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Otavio-Machado-Santos)

</div>

---

## 🚀 Sobre mim

Sou especialista em **Observabilidade e Automação de Infraestrutura**, com foco em ambientes críticos corporativos. Trabalho na **Flowbix** desde 2022, desenvolvendo soluções de monitoramento aumentadas por IA — integrando Zabbix, Grafana e modelos de linguagem (LLMs) para correlação automática de alertas, detecção de anomalias e previsibilidade de falhas.

Tenho uma visão de **produto aplicada à infraestrutura**: dashboards como produto, monitoramento como serviço mensurável. Desenvolvo pipelines de automação complexos com Python e n8n, construo plugins Grafana customizados e implemento arquiteturas multi-agente em ambientes de produção.

- 🔭 Atualmente trabalhando em soluções de **AI-Augmented NOC** na Flowbix
- 🤖 Apaixonado pela interseção entre **IA generativa e operações de infraestrutura**
- ⚡ Stack principal: **Zabbix · Grafana · Python · n8n · LLMs · Docker · Kubernetes**
- 🎯 Aberto a projetos freelance em **observabilidade, automação e AI Ops**

---

## 🛠️ Stack Técnica

**Observabilidade**
![Zabbix](https://img.shields.io/badge/Zabbix-CC0000?style=flat-square&logo=zabbix&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat-square&logo=grafana&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat-square&logo=prometheus&logoColor=white)

**Automação & IA**
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-EA4B71?style=flat-square&logo=n8n&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![Shell Script](https://img.shields.io/badge/Shell_Script-4EAA25?style=flat-square&logo=gnu-bash&logoColor=white)
![PowerShell](https://img.shields.io/badge/PowerShell-5391FE?style=flat-square&logo=powershell&logoColor=white)

**DevOps & Cloud**
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazon-aws&logoColor=white)
![Azure](https://img.shields.io/badge/Azure-0078D4?style=flat-square&logo=microsoft-azure&logoColor=white)

**Infraestrutura**
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)
![Proxmox](https://img.shields.io/badge/Proxmox-E57000?style=flat-square&logo=proxmox&logoColor=white)
![VMware](https://img.shields.io/badge/VMware-607078?style=flat-square&logo=vmware&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat-square&logo=nginx&logoColor=white)

**Databases**
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![MariaDB](https://img.shields.io/badge/MariaDB-003545?style=flat-square&logo=mariadb&logoColor=white)

**Frontend / Plugins**
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)

---

## 🔥 Projetos em Destaque

### 🖥️ NOC AI Dashboard — Zabbix + Grafana + LLM
> Dashboard de NOC em tempo real com IA embarcada para análise automática de incidentes

- Pipeline **n8n** que consome dados de incidentes ativos do Zabbix, gera insights estruturados via LLM (score de severidade, flags de escalação, priorização por tier de cliente)
- Painel Grafana com **~1.200 linhas de JavaScript** customizado — lógica de priorização por severidade (Disaster → Information) e tier (Platinum, Gold, Silver)
- Redução significativa do **MTTR** por correlação automática de alertas

**Stack:** \`Zabbix\` \`Grafana\` \`n8n\` \`Python\` \`LLM\` \`JavaScript\` \`HTML\`

---

### 🤖 GrafanaAI Studio — Desktop App Multi-instância
> Aplicação desktop com agente de IA para edição e geração de dashboards Grafana de forma assistida

- Arquitetura por projeto: **1 projeto = 1 cliente = credenciais isoladas**
- Carregamento lazy de JSON de dashboards via **tool calls**
- Editor Monaco integrado para edição direta do JSON dos dashboards
- Integração com contexto de design sempre carregado, reduzindo overhead em operações de edição

**Stack:** \`Tauri\` \`Rust\` \`React\` \`TypeScript\` \`Monaco Editor\` \`Zustand\` \`Grafana API\` \`LLM\`

---

### 💬 Flowbix AI NOC Copilot — Agente LangChain em n8n
> Agente conversacional sobre base de incidentes ativos com queries dinâmicas geradas por LLM

- Regras de negócio embarcadas: **severidade, MTTR, ACK status, priorização por tier de cliente**
- Queries SQL dinâmicas geradas por LLM sobre MySQL de incidentes em tempo real

**Stack:** \`LangChain\` \`n8n\` \`MySQL\` \`Python\` \`Groq\`

---

## 📊 GitHub Stats

<div align="center">

![Otávio's GitHub Stats](https://github-readme-stats.vercel.app/api?username=Otavio-Machado-Santos&show_icons=true&theme=dark&hide_border=true&bg_color=0d1117&title_color=F46800&icon_color=F46800&text_color=ffffff)
![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username=Otavio-Machado-Santos&layout=compact&theme=dark&hide_border=true&bg_color=0d1117&title_color=F46800&text_color=ffffff)

</div>

---

## 🏆 Certificações

- 🐧 **Linux Essentials** — Linux Professional Institute (LPI) · Nov/2024
- 📊 **Tuning em Zabbix** — Flowbix · 2024

---

## 📬 Contato

Estou aberto a **projetos freelance**, **oportunidades CLT/PJ** e colaborações na área de observabilidade, automação e AI Ops.

[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:otaviomachado2003@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/otávio-machado-santos)

---

<div align="center">
  <sub>⚡ Transformando infraestrutura em produto com IA e automação</sub>
</div>
