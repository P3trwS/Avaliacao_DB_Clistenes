from datetime import datetime
import connbd as conn
import pandas as pd

def inserir_livro(titulo: str, autor: str, ano: int):
    livro = {"titulo": titulo, "autor": autor, "ano": ano, "disponivel": True}
    livros.insert_one(livro)
    print(f"Livro '{titulo}' inserido com sucesso.")

def consultar_livro_especifico(titulo: str):
    livro = livros.find_one({"titulo": titulo})
    if livro:
        print(f"Livro encontrado: {livro.get('titulo')}, {livro.get('autor')}, {livro.get('ano')}")
    else:
        print("Livro não encontrado.")

def consultar_livro_todos():
    todos_livros = livros.find()
    for livro in todos_livros:
        disponivel = "Sim" if livro["disponivel"] else "Não"
        print(f"Título: {livro['titulo']}, Autor: {livro['autor']}, Ano: {livro['ano']}, Disponível: {disponivel}")

def atualizar_livro(titulo: str, novos_dados):
    resultado = livros.update_one({"titulo": titulo}, {"$set": novos_dados})
    if resultado.modified_count > 0:
        print("Livro atualizado com sucesso.")
    else:
        print("Livro não encontrado ou dados iguais aos existentes.")


def deletar_livro(titulo: str):
    resultado = livros.delete_one({"titulo": titulo})
    if resultado.deleted_count > 0:
        print("Livro deletado com sucesso.")
    else:
        print("Livro não encontrado.")


def inserir_usuario(nome: str, email = "Sem email"):
    usuario = {"nome": nome, "email": email}
    usuarios.insert_one(usuario)
    print(f"Usuário '{nome}' inserido com sucesso.")


def consultar_usuario(nome: str):
    usuario = usuarios.find_one({"nome": nome})
    if usuario:
        print(f"Usuário encontrado: {usuario}")
    else:
        print("Usuário não encontrado.")


def atualizar_usuario(nome: str, novos_dados):
    resultado = usuarios.update_one({"nome": nome}, {"$set": novos_dados})
    if resultado.modified_count > 0:
        print("Usuário atualizado com sucesso.")
    else:
        print("Usuário não encontrado ou dados iguais aos existentes.")


def deletar_usuario(nome: str):
    resultado = usuarios.delete_one({"nome": nome})
    if resultado.deleted_count > 0:
        print("Usuário deletado com sucesso.")
    else:
        print("Usuário não encontrado.")

def realizar_emprestimo(titulo_livro: str, nome_usuario):
    livro = livros.find_one({"titulo": titulo_livro, "disponivel": True})
    usuario = usuarios.find_one({"nome": nome_usuario})
    if usuario is None:
        print("Usuário não encontrado.")
        print("Cadastrando novo usuário...")
        inserir_usuario(nome_usuario, None)
        usuario = usuarios.find_one({"nome": nome_usuario})
    else:
        print("Usuário encontrado.")
        
    if livro and usuario:
        emprestimo = {
            "livro_id": livro["_id"],
            "usuario_id": usuario["_id"],
            "data_emprestimo": datetime.now(),
            "data_devolucao": None,
        }
        emprestimos.insert_one(emprestimo)
        livros.update_one({"_id": livro["_id"]}, {"$set": {"disponivel": False}})
        print(
            f"Empréstimo realizado para o livro '{titulo_livro}' ao usuário '{nome_usuario}'."
        )
    else:
        if not livro:
            print("Livro não disponível para empréstimo.")
        if not usuario:
            print("Usuário não encontrado.")


def devolver_livro(titulo_livro: str, nome_usuario: str):
    livro = livros.find_one({"titulo": titulo_livro})
    usuario = usuarios.find_one({"nome": nome_usuario})
    if livro and usuario:
        emprestimo = emprestimos.find_one(
            {
                "livro_id": livro["_id"],
                "usuario_id": usuario["_id"],
                "data_devolucao": None,
            }
        )
        if emprestimo:
            emprestimos.update_one(
                {"_id": emprestimo["_id"]}, {"$set": {"data_devolucao": datetime.now()}}
            )
            livros.update_one({"_id": livro["_id"]}, {"$set": {"disponivel": True}})
            print(f"Livro '{titulo_livro}' devolvido pelo usuário '{nome_usuario}'.")
        else:
            print("Empréstimo não encontrado.")
    else:
        if not livro:
            print("Livro não encontrado.")
        if not usuario:
            print("Usuário não encontrado.")


def consultar_emprestimos():
    todos_emprestimos = emprestimos.find()
    for emprestimo in todos_emprestimos:
        livro = livros.find_one({"_id": emprestimo["livro_id"]})
        usuario = usuarios.find_one({"_id": emprestimo["usuario_id"]})
        data_devolucao = (
            emprestimo["data_devolucao"]
            if emprestimo["data_devolucao"]
            else "Em aberto"
        )
        print(
            f"Livro: {livro['titulo']} - Usuário: {usuario['nome']} - Empréstimo em: {emprestimo['data_emprestimo']} - Devolução: {data_devolucao}"
        )


def main():

    client = conn.conn()

    db = client["biblioteca"]

    global livros, usuarios, emprestimos

    livros = db["livros"]
    usuarios = db["usuarios"]
    emprestimos = db["emprestimos"]

    while True:
        print("\nMenu:")
        print("1. Inserir Livro")
        print("2. Consultar Livro")
        print("3. Consultar Todos os Livros")
        print("4. Atualizar Livro")
        print("5. Deletar Livro")
        print("6. Inserir Usuário")
        print("7. Consultar Usuário")
        print("8. Atualizar Usuário")
        print("9. Deletar Usuário")
        print("10. Realizar Empréstimo")
        print("11. Devolver Livro")
        print("12. Consultar Empréstimos")
        print("0. Sair")

        opcao = input("Escolha uma opção: ")

        match opcao:
            case "1":
                titulo = input("Título do livro: ")
                autor = input("Autor do livro: ")
                ano = int(input("Ano de publicação: "))
                inserir_livro(titulo, autor, ano)

            case "2":
                titulo = input("Título do livro: ")
                consultar_livro_especifico(titulo)

            case "3":
                consultar_livro_todos()

            case "4":
                titulo = input("Título do livro: ")
                novos_dados = {}
                novo_titulo = input("Novo título (deixe em branco para não alterar): ")
                if novo_titulo:
                    novos_dados["titulo"] = novo_titulo
                novo_autor = input("Novo autor (deixe em branco para não alterar): ")
                if novo_autor:
                    novos_dados["autor"] = novo_autor
                novo_ano = input("Novo ano (deixe em branco para não alterar): ")
                if novo_ano:
                    novos_dados["ano"] = int(novo_ano)
                atualizar_livro(titulo, novos_dados)

            case "5":
                titulo = input("Título do livro: ")
                deletar_livro(titulo)

            case "6":
                nome = input("Nome do usuário: ")
                email = input("Email do usuário: ")
                inserir_usuario(nome, email)

            case "7":
                nome = input("Nome do usuário: ")
                consultar_usuario(nome)

            case "8":
                nome = input("Nome do usuário: ")
                novos_dados = {}
                novo_nome = input("Novo nome (deixe em branco para não alterar): ")
                if novo_nome:
                    novos_dados["nome"] = novo_nome
                novo_email = input("Novo email (deixe em branco para não alterar): ")
                if novo_email:
                    novos_dados["email"] = novo_email
                atualizar_usuario(nome, novos_dados)
                
            case "9":
                nome = input("Nome do usuário: ")
                deletar_usuario(nome)

            case "10":
                titulo_livro = input("Título do livro: ")
                nome_usuario = input("Nome do usuário: ")
                realizar_emprestimo(titulo_livro, nome_usuario)

            case "11":
                titulo_livro = input("Título do livro: ")
                nome_usuario = input("Nome do usuário: ")
                devolver_livro(titulo_livro, nome_usuario)

            case "12":
                consultar_emprestimos()
                
            case "0":
                break

            case _:
                print("Escolha umas das opções do menu.")

if __name__ == "__main__":
    main()
