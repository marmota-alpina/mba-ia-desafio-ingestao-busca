from search import search_prompt


def main():
    """
    Interface de chat interativa via CLI.
    Permite ao usuário fazer perguntas sobre o PDF ingerido.
    """
    print("=" * 60)
    print("  RAG Chat - Pergunte sobre o documento PDF")
    print("=" * 60)
    print("\nDigite 'sair', 'exit' ou 'quit' para encerrar")
    print("Digite 'limpar' ou 'clear' para limpar a tela\n")

    try:
        # Inicializa a chain (sem pergunta, apenas retorna a chain configurada)
        chain = search_prompt()
        print("✓ Sistema iniciado com sucesso!\n")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar o sistema: {e}")
        print("\nVerifique se:")
        print("  1. O arquivo .env está configurado corretamente")
        print("  2. O PostgreSQL está rodando (docker compose up -d)")
        print("  3. A ingestão foi executada (python src/ingest.py)")
        return

    # Loop principal do chat
    while True:
        try:
            # Solicita pergunta do usuário
            question = input("\n\033[1;34mPERGUNTA:\033[0m ").strip()

            # Comandos especiais
            if question.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Encerrando chat. Até logo!")
                break

            if question.lower() in ['limpar', 'clear']:
                import os
                os.system('clear' if os.name != 'nt' else 'cls')
                print("=" * 60)
                print("  RAG Chat - Pergunte sobre o documento PDF")
                print("=" * 60)
                continue

            # Ignora perguntas vazias
            if not question:
                continue

            # Processa a pergunta
            print("\n\033[2m🔍 Buscando informações...\033[0m")
            response = chain.invoke(question)

            # Exibe resposta
            print(f"\n\033[1;32mRESPOSTA:\033[0m {response}")
            print("\n" + "-" * 60)

        except KeyboardInterrupt:
            print("\n\n👋 Encerrando chat. Até logo!")
            break
        except Exception as e:
            print(f"\n\033[1;31m❌ Erro ao processar pergunta:\033[0m {e}")
            print("\nTente novamente ou digite 'sair' para encerrar.")


if __name__ == "__main__":
    main()
