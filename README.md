# Desafio MBA Engenharia de Software com IA - Full Cycle

## Ingestão e Busca Semântica com LangChain e PostgreSQL + pgVector

Sistema RAG (Retrieval-Augmented Generation) para ingestão de documentos PDF e busca semântica com respostas baseadas exclusivamente no conteúdo do documento.

---

## 🎯 Objetivo

Este projeto implementa:

1. **Ingestão**: Lê um arquivo PDF e armazena suas informações em um banco de dados PostgreSQL com extensão pgVector
2. **Busca**: Permite que o usuário faça perguntas via linha de comando (CLI) e receba respostas baseadas **apenas** no conteúdo do PDF

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.13+
- **Framework**: LangChain
- **Banco de Dados**: PostgreSQL 17 + pgVector
- **Execução**: Docker & Docker Compose
- **LLM Provider**: Google Gemini (alternativa: OpenAI)

---

## 📋 Pré-requisitos

- Python 3.13 ou superior
- Docker e Docker Compose
- API Key do Google Gemini ou OpenAI

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd mba-ia-desafio-ingestao-busca
```

### 2. Configure o ambiente virtual Python

```bash
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure sua API key:

**Para Google Gemini (Recomendado para este projeto):**
```bash
GOOGLE_API_KEY=sua_chave_aqui
GOOGLE_EMBEDDING_MODEL=models/text-embedding-004
```

**Ou para OpenAI:**
```bash
OPENAI_API_KEY=sk-sua_chave_aqui
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

As demais variáveis já estão pré-configuradas:
- `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag`
- `PG_VECTOR_COLLECTION_NAME=pdf_embeddings`
- `PDF_PATH=./document.pdf`

### 5. Inicie o banco de dados PostgreSQL

```bash
docker compose up -d
```

Aguarde alguns segundos para o banco inicializar. Você pode verificar o status com:

```bash
docker compose ps
```

---

## 📖 Como Executar

### Passo 1: Ingerir o PDF

Execute o script de ingestão para carregar o documento no banco de dados:

```bash
python src/ingest.py
```

**Saída esperada:**
```
Carregando PDF: ./document.pdf
✓ 34 página(s) carregada(s)

Dividindo documento em chunks...
✓ 67 chunk(s) criado(s)

Obtendo modelo de embeddings...
Usando Google Generative AI Embeddings...

Armazenando chunks no banco de dados (collection: pdf_embeddings)...

✅ Ingestão concluída com sucesso!
   - 67 chunks armazenados
   - Collection: pdf_embeddings
   - Banco de dados: localhost:5432/rag
```

### Passo 2: Executar o Chat

Inicie a interface de chat interativa:

```bash
python src/chat.py
```

**Exemplo de uso:**

```
============================================================
  RAG Chat - Pergunte sobre o documento PDF
============================================================

Digite 'sair', 'exit' ou 'quit' para encerrar
Digite 'limpar' ou 'clear' para limpar a tela

✓ Sistema iniciado com sucesso!

PERGUNTA: Qual o faturamento da Alfa Energia S.A.?

🔍 Buscando informações...

RESPOSTA: R$ 722.875.391,46

------------------------------------------------------------

PERGUNTA: Quando a Alfa Agronegócio Indústria foi fundada?

🔍 Buscando informações...

RESPOSTA: 1931

------------------------------------------------------------

PERGUNTA: Qual é a capital da França?

🔍 Buscando informações...

RESPOSTA: Não tenho informações necessárias para responder sua pergunta.

------------------------------------------------------------
```

---

## ✅ Validação do Sistema

O sistema **responde apenas com base no contexto** do PDF. Perguntas fora do escopo retornam a mensagem padrão:

### ✅ Perguntas dentro do contexto (respondidas):
- "Qual o faturamento da Alfa Energia S.A.?" → **R$ 722.875.391,46**
- "Quando a Alfa Agronegócio Indústria foi fundada?" → **1931**

### ❌ Perguntas fora do contexto (recusadas):
- "Qual é a capital da França?" → **Não tenho informações necessárias para responder sua pergunta.**
- "Quantos clientes temos em 2024?" → **Não tenho informações necessárias para responder sua pergunta.**
- "Você acha isso bom ou ruim?" → **Não tenho informações necessárias para responder sua pergunta.**

---

## 🔧 Comandos Úteis

### Parar o banco de dados
```bash
docker compose down
```

### Parar e remover volumes (limpa dados)
```bash
docker compose down -v
```

### Verificar logs do PostgreSQL
```bash
docker compose logs postgres
```

### Re-ingestão (limpar e recarregar)
```bash
python src/ingest.py
```
O script automaticamente remove a collection anterior antes de criar uma nova.

### Teste rápido sem interface interativa
```bash
python src/search.py "Sua pergunta aqui"
```

---

## 📁 Estrutura do Projeto

```
├── docker-compose.yml          # Configuração PostgreSQL + pgVector
├── requirements.txt            # Dependências Python
├── .env.example                # Template de variáveis de ambiente
├── .env                        # Variáveis de ambiente (não commitado)
├── document.pdf                # PDF para ingestão
├── src/
│   ├── ingest.py              # Script de ingestão do PDF
│   ├── search.py              # Módulo de busca semântica
│   └── chat.py                # Interface CLI para chat
├── CLAUDE.md                   # Documentação para Claude Code
├── PLANO_EXECUCAO.md          # Plano detalhado de desenvolvimento
└── README.md                   # Este arquivo
```

---

## 🧪 Detalhes Técnicos

### Ingestão (src/ingest.py)
- Carrega PDF usando `PyPDFLoader`
- Divide em chunks de **1000 caracteres** com **overlap de 150**
- Gera embeddings usando modelo configurado
- Armazena vetores no PostgreSQL com pgVector

### Busca (src/search.py)
- Conecta ao vectorstore existente
- Busca os **top 10 documentos** mais relevantes (k=10)
- Monta prompt com contexto recuperado
- Usa LLM para gerar resposta baseada apenas no contexto
- Implementado com **LCEL** (LangChain Expression Language)

### Chat (src/chat.py)
- Interface CLI interativa
- Loop de perguntas e respostas
- Comandos especiais: `sair`, `exit`, `quit`, `limpar`, `clear`
- Formatação colorida no terminal

### Prompt Template
O sistema usa um prompt rigoroso que:
- Instrui a LLM a responder **apenas** com base no contexto
- Fornece exemplos de perguntas fora do escopo
- Define mensagem padrão para respostas não encontradas

---

## 🔑 Obtendo API Keys

### Google Gemini (Grátis)
1. Acesse https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

### OpenAI (Pago)
1. Acesse https://platform.openai.com/api-keys
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave gerada

---

## 🐛 Troubleshooting

### Erro: "Quota exceeded" (Gemini)
- A API gratuita do Gemini tem limites diários
- Solução 1: Aguarde o reset da cota (24 horas)
- Solução 2: Crie uma nova API key
- Solução 3: Use modelo `text-embedding-004` no `.env`
- Solução 4: Configure uma API key da OpenAI

### Erro: "Connection refused" (PostgreSQL)
- Verifique se o Docker está rodando: `docker compose ps`
- Reinicie o banco: `docker compose restart postgres`
- Aguarde alguns segundos para inicialização completa

### Erro: "Collection not found"
- Execute a ingestão primeiro: `python src/ingest.py`

### Erro: "No API key configured"
- Verifique se o arquivo `.env` existe e está configurado
- Certifique-se de ter adicionado `GOOGLE_API_KEY` ou `OPENAI_API_KEY`

---

## 📚 Requisitos do Desafio

- ✅ Ingestão de PDF com chunks de 1000 caracteres e overlap de 150
- ✅ Armazenamento em PostgreSQL com pgVector
- ✅ Busca dos top 10 documentos mais relevantes (k=10)
- ✅ Respostas baseadas exclusivamente no contexto
- ✅ Mensagem padrão para perguntas fora do escopo
- ✅ Interface CLI interativa
- ✅ Suporte para OpenAI e Google Gemini
- ✅ Docker Compose para banco de dados
- ✅ Documentação completa

---

## 👨‍💻 Autor

Desenvolvido como parte do desafio do MBA em Engenharia de Software com IA - Full Cycle

---

## 📄 Licença

Este projeto é parte de um desafio educacional.
