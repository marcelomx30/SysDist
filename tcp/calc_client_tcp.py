import socket
import random
import time
import argparse

N_REQUESTS = 20
OPS = ['+', '-', '*', '/']


def generate_request(seq):
    op = random.choice(OPS)
    operand1 = round(random.uniform(-100, 100), 2)
    operand2 = round(random.uniform(-100, 100), 2)
    return f"CALC:{seq}:{operand1}:{op}:{operand2}"


def recvline(sock_file):
    return sock_file.readline().decode().strip()


def run_client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except ConnectionRefusedError:
        print(f"Erro: não foi possível conectar a {host}:{port}")
        return

    rfile = sock.makefile('rb')
    wfile = sock.makefile('wb')

    total_start = time.time()
    rtts = []
    req_sizes = []
    resp_sizes = []

    for seq in range(N_REQUESTS):
        msg = generate_request(seq)
        msg_bytes = (msg + '\n').encode()
        req_sizes.append(len(msg_bytes))

        t_start = time.time()
        wfile.write(msg_bytes)
        wfile.flush()

        response = recvline(rfile)
        rtt = (time.time() - t_start) * 1000
        rtts.append(rtt)
        resp_sizes.append(len(response.encode()))

        print(f"[{seq:02d}] {msg} -> {response}  (RTT: {rtt:.1f} ms)")

    total_time = time.time() - total_start
    avg_rtt = sum(rtts) / len(rtts) if rtts else 0.0
    max_rtt = max(rtts) if rtts else 0.0
    avg_req_size = sum(req_sizes) / len(req_sizes)
    avg_resp_size = sum(resp_sizes) / len(resp_sizes)

    print("\n" + "=" * 40)
    print("Resultados TCP")
    print("=" * 40)
    print(f"Tempo total:             {total_time:.3f} s")
    print(f"RTT médio:               {avg_rtt:.1f} ms")
    print(f"RTT máximo:              {max_rtt:.1f} ms")
    print(f"Tamanho médio request:   {avg_req_size:.1f} bytes")
    print(f"Tamanho médio response:  {avg_resp_size:.1f} bytes")

    rfile.close()
    wfile.close()
    sock.close()


def main():
    parser = argparse.ArgumentParser(description="Calculadora TCP — Cliente")
    parser.add_argument('--host', default='127.0.0.1', help='Endereço do servidor')
    parser.add_argument('--port', type=int, default=5001, help='Porta TCP')
    args = parser.parse_args()
    run_client(args.host, args.port)


if __name__ == '__main__':
    main()
