# Plano de Execução - Desafio Ingestão e Busca Semântica

## Visão Geral
Desenvolvimento de um sistema RAG (Retrieval-Augmented Generation) para ingestão de PDF e busca semântica usando LangChain, PostgreSQL com pgVector, e LLMs (OpenAI ou Gemini).

---

## Fase 1: Configuração do Ambiente

### 1.1 Infraestrutura
- [x] Docker Compose configurado com PostgreSQL + pgVector
- [x] Estrutura de pastas criada (`src/`, arquivos base)
- [ ] Arquivo `.env` configurado com as chaves de API

### 1.2 Dependências Python
- [x] Virtual environment criado (`.venv/`)
- [x] `requirements.txt` com todas as dependências
- [ ] Validar instalação: `pip install -r requirements.txt`

### 1.3 Variáveis de Ambiente
Criar `.env` baseado em `.env.example`:
```
GOOGLE_API_KEY=sua_chave_aqui          # OU
OPENAI_API_KEY=sua_chave_aqui

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=pdf_embeddings
PDF_PATH=./document.pdf

# Modelos
GOOGLE_EMBEDDING_MODEL=models/embedding-001
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

---

## Fase 2: Implementação da Ingestão (`src/ingest.py`)

### 2.1 Carregamento do PDF
```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader(PDF_PATH)
documents = loader.load()
```

### 2.2 Divisão em Chunks
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)
chunks = text_splitter.split_documents(documents)
```

### 2.3 Configuração de Embeddings
**Opção 1 - OpenAI:**
```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)
```

**Opção 2 - Gemini:**
```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001"
)
```

### 2.4 Armazenamento no PGVector
```python
from langchain_postgres import PGVector

vectorstore = PGVector.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name=PG_VECTOR_COLLECTION_NAME,
    connection=DATABASE_URL
)
```

### 2.5 Validação
- [ ] Executar `python src/ingest.py`
- [ ] Verificar no PostgreSQL se a collection foi criada
- [ ] Confirmar que os embeddings foram armazenados

---

## Fase 3: Implementação da Busca (`src/search.py`)

### 3.1 Conexão com o Banco Vetorial
```python
from langchain_postgres import PGVector

vectorstore = PGVector(
    collection_name=PG_VECTOR_COLLECTION_NAME,
    connection=DATABASE_URL,
    embeddings=embeddings  # Mesmo modelo usado na ingestão
)
```

### 3.2 Função de Busca Semântica
```python
def search_prompt(question):
    # Buscar os 10 documentos mais relevantes
    results = vectorstore.similarity_search_with_score(
        question,
        k=10
    )

    # Concatenar contexto
    context = "\n".join([doc.page_content for doc, score in results])

    # Montar prompt
    prompt = PROMPT_TEMPLATE.format(
        contexto=context,
        pergunta=question
    )

    return prompt
```

### 3.3 Integração com LLM
**Opção 1 - OpenAI:**
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",  # ou gpt-3.5-turbo
    temperature=0
)
```

**Opção 2 - Gemini:**
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0
)
```

### 3.4 Chain de Execução
```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def search_prompt(question):
    results = vectorstore.similarity_search_with_score(question, k=10)
    context = "\n".join([doc.page_content for doc, _ in results])

    prompt_template = PromptTemplate(
        input_variables=["contexto", "pergunta"],
        template=PROMPT_TEMPLATE
    )

    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run(contexto=context, pergunta=question)

    return response
```

---

## Fase 4: Interface CLI (`src/chat.py`)

### 4.1 Loop Interativo
```python
from search import search_prompt

def main():
    print("=== Chat RAG - Pergunte sobre o documento ===")
    print("Digite 'sair' para encerrar\n")

    while True:
        question = input("PERGUNTA: ").strip()

        if question.lower() in ['sair', 'exit', 'quit']:
            print("Encerrando chat...")
            break

        if not question:
            continue

        try:
            response = search_prompt(question)
            print(f"RESPOSTA: {response}\n")
            print("-" * 50 + "\n")
        except Exception as e:
            print(f"Erro ao processar pergunta: {e}\n")

if __name__ == "__main__":
    main()
```

### 4.2 Melhorias Opcionais
- [ ] Validação de entrada
- [ ] Tratamento de erros mais robusto
- [ ] Histórico de conversas
- [ ] Indicador de carregamento durante busca

---

## Fase 5: Testes e Validação

### 5.1 Testes de Ingestão
- [ ] Verificar se o PDF é carregado corretamente
- [ ] Confirmar número de chunks gerados
- [ ] Validar embeddings no banco de dados

### 5.2 Testes de Busca
**Perguntas dentro do contexto:**
- [ ] Testar perguntas que devem ter respostas no PDF
- [ ] Validar qualidade das respostas

**Perguntas fora do contexto:**
- [ ] "Qual é a capital da França?"
  - Esperado: "Não tenho informações necessárias para responder sua pergunta."
- [ ] "Quantos clientes temos em 2024?"
  - Esperado: "Não tenho informações necessárias para responder sua pergunta."
- [ ] "Você acha isso bom ou ruim?"
  - Esperado: "Não tenho informações necessárias para responder sua pergunta."

### 5.3 Testes de Edge Cases
- [ ] PDF vazio ou corrompido
- [ ] Perguntas muito longas
- [ ] Caracteres especiais na pergunta
- [ ] Conexão com banco falhando

---

## Fase 6: Documentação

### 6.1 README.md
Atualizar com:
- [ ] Descrição do projeto
- [ ] Pré-requisitos (Python 3.13+, Docker, API Keys)
- [ ] Instruções de instalação passo a passo
- [ ] Comandos de execução
- [ ] Exemplos de uso
- [ ] Troubleshooting comum

### 6.2 Comentários no Código
- [ ] Docstrings em todas as funções
- [ ] Comentários explicativos em lógica complexa
- [ ] Type hints onde aplicável

---

## Fase 7: Checklist Final

### Estrutura do Projeto
```
├── docker-compose.yml        ✓
├── requirements.txt          ✓
├── .env.example              ✓
├── .env                      (criar localmente)
├── src/
│   ├── ingest.py            (implementar)
│   ├── search.py            (implementar)
│   └── chat.py              (implementar)
├── document.pdf              ✓
├── README.md                 (atualizar)
└── CLAUDE.md                 ✓
```

### Ordem de Execução Final
1. [ ] `docker compose up -d`
2. [ ] Verificar saúde do PostgreSQL
3. [ ] `python src/ingest.py`
4. [ ] Confirmar ingestão bem-sucedida
5. [ ] `python src/chat.py`
6. [ ] Realizar testes de validação

### Requisitos Técnicos
- [ ] Chunks de 1000 caracteres com overlap de 150
- [ ] Busca retorna top 10 resultados (k=10)
- [ ] Prompt template exatamente como especificado
- [ ] Respostas apenas baseadas no contexto
- [ ] Mensagem padrão para perguntas fora do escopo

---

## Observações Importantes

### Escolha do Provider
- **OpenAI**: Modelos mais conhecidos, documentação extensa
  - Embedding: `text-embedding-3-small`
  - LLM: `gpt-4o-mini` (substituir `gpt-5-nano` que não existe)

- **Gemini**: Gratuito até certo limite, boa performance
  - Embedding: `models/embedding-001`
  - LLM: `gemini-2.0-flash-exp` (substituir `gemini-2.5-flash-lite` que não existe)

### Atenção aos Nomes dos Modelos
Os modelos especificados no `.prompt` não existem:
- ❌ `gpt-5-nano` → ✅ `gpt-4o-mini` ou `gpt-3.5-turbo`
- ❌ `gemini-2.5-flash-lite` → ✅ `gemini-2.0-flash-exp` ou `gemini-1.5-flash`

### Segurança
- [ ] Nunca commitar o arquivo `.env`
- [ ] `.env` está no `.gitignore`
- [ ] API Keys mantidas seguras

---

## Próximos Passos

1. **Imediato**: Implementar `src/ingest.py` completamente
2. **Seguinte**: Implementar `src/search.py` com chain LangChain
3. **Depois**: Implementar `src/chat.py` com loop interativo
4. **Final**: Testes, documentação e entrega no GitHub
