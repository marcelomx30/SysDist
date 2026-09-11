import socket
import random
import time
import argparse

TIMEOUT_S = 0.5       # 500 ms
MAX_RETRIES = 5
N_REQUESTS = 20
OPS = ['+', '-', '*', '/']


def generate_request(seq):
    op = random.choice(OPS)
    operand1 = round(random.uniform(-100, 100), 2)
    operand2 = round(random.uniform(-100, 100), 2)
    return f"CALC:{seq}:{operand1}:{op}:{operand2}"


def run_client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT_S)

    total_start = time.time()
    rtts = []
    retransmissions = 0
    lost = 0

    for seq in range(N_REQUESTS):
        msg = generate_request(seq)
        received = False

        for attempt in range(MAX_RETRIES):
            if attempt > 0:
                retransmissions += 1
                print(f"  [RETRANS] seq={seq} tentativa {attempt + 1}/{MAX_RETRIES}")

            t_start = time.time()
            sock.sendto(msg.encode(), (host, port))

            try:
                data, _ = sock.recvfrom(4096)
                rtt = (time.time() - t_start) * 1000
                rtts.append(rtt)
                print(f"[{seq:02d}] {msg} -> {data.decode()}  (RTT: {rtt:.1f} ms)")
                received = True
                break
            except socket.timeout:
                print(f"  [TIMEOUT] seq={seq} após {TIMEOUT_S * 1000:.0f} ms")

        if not received:
            lost += 1
            print(f"[{seq:02d}] PERDIDA definitivamente após {MAX_RETRIES} tentativas")

    total_time = time.time() - total_start
    avg_rtt = sum(rtts) / len(rtts) if rtts else 0.0
    max_rtt = max(rtts) if rtts else 0.0

    print("\n" + "=" * 40)
    print("Resultados UDP")
    print("=" * 40)
    print(f"Tempo total:             {total_time:.3f} s")
    print(f"RTT médio:               {avg_rtt:.1f} ms")
    print(f"RTT máximo:              {max_rtt:.1f} ms")
    print(f"Retransmissões:          {retransmissions}")
    print(f"Perdidas definitiv.:     {lost}")

    sock.close()


def main():
    parser = argparse.ArgumentParser(description="Calculadora UDP — Cliente")
    parser.add_argument('--host', default='127.0.0.1', help='Endereço do servidor')
    parser.add_argument('--port', type=int, default=5000, help='Porta UDP')
    args = parser.parse_args()
    run_client(args.host, args.port)


if __name__ == '__main__':
    main()
