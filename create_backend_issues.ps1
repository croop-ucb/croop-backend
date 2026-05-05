# create_backend_issues.ps1
# Script para criação das issues do repositório croop-backend.
# Pré-requisitos:
# - GitHub CLI instalado
# - gh auth login já executado
# - Executar este script dentro da raiz do repositório croop-backend

gh label create backend --color 0E8A16 --description "Tarefas do servidor e API" 2>$null
gh label create requisito --color 5319E7 --description "Issue vinculada ao Documento de Requisitos de Software" 2>$null

function New-CroopIssue {
    param (
        [string]$Title,
        [string]$Body
    )

    gh issue create `
        --title $Title `
        --body $Body `
        --label "backend,requisito"
}

New-CroopIssue `
    -Title "BACK-001 - Implementar endpoint de cadastro de usuário (UC-001)" `
    -Body @"
UC relacionado:
- UC-001 - Realizar Cadastro de Usuário

Regras de negócio:
- RN-001 - Validação de Cadastro
- RN-002 - Autenticação
- RN-013 - Validação de Senha

Objetivo:
Implementar no backend o endpoint responsável pelo cadastro de novos usuários, com validação de dados e persistência no banco de dados.

Escopo:
- Criar schema Pydantic para request e response de cadastro.
- Validar formato de e-mail (usuario@dominio.com).
- Verificar se o e-mail já está cadastrado.
- Validar senha conforme RN-013 (mín. 6 caracteres, maiúscula, minúscula, número, sem espaços, diferente do e-mail).
- Validar confirmação de senha.
- Persistir usuário com senha em hash (bcrypt).
- Retornar resposta de sucesso ou erro adequada.

Critérios de aceite:
- Dado um e-mail inválido, quando o endpoint for chamado, então deve retornar HTTP 422 com mensagem de erro.
- Dado um e-mail já cadastrado, quando o endpoint for chamado, então deve retornar HTTP 409.
- Dada uma senha que não atenda aos critérios da RN-013, quando o endpoint for chamado, então deve retornar HTTP 422.
- Dadas confirmações de senha divergentes, quando o endpoint for chamado, então deve retornar HTTP 422.
- Dados os dados válidos, quando o endpoint for chamado, então deve persistir o usuário e retornar HTTP 201.
"@

New-CroopIssue `
    -Title "BACK-002 - Implementar endpoint de login e autenticação JWT (UC-002)" `
    -Body @"
UC relacionado:
- UC-002 - Realizar Login

Regras de negócio:
- RN-002 - Autenticação

Objetivo:
Implementar no backend o endpoint de login que valida credenciais e retorna token JWT para acesso às rotas protegidas.

Escopo:
- Criar schema Pydantic para request de login.
- Validar formato dos dados informados.
- Verificar se o e-mail está cadastrado.
- Validar e-mail e senha contra o registro existente.
- Gerar e retornar token JWT em caso de sucesso.
- Implementar dependência de autenticação para rotas protegidas.

Critérios de aceite:
- Dadas credenciais corretas, quando o endpoint for chamado, então deve retornar HTTP 200 com token JWT válido.
- Dadas credenciais inválidas, quando o endpoint for chamado, então deve retornar HTTP 401.
- Dado e-mail não cadastrado, quando o endpoint for chamado, então deve retornar HTTP 401.
- Dado um token válido, quando usado em rota protegida, então deve permitir acesso.
- Dado um token inválido ou ausente, quando usado em rota protegida, então deve retornar HTTP 401.
"@

New-CroopIssue `
    -Title "BACK-003 - Implementar CRUD do catálogo de plantas (UC-003)" `
    -Body @"
UC relacionado:
- UC-003 - Gerenciar Catálogo de Plantas (CRUD)

Regras de negócio:
- RN-003 - Cadastro de Planta
- RN-004 - Catálogo Individual

Objetivo:
Implementar os endpoints de criação, leitura, atualização e remoção de plantas no catálogo pessoal do usuário autenticado.

Escopo:
- Criar schemas Pydantic para request e response de planta.
- Implementar endpoint POST para cadastro de planta (espécie obrigatória, ambiente obrigatório).
- Implementar endpoint GET para listar plantas do usuário autenticado.
- Implementar endpoint GET para detalhar uma planta.
- Implementar endpoint PUT/PATCH para edição de planta.
- Implementar endpoint DELETE para remoção de planta.
- Garantir isolamento: usuário só acessa suas próprias plantas (RN-004).

Critérios de aceite:
- Dado usuário autenticado sem espécie informada, quando tentar cadastrar planta, então deve retornar HTTP 422.
- Dado usuário autenticado sem ambiente informado, quando tentar cadastrar planta, então deve retornar HTTP 422.
- Dado usuário autenticado, quando listar plantas, então deve retornar apenas suas próprias plantas.
- Dado usuário A tentando acessar planta do usuário B, quando fizer a requisição, então deve retornar HTTP 403 ou 404.
- Dados os dados válidos, quando o cadastro for realizado, então deve retornar HTTP 201 com os dados da planta criada.
"@

New-CroopIssue `
    -Title "BACK-004 - Implementar endpoint de associação planta-dispositivo IoT (UC-004)" `
    -Body @"
UC relacionado:
- UC-004 - Associar Planta ao Dispositivo IoT

Regras de negócio:
- RN-005 - Associação Planta-Dispositivo

Objetivo:
Implementar no backend o endpoint responsável por vincular uma planta cadastrada a um dispositivo IoT disponível.

Escopo:
- Criar schema Pydantic para request e response de associação.
- Validar se a planta pertence ao usuário autenticado.
- Validar se o dispositivo informado existe.
- Verificar se o dispositivo já está vinculado a outra planta.
- Verificar se a planta já possui dispositivo ativo.
- Persistir o vínculo planta-dispositivo.
- Retornar confirmação da associação.

Critérios de aceite:
- Dado um dispositivo já vinculado a outra planta, quando tentar associá-lo, então deve retornar HTTP 409.
- Dada uma planta já vinculada a um dispositivo ativo, quando tentar associar outro, então deve retornar HTTP 409.
- Dados planta e dispositivo válidos e disponíveis, quando a associação for confirmada, então deve retornar HTTP 201.
- Dado usuário tentando associar planta de outro usuário, quando fizer a requisição, então deve retornar HTTP 403 ou 404.
"@

New-CroopIssue `
    -Title "BACK-005 - Implementar endpoint de recebimento de leituras de umidade (UC-005)" `
    -Body @"
UC relacionado:
- UC-005 - Monitorar Umidade do Solo

Regras de negócio:
- RN-006 - Frequência de Leitura

Objetivo:
Implementar no backend o endpoint que recebe e registra dados de umidade enviados pelo dispositivo IoT.

Escopo:
- Criar schema Pydantic para recebimento dos dados do sensor (umidade em %, data, hora).
- Validar os dados recebidos (formato e valores dentro do esperado).
- Identificar a planta associada ao dispositivo.
- Registrar a leitura no banco de dados.
- Rejeitar leituras fora do padrão ou de dispositivos sem planta vinculada.
- Controlar frequência mínima de envio (RN-006: mínimo 5 minutos entre leituras).

Critérios de aceite:
- Dados válidos de umidade de dispositivo com planta vinculada, quando recebidos, então devem ser persistidos e retornar HTTP 201.
- Dados inválidos ou fora do padrão, quando recebidos, então devem ser descartados e retornar HTTP 422.
- Dado dispositivo sem planta vinculada, quando enviar leitura, então deve retornar HTTP 404.
- Dado intervalo inferior a 5 minutos desde a última leitura, quando receber nova leitura, então deve retornar HTTP 429.
"@

New-CroopIssue `
    -Title "BACK-006 - Implementar lógica de irrigação automática (UC-006)" `
    -Body @"
UC relacionado:
- UC-006 - Executar Irrigação Automática

Regras de negócio:
- RN-007 - Decisão de Irrigação
- RN-008 - Personalização por Planta
- RN-012 - Registro de histórico

Objetivo:
Implementar no backend a lógica que avalia a umidade recebida e decide automaticamente se deve acionar irrigação, registrando o resultado no histórico.

Escopo:
- Recuperar parâmetros ideais da espécie ou valores personalizados da planta (RN-008).
- Comparar umidade atual com a faixa ideal.
- Acionar irrigação se umidade < nível mínimo.
- Não acionar se umidade estiver dentro ou acima da faixa ideal.
- Registrar a decisão no histórico (RN-012): data/hora, tipo (automático), status (sucesso/falha).
- Agendar nova tentativa em caso de falha de comunicação com dispositivo.
- Gerar notificação ao usuário após 3 falhas em 20 minutos.

Critérios de aceite:
- Dada umidade abaixo do nível mínimo, quando a lógica for executada, então deve acionar irrigação e registrar no histórico.
- Dada umidade dentro da faixa ideal, quando a lógica for executada, então não deve acionar irrigação e deve registrar ausência de necessidade.
- Dada umidade acima da faixa, quando a lógica for executada, então não deve acionar irrigação e deve registrar alerta.
- Dado erro de comunicação com dispositivo, quando ocorrer, então deve registrar falha e agendar nova tentativa em 5 minutos.
- Dadas 3 falhas em até 20 minutos, quando ocorrerem, então deve gerar notificação ao usuário.
"@

New-CroopIssue `
    -Title "BACK-007 - Implementar endpoint de irrigação manual (UC-007)" `
    -Body @"
UC relacionado:
- UC-007 - Solicitar Irrigação Manual

Regras de negócio:
- RN-009 - Irrigação Manual Controlada
- RN-012 - Registro de histórico

Objetivo:
Implementar no backend o endpoint que permite ao usuário solicitar irrigação manual de uma planta vinculada a dispositivo.

Escopo:
- Validar que a planta pertence ao usuário autenticado.
- Verificar se a planta possui dispositivo vinculado.
- Verificar umidade atual da planta.
- Bloquear irrigação se umidade estiver acima do limite máximo (RN-009).
- Enviar comando de irrigação ao dispositivo.
- Registrar ação no histórico (RN-012): data/hora, tipo (manual), status.
- Retornar confirmação ou erro ao usuário.

Critérios de aceite:
- Dado usuário autenticado com planta vinculada, quando solicitar irrigação manual, então deve enviar comando ao dispositivo e retornar HTTP 200.
- Dada umidade acima do limite máximo, quando solicitada irrigação manual, então deve retornar HTTP 409 com mensagem de alerta.
- Dada falha de comunicação com dispositivo, quando a irrigação for solicitada, então deve retornar HTTP 503 e registrar falha.
- Toda irrigação manual executada deve gerar registro no histórico com tipo, data/hora e status.
"@

New-CroopIssue `
    -Title "BACK-008 - Implementar geração de cronograma de cuidados (UC-008)" `
    -Body @"
UC relacionado:
- UC-008 - Gerar Cronograma de Cuidados

Regras de negócio:
- RN-008 - Personalização por Planta
- RN-010 - Geração de Cronograma
- RN-012 - Registro de histórico

Objetivo:
Implementar no backend a lógica responsável por gerar automaticamente cronogramas personalizados de cuidados para cada planta do usuário.

Escopo:
- Identificar plantas cadastradas do usuário.
- Consultar parâmetros ideais da espécie e valores personalizados (RN-008).
- Analisar histórico de irrigação e leituras disponíveis.
- Calcular frequência ideal de cuidados considerando espécie, ambiente e histórico (RN-010).
- Definir horários e intervalos de irrigação.
- Persistir o cronograma gerado.
- Utilizar parâmetros padrão quando dados históricos estiverem ausentes.
- Retornar cronograma disponível ao usuário.

Critérios de aceite:
- Dado usuário com plantas cadastradas, quando o cronograma for gerado, então deve considerar espécie, ambiente e histórico disponível.
- Dado ausência de histórico, quando o cronograma for gerado, então deve utilizar valores base da espécie.
- Dado ambiente alterado na planta, quando o cronograma for recalculado, então deve refletir o novo ambiente.
- Dada personalização de umidade pelo usuário, quando o cronograma for gerado, então deve usar os valores personalizados.
"@

New-CroopIssue `
    -Title "BACK-009 - Implementar sistema de notificações (UC-009)" `
    -Body @"
UC relacionado:
- UC-009 - Receber Notificações

Regras de negócio:
- RN-011 - Notificações Inteligentes
- RN-012 - Registro de histórico

Objetivo:
Implementar no backend a lógica de geração, envio e registro de notificações ao usuário sobre eventos relevantes do sistema.

Escopo:
- Monitorar eventos relevantes: necessidade de irrigação, excesso de água, falha do sensor.
- Gerar notificação apenas quando necessário (RN-011).
- Não duplicar notificações do mesmo evento em intervalo inferior a 30 minutos (RN-011).
- Persistir notificações geradas no banco de dados.
- Registrar envio de cada notificação no histórico (RN-012).
- Disponibilizar endpoint para consulta de notificações do usuário.

Critérios de aceite:
- Dado evento relevante identificado, quando a lógica for executada, então deve gerar e registrar a notificação.
- Dado evento repetido em menos de 30 minutos, quando a lógica for executada, então não deve gerar nova notificação.
- Dado evento que não exija notificação, quando avaliado, então nenhum alerta deve ser gerado.
- Dado usuário autenticado, quando consultar notificações, então deve receber apenas suas próprias notificações.
"@

New-CroopIssue `
    -Title "BACK-010 - Implementar endpoint de consulta do histórico de cuidados (UC-010)" `
    -Body @"
UC relacionado:
- UC-010 - Consultar Histórico de Cuidados

Regras de negócio:
- RN-012 - Registro de histórico

Objetivo:
Implementar no backend o endpoint para consulta do histórico de cuidados do usuário, incluindo irrigações, leituras de sensores e notificações.

Escopo:
- Recuperar registros de irrigação, sensores e notificações do usuário autenticado.
- Organizar dados por data e hora.
- Implementar paginação para grandes volumes de dados.
- Garantir isolamento: usuário acessa apenas seu próprio histórico.
- Retornar erro adequado quando não houver registros ou ocorrer falha na consulta.

Critérios de aceite:
- Dado usuário autenticado com registros, quando consultar o histórico, então deve receber dados organizados por data e hora.
- Dado usuário sem registros, quando consultar o histórico, então deve retornar resposta vazia com HTTP 200.
- Dado grande volume de dados, quando o histórico for consultado, então os dados devem ser retornados com paginação.
- Dado usuário A tentando acessar histórico do usuário B, quando fizer a requisição, então deve retornar HTTP 403 ou 404.
"@
