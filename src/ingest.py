import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
DATABASE_URL = os.getenv("DATABASE_URL")
PG_VECTOR_COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def get_embeddings():
    """
    Retorna o modelo de embeddings baseado nas chaves de API configuradas.
    Prioriza OpenAI se ambas estiverem configuradas.
    """
    if OPENAI_API_KEY:
        from langchain_openai import OpenAIEmbeddings
        print("Usando OpenAI Embeddings...")
        return OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        )
    elif GOOGLE_API_KEY:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        print("Usando Google Generative AI Embeddings...")
        return GoogleGenerativeAIEmbeddings(
            model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
        )
    else:
        raise ValueError(
            "Nenhuma API key configurada. Configure OPENAI_API_KEY ou GOOGLE_API_KEY no arquivo .env"
        )


def ingest_pdf():
    """
    Carrega o PDF, divide em chunks e armazena no banco de dados PostgreSQL com pgVector.
    """
    if not PDF_PATH:
        raise ValueError("PDF_PATH não configurado no arquivo .env")

    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {PDF_PATH}")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não configurado no arquivo .env")

    if not PG_VECTOR_COLLECTION_NAME:
        raise ValueError("PG_VECTOR_COLLECTION_NAME não configurado no arquivo .env")

    print(f"Carregando PDF: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    print(f"✓ {len(documents)} página(s) carregada(s)")

    print("\nDividindo documento em chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✓ {len(chunks)} chunk(s) criado(s)")

    print("\nObtendo modelo de embeddings...")
    embeddings = get_embeddings()

    print(f"\nArmazenando chunks no banco de dados (collection: {PG_VECTOR_COLLECTION_NAME})...")

    # Remove collection anterior se existir (para re-ingestão limpa)
    try:
        PGVector.drop_collection(
            collection_name=PG_VECTOR_COLLECTION_NAME,
            connection=DATABASE_URL
        )
        print(f"✓ Collection '{PG_VECTOR_COLLECTION_NAME}' anterior removida")
    except Exception:
        pass  # Collection não existia ainda

    vectorstore = PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=PG_VECTOR_COLLECTION_NAME,
        connection=DATABASE_URL,
        pre_delete_collection=False  # Já removemos manualmente acima
    )

    print(f"\n✅ Ingestão concluída com sucesso!")
    print(f"   - {len(chunks)} chunks armazenados")
    print(f"   - Collection: {PG_VECTOR_COLLECTION_NAME}")
    print(f"   - Banco de dados: {DATABASE_URL.split('@')[-1]}")


if __name__ == "__main__":
    try:
        ingest_pdf()
    except Exception as e:
        print(f"\n❌ Erro durante a ingestão: {e}")
        raise
