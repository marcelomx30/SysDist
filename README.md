# Atividade: Comunicação com Sockets — UDP vs. TCP

Implementação em Python da calculadora remota cliente-servidor, cobrindo UDP, TCP e Protobuf.

## Estrutura

```
udp/
  calc_server_udp.py   — servidor UDP com perda simulada
  calc_client_udp.py   — cliente UDP com timeout + retransmissão
tcp/
  calc_server_tcp.py   — servidor TCP (ThreadingTCPServer)
  calc_client_tcp.py   — cliente TCP
proto/
  calc.proto           — definição das mensagens Protobuf
  calc_pb2.py          — gerado pelo protoc (ver abaixo)
  calc_server_proto.py — servidor TCP + Protobuf
  calc_client_proto.py — cliente TCP + Protobuf
```

## Dependências

```bash
pip install protobuf
```

Para a Parte 4, instale também o compilador `protoc`:

```bash
# Arch Linux
sudo pacman -S protobuf

# Ubuntu/Debian
sudo apt install protobuf-compiler

# macOS
brew install protobuf
```

## Parte 1 — UDP

### Gerar o código Protobuf (necessário apenas para a Parte 4)

```bash
cd proto
protoc --python_out=. calc.proto
```

### Executar o servidor

```bash
# Sem perda (0%)
python udp/calc_server_udp.py

# 10% de perda
python udp/calc_server_udp.py --loss-rate 0.1

# 30% de perda
python udp/calc_server_udp.py --loss-rate 0.3
```

Opções disponíveis:
- `--host` (padrão: `127.0.0.1`)
- `--port` (padrão: `5000`)
- `--loss-rate` (padrão: `0.0`)

### Executar o cliente

```bash
python udp/calc_client_udp.py
```

Opções disponíveis:
- `--host` (padrão: `127.0.0.1`)
- `--port` (padrão: `5000`)

O cliente envia 20 requisições com timeout de 500 ms e até 5 tentativas por requisição. Ao final, exibe: tempo total, RTT médio, RTT máximo, retransmissões e requisições perdidas definitivamente.

---

## Parte 2 — TCP

### Executar o servidor

```bash
python tcp/calc_server_tcp.py
```

Opções: `--host` (padrão: `127.0.0.1`), `--port` (padrão: `5001`)

### Executar o cliente

```bash
python tcp/calc_client_tcp.py
```

O cliente envia 20 requisições e exibe: tempo total, RTT médio, RTT máximo e tamanho médio das mensagens em bytes (para comparação com a Parte 4).

---

## Parte 3 — Experimento

Execute o cliente UDP três vezes variando o `--loss-rate` do servidor (0%, 10%, 30%) e registre os resultados. Depois execute o cliente TCP uma vez. Compare os dados obtidos para responder às questões do formulário.

---

## Parte 4 — Protobuf

### Gerar o código

```bash
cd proto
protoc --python_out=. calc.proto
```

Isso gera `proto/calc_pb2.py`. Execute os scripts a partir da pasta `proto/` (ou ajuste o `PYTHONPATH`):

### Executar o servidor

```bash
cd proto
python calc_server_proto.py
```

Opções: `--host` (padrão: `127.0.0.1`), `--port` (padrão: `5002`)

### Executar o cliente

```bash
cd proto
python calc_client_proto.py
```

O cliente exibe o tamanho médio dos payloads Protobuf (bytes) para comparação com os tamanhos em texto puro da Parte 2.

---

## Protocolo de mensagens

### Texto puro (Partes 1 e 2)

```
Requisição:  CALC:<seq>:<operando1>:<op>:<operando2>
Resposta OK: RESULT:<seq>:<resultado>
Resposta err: ERROR:<seq>:<mensagem>
```

### Protobuf (Parte 4)

Mensagens binárias enquadradas com prefixo de 4 bytes (big-endian) indicando o tamanho do payload. A definição completa está em `proto/calc.proto`.
