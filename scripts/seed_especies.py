#!/usr/bin/env python3
"""
scripts/seed_especies.py

Seed de espécies de plantas para o projeto Croop.
Fontes: Perenual API (dados botânicos) + DeepL API (tradução PT-BR).

LIMITES DO PLANO:
  Perenual Personal: 100 requests/dia, acesso a IDs 1-3000
  DeepL Free:        500.000 chars/mês | 1.000.000 chars trial (uso único)

EXECUÇÃO (a partir da raiz do projeto):
  py scripts/seed_especies.py

O script para automaticamente ao atingir MAX_REQUESTS_SESSAO.
Execute novamente no dia seguinte para continuar — registros já inseridos
são atualizados (não duplicados).
"""

import math
import os
import random
import re
import sys
import logging
import time
from datetime import datetime

# Adiciona a raiz do projeto ao sys.path para importar os módulos da aplicação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.especie import Especie

# ──────────────────────────────────────────────────────────────────────────────
# Chaves das APIs (arquivo local, não versionar)
# ──────────────────────────────────────────────────────────────────────────────

CHAVE_PERENUAL = "pegar no site da api"
CHAVE_DEEPL = "pegar no site da api"

# ──────────────────────────────────────────────────────────────────────────────
# URLs das APIs
# ──────────────────────────────────────────────────────────────────────────────

PERENUAL_LIST_URL = "https://perenual.com/api/v2/species-list"
PERENUAL_DETAILS_URL = "https://perenual.com/api/v2/species/details/{id}"
PERENUAL_CARE_URL = "https://perenual.com/api/species-care-guide-list"
DEEPL_URL = "https://api-free.deepl.com/v2/translate"

# ──────────────────────────────────────────────────────────────────────────────
# Configuração de volume e cotas
#
# LIMITE_ESPECIES     — total de espécies a processar no projeto (IDs 1-N)
#                       Recomendado: 150 (seguro no DeepL free e ~4 dias Perenual)
#                       Máximo seguro p/ DeepL free (500K chars/mês): ~200
#                       Máximo acessível no plano Personal: 3000
#
# MAX_REQUESTS_SESSAO — requests por execução (plano Personal: 100/dia)
#                       Deixe 10 de margem → use 90
#                       Com 90: ~43 novas espécies por execução
#
# DEEPL_AVISO_CHARS   — avisa se a sessão vai usar mais que este valor
# ──────────────────────────────────────────────────────────────────────────────

LIMITE_ESPECIES = 150
MAX_REQUESTS_SESSAO = 90
DEEPL_AVISO_CHARS = 400_000

# ──────────────────────────────────────────────────────────────────────────────
# Parâmetros de robustez
# ──────────────────────────────────────────────────────────────────────────────

MAX_RETRIES = 5
BASE_DELAY = 1.5
REQUEST_TIMEOUT = 30
DELAY_PERENUAL = 1.5
DEEPL_BATCH = 30

# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("seed_especies")

# ──────────────────────────────────────────────────────────────────────────────
# Contador global de requests (controle de cota diária)
# ──────────────────────────────────────────────────────────────────────────────

_requests_feitos: int = 0


def _incrementar_requests() -> None:
    global _requests_feitos
    _requests_feitos += 1


def _pode_continuar() -> bool:
    """Retorna True se ainda há cota disponível para esta sessão."""
    return _requests_feitos < MAX_REQUESTS_SESSAO


# ──────────────────────────────────────────────────────────────────────────────
# Cache de traduções em memória
# ──────────────────────────────────────────────────────────────────────────────

_cache_traducao: dict[str, str] = {}

# ──────────────────────────────────────────────────────────────────────────────
# HTTP com retry e exponential backoff
# ──────────────────────────────────────────────────────────────────────────────

def _request(
    method: str,
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    json_body: dict | None = None,
    contar_cota: bool = True,
) -> dict | None:
    """
    Executa request HTTP com retry e exponential backoff.
    contar_cota=True: incrementa o contador da cota diária da Perenual.
    contar_cota=False: para chamadas à DeepL (sem limite diário relevante).
    """
    if contar_cota:
        _incrementar_requests()

    for tentativa in range(1, MAX_RETRIES + 1):
        try:
            if method == "GET":
                resp = requests.get(
                    url, params=params, headers=headers, timeout=REQUEST_TIMEOUT
                )
            else:
                resp = requests.post(
                    url, headers=headers, json=json_body, timeout=REQUEST_TIMEOUT
                )

            if resp.status_code == 200:
                return resp.json()

            if resp.status_code == 429:
                espera = BASE_DELAY * (2 ** tentativa)
                log.warning(
                    f"[{tentativa}/{MAX_RETRIES}] Rate limit (429) em {url}. "
                    f"Aguardando {espera:.1f}s..."
                )
                time.sleep(espera)
                continue

            if resp.status_code in (500, 502, 503, 504):
                espera = BASE_DELAY * (2 ** tentativa)
                log.warning(
                    f"[{tentativa}/{MAX_RETRIES}] Erro servidor ({resp.status_code}) "
                    f"em {url}. Aguardando {espera:.1f}s..."
                )
                time.sleep(espera)
                continue

            log.error(
                f"HTTP {resp.status_code} em {url}. "
                f"Corpo: {resp.text[:200]}"
            )
            return None

        except requests.exceptions.ConnectionError as exc:
            espera = BASE_DELAY * (2 ** tentativa)
            log.warning(
                f"[{tentativa}/{MAX_RETRIES}] Erro de conexão em {url}: {exc}. "
                f"Aguardando {espera:.1f}s..."
            )
            time.sleep(espera)

        except requests.exceptions.Timeout:
            espera = BASE_DELAY * (2 ** tentativa)
            log.warning(
                f"[{tentativa}/{MAX_RETRIES}] Timeout em {url}. "
                f"Aguardando {espera:.1f}s..."
            )
            time.sleep(espera)

        except Exception as exc:  # noqa: BLE001
            log.error(f"Erro inesperado em {url}: {exc}")
            return None

    log.error(f"Esgotadas {MAX_RETRIES} tentativas para {url}.")
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Perenual — listagem (apenas as páginas necessárias para LIMITE_ESPECIES)
# ──────────────────────────────────────────────────────────────────────────────

def buscar_listagem() -> list[dict]:
    """
    Busca a página 1 para descobrir o total de páginas disponíveis, depois
    sorteia aleatoriamente as demais para garantir variedade entre sessões.
    Cada página = 1 request da cota diária.
    """
    log.info("=== [1/5] Coletando listagem de espécies ===")

    paginas_necessarias = math.ceil(LIMITE_ESPECIES / 30)

    primeira = _request(
        "GET",
        PERENUAL_LIST_URL,
        params={"key": CHAVE_PERENUAL, "page": 1},
    )
    if not primeira:
        log.error("Falha ao buscar primeira página. Abortando.")
        sys.exit(1)

    ultima_disponivel = primeira.get("last_page", 1)
    total_api = primeira.get("total", 0)

    # Sorteia páginas aleatórias do pool completo (exclui página 1, já buscada)
    pool = list(range(2, min(ultima_disponivel, 100) + 1))
    random.shuffle(pool)
    paginas_extras = pool[: paginas_necessarias - 1]

    log.info(
        f"API tem {total_api} espécies ({ultima_disponivel} páginas). "
        f"Buscando página 1 + páginas aleatórias: {sorted(paginas_extras)}"
    )

    acumuladas: list[dict] = list(primeira.get("data", []))

    for pagina in paginas_extras:
        if not _pode_continuar():
            log.warning("Cota de requests atingida durante a listagem.")
            break
        time.sleep(DELAY_PERENUAL)
        dados = _request(
            "GET",
            PERENUAL_LIST_URL,
            params={"key": CHAVE_PERENUAL, "page": pagina},
        )
        if dados:
            acumuladas.extend(dados.get("data", []))
        else:
            log.warning(f"  Página {pagina} falhou. Continuando...")

    random.shuffle(acumuladas)
    resultado = [e for e in acumuladas if e.get("id", 9999) <= 3000][:LIMITE_ESPECIES]
    log.info(f"Listagem concluída: {len(resultado)} espécies para processar.")
    return resultado


# ──────────────────────────────────────────────────────────────────────────────
# Perenual — detalhes e care guide
# ──────────────────────────────────────────────────────────────────────────────

def buscar_detalhes(especie_id: int) -> dict | None:
    url = PERENUAL_DETAILS_URL.format(id=especie_id)
    return _request("GET", url, params={"key": CHAVE_PERENUAL})


def buscar_care_guide(especie_id: int) -> list[dict]:
    dados = _request(
        "GET",
        PERENUAL_CARE_URL,
        params={"key": CHAVE_PERENUAL, "species_id": especie_id},
    )
    if not dados:
        return []
    itens = dados.get("data", [])
    if not itens:
        return []
    return itens[0].get("section", [])


# ──────────────────────────────────────────────────────────────────────────────
# Banco de dados — verificação de existência
# ──────────────────────────────────────────────────────────────────────────────

def _ja_existe_no_banco(db: Session, nome_cientifico: str | None) -> bool:
    """
    Verifica se uma espécie com esse nome científico já existe no banco.
    Usado para evitar requests desnecessários à API em re-execuções.
    """
    if not nome_cientifico:
        return False
    return (
        db.query(Especie)
        .filter(Especie.nome_cientifico == nome_cientifico[:150])
        .first()
        is not None
    )


# ──────────────────────────────────────────────────────────────────────────────
# Normalização de campos
# ──────────────────────────────────────────────────────────────────────────────

def _nome_cientifico(scientific_name) -> str | None:
    if not scientific_name:
        return None
    if isinstance(scientific_name, list):
        return scientific_name[0].strip() if scientific_name else None
    return str(scientific_name).strip() or None


def _parse_frequencia_irrigacao(benchmark: dict | None) -> int | None:
    if not benchmark:
        return None
    valor_str = str(benchmark.get("value", "")).strip()
    unidade = str(benchmark.get("unit", "")).strip().lower()
    if not valor_str or unidade not in ("days", "day"):
        return None
    match = re.match(r"^(\d+)\s*-\s*(\d+)$", valor_str)
    if match:
        return round((int(match.group(1)) + int(match.group(2))) / 2)
    if valor_str.isdigit():
        return int(valor_str)
    return None


def _sunlight_string(sunlight) -> str | None:
    if not sunlight:
        return None
    if isinstance(sunlight, list):
        partes = [str(s).strip() for s in sunlight if s]
        texto = ", ".join(partes)
    else:
        texto = str(sunlight).strip()
    return texto or None


def _care_guide_string(secoes: list[dict]) -> str | None:
    partes = []
    for secao in secoes:
        tipo = str(secao.get("type", "")).strip().upper()
        descricao = str(secao.get("description", "")).strip()
        if tipo and descricao:
            partes.append(f"{tipo}\n\n{descricao}")
    return "\n\n---\n\n".join(partes) or None


# ──────────────────────────────────────────────────────────────────────────────
# Consolidação em memória
# ──────────────────────────────────────────────────────────────────────────────

def consolidar(
    item_lista: dict,
    detalhes: dict | None,
    secoes_cuidado: list[dict],
) -> dict:
    fonte = detalhes if detalhes else item_lista

    nome_cient = _nome_cientifico(fonte.get("scientific_name"))
    nome_comum_en = (fonte.get("common_name") or "").strip() or None

    descricao_en: str | None = None
    if detalhes:
        raw = (detalhes.get("description") or "").strip()
        descricao_en = raw or None

    sunlight_raw = (detalhes or {}).get("sunlight") or item_lista.get("sunlight")
    luz_en = _sunlight_string(sunlight_raw)

    frequencia = _parse_frequencia_irrigacao(
        (detalhes or {}).get("watering_general_benchmark")
    )

    observacoes_en = _care_guide_string(secoes_cuidado)

    return {
        "nome_cientifico": nome_cient,
        "_nome_comum_en": nome_comum_en,
        "_descricao_en": descricao_en,
        "_luz_en": luz_en,
        "_observacoes_en": observacoes_en,
        "frequencia_media_irrigacao": frequencia,
        "nome_comum": None,
        "descricao": None,
        "necessidade_luz": None,
        "observacoes_cuidado": None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# DeepL — tradução em lote (sem contar na cota do Perenual)
# ──────────────────────────────────────────────────────────────────────────────

def _traduzir_lote_deepl(textos: list[str]) -> list[str]:
    dados = _request(
        "POST",
        DEEPL_URL,
        headers={"Authorization": f"DeepL-Auth-Key {CHAVE_DEEPL}"},
        json_body={"text": textos, "target_lang": "PT-BR"},
        contar_cota=False,
    )
    if not dados or "translations" not in dados:
        log.warning(
            f"DeepL não retornou traduções para lote de {len(textos)} texto(s). "
            "Mantendo originais."
        )
        return list(textos)
    return [
        t.get("text", original)
        for t, original in zip(dados["translations"], textos)
    ]


def traduzir_em_lote(textos_unicos: list[str]) -> dict[str, str]:
    resultado: dict[str, str] = {}
    novos: list[str] = []

    for texto in textos_unicos:
        if texto in _cache_traducao:
            resultado[texto] = _cache_traducao[texto]
        else:
            novos.append(texto)

    total_chars_novos = sum(len(t) for t in novos)
    log.info(
        f"Textos do cache: {len(resultado)} | "
        f"Novos para DeepL: {len(novos)} | "
        f"Chars a enviar: {total_chars_novos:,}"
    )
    if total_chars_novos > DEEPL_AVISO_CHARS:
        log.warning(
            f"ATENÇÃO: {total_chars_novos:,} chars excedem o aviso de "
            f"{DEEPL_AVISO_CHARS:,}. Verifique sua cota mensal DeepL."
        )

    total_lotes = max(1, math.ceil(len(novos) / DEEPL_BATCH))
    for i in range(0, len(novos), DEEPL_BATCH):
        lote = novos[i : i + DEEPL_BATCH]
        lote_num = i // DEEPL_BATCH + 1
        log.info(f"  Lote DeepL {lote_num}/{total_lotes}: {len(lote)} texto(s)...")
        traducoes = _traduzir_lote_deepl(lote)
        for original, traduzido in zip(lote, traducoes):
            _cache_traducao[original] = traduzido
            resultado[original] = traduzido

    return resultado


def _coletar_textos(especies: list[dict]) -> list[str]:
    vistos: set[str] = set()
    for esp in especies:
        for campo in ("_nome_comum_en", "_descricao_en", "_luz_en", "_observacoes_en"):
            val = esp.get(campo)
            if val and val.strip():
                vistos.add(val.strip())
    return list(vistos)


def aplicar_traducoes(especies: list[dict], mapa: dict[str, str]) -> None:
    for esp in especies:
        def _t(campo: str) -> str | None:
            val = esp.get(campo)
            if not val:
                return None
            return mapa.get(val.strip(), val.strip())

        esp["nome_comum"] = _t("_nome_comum_en")
        esp["descricao"] = _t("_descricao_en")
        esp["observacoes_cuidado"] = _t("_observacoes_en")
        luz = _t("_luz_en")
        esp["necessidade_luz"] = luz[:50] if luz else None


# ──────────────────────────────────────────────────────────────────────────────
# Persistência — upsert por nome científico
# ──────────────────────────────────────────────────────────────────────────────

def upsert_especie(db: Session, dados: dict) -> bool:
    """Retorna True se criou, False se atualizou."""
    nome_cient = dados.get("nome_cientifico")
    if nome_cient:
        nome_cient = nome_cient[:150]

    nome_comum_raw = (
        dados.get("nome_comum")
        or dados.get("_nome_comum_en")
        or "Espécie desconhecida"
    )
    nome_comum = nome_comum_raw[:100]

    existente: Especie | None = None
    if nome_cient:
        existente = (
            db.query(Especie)
            .filter(Especie.nome_cientifico == nome_cient)
            .first()
        )

    if existente:
        existente.nome_comum = nome_comum
        if dados.get("descricao"):
            existente.descricao = dados["descricao"]
        if dados.get("necessidade_luz"):
            existente.necessidade_luz = dados["necessidade_luz"]
        if dados.get("frequencia_media_irrigacao") is not None:
            existente.frequencia_media_irrigacao = dados["frequencia_media_irrigacao"]
        if dados.get("observacoes_cuidado"):
            existente.observacoes_cuidado = dados["observacoes_cuidado"]
        return False

    nova = Especie(
        nome_comum=nome_comum,
        nome_cientifico=nome_cient,
        descricao=dados.get("descricao"),
        faixa_umidade_min=None,
        faixa_umidade_max=None,
        frequencia_media_irrigacao=dados.get("frequencia_media_irrigacao"),
        necessidade_luz=dados.get("necessidade_luz"),
        observacoes_cuidado=dados.get("observacoes_cuidado"),
    )
    db.add(nova)
    return True


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    t_inicio = time.time()

    log.info("=" * 62)
    log.info("  Croop — Seed de Espécies de Plantas")
    log.info(f"  Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"  Alvo: {LIMITE_ESPECIES} espécies | Cota por sessão: {MAX_REQUESTS_SESSAO} requests")
    log.info("=" * 62)

    db: Session = SessionLocal()

    # ── Teste de conexão com o banco (antes de qualquer chamada à API) ────────
    log.info("Testando conexão com o banco de dados...")
    try:
        db.execute(text("SELECT 1"))
        log.info("Conexão com o banco: OK")
    except Exception as exc:
        log.error(f"Falha na conexão com o banco: {exc}")
        log.error("Abortando sem fazer nenhuma chamada à API.")
        db.close()
        sys.exit(1)

    # ── Fase 1: Listagem ──────────────────────────────────────────────────────
    lista_bruta = buscar_listagem()
    if not lista_bruta:
        log.error("Nenhuma espécie na listagem. Abortando.")
        db.close()
        sys.exit(1)

    log.info(
        f"Requests usados na listagem: {_requests_feitos}/{MAX_REQUESTS_SESSAO}"
    )

    # ── Fase 2: Detalhes e care guides (apenas para novas espécies) ───────────
    log.info("=== [2/5] Buscando detalhes e care guides ===")

    especies_consolidadas: list[dict] = []
    puladas_banco = 0
    erros_detalhes = 0
    erros_care = 0
    total = len(lista_bruta)
    cota_atingida = False

    for i, item in enumerate(lista_bruta, start=1):
        especie_id = item.get("id")
        sci_names = item.get("scientific_name") or []
        nome_cient_lista = (
            sci_names[0].strip() if sci_names else None
        )
        nome_log = nome_cient_lista or item.get("common_name", f"ID:{especie_id}")

        # Verificar se já está no banco (evita requests desnecessários em re-execuções)
        if _ja_existe_no_banco(db, nome_cient_lista):
            puladas_banco += 1
            continue

        # Verificar cota antes de cada par de requests (details + care)
        if _requests_feitos + 2 > MAX_REQUESTS_SESSAO:
            cota_atingida = True
            log.warning(
                f"Cota de {MAX_REQUESTS_SESSAO} requests/dia atingida em {i}/{total}. "
                f"Execute novamente amanhã para continuar."
            )
            break

        # Detalhes
        time.sleep(DELAY_PERENUAL)
        detalhes: dict | None = None
        if especie_id:
            detalhes = buscar_detalhes(especie_id)
            if not detalhes:
                log.warning(f"  Detalhes ausentes para '{nome_log}'")
                erros_detalhes += 1

        # Care guide
        time.sleep(DELAY_PERENUAL)
        secoes: list[dict] = []
        if especie_id:
            secoes = buscar_care_guide(especie_id)
            if not secoes:
                erros_care += 1

        especies_consolidadas.append(consolidar(item, detalhes, secoes))

        if i % 50 == 0:
            log.info(
                f"  [{i}/{total}] Requests usados: "
                f"{_requests_feitos}/{MAX_REQUESTS_SESSAO} | "
                f"Puladas (já no banco): {puladas_banco}"
            )

    log.info(
        f"Coleta concluída: {len(especies_consolidadas)} consolidadas | "
        f"{puladas_banco} já no banco | "
        f"{erros_detalhes} sem detalhes | {erros_care} sem care guide | "
        f"Requests usados: {_requests_feitos}/{MAX_REQUESTS_SESSAO}"
    )

    # ── Fase 3: Tradução (apenas para espécies novas desta sessão) ────────────
    log.info("=== [3/5] Traduzindo textos via DeepL ===")

    # especies_consolidadas contém apenas as novas (puladas foram descartadas acima)
    textos_para_traduzir = _coletar_textos(especies_consolidadas)
    log.info(f"Textos únicos a traduzir (novas espécies): {len(textos_para_traduzir)}")

    mapa_traducao: dict[str, str] = {}
    if textos_para_traduzir:
        mapa_traducao = traduzir_em_lote(textos_para_traduzir)
        aplicar_traducoes(especies_consolidadas, mapa_traducao)

    log.info(f"Tradução concluída: {len(mapa_traducao)} textos traduzidos.")

    # ── Fase 4: Persistência ──────────────────────────────────────────────────
    log.info("=== [4/5] Persistindo no banco de dados ===")

    criados = 0
    atualizados = 0
    erros_db = 0

    try:
        for i, dados in enumerate(especies_consolidadas, start=1):
            nome_ref = dados.get("nome_cientifico") or dados.get("_nome_comum_en") or f"idx:{i}"
            try:
                foi_criado = upsert_especie(db, dados)
                db.commit()
                if foi_criado:
                    criados += 1
                else:
                    atualizados += 1
            except Exception as exc:  # noqa: BLE001
                db.rollback()
                erros_db += 1
                log.error(f"  Erro ao persistir '{nome_ref}': {exc}")

            if i % 50 == 0 or i == len(especies_consolidadas):
                log.info(
                    f"  [{i}/{len(especies_consolidadas)}] "
                    f"Criados: {criados} | Atualizados: {atualizados} | Erros: {erros_db}"
                )
    finally:
        db.close()

    # ── Fase 5: Resumo ────────────────────────────────────────────────────────
    duracao = time.time() - t_inicio
    minutos, segundos = divmod(int(duracao), 60)

    total_chars_traduzidos = sum(len(t) for t in mapa_traducao)

    log.info("=" * 62)
    log.info("  RESUMO DA SESSÃO")
    log.info(f"  Espécies no alvo (LIMITE_ESPECIES):  {LIMITE_ESPECIES}")
    log.info(f"  Espécies na listagem:                {total}")
    log.info(f"  Puladas (já estavam no banco):        {puladas_banco}")
    log.info(f"  Erros na busca de detalhes:           {erros_detalhes}")
    log.info(f"  Espécies sem care guide:              {erros_care}")
    log.info(f"  Chars enviados à DeepL:               {total_chars_traduzidos:,}")
    log.info(f"  Registros criados:                    {criados}")
    log.info(f"  Registros atualizados:                {atualizados}")
    log.info(f"  Erros de persistência:                {erros_db}")
    log.info(f"  Requests Perenual usados:             {_requests_feitos}/{MAX_REQUESTS_SESSAO}")
    log.info(f"  Tempo total:                          {minutos}m {segundos}s")

    if cota_atingida:
        processadas_total = criados + atualizados
        restantes = LIMITE_ESPECIES - processadas_total
        log.info("─" * 62)
        log.info(f"  Cota diária atingida. Faltam ~{restantes} espécies.")
        log.info("  Execute novamente amanhã para continuar.")

    log.info("=" * 62)


if __name__ == "__main__":
    main()
