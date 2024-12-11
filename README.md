# Documentação da Aplicação de Sorteio com gRPC

## Visão Geral

A aplicação consiste em um servidor gRPC que fornece números sorteados e um cliente web que interage com o servidor. A comunicação é feita usando **gRPC** e o cliente utiliza **Flask** e **Flask-SocketIO** para uma interface web interativa.

---

## Arquivo `sorteio.proto`

### Descrição

O arquivo `sorteio.proto` define o serviço gRPC e os tipos de mensagens usados na comunicação.

```proto
syntax = "proto3";

service SorteioService {
  rpc IniciarSorteio(Empty) returns (stream NumeroSorteado);
}

message NumeroSorteado {
  int32 numero = 1;
}

message Empty {}
```

### Explicação

- **Serviço `SorteioService`:**
  - Método `IniciarSorteio`: Inicia o sorteio e retorna um stream de números sorteados.
- **Mensagens:**
  - `NumeroSorteado`: Contém o número sorteado (inteiro).
  - `Empty`: Mensagem vazia usada como entrada para iniciar o sorteio.

### Geração de Arquivos Python

Comando usado para gerar os arquivos:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. sorteio.proto
```

---

## Arquivo `servidor.py`

### Descrição

O arquivo `servidor.py` implementa o servidor gRPC, gerencia o sorteio e utiliza um banco de dados SQLite para armazenar números sorteáveis.

### Estrutura

1. **Configuração do Banco de Dados:**
   - **`setup_database()`**: Cria a tabela `numeros` para armazenar números sorteáveis.
   - **`generate_numbers()`**: Insere 100 números aleatórios no banco.

2. **Classe `SorteioService`:**
   - **Atributos:**
     - `numeros_sorteados`: Lista de números sorteados.
     - `numeros_jogador`: Conjunto de números da cartela do jogador.
   - **Métodos:**
     - `set_cartela_jogador(cartela)`: Define os números da cartela do jogador.
     - `IniciarSorteio(request, context)`: Gera números sorteados e verifica se o jogador ganhou.
     - `emitir_evento_fim_sorteio(ganhou)`: Exibe no console o resultado do sorteio.

3. **Execução do Servidor:**
   - Configura o banco, inicia o servidor gRPC e escuta na porta `50051`.

### Fluxo do Sorteio

1. O servidor recupera números do banco e embaralha.
2. Envia os números sorteados ao cliente.
3. Após o sorteio, verifica se o jogador ganhou.
4. Envia `-1` para sinalizar o fim e exibe o resultado no console.

### Código Simplificado

```python
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
sorteio_pb2_grpc.add_SorteioServiceServicer_to_server(SorteioService(), server)
server.add_insecure_port("[::]:50051")
server.start()
server.wait_for_termination()
```

---

## Arquivo `app.py`

### Descrição

O arquivo `app.py` implementa o cliente usando Flask e Flask-SocketIO. Ele se comunica com o servidor gRPC e atualiza o frontend em tempo real.

### Estrutura

1. **Configuração:**
   - Flask para gerenciar rotas.
   - Flask-SocketIO para comunicação em tempo real.
   - Conexão com o servidor gRPC na porta `50051`.

2. **Rotas:**
   - **`/`:** Renderiza a página inicial.
   - **`/nova_cartela`:** Gera uma nova cartela e retorna como JSON.
   - **`/iniciar_sorteio`:** Inicia o sorteio em uma thread separada.
   - **`/reiniciar_jogo`:** Gera uma nova cartela e limpa a interface.

3. **Lógica de Sorteio:**
   - Escuta os números sorteados do servidor gRPC.
   - Atualiza o frontend com números sorteados e o resultado final.

### Fluxo de Funcionamento

1. O usuário gera uma cartela pelo frontend.
2. Inicia o sorteio, chamando o backend.
3. O backend escuta números do servidor gRPC e atualiza o frontend.
4. O sorteio termina, e o resultado é enviado ao frontend.

### Código Simplificado

```python
@app.route('/nova_cartela')
def nova_cartela():
    cartela = random.sample(range(1, 100), 5)
    return jsonify(cartela=cartela)

@app.route('/iniciar_sorteio')
def iniciar_sorteio_endpoint():
    thread = threading.Thread(target=iniciar_sorteio)
    thread.start()
    return jsonify(status='Sorteio iniciado')
```

---

## Conclusão

A aplicação demonstra uma integração eficiente entre gRPC e uma interface web. O uso de Flask-SocketIO para atualizações em tempo real torna a experiência do usuário interativa.
