import socket
import random
import time
import struct
import argparse
import calc_pb2

N_REQUESTS = 20
OPS = ['+', '-', '*', '/']


def generate_request(seq):
    req = calc_pb2.CalcRequest()
    req.seq = seq
    req.operand1 = round(random.uniform(-100, 100), 2)
    req.op = random.choice(OPS)
    req.operand2 = round(random.uniform(-100, 100), 2)
    return req


def recvall(sock, n):
    """Recebe exatamente n bytes do socket."""
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def send_framed(sock, msg_bytes):
    """Envia mensagem com prefixo de 4 bytes (big-endian) de tamanho."""
    sock.sendall(struct.pack('>I', len(msg_bytes)) + msg_bytes)


def recv_framed(sock):
    """Recebe mensagem com prefixo de 4 bytes de tamanho."""
    header = recvall(sock, 4)
    if header is None:
        return None
    length = struct.unpack('>I', header)[0]
    return recvall(sock, length)


def run_client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except ConnectionRefusedError:
        print(f"Erro: não foi possível conectar a {host}:{port}")
        return

    total_start = time.time()
    rtts = []
    req_sizes = []
    resp_sizes = []

    for seq in range(N_REQUESTS):
        req = generate_request(seq)
        req_bytes = req.SerializeToString()
        req_sizes.append(len(req_bytes))

        t_start = time.time()
        send_framed(sock, req_bytes)

        resp_bytes = recv_framed(sock)
        rtt = (time.time() - t_start) * 1000
        rtts.append(rtt)

        if resp_bytes is None:
            print(f"[{seq:02d}] Conexão encerrada inesperadamente")
            break

        resp_sizes.append(len(resp_bytes))
        response = calc_pb2.CalcResponse()
        response.ParseFromString(resp_bytes)

        which = response.WhichOneof('result')
        val = response.value if which == 'value' else response.error
        print(f"[{seq:02d}] {req.operand1}{req.op}{req.operand2} -> {which}={val}  (RTT: {rtt:.1f} ms)")

    total_time = time.time() - total_start
    avg_rtt = sum(rtts) / len(rtts) if rtts else 0.0
    max_rtt = max(rtts) if rtts else 0.0
    avg_req_size = sum(req_sizes) / len(req_sizes) if req_sizes else 0.0
    avg_resp_size = sum(resp_sizes) / len(resp_sizes) if resp_sizes else 0.0

    print("\n" + "=" * 40)
    print("Resultados Proto (TCP + Protobuf)")
    print("=" * 40)
    print(f"Tempo total:             {total_time:.3f} s")
    print(f"RTT médio:               {avg_rtt:.1f} ms")
    print(f"RTT máximo:              {max_rtt:.1f} ms")
    print(f"Tamanho médio request:   {avg_req_size:.1f} bytes  (payload protobuf)")
    print(f"Tamanho médio response:  {avg_resp_size:.1f} bytes  (payload protobuf)")

    sock.close()


def main():
    parser = argparse.ArgumentParser(description="Calculadora Proto — Cliente")
    parser.add_argument('--host', default='127.0.0.1', help='Endereço do servidor')
    parser.add_argument('--port', type=int, default=5002, help='Porta TCP')
    args = parser.parse_args()
    run_client(args.host, args.port)


if __name__ == '__main__':
    main()
