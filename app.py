from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import grpc
import sorteio_pb2
import sorteio_pb2_grpc
import random
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Variável para armazenar a cartela do cliente
cartela = []

# Conectar ao servidor gRPC
channel = grpc.insecure_channel('localhost:50051')
stub = sorteio_pb2_grpc.SorteioServiceStub(channel)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nova_cartela')
def nova_cartela():
    global cartela
    cartela = random.sample(range(1, 100), 5)
    return jsonify(cartela=cartela)

def iniciar_sorteio():
    global cartela
    response_stream = stub.IniciarSorteio(sorteio_pb2.Empty())

    numeros_sorteados = []  # Lista para armazenar todos os números sorteados

    for numero_sorteado in response_stream:
        numero = numero_sorteado.numero

        # Número -1 indica que o sorteio terminou
        if numero == -1:
            # Verifica se o jogador ganhou
            ganhou = all(num in numeros_sorteados for num in cartela)
            resultado = "Parabéns! Você ganhou." if ganhou else "Que pena, quem sabe na próxima. Quer jogar de novo?"
            # Envia evento ao frontend com o resultado
            socketio.emit('fim_sorteio', {'mensagem': resultado})
            break

        # Adiciona o número à lista de sorteados
        numeros_sorteados.append(numero)

        # Envia o número sorteado ao frontend
        socketio.emit('novo_numero', {'numero': numero, 'bingo': numero in cartela})



@app.route('/iniciar_sorteio')
def iniciar_sorteio_endpoint():
    thread = threading.Thread(target=iniciar_sorteio)
    thread.start()
    return jsonify(status='Sorteio iniciado')

@app.route('/reiniciar_jogo')
def reiniciar_jogo():
    global cartela
    cartela = random.sample(range(1, 100), 5)  # Gera uma nova cartela
    socketio.emit('reiniciar_jogo')  # Notifica o frontend para limpar a tela
    return jsonify(status='Jogo reiniciado')

if __name__ == '__main__':
    socketio.run(app, debug=True)
