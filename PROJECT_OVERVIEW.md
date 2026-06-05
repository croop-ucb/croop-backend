# PROJECT_OVERVIEW.md — Croop Backend

Atualizado em junho de 2026 com base na análise do código real.

---

## 1. Visão Geral

Backend da plataforma Croop, um sistema de gerenciamento de plantas com suporte a
automação via dispositivos IoT, monitoramento de umidade, irrigação automatizada,
cronogramas de cuidado e recomendações geradas por IA.

A API é construída em FastAPI, exposta via Uvicorn, persiste dados no PostgreSQL
via SQLAlchemy 2.0 e gerencia o schema do banco com Alembic.

**Estado atual:** em desenvolvimento ativo. O modelo de dados está completo (14 tabelas
migradas). Endpoints funcionais cobrem usuários, plantas, espécies, notificações,
histórico de cuidados e motor de eventos. A camada de services tem implementações
reais para notificações e eventos de sensor.

---

## 2. Stack

| Componente        | Tecnologia                      | Versão        |
|-------------------|---------------------------------|---------------|
| Framework HTTP    | FastAPI                         | 0.136.0       |
| Servidor ASGI     | Uvicorn                         | 0.46.0        |
| ORM               | SQLAlchemy                      | 2.0.49        |
| Banco de dados    | PostgreSQL                      | —             |
| Driver DB         | psycopg2-binary                 | 2.9.12        |
| Migrations        | Alembic                         | 1.18.4        |
| Validação         | Pydantic v2                     | 2.13.3        |
| Configuração      | pydantic-settings               | 2.14.0        |
| Autenticação      | python-jose (JWT) + bcrypt      | 3.5.0 / 5.0.0 |
| Lint              | Ruff                            | 0.15.12       |
| Testes            | pytest                          | 9.0.3         |
| CI/CD             | GitHub Actions                  | —             |

---

## 3. Arquitetura do Sistema

O backend segue uma arquitetura em camadas:

```
HTTP Request
    └── Router (app/routers/)
            └── Dependency Injection (get_db, get_current_user)
                    └── Service (app/services/)  ← parcialmente implementado
                            └── CRUD (app/crud/)
                                    └── Model SQLAlchemy (app/models/)
                                            └── PostgreSQL
                                                    └── Response via Pydantic Schema
```

**Camadas presentes:**
- **Routers** — recebem HTTP, validam via schema, chamam CRUD ou lógica inline
- **Schemas** — definem contratos de entrada e saída (Pydantic v2)
- **CRUD** — operações atômicas de banco, sem lógica de negócio (apenas `crud/planta.py`)
- **Models** — mapeamento ORM das 14 tabelas PostgreSQL
- **Core** — configuração, segurança e dependências reutilizáveis
- **Services** — parcialmente implementado: `evento_notificacao_service.py` e `notificacao_service.py`

**Inconsistência de camadas:**
- `routers/usuarios.py` faz queries diretas ao banco sem passar por `crud/` ou `services/`
- `routers/planta.py` mistura CRUD (via `crud/`) com lógica de irrigação inline no endpoint `/irrigar`
- `routers/historico.py` agrega dados de três tabelas diretamente no handler

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
│   │   ├── usuarios.py               # POST /usuarios/cadastro, /login, GET /protegido
│   │   ├── planta.py                 # CRUD /plantas/ + POST /plantas/{id}/irrigar
│   │   ├── especie.py                # GET /especies/ com busca por nome
│   │   ├── notificacao.py            # GET /notificacoes/ — BUG: user.id_usuario
│   │   ├── eventos.py                # POST /eventos/sensor — BUG: user.id_usuario
│   │   └── historico.py              # GET /historico/ com paginação
│   ├── schemas/
│   │   ├── usuario.py                # UsuarioCadastroRequest/Response, TokenResponse
│   │   ├── planta.py                 # PlantaCreate, PlantaUpdate, PlantaResponse
│   │   ├── especie.py                # EspecieResponse
│   │   ├── notificacao.py            # NotificacaoResponse
│   │   └── historico.py              # HistoricoResponse (com paginação)
│   ├── services/
│   │   ├── notificacao_service.py    # gerar_notificacao + deduplicação 30min (RN-011)
│   │   └── evento_notificacao_service.py  # processar_evento_sensor (UC-009)
│   ├── utils/                        # vazio
│   └── main.py                       # instância FastAPI + CORSMiddleware + routers
├── tests/                            # vazio — sem testes implementados
├── .env.example
├── alembic.ini
├── pytest.ini
└── ruff.toml
```

---

## 5. Principais Módulos

### `app/main.py`
Instancia o `FastAPI` com título de `settings.app_name` e registra todos os routers.
`CORSMiddleware` está configurado permitindo `http://localhost:8081` (Expo dev server).
Para produção, `allow_origins` precisa ser atualizado com as origens reais.

### `app/core/config.py`
Singleton `settings` carregado na inicialização via `pydantic-settings`. O campo
`database_url` é obrigatório — a aplicação falha se ausente.

### `app/core/security.py`
Centraliza autenticação: `hash_senha` (bcrypt), `verificar_senha`, `criar_token` (JWT HS256)
e `verificar_token`. **Bug ativo:** `SECRET_KEY` hardcoded como `"senha_aleatoria_token1234"`,
ignorando `settings.secret_key` do `.env`. Trocar o `.env` não tem efeito algum.
`datetime.utcnow()` é usado aqui — depreciado no Python 3.12+.

### `app/core/deps.py`
Define `get_current_user` como FastAPI dependency. Decodifica o JWT e retorna o
payload como `dict`. O token contém `{"sub": email, "id_usuario": int}`.

### `app/crud/planta.py`
Único arquivo CRUD implementado. Operações: `create_planta`, `get_planta`,
`get_plantas`, `update_planta`, `delete_planta`. Recebe `db: Session` como parâmetro
sem lógica de negócio.

### `app/services/notificacao_service.py`
Implementa `gerar_notificacao` com deduplicação: verifica se existe notificação do
mesmo tipo para o mesmo usuário/planta nos últimos 30 minutos antes de criar (RN-011).

### `app/services/evento_notificacao_service.py`
Motor de eventos do UC-009: recebe leitura do sensor e dispara notificações por
regras fixas (`umidade < 30` → irrigar; `umidade > 80` → excesso; `sensor_ok=False`
→ falha de sensor). Os limiares são hardcoded — não consultam `faixa_umidade_min/max`
da espécie.

---

## 6. Fluxos Principais

### 6.1 Cadastro de Usuário — `POST /usuarios/cadastro`

```
1. Request body → UsuarioCadastroRequest
   - Pydantic valida: senha ≥6 chars, maiúscula, minúscula, número, sem espaços
   - Confirma senha == confirmacao_senha, senha != email

2. Handler (routers/usuarios.py) — lógica de banco inline (sem crud/)
   - Verifica e-mail duplicado → HTTP 409 se existir
   - Instancia Usuario com senha_hash = bcrypt(senha)
   - db.add() → db.commit() → db.refresh()

3. Retorna UsuarioCadastroResponse (id, nome, email, data_cadastro)
   HTTP 201 Created
```

### 6.2 Login — `POST /usuarios/login`

```
1. Request body → UsuarioLoginRequest (email + senha)

2. Handler (routers/usuarios.py) — lógica de banco inline (sem crud/)
   - Busca usuário por e-mail → HTTP 401 se não encontrar
   - bcrypt.checkpw → HTTP 401 se inválida

3. criar_token({"sub": email, "id_usuario": id}) → JWT com SECRET_KEY hardcoded

4. Retorna TokenResponse {"access_token": "...", "token_type": "bearer"}
```

### 6.3 CRUD de Plantas — `POST /plantas/` (autenticado)

```
1. Header: Authorization: Bearer <token>
   → get_current_user decodifica JWT → retorna payload dict com "id_usuario"

2. Request body → PlantaCreate (id_especie obrigatório, ambiente obrigatório)

3. Handler → crud.create_planta(db, data, user["id_usuario"])
   - Instancia Planta, db.add() → db.commit() → db.refresh()

4. Retorna PlantaResponse HTTP 201
```

### 6.4 Irrigação Manual — `POST /plantas/{id}/irrigar` (autenticado)

```
1. Busca planta do usuário → 404 se não encontrar
2. Verifica vínculo ativo com dispositivo → 400 se não vinculado
3. Busca última leitura de umidade → 400 se não existir
4. Busca espécie → usa faixa_umidade_max (default 80 se null)
5. Se umidade >= limite → registra HistoricoCuidado + HTTP 409 "Umidade acima do limite"
6. Simula envio ao dispositivo (sucesso_dispositivo = True hardcoded)
7. Registra HistoricoCuidado de sucesso
8. Retorna {"mensagem": "Irrigação manual enviada com sucesso"}
```

**Nota:** a comunicação real com o dispositivo IoT não está implementada — há
uma variável `sucesso_dispositivo = True` sempre hardcoded.

### 6.5 Motor de Eventos — `POST /eventos/sensor` (autenticado)

```
1. Recebe: planta_id, umidade (float|None), sensor_ok (bool)
2. ⚠️  Bug: usa user.id_usuario (AttributeError) — deve ser user["id_usuario"]
3. Chama processar_evento_sensor → gera notificações conforme regras fixas
```

### 6.6 Histórico — `GET /historico/` (autenticado)

```
1. Carrega em memória: todos HistoricoCuidado + LeituraUmidade + Notificacao do usuário
2. Ordena por data_hora desc
3. Aplica paginação manual (pagina, limite)
4. Retorna HistoricoResponse com total, pagina, limite, registros
```

**Risco de performance:** carrega todos os registros em memória antes de paginar.
Com volumes grandes (RNF-017: 12 meses de histórico) isso pode ser lento.

---

## 7. Configuração do Banco de Dados

Variáveis lidas do `.env` (ver `.env.example`):

```
DATABASE_URL=postgresql://postgres:SENHA@localhost:5432/croop?client_encoding=utf8
SECRET_KEY=change-me          # lido pelo settings mas IGNORADO por security.py
ACCESS_TOKEN_EXPIRE_MINUTES=60
APP_NAME=Croop API
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
```

O `DATABASE_URL` é o único campo sem valor padrão — a aplicação não inicializa sem ele.

---

## 8. Alembic e Migrations

### Configuração

O `alembic.ini` tem `sqlalchemy.url` vazio intencionalmente. A URL é injetada em
`alembic/env.py` via:

```python
config.set_main_option("sqlalchemy.url", settings.database_url)
```

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
alembic upgrade head              # aplicar migrations pendentes
alembic revision --autogenerate -m "descricao"  # gerar nova migration
alembic downgrade -1              # reverter última migration
alembic history                   # ver histórico
```

**Regra:** todo novo model deve ser adicionado em `app/models/__init__.py` antes de
executar `--autogenerate`.

---

## 9. Endpoints Existentes

### Autenticação (`/usuarios`)

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/usuarios/cadastro` | Não | Cadastra novo usuário |
| POST | `/usuarios/login` | Não | Autentica e retorna JWT |
| GET | `/usuarios/protegido` | Bearer | Rota de teste de autenticação |

### Plantas (`/plantas`)

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/plantas/` | Bearer | Cria nova planta |
| GET | `/plantas/` | Bearer | Lista plantas do usuário |
| GET | `/plantas/{id}` | Bearer | Detalha uma planta |
| PUT | `/plantas/{id}` | Bearer | Atualiza uma planta |
| DELETE | `/plantas/{id}` | Bearer | Remove uma planta |
| POST | `/plantas/{id}/irrigar` | Bearer | Irrigação manual |

### Espécies (`/especies`)

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/especies/` | Bearer | Lista espécies com busca opcional por nome |

Query param: `?busca=texto` — filtra por `nome_comum` ou `nome_cientifico` (ilike).

### Notificações (`/notificacoes`)

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/notificacoes/` | Bearer | Lista notificações do usuário — **BUG: AttributeError** |

### Eventos (`/eventos`)

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/eventos/sensor` | Bearer | Processa evento de sensor IoT — **BUG: AttributeError** |

Query params: `planta_id`, `umidade` (opcional), `sensor_ok` (bool, default true).

### Histórico (`/historico`)

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/historico/` | Bearer | Histórico paginado de cuidados + leituras + notificações |

Query params: `pagina` (default 1), `limite` (default 10).

### Utilitários

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| GET | `/health` | Não | Verifica se a API está rodando |
| GET | `/db-test` | Não | Verifica conexão com o banco |

---

## 10. Padrões Identificados

### Schemas Pydantic (padrão a manter)

```python
class EntidadeBase(BaseModel):        # campos compartilhados
class EntidadeCreate(EntidadeBase):   # campos de criação
class EntidadeUpdate(BaseModel):      # todos Optional (atualização parcial)
class EntidadeResponse(EntidadeBase): # saída
    id_entidade: int
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

### Acesso ao usuário autenticado (padrão correto)

`get_current_user` retorna um `dict` — acessar sempre com `user["id_usuario"]`,
**nunca** com `user.id_usuario` (causa `AttributeError`).

---

## 11. Bugs Ativos

| Severidade | Localização | Problema |
|---|---|---|
| **Crítico** | `core/security.py:14` | `SECRET_KEY` hardcoded — `.env` ignorado para JWT |
| **Crítico** | `routers/notificacao.py:18` | `user.id_usuario` → `AttributeError` em runtime |
| **Crítico** | `routers/eventos.py:20` | `user.id_usuario` → `AttributeError` em runtime |
| Alto | `services/evento_notificacao_service.py` | Limiares de umidade fixos (< 30 / > 80) — ignora `faixa_umidade_min/max` da espécie |
| Alto | `routers/planta.py` (irrigar) | `sucesso_dispositivo = True` hardcoded — sem comunicação IoT real |
| Médio | `core/security.py:21` | `datetime.utcnow()` depreciado no Python 3.12+ |
| Médio | `routers/historico.py` | Carrega tudo em memória antes de paginar — risco de performance com volumes grandes |
| Médio | `main.py` | CORS restrito a `localhost:8081` — precisará de atualização para produção |
| Baixo | `routers/db_test.py` | Sem autenticação, expõe erros internos do banco |
| Baixo | `ci.yml` | CI aceita zero testes (`pytest || exit 5`) |

---

## 12. Riscos Técnicos e Arquiteturais

| Risco | Severidade | Descrição |
|-------|------------|-----------|
| `SECRET_KEY` hardcoded | Crítico | Rotacionar a chave requer alterar o código, não apenas o `.env` |
| Lógica de banco inline nos routers de usuários | Alto | Dificulta testes e viola separação de camadas |
| Sem testes automatizados | Alto | Nenhum teste de integração ou unitário implementado |
| Paginação em memória no histórico | Alto | Lento com volumes grandes (100 plantas × 12 meses) |
| IoT não integrado | Alto | `/irrigar` e `/eventos/sensor` simulam comunicação; não enviam comandos reais |
| Sem validação de FK (IntegrityError vira HTTP 500) | Alto | `crud/planta.py` não captura erro de `id_especie` inválido |
| CPF sem validação de formato ou dígito verificador | Médio | `schemas/usuario.py` aceita qualquer string |
| Sem paginação em `GET /plantas/` | Médio | Lista toda em um request; escala mal com muitas plantas |

---

## 13. Integrações Previstas (não implementadas)

### Dispositivo IoT

Evidenciado pelos models: `DispositivoIot`, `SensorUmidade`, `BombaDagua`,
`LeituraUmidade`, `Irrigacao`, `VinculoPlantaDispositivo`. O campo
`origem_decisao` em `Irrigacao` diferencia irrigações manuais, automáticas e por IA.

Atualmente o endpoint `/eventos/sensor` recebe dados manualmente (simulando o que
o dispositivo enviaria). A comunicação real com hardware (MQTT, REST do ESP32)
não está implementada.

### Módulo de IA / Recomendação

O model `RecomendacaoIA` e os campos `faixa_umidade_min`, `faixa_umidade_max`,
`frequencia_media_irrigacao` em `Especie` estão no banco mas nenhum serviço de IA
está implementado.

---

## 14. Recomendações — Próximos Passos

### Correções imediatas (antes de qualquer nova feature)

1. **`SECRET_KEY`:** substituir o literal em `security.py` por `settings.secret_key`
2. **`routers/notificacao.py`:** trocar `user.id_usuario` por `user["id_usuario"]`
3. **`routers/eventos.py`:** trocar `user.id_usuario` por `user["id_usuario"]`
4. **`datetime.utcnow()`:** substituir por `datetime.now(timezone.utc)` em `security.py`

### Melhorias de qualidade

5. **Criar `crud/usuario.py`:** mover queries de `routers/usuarios.py` para CRUD dedicado
6. **Paginação no histórico:** fazer a query com `LIMIT/OFFSET` no banco, não em memória
7. **Capturar `IntegrityError`** nos CRUDs com FKs — retornar HTTP 422 em vez de 500
8. **Motor de eventos:** usar `faixa_umidade_min/max` da espécie em vez de limiares fixos
9. **CORS:** parametrizar `allow_origins` via `settings` para suportar produção
10. **Implementar testes** — ao menos integração para cadastro, login e CRUD de plantas

### Infraestrutura pendente

11. **Comunicação IoT real:** substituir `sucesso_dispositivo = True` por integração real
12. **`app/services/`:** implementar service de plantas para encapsular irrigação e vinculação
