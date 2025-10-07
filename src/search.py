import os
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def get_embeddings():
    """
    Retorna o modelo de embeddings baseado nas chaves de API configuradas.
    Prioriza OpenAI se ambas estiverem configuradas.
    """
    if OPENAI_API_KEY:
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        )
    elif GOOGLE_API_KEY:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
        )
    else:
        raise ValueError(
            "Nenhuma API key configurada. Configure OPENAI_API_KEY ou GOOGLE_API_KEY no arquivo .env"
        )


def get_llm():
    """
    Retorna o modelo LLM baseado nas chaves de API configuradas.
    Prioriza OpenAI se ambas estiverem configuradas.
    """
    if OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o-mini",  # Modelo válido (gpt-5-nano não existe)
            temperature=0
        )
    elif GOOGLE_API_KEY:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",  # Modelo válido (gemini-2.5-flash-lite não existe)
            temperature=0
        )
    else:
        raise ValueError(
            "Nenhuma API key configurada. Configure OPENAI_API_KEY ou GOOGLE_API_KEY no arquivo .env"
        )


def search_prompt(question=None):
    """
    Cria e retorna uma chain LangChain para busca semântica e geração de respostas.

    Args:
        question: Se fornecida, executa a busca imediatamente. Se None, retorna apenas a chain.

    Returns:
        Se question=None: retorna a chain configurada
        Se question fornecida: retorna a resposta da LLM
    """
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não configurado no arquivo .env")

    if not PG_VECTOR_COLLECTION_NAME:
        raise ValueError("PG_VECTOR_COLLECTION_NAME não configurado no arquivo .env")

    # Obter embeddings e LLM
    embeddings = get_embeddings()
    llm = get_llm()

    # Conectar ao vectorstore existente
    vectorstore = PGVector(
        collection_name=PG_VECTOR_COLLECTION_NAME,
        connection=DATABASE_URL,
        embeddings=embeddings
    )

    # Criar retriever que busca os top 10 documentos
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10}
    )

    # Criar prompt template
    prompt = PromptTemplate(
        input_variables=["contexto", "pergunta"],
        template=PROMPT_TEMPLATE
    )

    # Função para formatar os documentos recuperados
    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    # Criar a chain usando LCEL (LangChain Expression Language)
    chain = (
        {
            "contexto": retriever | format_docs,
            "pergunta": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    # Se uma pergunta foi fornecida, executa a chain
    if question:
        return chain.invoke(question)

    # Caso contrário, retorna a chain para uso posterior
    return chain


if __name__ == "__main__":
    # Teste rápido
    import sys

    if len(sys.argv) > 1:
        pergunta = " ".join(sys.argv[1:])
        print(f"PERGUNTA: {pergunta}")
        print(f"RESPOSTA: {search_prompt(pergunta)}")
    else:
        print("Uso: python search.py <sua pergunta>")
        print("Exemplo: python search.py Qual o faturamento da empresa?")
