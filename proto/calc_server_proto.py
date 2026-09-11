import socketserver
import struct
import argparse
import calc_pb2


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


def recv_framed(rfile):
    """Lê uma mensagem com prefixo de 4 bytes (big-endian) indicando o tamanho."""
    header = rfile.read(4)
    if len(header) < 4:
        return None
    length = struct.unpack('>I', header)[0]
    data = rfile.read(length)
    return data if len(data) == length else None


def send_framed(wfile, msg_bytes):
    """Envia uma mensagem com prefixo de 4 bytes indicando o tamanho."""
    wfile.write(struct.pack('>I', len(msg_bytes)) + msg_bytes)
    wfile.flush()


class CalcProtoHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print(f"[CONN] {self.client_address}")
        try:
            while True:
                data = recv_framed(self.rfile)
                if data is None:
                    break

                request = calc_pb2.CalcRequest()
                request.ParseFromString(data)

                response = calc_pb2.CalcResponse()
                response.seq = request.seq

                try:
                    result = calculate(request.operand1, request.op, request.operand2)
                    response.value = result
                except ZeroDivisionError as e:
                    response.error = str(e)
                except Exception as e:
                    response.error = str(e)

                send_framed(self.wfile, response.SerializeToString())
                which = response.WhichOneof('result')
                val = response.value if which == 'value' else response.error
                print(f"[OK] seq={request.seq} {request.operand1}{request.op}{request.operand2} -> {which}={val}")
        except (ConnectionResetError, BrokenPipeError):
            pass
        print(f"[DISC] {self.client_address}")


def main():
    parser = argparse.ArgumentParser(description="Calculadora Proto — Servidor")
    parser.add_argument('--host', default='127.0.0.1', help='Endereço de escuta')
    parser.add_argument('--port', type=int, default=5002, help='Porta TCP')
    args = parser.parse_args()

    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((args.host, args.port), CalcProtoHandler) as server:
        print(f"Proto server ouvindo em {args.host}:{args.port}")
        server.serve_forever()


if __name__ == '__main__':
    main()
