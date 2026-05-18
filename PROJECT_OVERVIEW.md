# PROJECT_OVERVIEW.md — Croop Backend

## 1. Visão Geral

Backend da plataforma Croop, um sistema de gerenciamento de plantas com suporte a
automação via dispositivos IoT, monitoramento de umidade, irrigação automatizada,
cronogramas de cuidado e recomendações geradas por IA.

A API é construída em FastAPI, exposta via Uvicorn, persiste dados no PostgreSQL
via SQLAlchemy 2.0 e gerencia o schema do banco com Alembic.

Estado atual: em desenvolvimento ativo. O modelo de dados está completo (14 tabelas
migradas), mas apenas as entidades Usuario e Planta possuem endpoints funcionais.

---

## 2. Stack

| Componente        | Tecnologia                      | Versão     |
|-------------------|---------------------------------|------------|
| Framework HTTP    | FastAPI                         | 0.136.0    |
| Servidor ASGI     | Uvicorn                         | 0.46.0     |
| ORM               | SQLAlchemy                      | 2.0.49     |
| Banco de dados    | PostgreSQL                      | —          |
| Driver DB         | psycopg2-binary                 | 2.9.12     |
| Migrations        | Alembic                         | 1.18.4     |
| Validação         | Pydantic v2                     | 2.13.3     |
| Configuração      | pydantic-settings               | 2.14.0     |
| Autenticação      | python-jose (JWT) + bcrypt      | 3.5.0 / 5.0.0 |
| Lint              | Ruff                            | 0.15.12    |
| Testes            | pytest                          | 9.0.3      |
| CI/CD             | GitHub Actions                  | —          |

---

## 3. Arquitetura do Sistema

O backend segue uma arquitetura em camadas:

```
HTTP Request
    └── Router (app/routers/)
            └── Dependency Injection (get_db, get_current_user)
                    └── Service (app/services/)  ← camada prevista, ainda vazia
                            └── CRUD (app/crud/)
                                    └── Model SQLAlchemy (app/models/)
                                            └── PostgreSQL
                                                    └── Response via Pydantic Schema
```

**Camadas presentes:**
- **Routers** — recebem HTTP, validam via schema, chamam CRUD ou lógica inline
- **Schemas** — definem contratos de entrada e saída (Pydantic v2)
- **CRUD** — operações atômicas de banco, sem lógica de negócio
- **Models** — mapeamento ORM das tabelas PostgreSQL
- **Core** — configuração, segurança e dependências reutilizáveis

**Camada prevista mas não implementada:**
- **Services** — `app/services/` existe mas está vazio; deve conter regras de negócio

---

## 4. Estrutura de Pastas

```
croop-backend/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # lint + testes em PRs e pushs
│       └── auto-pr.yml               # criação automática de PRs
├── alembic/
│   ├── env.py                        # configuração Alembic (injeta DATABASE_URL via settings)
│   ├── script.py.mako                # template de migration
│   └── versions/
│       ├── 75c1d7e6291f_*.py         # CREATE TABLE usuarios
│       ├── 6a7d3a6b98de_*.py         # CREATE TABLE especies
│       ├── 0bdcada56da3_*.py         # CREATE TABLE plantas
│       └── 070a46c0ce90_*.py         # CREATE TABLE 11 tabelas restantes
├── app/
│   ├── core/
│   │   ├── config.py                 # Settings via pydantic-settings (lê .env)
│   │   ├── deps.py                   # get_current_user (dependency JWT)
│   │   └── security.py               # hash bcrypt + geração/verificação JWT
│   ├── crud/
│   │   └── planta.py                 # create, get, list, update, delete de Planta
│   ├── db/
│   │   ├── base.py                   # re-exporta Base (para Alembic)
│   │   ├── init_db.py                # vazio (reservado para seed futuro)
│   │   └── session.py                # engine + SessionLocal + get_db()
│   ├── models/
│   │   ├── __init__.py               # registra todos os 14 modelos (crítico para Alembic)
│   │   ├── usuario.py
│   │   ├── especie.py
│   │   ├── planta.py
│   │   ├── dispositivo_iot.py
│   │   ├── sensor_umidade.py
│   │   ├── bomba_dagua.py
│   │   ├── vinculo_planta_dispositivo.py
│   │   ├── leitura_umidade.py
│   │   ├── irrigacao.py
│   │   ├── historico_cuidado.py
│   │   ├── recomendacao_ia.py
│   │   ├── cronograma_cuidado.py
│   │   ├── item_cronograma.py
│   │   └── notificacao.py
│   ├── routers/
│   │   ├── health.py                 # GET /health
│   │   ├── db_test.py                # GET /db-test
│   │   ├── usuarios.py               # POST /usuarios/cadastro, /login
│   │   └── planta.py                 # CRUD /plantas/
│   ├── schemas/
│   │   ├── usuario.py                # UsuarioCadastroRequest/Response, TokenResponse
│   │   └── planta.py                 # PlantaCreate, PlantaUpdate, PlantaResponse
│   ├── services/                     # vazio — reservado para lógica de negócio
│   ├── utils/                        # vazio
│   └── main.py                       # instância FastAPI + inclusão de routers
├── tests/                            # vazio — sem testes implementados
├── .env.example
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── ruff.toml
```

---

## 5. Principais Módulos

### `app/main.py`
Ponto de entrada da aplicação. Instancia o `FastAPI` com título lido de `settings.app_name`
e registra os quatro routers ativos. Não tem middleware configurado.

### `app/core/config.py`
Singleton `settings` carregado uma vez na inicialização. Usa `pydantic-settings` para
ler variáveis do `.env`. O campo `database_url` é obrigatório — a aplicação falha na
inicialização se ausente.

### `app/core/security.py`
Centraliza autenticação: `hash_senha` (bcrypt), `verificar_senha`, `criar_token` (JWT HS256)
e `verificar_token`. **Atenção:** `SECRET_KEY` está hardcoded neste arquivo como
`"senha_aleatoria_token1234"`, ignorando `settings.secret_key`.

### `app/core/deps.py`
Define `get_current_user` como FastAPI dependency. Decodifica o JWT via `python-jose`
e retorna o payload como `dict`. Usado como `Depends(get_current_user)` nos endpoints
protegidos.

### `app/db/session.py`
Cria o `engine` SQLAlchemy 2.0 e a `SessionLocal`. Define `Base` (DeclarativeBase).
`get_db()` é um generator que abre sessão por request e garante fechamento no `finally`.

### `app/models/__init__.py`
Importa todos os 14 modelos e define `__all__`. Este arquivo é crítico: sem ele,
o `alembic/env.py` não registra as tabelas no `Base.metadata` e o autogenerate quebra.

### `app/crud/planta.py`
Único arquivo CRUD implementado. Operações: `create_planta`, `get_planta`,
`get_plantas`, `update_planta`, `delete_planta`. Recebe `db: Session` como parâmetro
e não contém lógica de negócio — apenas acesso ao banco.

---

## 6. Fluxos Principais

### 6.1 Cadastro de Usuário — `POST /usuarios/cadastro`

```
1. Request body → UsuarioCadastroRequest
   - Pydantic valida: senha ≥6 chars, maiúscula, minúscula, número, sem espaços
   - Confirma senha == confirmacao_senha
   - Confirma senha != email

2. Handler (routers/usuarios.py)
   - db.query(Usuario).filter(email == dados.email) → verifica duplicata
   - Se existir: HTTP 409 Conflict

3. Instancia Usuario com senha_hash = bcrypt(senha)
   - db.add() → db.commit() → db.refresh()

4. Retorna UsuarioCadastroResponse (id, nome, email, data_cadastro)
   HTTP 201 Created
```

### 6.2 Login — `POST /usuarios/login`

```
1. Request body → UsuarioLoginRequest (email + senha)

2. Handler (routers/usuarios.py)
   - db.query(Usuario).filter(email) → busca usuário
   - Se não encontrar: HTTP 401
   - bcrypt.checkpw(senha, senha_hash)
   - Se inválida: HTTP 401

3. criar_token({"sub": email}) → JWT assinado com SECRET_KEY hardcoded
   ACCESS_TOKEN_EXPIRE_MINUTES = 60

4. Retorna TokenResponse {"access_token": "...", "token_type": "bearer"}
```

### 6.3 CRUD de Plantas — `POST /plantas/` (autenticado)

```
1. Header: Authorization: Bearer <token>
   → get_current_user decodifica JWT → retorna payload dict

2. Request body → PlantaCreate
   - Pydantic valida: id_especie obrigatório, ambiente obrigatório

3. Handler (routers/planta.py)
   → crud.create_planta(db, data, user["sub"])
   ⚠️  ATENÇÃO: código atual usa user.id_usuario (AttributeError em runtime)

4. crud/planta.py
   - instancia Planta(**data.model_dump(), id_usuario=user_id)
   - db.add() → db.commit() → db.refresh()

5. Retorna PlantaResponse (from_attributes=True serializa ORM → dict)
   HTTP 201 Created
```

---

## 7. Configuração do Banco de Dados

Variáveis lidas do `.env` (ver `.env.example`):

```
DATABASE_URL=postgresql://postgres:SENHA@localhost:5432/croop?client_encoding=utf8
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=60
APP_NAME=Croop API
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
```

O `DATABASE_URL` é o único campo sem valor padrão — a aplicação não inicializa sem ele.
`SECRET_KEY` tem default `"change-me"` mas **não é lido por `security.py`** (bug ativo).

---

## 8. Alembic e Migrations

### Configuração

O `alembic.ini` tem `sqlalchemy.url` vazio intencionalmente. A URL é injetada em
`alembic/env.py` via:

```python
config.set_main_option("sqlalchemy.url", settings.database_url)
```

Isso garante que a URL nunca esteja hardcoded no repositório.

O `env.py` importa `app.models` antes de definir `target_metadata`, registrando todas
as 14 tabelas no `Base.metadata` para suporte ao autogenerate.

### Cadeia de Migrations

```
(base)
  └── 75c1d7e6291f — CREATE TABLE usuarios
        └── 6a7d3a6b98de — CREATE TABLE especies
              └── 0bdcada56da3 — CREATE TABLE plantas
                    └── 070a46c0ce90 — CREATE TABLE dispositivo_iot, bomba_dagua,
                                       cronograma_cuidado, historico_cuidado,
                                       notificacao, recomendacao_ia, sensor_umidade,
                                       vinculo_planta_dispositivo, irrigacao,
                                       item_cronograma, leitura_umidade
                                       + ALTER TABLE plantas (ativa → nullable)
```

Todas as migrations possuem `downgrade()` implementado.

### Comandos essenciais

```bash
# Aplicar migrations pendentes
alembic upgrade head

# Gerar nova migration a partir dos models
alembic revision --autogenerate -m "descricao"

# Reverter última migration
alembic downgrade -1

# Ver histórico
alembic history
```

**Regra:** todo novo model deve ser adicionado em `app/models/__init__.py` antes de
executar `--autogenerate`.

---

## 9. Padrões Identificados

### Schemas Pydantic (padrão a manter)

```python
class EntidadeBase(BaseModel):        # campos compartilhados
class EntidadeCreate(EntidadeBase):   # campos de criação (herda base)
class EntidadeUpdate(BaseModel):      # todos Optional (atualização parcial)
class EntidadeResponse(EntidadeBase): # saída, com from_attributes = True
    id_entidade: int
    data_cadastro: datetime
    class Config:
        from_attributes = True
```

### CRUD por entidade (padrão a manter)

```python
# app/crud/<entidade>.py
def create_<entidade>(db: Session, data: EntidadeCreate, ...) -> Entidade
def get_<entidade>(db: Session, id: int, ...) -> Entidade | None
def get_<entidades>(db: Session, ...) -> list[Entidade]
def update_<entidade>(db: Session, obj: Entidade, data: EntidadeUpdate) -> Entidade
def delete_<entidade>(db: Session, obj: Entidade) -> None
```

### Models SQLAlchemy 2.0 (padrão a manter)

```python
from app.db.session import Base  # importar sempre de session, não de base

class Entidade(Base):
    __tablename__ = "entidades"
    id_entidade: Mapped[int] = mapped_column(primary_key=True, index=True)
    campo: Mapped[str] = mapped_column(String(100), nullable=False)
    campo_opcional: Mapped[str | None] = mapped_column(String(100), nullable=True)
```

### Relacionamentos com TYPE_CHECKING (padrão a manter)

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.outra import Outra

class Entidade(Base):
    filhos: Mapped[list["Outra"]] = relationship(back_populates="pai")
```

### Endpoints protegidos (padrão a manter)

```python
@router.get("/", response_model=list[EntidadeResponse])
def listar(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return crud.get_entidades(db, user_id)
```

---

## 10. Integrações Previstas

As integrações a seguir são inferidas exclusivamente da estrutura de models e tabelas
presentes no banco. Nenhuma integração está implementada nos endpoints até o momento.

### 10.1 Frontend Mobile

- Consome a API REST via JWT (Bearer token)
- Fluxo: cadastro → login → token → chamadas autenticadas
- Endpoints funcionais: `/usuarios/cadastro`, `/usuarios/login`, CRUD `/plantas/`
- Endpoints previstos pelos models: espécies, dispositivos, notificações, cronogramas

### 10.2 Dispositivo IoT

Evidenciado pelos models:
- `DispositivoIot` — registro do hardware (código de série, status, WiFi, localização)
- `SensorUmidade` — sensor físico vinculado ao dispositivo
- `BombaDagua` — atuador de irrigação vinculado ao dispositivo
- `LeituraUmidade` — série temporal de leituras do sensor
- `Irrigacao` — registro de cada evento de irrigação (manual ou automático)
- `VinculoPlantaDispositivo` — associação N:N entre plantas e dispositivos

O campo `origem_decisao` em `Irrigacao` e `origem_evento` em `HistoricoCuidado`
sugerem que o sistema diferenciará irrigações manuais (app), automáticas (IoT) e
recomendadas (IA).

### 10.3 Módulo de IA / Recomendação

Evidenciado pelo model `RecomendacaoIA`:
- `tipo_recomendacao` — categoria da recomendação
- `descricao_recomendacao` — texto gerado
- `nivel_prioridade` — urgência (String 20)
- `status_recomendacao` — ciclo de vida da recomendação
- `justificativa` — raciocínio do modelo

O model `Especie` contém `faixa_umidade_min`, `faixa_umidade_max` e
`frequencia_media_irrigacao` — parâmetros que alimentariam o módulo de IA para avaliar
se a umidade atual está adequada e recomendar irrigação.

---

## 11. Pontos Críticos

### Bug de runtime — autenticação de plantas

`routers/planta.py` usa `user.id_usuario`, mas `get_current_user` retorna um `dict`
Python (payload do JWT), não um objeto com atributos. O token é criado com
`{"sub": email}` — sem `id_usuario`. **Todos os endpoints de `/plantas/` lançam
`AttributeError` em runtime.**

Correção necessária: incluir `id_usuario` no payload do token na criação, e acessar
via `user["id_usuario"]` no handler.

### SECRET_KEY desconectado da configuração

`security.py` define `SECRET_KEY = "senha_aleatoria_token1234"` como literal hardcoded.
`settings.secret_key` do `.env` nunca é lido para JWT. Trocar o valor no `.env` não
tem efeito.

### Lógica de banco no router de usuários

`routers/usuarios.py` faz queries, instancia models e chama commit diretamente, sem
passar por `crud/` ou `services/`. Viola a separação de camadas e dificulta testes.

---

## 12. Riscos Técnicos e Arquiteturais

| Risco | Severidade | Localização |
|-------|------------|-------------|
| `user.id_usuario` inexiste no payload JWT | **Crítico** | `routers/planta.py:19,28,38,55,69` |
| `SECRET_KEY` hardcoded ignorando `.env` | **Crítico** | `core/security.py:14` |
| Sem validação de FK ao criar planta (IntegrityError vira HTTP 500) | Alto | `crud/planta.py:6` |
| CPF sem validação de formato ou dígito verificador | Alto | `schemas/usuario.py` |
| `datetime.utcnow()` depreciado (Python 3.12+) | Médio | `core/security.py:21` |
| Sem CORS configurado | Médio | `main.py` |
| Sem paginação em listagens | Médio | `routers/planta.py:23` |
| Lógica de banco inline no router de usuários | Médio | `routers/usuarios.py` |
| Importação inconsistente de `Base` nos models | Baixo | models de IoT vs. core |
| `GET /db-test` sem autenticação expõe erros internos | Baixo | `routers/db_test.py` |
| CI passa com zero testes (`pytest \|\| exit 5`) | Baixo | `.github/workflows/ci.yml` |
| `app/models/placeholder.py` vazio | Baixo | `app/models/placeholder.py` |

---

## 13. Endpoints Existentes

### Autenticação (`/usuarios`)

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/usuarios/cadastro` | Não | Cadastra novo usuário |
| POST | `/usuarios/login` | Não | Autentica e retorna JWT |
| GET | `/usuarios/protegido` | Bearer | Rota de teste de autenticação |

#### POST `/usuarios/cadastro`
**Request body:**
```json
{
  "nome": "string",
  "cpf": "string",
  "email": "user@example.com",
  "senha": "string",
  "confirmacao_senha": "string"
}
```
**Regras de senha:** mínimo 6 chars, 1 maiúscula, 1 minúscula, 1 número, sem espaços, diferente do email.

**Response 201:**
```json
{
  "id_usuario": 1,
  "nome": "string",
  "email": "user@example.com",
  "data_cadastro": "2024-01-01T00:00:00"
}
```
**Erros:** `409` e-mail já cadastrado.

---

#### POST `/usuarios/login`
**Request body:**
```json
{
  "email": "user@example.com",
  "senha": "string"
}
```
**Response 200:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```
**Erros:** `401` credenciais inválidas.

---

#### GET `/usuarios/protegido`
**Header:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "mensagem": "Você está autenticado!",
  "user": { "sub": "email@example.com", "id_usuario": 1 }
}
```

---

### Plantas (`/plantas`) — todos requerem autenticação

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/plantas/` | Bearer | Cria nova planta |
| GET | `/plantas/` | Bearer | Lista plantas do usuário autenticado |
| GET | `/plantas/{planta_id}` | Bearer | Detalha uma planta |
| PUT | `/plantas/{planta_id}` | Bearer | Atualiza uma planta |
| DELETE | `/plantas/{planta_id}` | Bearer | Remove uma planta |

**Header obrigatório em todos:** `Authorization: Bearer <token>`

#### POST `/plantas/`
**Request body:**
```json
{
  "id_especie": 1,
  "ambiente": "string",
  "nome_personalizado": "string (opcional)",
  "porte": "string (opcional)",
  "localizacao_descricao": "string (opcional)",
  "observacoes": "string (opcional)",
  "ativa": true
}
```
**Response 201:**
```json
{
  "id_planta": 1,
  "id_usuario": 1,
  "id_especie": 1,
  "ambiente": "string",
  "nome_personalizado": "string",
  "porte": "string",
  "localizacao_descricao": "string",
  "observacoes": "string",
  "ativa": true,
  "data_cadastro": "2024-01-01T00:00:00"
}
```

---

#### GET `/plantas/`
**Response 200:** array de `PlantaResponse` (mesmo schema acima).

---

#### GET `/plantas/{planta_id}`
**Response 200:** `PlantaResponse`.
**Erros:** `404` planta não encontrada.

---

#### PUT `/plantas/{planta_id}`
**Request body (todos opcionais):**
```json
{
  "nome_personalizado": "string",
  "porte": "string",
  "ambiente": "string",
  "localizacao_descricao": "string",
  "observacoes": "string",
  "ativa": true
}
```
**Response 200:** `PlantaResponse` atualizado.
**Erros:** `404` planta não encontrada.

---

#### DELETE `/plantas/{planta_id}`
**Response:** `204 No Content`.
**Erros:** `404` planta não encontrada.

---

### Utilitários

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/health` | Não | Verifica se a API está rodando |
| GET | `/db-test` | Não | Verifica conexão com o banco de dados |

#### GET `/health`
**Response 200:** `{ "status": "ok" }`

#### GET `/db-test`
**Response 200:** `{ "status": "connected" }` ou `{ "status": "error", "detail": "..." }`

---

## 14. Recomendações para Futuras Sessões

### Correções imediatas (antes de qualquer nova feature)

1. **Corrigir o payload JWT:** adicionar `id_usuario` ao token em `criar_token()` e
   atualizar `routers/planta.py` para acessar `user["id_usuario"]`

2. **Conectar `SECRET_KEY` ao `.env`:** substituir o literal em `security.py` por
   `from app.core.config import settings` e usar `settings.secret_key`

3. **Criar `crud/usuario.py`:** mover as queries de `routers/usuarios.py` para um
   módulo CRUD dedicado

### Padrões a seguir em novas implementações

4. **Todo novo model → registrar em `app/models/__init__.py`** antes de gerar migration

5. **Todo endpoint novo → schema Create + Update + Response separados** no arquivo
   `schemas/<entidade>.py` correspondente

6. **Todo endpoint que retorna lista → implementar paginação** (limit/offset ou cursor)

7. **Capturar `IntegrityError`** nos CRUDs que recebem FKs de entrada do usuário,
   retornando HTTP 422 com mensagem clara em vez de HTTP 500

8. **Importar `Base` sempre de `app.db.session`** nos novos models (padronizar o que
   já existe nos models de IoT)

### Infraestrutura

9. **Adicionar `CORSMiddleware`** em `main.py` antes de integrar com o frontend mobile

10. **Implementar testes** — ao menos testes de integração para os fluxos de cadastro,
    login e CRUD de plantas; o CI já está configurado para rodar pytest

11. **Implementar `app/services/`** antes de adicionar lógica que envolva múltiplas
    entidades (ex.: criar planta + vincular dispositivo + iniciar cronograma)
