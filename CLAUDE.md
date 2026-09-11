# Atividade: Comunicação com Sockets — UDP vs. TCP

**Disciplina:** Sistemas Distribuídos / Capítulo 4 (Comunicação entre Processos)
**Prazo:** Até o dia 20/09 23h59
**Linguagem escolhida: Python**

---

## 1. Objetivo

Implementar o mesmo serviço cliente-servidor duas vezes — uma vez sobre UDP, outra sobre TCP — e comparar empiricamente o comportamento dos dois protocolos diante de perda de mensagens. O trabalho conecta diretamente com o que foi visto no capítulo: a API de sockets, o modelo de requisição-e-resposta e a discussão sobre quando usar cada protocolo.

Ao final, o aluno deve conseguir responder: **"Por que o TCP não perde mensagens e o UDP sim (e o que custa resolver isso)?"**

---

## 2. Cenário: Calculadora Remota

Cliente e servidor implementam um protocolo simples de requisição-e-resposta para operações matemáticas:

- O cliente envia requisições no formato `CALC:<n>:<operando1>:<op>:<operando2>`, onde `n` é o número de sequência (0, 1, 2, …), `operando1` e `operando2` são números (inteiros ou decimais) e `op` é uma das operações: `+`, `-`, `*`, `/`.
- O servidor executa a operação e responde com `RESULT:<n>:<resultado>`.
- Em caso de divisão por zero ou operação inválida, o servidor responde com `ERROR:<n>:<mensagem de erro>`.

Esse serviço é propositalmente simples: o foco da avaliação está no comportamento de rede, não na lógica de negócio.

**Exemplo de interação:**

```
Cliente → CALC:0:10:+:5
Servidor → RESULT:0:15.0
Cliente → CALC:1:8:/:0
Servidor → ERROR:1:divisão por zero
Cliente → CALC:2:3.5:*:2
Servidor → RESULT:2:7.0
```

---

## 3. Parte 1: Implementação UDP

- **CalcServerUDP:** recebe datagramas, executa a operação matemática e responde com o resultado.
- **CalcClientUDP:** envia uma sequência de N = 20 requisições de cálculo numeradas (geradas aleatoriamente), uma de cada vez (aguarda a resposta antes de enviar a próxima), e mede o tempo de ida-e-volta (RTT) de cada uma.
- **Perda simulada:** o servidor deve descartar propositalmente uma fração configurável das mensagens recebidas (ex.: `--loss-rate 0.1` para 10%), sorteando aleatoriamente quais "perder" (recebe, mas não responde). Isso simula, de forma controlada, a falha de omissão que o UDP não trata sozinho.
- **Confiabilidade no cliente:** o CalcClientUDP deve implementar um mecanismo simples de **timeout + retransmissão**: se a resposta não chegar dentro de X ms (sugestão: 500 ms), reenviar a mesma requisição, até um máximo de tentativas (sugestão: 5). Se esgotar as tentativas, registrar a requisição como perdida e continuar.
- O servidor deve suportar múltiplos clientes concorrentes sem travar.

---

## 4. Parte 2: Implementação TCP

- **CalcServerTCP:** aceita conexões e executa operações matemáticas para cada cliente.
- **CalcClientTCP:** mesmo comportamento do cliente UDP (N=20 requisições numeradas, mede RTT), mas **sem lógica de retransmissão** (não deve ser necessária).
- O servidor deve tratar múltiplos clientes concorrentes, cada um em sua própria thread.
- Não precisa implementar perda simulada. O TCP entrega tudo, na ordem, sem tratamento adicional.

---

## 5. Parte 3: Experimento e Análise

Execute o cliente 3 vezes contra o servidor UDP, variando a taxa de perda simulada: **0%, 10%, 30%**. Depois, execute uma vez contra o servidor TCP.

Para cada execução, registre:

- Tempo total da sequência completa
- RTT médio e RTT máximo
- Número de retransmissões (apenas UDP)
- Requisições perdidas definitivamente, se houver (esgotou tentativas)

---

## 6. Parte 4: Implementação com Protocol Buffers (protobuf)

Reimplementar a calculadora remota usando **Protocol Buffers** como formato de serialização das mensagens, no lugar do protocolo textual das partes anteriores.

- **CalcServerProto** e **CalcClientProto** usando TCP.
- Usar a biblioteca oficial do protobuf para Python e o compilador `protoc` para gerar o código a partir do `.proto`.
- O comportamento deve ser equivalente ao da Parte 2 (TCP, N=20 requisições, mede RTT), mas com as mensagens serializadas em binário pelo protobuf.
- Medir e registrar o **tamanho médio das mensagens (em bytes)** e comparar com o protocolo textual da Parte 2.

---

## 7. Requisitos Técnicos

- Uso explícito da **API de sockets nativa do Python** (módulo `socket`). Não usar bibliotecas de alto nível que escondam a diferença entre UDP e TCP (ex.: frameworks HTTP prontos).
- Código organizado em pelo menos **6 arquivos/módulos** (servidor e cliente para cada parte: UDP, TCP, Proto).
- Tratamento básico de erros (conexão recusada, timeout, divisão por zero, operação inválida, etc.) sem travar o programa.

---

## 8. Entrega (via Google Forms)

No formulário, submeter:

- O código-fonte completo (arquivo `.zip` ou link para repositório). Incluir o arquivo `.proto` da Parte 4.
- Um `README.md` com instruções de como compilar/executar cada parte.
- As respostas às questões elaboradas.

---

## 9. Formulário de Entrega

### Dados do Aluno

**Nome:**

**Matrícula:**

**Turma:**

**Código (caso tenha preparado em arquivo .zip):**
_(upload de 1 arquivo, máx. 10 MB)_

**Código (caso prefira enviar link do repositório git):**

---

### Parte 1 — UDP

**Dados das execuções UDP:**

| Taxa de Perda | Tempo total (s) | RTT médio (ms) | Retransmissões | Perdidas definitivamente |
|---------------|-----------------|----------------|----------------|--------------------------|
| 0%            |                 |                |                |                          |
| 10%           |                 |                |                |                          |
| 30%           |                 |                |                |                          |

**Descreva como você implementou o timeout + retransmissão no cliente UDP. O que acontece quando o número máximo de tentativas é esgotado? O cliente consegue detectar sozinho que uma requisição foi perdida?**

> _Resposta:_

---

### Parte 2 — TCP

**Dados da execução TCP:**

| Tempo total (s) | RTT médio (ms) |
|-----------------|----------------|
|                 |                |

**Como o servidor TCP trata múltiplos clientes?**

- [ ] Thread por cliente
- [ ] Async
- [ ] Processos
- [ ] Sem concorrência

**Por que o cliente TCP não precisou de timeout ou retransmissão, enquanto o cliente UDP precisou? Compare os tempos e RTTs das duas implementações com perda 0%.**

> _Resposta:_

---

### Parte 3 — Análise

**O que acontece com as requisições quando o cliente UDP roda sem retransmissão? Com ela ativada, o que muda — e a que custo em tempo? Apoie com os dados coletados.**

> _Resposta:_

**Dado que UDP exige todo esse trabalho extra para ser confiável, por que ele ainda é usado em sistemas reais? Cite pelo menos um exemplo concreto e justifique.**

> _Resposta:_

---

### Parte 4 — Protobuf

**Comparar tamanho médio das mensagens:**

| Formato         | Tamanho médio (bytes) |
|-----------------|-----------------------|
| Texto puro (Parte 2) |                  |
| Protobuf (Parte 4)   |                  |

**Como você mediu o tamanho das mensagens?**

> _Resposta:_

**Em qual cenário real você escolheria protobuf em vez de texto simples? Foi mais fácil ou mais difícil de implementar? E por quê?**

> _Resposta:_
