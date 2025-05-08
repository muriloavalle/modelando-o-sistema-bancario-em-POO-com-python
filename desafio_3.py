from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, nome, endereco):
        self.nome = nome
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(nome, endereco)
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def depositar(self, valor):
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True

    def sacar(self, valor):
        if valor > self._saldo:
            print("\n@@@ Operação falhou! Saldo insuficiente. @@@")
            return False
        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__])

        if valor > self.limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
        elif numero_saques >= self.limite_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
            Agência: {self.agencia}
            C/C: {self.numero}
            Titular: {self.cliente.nome}
            Saldo: R$ {self.saldo:.2f}
        """


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


def menu():
    return input("""
======> M E N U <======
[d] Depositar
[s] Sacar
[e] Extrato
[nu] Novo Usuario
[nc] Nova Conta
[lc] Listar Contas
[q] Sair
=======================
=> """)


def depositar(clientes):
    cpf = input("Informe o CPF do usuário: ")
    cliente = next((c for c in clientes if c.cpf == cpf), None)

    if cliente and cliente.contas:
        valor = float(input("Informe o valor do depósito: "))
        conta = cliente.contas[0]
        deposito = Deposito(valor)
        cliente.realizar_transacao(conta, deposito)
    else:
        print("Cliente ou conta não encontrada.")


def sacar(clientes):
    cpf = input("Informe o CPF do usuário: ")
    cliente = next((c for c in clientes if c.cpf == cpf), None)

    if cliente and cliente.contas:
        valor = float(input("Informe o valor do saque: "))
        conta = cliente.contas[0]
        saque = Saque(valor)
        cliente.realizar_transacao(conta, saque)
    else:
        print("Cliente ou conta não encontrada.")


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do usuário: ")
    cliente = next((c for c in clientes if c.cpf == cpf), None)

    if cliente and cliente.contas:
        conta = cliente.contas[0]
        print("\n================ EXTRATO ================")
        for transacao in conta.historico.transacoes:
            print(f"{transacao['tipo']}: R$ {transacao['valor']:.2f} em {transacao['data']}")
        print(f"\nSaldo: R$ {conta.saldo:.2f}")
        print("=========================================")
    else:
        print("Cliente ou conta não encontrada.")


def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente numeros): ")
    cliente = next((c for c in clientes if c.cpf == cpf), None)

    if cliente:
        print("Usuário com este CPF já existe.")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro - número - bairro - cidade/UF): ")

    novo_cliente = PessoaFisica(nome, data_nascimento, cpf, endereco)
    clientes.append(novo_cliente)
    print("Usuário criado com sucesso!")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do usuário: ")
    cliente = next((c for c in clientes if c.cpf == cpf), None)

    if cliente:
        conta = ContaCorrente(numero_conta, cliente)
        cliente.adicionar_conta(conta)
        contas.append(conta)
        numero_conta += 1
        print("Conta criada com sucesso!")
    else:
        print("Usuário não encontrado. Crie o usuário antes de criar a conta.")


def listar_contas(contas):
    if contas:
        for conta in contas:
            print(conta)
    else:
        print("Nenhuma conta cadastrada.")


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


main()
