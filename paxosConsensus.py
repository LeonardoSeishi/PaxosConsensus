import collections
from abc import ABC, abstractmethod


class PaxosValue:
    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value
    

class PaxosProtocol(ABC):
    @abstractmethod
    def prepare(self, proposal_id):
        pass

    @abstractmethod
    def promise(self, proposal_id, last_accepted_proposal):
        pass

    @abstractmethod
    def accept(self, proposal_id, value):
        pass

    @abstractmethod
    def learn(self, accepted_value):
        pass


class PaxosNode(PaxosProtocol):
    def __init__(self, node_id):
        self.node_id = node_id
        self.neighbors = []  # Lista de nós vizinhos
        #self.proposed_value = None
        #self.accepted_value = None
        self.proposed_leader = None
        self.accepted_leader = None
        self.promise_count = 0
        self.last_accepted_proposal = None
        self.proposal_counter = 0  # Contador para gerar IDs de propostas únicas


    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def run_paxos(self, value):
        proposal_id = self.generate_proposal_id()
        self.proposed_value = PaxosValue(value)

        # Fase de preparação (Prepare)
        self.prepare(proposal_id)

        if __name__ == "__main__":
            print(f"Node {self.node_id} proposing value: {value}")


    def run_leader_election(self):
        proposal_id = self.generate_proposal_id()
        self.proposed_leader = self.node_id

        self.prepare(proposal_id)



    def prepare(self, proposal_id):
        for node in self.neighbors:
            node.promise(proposal_id, self.last_accepted_proposal)


    def promise(self, proposal_id, last_accepted_proposal):
        # Verifica se a proposta atual é maior do que a última aceita
        if (last_accepted_proposal is None) or (proposal_id > last_accepted_proposal):
            self.last_accepted_proposal = proposal_id
            self.accepted_leader = self.proposed_leader
            for node in self.neighbors:
                node.accept(proposal_id, self.proposed_leader)
            # Envia promessa para o nó que fez a proposta
            # (neste exemplo, assumindo uma função receive_promise no outro nó)
            # Você precisará implementar a lógica de envio da promessa
            # node.receive_promise(self.node_id, proposal_id)
        else:
            # Rejeita a proposta porque já tem uma proposta mais recente aceita
            pass


    def accept(self, proposal_id, value):
        # Verifica se obteve promessas suficientes na fase de preparação
        if self.promise_count > len(self.neighbors) / 2:
            # Se a proposta atual for a mais recente aceita
            if proposal_id == self.last_accepted_proposal:
                #self.accepted_value = value
                self.accepted_leader = value

                for node in self.neighbors:
                    # Envia mensagem de aceitação para os outros nós
                    node.learn(value)
            else:
                # Se a proposta não for a mais recente aceita, pode não estar atualizado
                # ou pode ser um nó desatualizado, portanto, deve começar o processo novamente
                #self.run_paxos(self.proposed_value.value)  # Reinicia o processo de Paxos com a proposta atual
                self.run_leader_election(self.proposed_leader)
        else:
            # Se não obteve promessas suficientes, pode tentar novamente
            #self.run_paxos(self.proposed_value.getValue())  # Reinicia o processo de Paxos com a proposta atual
            self.run_leader_election(self.proposed_leader)


    def learn(self, accepted_value):
        if self.accepted_value is None:
            self.accepted_value = accepted_value
            print(f"Node {self.node_id} learned the accepted value: {self.accepted_value}")
        else:
            # Se já aprendeu um valor, pode ser um conflito ou um nó desatualizado
            # Pode reiniciar o processo de Paxos ou lidar com o conflito conforme necessário
            pass


    def generate_proposal_id(self):
        self.proposal_counter += 1
        return self.proposal_counter






#testanto com mensagens de debugg
if __name__ == "__main__":
    # Criando os nós
    nodes = []
    for i in range(1, 4):
        nodes.append(PaxosNode(i))

    # Adicionando vizinhos para cada nó
    nodes[0].add_neighbor(nodes[1])
    nodes[0].add_neighbor(nodes[2])

    nodes[1].add_neighbor(nodes[0])
    nodes[1].add_neighbor(nodes[2])

    nodes[2].add_neighbor(nodes[0])
    nodes[2].add_neighbor(nodes[1])

    # Iniciando a eleição de líder
    nodes[0].run_leader_election()

    # Verificando o líder eleito
    leader = max(nodes, key=lambda node: node.accepted_leader)
    print(f"Líder eleito: Node {leader.node_id} com ID {leader.accepted_leader}")