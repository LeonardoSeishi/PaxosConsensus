from paxosConsensus import PaxosNode, PaxosValue

#arquivo de testes sem mensagens de debugg

# Criando alguns nós
node1 = PaxosNode(1)
node2 = PaxosNode(2)
node3 = PaxosNode(3)

# Adicionando vizinhos para cada nó
node1.add_neighbor(node2)
node1.add_neighbor(node3)

node2.add_neighbor(node1)
node2.add_neighbor(node3)

node3.add_neighbor(node1)
node3.add_neighbor(node2)

# Executando o algoritmo de Paxos em um dos nós
node1.run_paxos("Value to propose")