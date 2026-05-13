# Clinic Agentic Platform

Plataforma baseada em **Google ADK (Agent Development Kit)** e **google-agents-cli** para orquestração inteligente de atendimento clínico.

---

## Objetivo do Projeto

O **AI Patient Care Orchestrator** é um agente conversacional inteligente projetado para clínicas médicas. Suas responsabilidades principais são:

- **Agendamento de consultas**: Gerenciar marcação, remarcação e cancelamento de horários com base na disponibilidade da clínica.
- **RAG de Protocolos Clínicos**: Responder dúvidas de profissionais de saúde com base em documentos institucionais — manuais de conduta, protocolos e diretrizes clínicas — utilizando **Vertex AI Search** para grounded responses.

O agente **não realiza diagnósticos** nem substitui avaliação médica, atuando exclusivamente como suporte administrativo e informacional.

---

## Arquitetura Técnica

| Camada            | Tecnologia                                  |
| ----------------- | ------------------------------------------- |
| Framework Agent   | google-agents-cli v0.1.3 + Google ADK       |
| Modelo de Linguagem | Gemini 2.0 Flash                          |
| RAG / Grounding   | Vertex AI Search (Agent Platform Search)    |
| Infraestrutura    | Cloud Run + Terraform (`agents-cli infra`)  |
| Observabilidade   | Cloud Logging + Cloud Trace                 |
| Gerenciamento     | `uv` para dependências Python               |

### Fluxo de Dados

```
Usuário → Gemini 2.0 Flash (ADK Agent) → Tools (Agendamento / RAG)
         → Vertex AI Search (grounding) → Resposta contextualizada
```

---

## Estrutura de Pastas

```
/
├── AI_CONTEXT.md         # Memória persistente do assistente (contexto do projeto)
├── README.md             # Este documento
├── agent-core/           # Núcleo do agente — código-fonte, configuração e lógica
│   ├── app/
│   │   ├── agent.yaml    # Definição do agente (system instructions, tools, modelos)
│   │   └── ...           # Tools e callbacks implementados em Python/ADK
│   ├── deployment/       # IaC — Terraform e configuração para Cloud Run
│   ├── sample_data/      # Documentos de exemplo para ingestão no datastore RAG
│   ├── tests/            # Testes unitários e de integração
│   ├── pyproject.toml    # Dependências gerenciadas via uv
│   └── uv.lock           # Lockfile das dependências
└── .gitignore
```

### Descrição dos Diretórios

- **agent-core/app**: Código do agente ADK — `agent.yaml`, tools (agendamento, RAG), callbacks e lógica de orquestração.
- **agent-core/deployment**: Infraestrutura como código (IaC) usando Terraform. Provisiona Cloud Run, IAM, APIs e o datastore do Vertex AI Search.
- **agent-core/sample_data**: Conjunto de documentos de exemplo (PDFs, markdown) para popular o datastore RAG. Substituir pelos documentos reais da clínica antes da ingestão.

---

## Fluxo de Trabalho (ADLC — Agent Development Lifecycle)

```bash
# 1. Instalar dependências do agente
cd agent-core && agents-cli install

# 2. Provisionar infraestrutura do datastore (Vertex AI Search)
agents-cli infra datastore

# 3. Ingerir documentos no datastore RAG
agents-cli data-ingestion

# 4. Executar o playground interativo para testar o agente
agents-cli playground
```

### Comandos Adicionais

| Comando                        | Descrição                                      |
| ------------------------------ | ---------------------------------------------- |
| `agents-cli eval`              | Avaliar o agente com conjuntos de teste         |
| `agents-cli deploy`            | Fazer deploy para Cloud Run                    |
| `agents-cli publish`           | Publicar no Gemini Enterprise (Google Workspace)|
| `agents-cli scaffold enhance`  | Adicionar CI/CD, domínio customizado etc.       |

---

## Segurança e Compliance

O projeto segue boas práticas de segurança para ambientes de saúde:

- **LGPD (Lei Geral de Proteção de Dados)** e **HIPAA (Health Insurance Portability and Accountability Act)**: Nenhuma informação pessoal identificável (PII) é exposta em logs, respostas ou traces.
- **Proibição de diagnósticos automáticos**: O agente é explicitamente instruído via `agent.yaml` a **não** emitir diagnósticos, prognósticos ou prescrições. Seu papel limita-se a agendamento e consulta a documentos clínicos previamente aprovados.
- **Auditoria**: Todas as interações são logadas no Cloud Logging para rastreabilidade.
- **Grounding obrigatório**: Respostas baseadas em RAG são sempre grounded no datastore — o modelo não pode inventar protocolos ou diretrizes.

---

## Stack Tecnológica

```
Python 3.11+ | Google ADK | google-agents-cli v0.1.3 | Gemini 2.0 Flash
Vertex AI Search | Cloud Run | Terraform | Cloud Logging | uv
```

---

## Licença

Proprietário — LDP Labs Clinic. Uso interno e controlado.
