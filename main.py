import os
import tiktoken

# Função para corrigir o caminho e garantir que as barras invertidas sejam duplicadas
def fix_path(path):
    return path.replace("\\", "\\\\")  # Substitui todas as barras invertidas simples por barras invertidas duplas

# Função para contar os tokens de um texto
def count_tokens(text):
    encoding = tiktoken.get_encoding("cl100k_base")  # Usando o encoding de GPT-4
    tokens = encoding.encode(text)
    return len(tokens)

# Função para processar diretório e dividir os arquivos Java
def process_directory(directory, output_file_prefix, max_tokens_per_file=2000):
    file_counter = 1
    current_tokens = 0
    current_output_file = f'{output_file_prefix}_{file_counter}.txt'
    out_file = open(current_output_file, 'w', encoding='utf-8')

    try:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as java_file:
                        content = java_file.read()

                        # Contar tokens do conteúdo do arquivo
                        content_tokens = count_tokens(content)

                        # Se o arquivo inteiro não couber, divida-o em partes menores
                        if content_tokens > max_tokens_per_file:
                            start = 0
                            while start < len(content):
                                chunk = content[start:start + (max_tokens_per_file * 4)]
                                chunk_tokens = count_tokens(chunk)

                                if current_tokens + chunk_tokens > max_tokens_per_file:
                                    out_file.close()
                                    file_counter += 1
                                    current_output_file = f'{output_file_prefix}_{file_counter}.txt'
                                    out_file = open(current_output_file, 'w', encoding='utf-8')
                                    current_tokens = 0

                                out_file.write(f'// Parte do arquivo {file_path}\n')
                                out_file.write(chunk)
                                out_file.write('\n\n')
                                current_tokens += chunk_tokens
                                start += len(chunk)
                        else:
                            # Se ultrapassar o limite de tokens do arquivo atual, crie um novo
                            if current_tokens + content_tokens > max_tokens_per_file:
                                out_file.close()
                                file_counter += 1
                                current_output_file = f'{output_file_prefix}_{file_counter}.txt'
                                out_file = open(current_output_file, 'w', encoding='utf-8')
                                current_tokens = 0

                            # Escreva o arquivo normalmente
                            out_file.write(f'// Conteúdo de {file_path}\n')
                            out_file.write(content)
                            out_file.write('\n')
                            current_tokens += content_tokens
    finally:
        if not out_file.closed:
            out_file.close()

    print(f'Arquivos Java processados e divididos em arquivos com prefixo {output_file_prefix}_*.txt.')

# Caminho do diretório do seu projeto Java
if __name__ == '__main__':
    directory_path = r'C:\Users\Usuario\IdeaProjects\Github\EngSoft2-Project3\src\main\java\br\com\catolicapb\project3\model'  # Caminho do diretório
    directory_path = fix_path(directory_path)  # Corrigir o caminho
    output_file_prefix = 'output'  # Prefixo para os arquivos de saída
    max_tokens_per_file = 4000  # Limite de tokens por arquivo para facilitar cópia no chat
    process_directory(directory_path, output_file_prefix, max_tokens_per_file)
