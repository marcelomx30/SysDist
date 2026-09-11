import socket
import random
import argparse


def calculate(operand1, op, operand2):
    if op == '+':
        return operand1 + operand2
    elif op == '-':
        return operand1 - operand2
    elif op == '*':
        return operand1 * operand2
    elif op == '/':
        if operand2 == 0:
            raise ZeroDivisionError("divisão por zero")
        return operand1 / operand2
    else:
        raise ValueError(f"operação inválida: {op}")


def parse_request(msg):
    # Formato esperado: CALC:<n>:<operando1>:<op>:<operando2>
    parts = msg.split(':')
    if len(parts) != 5 or parts[0] != 'CALC':
        raise ValueError(f"formato inválido: {msg}")
    seq = int(parts[1])
    operand1 = float(parts[2])
    op = parts[3]
    operand2 = float(parts[4])
    return seq, operand1, op, operand2


def extract_seq(msg):
    parts = msg.split(':')
    return int(parts[1]) if len(parts) >= 2 else 0


def run_server(host, port, loss_rate):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"UDP server ouvindo em {host}:{port} (loss rate: {loss_rate * 100:.0f}%)")

    while True:
        data, addr = sock.recvfrom(4096)
        msg = data.decode()

        if random.random() < loss_rate:
            print(f"[DROP] {msg} (de {addr})")
            continue

        try:
            seq, operand1, op, operand2 = parse_request(msg)
            result = calculate(operand1, op, operand2)
            response = f"RESULT:{seq}:{result}"
        except ZeroDivisionError as e:
            response = f"ERROR:{extract_seq(msg)}:{e}"
        except Exception as e:
            response = f"ERROR:{extract_seq(msg)}:{e}"

        sock.sendto(response.encode(), addr)
        print(f"[OK] {msg} -> {response}")


def main():
    parser = argparse.ArgumentParser(description="Calculadora UDP — Servidor")
    parser.add_argument('--host', default='127.0.0.1', help='Endereço de escuta')
    parser.add_argument('--port', type=int, default=5000, help='Porta UDP')
    parser.add_argument('--loss-rate', type=float, default=0.0,
                        help='Fração de mensagens descartadas (0.0 a 1.0)')
    args = parser.parse_args()
    run_server(args.host, args.port, args.loss_rate)


if __name__ == '__main__':
    main()
