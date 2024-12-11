from concurrent import futures
import grpc
import sorteio_pb2
import sorteio_pb2_grpc
import sqlite3
import random
import time

# Banco SQLite
DB_FILE = "sorteio.db"

# Função para configurar o banco de dados
def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS numeros (id INTEGER PRIMARY KEY, numero INTEGER)")
    conn.commit()
    conn.close()

# Função para gerar números aleatórios no banco
def generate_numbers():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Gera 100 números aleatórios para sorteio
    cursor.executemany("INSERT INTO numeros (numero) VALUES (?)", [(random.randint(1, 100),) for _ in range(100)])
    conn.commit()
    conn.close()

class SorteioService(sorteio_pb2_grpc.SorteioServiceServicer):
    def __init__(self):
        self.numeros_sorteados = []
        self.numeros_jogador = set()  # Números da cartela do jogador
    
    def set_cartela_jogador(self, cartela):
        """Define os números da cartela do jogador"""
        self.numeros_jogador = set(cartela)

    def IniciarSorteio(self, request, context):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Pega todos os números disponíveis
        cursor.execute("SELECT DISTINCT numero FROM numeros")
        numeros_disponiveis = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Embaralha os números e escolhe os 10 primeiros
        random.shuffle(numeros_disponiveis)
        self.numeros_sorteados = numeros_disponiveis[:10]

        for numero in self.numeros_sorteados:
            yield sorteio_pb2.NumeroSorteado(numero=numero)
            time.sleep(2)  # Delay de 2 segundos

        # Verifica se o jogador ganhou
        ganhou = self.numeros_jogador.issubset(self.numeros_sorteados)

        # Sinaliza o fim do sorteio
        yield sorteio_pb2.NumeroSorteado(numero=-1)  # Indica fim do sorteio

        # Emite evento de fim do sorteio com resultado
        self.emitir_evento_fim_sorteio(ganhou)

    def emitir_evento_fim_sorteio(self, ganhou):
        """Emite um evento de fim de sorteio."""
        print(f"Sorteio finalizado. Resultado: {'Ganhou' if ganhou else 'Não ganhou'}")



# Função para rodar o servidor gRPC
def serve():
    setup_database()
    generate_numbers()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sorteio_pb2_grpc.add_SorteioServiceServicer_to_server(SorteioService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Servidor iniciado na porta 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
