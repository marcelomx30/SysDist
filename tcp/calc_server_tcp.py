import socketserver
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


class CalcHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print(f"[CONN] {self.client_address}")
        try:
            while True:
                line = self.rfile.readline()
                if not line:
                    break
                msg = line.decode().strip()
                if not msg:
                    continue

                try:
                    seq, operand1, op, operand2 = parse_request(msg)
                    result = calculate(operand1, op, operand2)
                    response = f"RESULT:{seq}:{result}\n"
                except ZeroDivisionError as e:
                    response = f"ERROR:{extract_seq(msg)}:{e}\n"
                except Exception as e:
                    response = f"ERROR:{extract_seq(msg)}:{e}\n"

                self.wfile.write(response.encode())
                self.wfile.flush()
                print(f"[OK] {msg} -> {response.strip()}")
        except (ConnectionResetError, BrokenPipeError):
            pass
        print(f"[DISC] {self.client_address}")


def main():
    parser = argparse.ArgumentParser(description="Calculadora TCP — Servidor")
    parser.add_argument('--host', default='127.0.0.1', help='Endereço de escuta')
    parser.add_argument('--port', type=int, default=5001, help='Porta TCP')
    args = parser.parse_args()

    # allow_reuse_address evita "Address already in use" ao reiniciar
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((args.host, args.port), CalcHandler) as server:
        print(f"TCP server ouvindo em {args.host}:{args.port} (thread por cliente)")
        server.serve_forever()


if __name__ == '__main__':
    main()
