Seu objetivo esta semana **não é construir um produto**, é fazer seu cérebro 
internalizar o padrão:

> FastAPI → Supervisor → Agent → Tool → Response

Quanto mais vezes você repetir esse fluxo, mais natural ele ficará.

Eu escolheria projetos que possam ser feitos em **1 a 2 horas** cada.

---

# Projeto 1 - Restaurante (Minha recomendação)

```
                FastAPI
                    |
             Supervisor (LangGraph)
              /               \
             /                 \
     Reservation Agent     Menu Agent
```

### Reservation Agent

Responsável por:

* reservar mesa
* cancelar reserva
* consultar reserva

Tools:

* reserve_table()
* cancel_table()
* get_reservation()

---

### Menu Agent

Responsável por:

* mostrar cardápio
* informar preço
* verificar ingredientes

Tools:

* get_menu()
* get_price()

---

Exemplos

```
Quero reservar uma mesa.
```

↓

Supervisor

↓

Reservation Agent

---

```
Quanto custa o hambúrguer?
```

↓

Supervisor

↓

Menu Agent

---

# Projeto 2 - Clínica

```
Supervisor
   |
-------------------------
|                       |
Appointment Agent    Doctor Agent
```

Appointment Agent

* marcar consulta
* cancelar consulta

Doctor Agent

* especialidades
* horários
* informações do médico

---

# Projeto 3 - Biblioteca

```
Supervisor
      |
----------------------
|                    |
Book Agent      Member Agent
```

Book Agent

* procurar livro
* disponibilidade

Member Agent

* empréstimos
* multas
* renovação

---

# Projeto 4 - Loja Online

Supervisor

↓

Product Agent

* pesquisar produto
* preço
* estoque

Order Agent

* acompanhar pedido
* cancelar pedido

---

# Projeto 5 - Hotel

Supervisor

↓

Reservation Agent

* reservar quarto
* cancelar

Room Agent

* tipos de quarto
* preço
* comodidades

---

# Projeto 6 - Cinema

Supervisor

↓

Movie Agent

* filmes
* horários

Ticket Agent

* comprar ingresso
* cancelar

---

# Projeto 7 - Academia

Supervisor

↓

Workout Agent

* montar treino
* consultar exercícios

Membership Agent

* planos
* pagamentos

---

# Projeto 8 - Companhia Aérea

Supervisor

↓

Flight Agent

* buscar voos
* horários

Reservation Agent

* comprar
* cancelar

---

# Projeto 9 - Pet Shop

Supervisor

↓

Appointment Agent

* banho
* tosa

Product Agent

* ração
* brinquedos

---

# Projeto 10 - Suporte Técnico

Supervisor

↓

Network Agent

* internet
* Wi-Fi

Computer Agent

* senha
* computador
* impressora

---

## Eu seguiria exatamente a mesma arquitetura em todos

```
app/
│
├── main.py
│
├── supervisor/
│   └── graph.py
│
├── agents/
│   ├── reservation_agent.py
│   └── menu_agent.py
│
├── tools/
│   ├── reservation_tools.py
│   └── menu_tools.py
│
├── schemas.py
│
└── state.py
```

Você praticamente só troca o domínio do problema.

---

## O padrão que você deve repetir

Em todos os projetos, mantenha o fluxo idêntico:

1. O usuário envia uma pergunta para um endpoint do FastAPI (`POST /chat`).
2. O Supervisor (LangGraph) analisa a intenção da mensagem.
3. O Supervisor escolhe qual dos dois agentes deve responder.
4. O agente (LangChain) usa uma ou mais tools para obter os dados 
necessários.
5. O agente devolve a resposta ao Supervisor.
6. O Supervisor retorna a resposta final pela API.

Quando esse ciclo estiver automático, você terá aprendido o essencial da 
orquestração de agentes.

## Um desafio extra para acelerar o aprendizado

Depois de fazer 4 ou 5 projetos, pare de criar projetos novos e comece a 
**trocar apenas os agentes**.

Por exemplo:

* Restaurante → Restaurante + Delivery
* Loja → Loja + Pagamentos
* Clínica → Clínica + Convênio
* Hotel → Hotel + Fidelidade

Assim você perceberá que o domínio muda, mas a arquitetura permanece 
praticamente a mesma. Esse é exatamente o tipo de repetição que ajuda a 
consolidar conceitos de LangGraph, LangChain e FastAPI.

