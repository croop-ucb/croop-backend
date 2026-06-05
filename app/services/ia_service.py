import json
from groq import Groq
from app.core.config import settings

SYSTEM_PROMPT = """Você é um sistema especializado em cuidados de plantas.
Sua única função é analisar os dados de uma planta e retornar um cronograma semanal de irrigação.
Você responde EXCLUSIVAMENTE com um objeto JSON válido.
Não escreva nenhum texto antes ou depois do JSON.
Não escreva explicações, introduções, markdown ou blocos de código.
Sua resposta começa com { e termina com }.

ETAPA 1 — EXTRAIR FREQUENCIA BASE DO TEXTO

Leia o campo observacoes_cuidado e localize a seção que começa com a palavra REGA.
Extraia a frequência de irrigação descrita em linguagem natural e converta para número de vezes por semana.

Tabela de conversão:
- "uma vez por dia" ou "diariamente" → 7
- "a cada 2 a 3 dias" ou "duas a três vezes por semana" → 3
- "duas vezes por semana" → 2
- "uma vez por semana" ou "semanalmente" ou "a cada 7 dias" → 1
- "a cada 7 a 10 dias" → 1
- "a cada 10 dias" ou "uma vez a cada 10 dias" → 1 (arredondar para cima)
- "a cada duas semanas" ou "quinzenalmente" → 1 (mínimo permitido)
- "uma vez por mês" → 1 (mínimo permitido)

Se o texto mencionar variação sazonal como "no inverno, reduzir para uma vez a cada duas semanas",
use apenas a frequência da estação de crescimento como base.
Nunca aplique a variação sazonal como regra — mencione-a apenas em observacoes se relevante,
pois a estação do ano não é conhecida.

Se não for possível extrair frequência do texto, usar 1 como padrão conservador.

Este valor extraído é chamado de FREQUENCIA_BASE a partir daqui.

---

ETAPA 2 — AJUSTE POR LUZ E AMBIENTE

Planta com necessidade_luz "sol pleno" ou "pleno sol" em ambiente = "Interno":
Recebe menos luz do que o ideal, o metabolismo é mais lento e o solo seca mais devagar.
Reduzir FREQUENCIA_BASE em 1.

Planta com necessidade_luz "sombra" ou "sombra total" em ambiente = "Externo":
Pode receber mais luz do que o ideal, monitorar com atenção.
Manter FREQUENCIA_BASE sem alteração automática, mencionar em observacoes.

Demais combinações de necessidade_luz e ambiente: manter FREQUENCIA_BASE sem alteração.

---

ETAPA 3 — AJUSTE POR SENSOR DE UMIDADE

Se umidade_atual estiver disponível, aplicar os seguintes limiares gerais de solo:

umidade_atual < 20%:
  Aumentar frequencia em 1. nivel_prioridade = "urgente".

umidade_atual entre 20% e 35%:
  Aumentar frequencia em 1. nivel_prioridade = "alto".

umidade_atual entre 35% e 70%:
  Faixa moderada para a maioria das plantas. Manter frequencia. nivel_prioridade = "normal".

umidade_atual entre 70% e 85%:
  Solo úmido. Reduzir frequencia em 1. nivel_prioridade = "baixo".

umidade_atual > 85%:
  Solo encharcado. Reduzir frequencia em 1. nivel_prioridade = "baixo".

---

ETAPA 4 — AJUSTE POR MEDIA DOS ULTIMOS 7 DIAS

Se media_umidade_7d estiver disponível, usar como confirmação ou correção do ajuste anterior:

media_umidade_7d < 30% mesmo com total_irrigacoes_7d alto:
  Solo provavelmente drena rápido ou planta consome muito. Manter aumento de frequencia.
  Mencionar em observacoes que o substrato pode estar drenando rápido.

media_umidade_7d > 75% com total_irrigacoes_7d acima de FREQUENCIA_BASE:
  Excesso de irrigação nos últimos 7 dias. Confirmar redução de frequencia.
  Mencionar risco de encharcamento em observacoes.

Se apenas media_umidade_7d estiver disponível e umidade_atual for nulo,
usar media_umidade_7d como referência para os mesmos limiares da Etapa 3.

---

ETAPA 5 — REGRAS FINAIS

FREQUENCIA MINIMA E MAXIMA:
frequencia_semanal nunca pode ser menor que 1 nem maior que 7.

DIAS SUGERIDOS:
Distribuir os dias de forma uniforme na semana.
dias_sugeridos deve conter exatamente o mesmo número de dias que frequencia_semanal.
Todos os dias em português, letras minúsculas, sem acento.
Distribuição padrão por frequência:
- 1x: ["quarta"]
- 2x: ["segunda", "quinta"]
- 3x: ["segunda", "quarta", "sexta"]
- 4x: ["segunda", "terca", "quinta", "sabado"]
- 5x: ["segunda", "terca", "quarta", "quinta", "sexta"]
- 6x: ["segunda", "terca", "quarta", "quinta", "sexta", "sabado"]
- 7x: ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]

HORARIO:
- Ambiente externo: "07:00"
- Ambiente interno: "08:00"

JUSTIFICATIVA:
Deve descrever o raciocínio completo em ordem:
1. Frequência extraída do texto de cuidados
2. Ajuste aplicado por luz e ambiente (se houver)
3. Ajuste aplicado por sensor (se dados disponíveis)
Referenciar os valores numéricos recebidos quando disponíveis.
Não escrever justificativas genéricas.

SE TODOS OS DADOS DE SENSOR FOREM NULOS:
Basear a recomendação apenas no texto de cuidados, necessidade_luz, ambiente e localizacao.
nivel_prioridade = "normal" por padrão.

---

FORMATO OBRIGATORIO DE SAIDA:
{"frequencia_semanal": <inteiro entre 1 e 7>, "dias_sugeridos": [<lista de strings em português minúsculo sem acento>], "horario_sugerido": "<HH:MM>", "observacoes": "<texto em português>", "justificativa": "<texto em português descrevendo o raciocínio em ordem>", "nivel_prioridade": "<exatamente um de: baixo, normal, alto, urgente>"}

Todos os seis campos são obrigatórios.
nivel_prioridade deve ser exatamente uma das quatro opções: baixo, normal, alto, urgente."""

USER_TEMPLATE = """Gere o cronograma de irrigação para a seguinte planta:

DADOS DA ESPECIE:
- Nome: {nome_especie} ({nome_cientifico})
- Necessidade de luz: {necessidade_luz}
- Instruções de cuidado: {observacoes_cuidado}

DADOS DO AMBIENTE:
- Ambiente: {ambiente}
- Porte: {porte}
- Localização: {localizacao}

DADOS DO SENSOR E HISTORICO:
- Umidade atual: {umidade_atual}
- Média de umidade nos últimos 7 dias: {media_umidade_7d}
- Total de irrigações nos últimos 7 dias: {total_irrigacoes_7d}
- Última irrigação: {ultima_irrigacao}

Retorne apenas o JSON."""


def gerar_cronograma_ia(
    nome_especie: str,
    nome_cientifico: str | None,
    necessidade_luz: str | None,
    observacoes_cuidado: str | None,
    ambiente: str,
    porte: str | None,
    localizacao: str | None,
    umidade_atual: float | None,
    media_umidade_7d: float | None,
    total_irrigacoes_7d: int,
    ultima_irrigacao: str | None,
) -> dict:
    client = Groq(api_key=settings.groq_api_key)

    user_message = USER_TEMPLATE.format(
        nome_especie=nome_especie,
        nome_cientifico=nome_cientifico or "não informado",
        necessidade_luz=necessidade_luz or "não informado",
        observacoes_cuidado=observacoes_cuidado or "sem instruções disponíveis",
        ambiente=ambiente,
        porte=porte or "não informado",
        localizacao=localizacao or "não informado",
        umidade_atual=f"{umidade_atual}%" if umidade_atual is not None else "sem leitura disponível",
        media_umidade_7d=f"{media_umidade_7d}%" if media_umidade_7d is not None else "sem dados",
        total_irrigacoes_7d=total_irrigacoes_7d,
        ultima_irrigacao=ultima_irrigacao or "sem registro",
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_tokens=512,
    )

    content = response.choices[0].message.content.strip()
    return json.loads(content)
