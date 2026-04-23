# Croop Backend

Backend da aplicação **Croop**, um sistema de monitoramento e irrigação automatizada de plantas com integração IoT e módulo de recomendação inteligente.

## Tecnologias utilizadas

- Python 3.11
- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy 2.0
- Alembic

## Sobre o projeto

O backend do Croop é responsável por centralizar a lógica de negócio do sistema, incluindo autenticação, gerenciamento de plantas, armazenamento de leituras de sensores, controle de dispositivos IoT, registro de irrigações, histórico de eventos, notificações e integração com o módulo de recomendação.

## Principais responsabilidades

- Gerenciar usuários e autenticação
- Gerenciar espécies e catálogo de plantas
- Registrar e consultar leituras de umidade
- Gerenciar dispositivos IoT, sensores e bombas d'água
- Registrar irrigações automáticas e manuais
- Armazenar histórico de cuidados
- Fornecer dados para recomendações e cronogramas

## Estrutura do banco de dados

As principais entidades modeladas no backend são:

- Usuario
- Especie
- Planta
- DispositivoIot
- SensorUmidade
- BombaDagua
- LeituraUmidade
- Irrigacao
- HistoricoCuidado
- RecomendacaoIA
- CronogramaCuidado
- ItemCronograma
- Notificacao
- VinculoPlantaDispositivo

## Configuração do ambiente

### 1. Clonar o repositório

```bash
git clone <repo-url>
cd croop-backend
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

### 3. Ativar o ambiente virtual

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 5. Criar o arquivo `.env`

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
APP_NAME="Croop API"
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000

DATABASE_URL=postgresql+psycopg://postgres:SENHA@localhost:5432/croop
SECRET_KEY=sua-chave-secreta
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Banco de dados

### Criar o banco PostgreSQL

```sql
CREATE DATABASE croop;
```

### Executar as migrations

```bash
alembic upgrade head
```

## Executando o projeto

Inicie o servidor de desenvolvimento com:

```bash
uvicorn app.main:app --reload
```

A aplicação ficará disponível em:

```text
http://127.0.0.1:8000
```

## Documentação da API

A documentação automática gerada pelo FastAPI pode ser acessada em:

```text
http://127.0.0.1:8000/docs
```

## Estrutura inicial do projeto

```text
croop-backend/
├── alembic/
├── app/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── tests/
├── .env
├── .env.example
├── alembic.ini
├── requirements.txt
└── README.md
```

## Estado atual do backend

Atualmente, o projeto já possui:

- conexão com PostgreSQL configurada
- migrations com Alembic funcionando
- modelagem inicial do banco implementada
- estrutura base do backend organizada

## Próximos passos

- Implementar schemas com Pydantic
- Criar endpoints da API
- Implementar autenticação
- Integrar leituras do dispositivo IoT
- Desenvolver a lógica de recomendação

## Observação

Este repositório corresponde apenas ao backend do sistema. O frontend mobile e o módulo IoT são mantidos separadamente.
