<img src="assets/doc-eng.jpeg" alt="Engenheiro de MLOps Orquestrando Agentes" width="500"/>

# Clinic Agentic Platform

Plataforma baseada em **Google ADK (Agent Development Kit)** e **google-agents-cli** para orquestração inteligente de atendimento clínico.

---

## Objetivo do Projeto

O **AI Patient Care Orchestrator** é um agente conversacional inteligente projetado para clínicas médicas. Suas responsabilidades principais são:

- **Agendamento de consultas**: Gerenciar marcação, remarcação e cancelamento de horários com base na disponibilidade da clínica através de um sub-agente dedicado.
- **RAG de Protocolos Clínicos**: Responder dúvidas de profissionais de saúde com base em documentos institucionais — manuais de conduta, protocolos e diretrizes clínicas — utilizando **Vertex AI Search** para respostas ancoradas (grounded responses).

O agente **não realiza diagnósticos** nem substitui avaliação médica, atuando exclusivamente como suporte administrativo e informacional.

---

## Arquitetura Técnica

O projeto adota o padrão **Supervisor-Worker (Multi-Agente)**. O agente principal (Root) atua como roteador e orquestrador de intenções, delegando tarefas complexas de escrita e estado para sub-agentes especialistas e consultas semânticas para o motor de RAG.

| Camada              | Tecnologia                                 |
| ------------------- | ------------------------------------------ |
| Framework Agent     | google-agents-cli v0.1.3 + Google ADK      |
| Modelo de Linguagem | Gemini 2.0 Flash                           |
| RAG / Ancoragem     | Vertex AI Search (Agent Platform Search)   |
| Infraestrutura      | Cloud Run + Terraform (`agents-cli infra`) |
| Observabilidade     | Cloud Logging + Cloud Trace                |
| Gerenciamento       | `uv` para dependências Python              |

### Diagrama da Arquitetura

![Diagrama de Arquitetura do Sistema](assets/arch.jpeg)

### Descrição dos Diretórios

- **agent-core/app**: Código do agente ADK — `agent.yaml`, ferramentas (agendamento, RAG), sub-agentes e lógica de orquestração em Python.
- **agent-core/deployment**: Infraestrutura como código (IaC) usando Terraform. Prepara Cloud Run, papéis do IAM, APIs e o datastore do Vertex AI Search.
- **agent-core/evals**: Contém o _Golden Dataset_ com casos capciosos para testar regressão e segurança do modelo antes do deploy.
- **agent-core/sample_data**: Conjunto de documentos de exemplo (PDFs, markdown) para popular o datastore RAG.

---

## Fluxo de Trabalho (ADLC — Ciclo de Vida de Desenvolvimento do Agente)

```bash
# 1. Instalar dependências do agente e ferramentas de avaliação
cd agent-core && uv sync --extra eval

# 2. Provisionar infraestrutura do datastore (Vertex AI Search) no escopo global
agents-cli infra datastore

# 3. Ingerir e indexar documentos no datastore RAG
agents-cli data-ingestion

# 4. Executar os testes de qualidade linguística e segurança (LLM-as-a-Judge)
agents-cli eval run --evalset evals/golden_dataset.json --config tests/eval/eval_config.json

# 5. Executar o playground interativo local para testar o agente
agents-cli playground

```

### Comandos Adicionais

| Comando                       | Descrição                                        |
| ----------------------------- | ------------------------------------------------ |
| `agents-cli lint`             | Verifica a qualidade e formatação do código      |
| `agents-cli deploy`           | Realiza o deploy da imagem para o Cloud Run      |
| `agents-cli publish`          | Publicar no Gemini Enterprise (Google Workspace) |
| `agents-cli scaffold enhance` | Adicionar esteira de CI/CD corporativa           |

---

## Segurança, Compliance e MLOps

O projeto aplica engenharia de software rigorosa para mitigar riscos comuns em IA Generativa aplicada à saúde:

- **Proteção de Dados (LGPD/HIPAA):** A tipagem com **Pydantic** e o parâmetro `Field(pattern=...)` validam inputs estritamente na camada de código. Nenhuma informação pessoal identificável (PII) é exposta em logs ou respostas.
- **Proibição de Diagnósticos Automáticos:** O agente é blindado via instruções de sistema na arquitetura Multi-Agente. Tentativas de obter prescrições disparam uma cláusula de barreira imediata redirecionando o usuário para o 192 (SAMU).
- **Esteira de LLMOps Automatizada:** O pipeline configurado no GitHub Actions roda testes funcionais e de comportamento de IA a cada integração. Se a nota do juiz (LLM Judge) for inferior ao limite configurado (0.8), a build falha e o deploy é bloqueado.
- **Rastreabilidade Ponta a Ponta:** OpenTelemetry integrado nativamente captura cada span de execução (`call_llm`, `tool_execution`), facilitando a auditoria SRE de custos de tokens e gargalos de latência.

---

## Stack Tecnológica

```
Python 3.11+ | Google ADK | google-agents-cli v0.1.3 | Gemini 2.0 Flash
Vertex AI Search | Cloud Run | Terraform | Cloud Trace | Cloud Logging | uv

```

---

## Prova de Conceito (PoC) & Validação Local

Os testes locais utilizando o `agents-cli playground` evidenciam o comportamento correto e determinístico do ecossistema de agentes diante de diferentes cenários.

### 1. Interação e Guardrails de Segurança

O agente foi submetido a cenários de teste críticos:

- **Casos de Emergência/Diagnóstico:** Ao relatar sintomas de infarto, o agente aplicou imediatamente as diretrizes de segurança, recusando o diagnóstico e instruindo o paciente a buscar atendimento médico de emergência.
- **Processo de Coleta de Parâmetros (Slot Filling):** Ao solicitar um agendamento informando dados parciais, o agente identificou a ambiguidade temporal ("amanhã") e a falta de identificação, solicitando ativamente a data exata e o sobrenome do paciente antes de delegar a execução ao sub-agente.

---

### 2. Observabilidade e Rastreamento de Traces (Spans)

Através do painel de rastreamento do ADK, monitoramos o ciclo de vida de cada requisição. O agente registrou com sucesso a hierarquia de execução das chamadas (`root_agent` -> `call_llm` -> `generate_content`), permitindo analisar métricas de latência ponta a ponta e auditar o comportamento do modelo.

---

### 3. Simulação do Canal de Atendimento (WhatsApp)

Desenvolvemos uma interface estática simulando a experiência final do paciente em canais de mensageria rápida. Os testes demonstram o fluxo de conversação fluido, a retenção de estado da máquina de diálogos e o disparo simulado da ferramenta (`book_appointment`) após a coleta dos dados obrigatórios.

---

### POC

![Simulação do Atendimento via WhatsApp](assets/wapp.jpg)

![Interface de Chat do Playground](assets/cap-01.jpg)

![Métricas de Latência e Traces de Execução](assets/cap-02.jpg)
