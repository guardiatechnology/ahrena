# Lexis: Foco do Agente no Plan Ativo

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Comportamento do agente quando uma sub-issue Plan está em `status: development` e a sessão corrente é a owner declarada

## Lei

> **Quando uma sub-issue Plan está em `status: development` e a sessão corrente é a owner declarada (assignee), o agente DEVE recusar requisições do usuário para trabalho não-relacionado até que o Plan transicione para `status: to review`. A recusa DEVE mencionar o Plan ativo (número, status atual, ETA estimada para `to review` quando conhecida) e oferecer ao usuário a alternativa explícita: tratar a requisição como (a) achado tangencial ao Plan atual, (b) novo Plan sub-issue sob o mesmo parent Issue, (c) nova Issue parent, ou (d) bloqueador crítico declarado.**

## Protocolo de Recusa

Ao receber uma requisição não-relacionada com um Plan ativo, o agente DEVE:

1. Identificar o Plan ativo: número da sub-issue, título, status, ETA estimada para `to review` quando conhecida
2. Declarar a recusa de forma direta: "Há um Plan ativo em `status: development` (Plan #{N}: {título}); não posso iniciar trabalho não-relacionado até `to review`."
3. Apresentar ao usuário as quatro opções discretas:
   - **(a)** A requisição é achado tangencial ao Plan ativo → aplicar `lex-no-silent-tech-debt` (Protocolo de Achado Tangencial)
   - **(b)** É novo Plan sub-issue sob o mesmo parent Issue → registrar e tratar após `to review`
   - **(c)** É nova Issue parent (capability nova) → registrar e tratar após `to review`
   - **(d)** É bloqueador crítico declarado → tratar agora, retomar Plan ao concluir
4. Aguardar a escolha do usuário antes de qualquer ação
5. Retomar o Plan ativo após tratar a exceção (quando aplicável), com checkpoint explícito do ponto de retomada

## Exemplos

### Correto

```
Usuário: Antes de continuar, pode revisar este outro repo aqui?
Agente: Há um Plan ativo: #163 (codify 3 Lexis HARD-GATE rules), em
        `status: development`, ETA para `to review` ~10min.
        Não posso iniciar trabalho em outro repo agora. Você prefere:
        (a) Registrar como Plan novo sob o parent #140 e tratar após esta PR?
        (b) Abrir Issue parent nova se for capability separada?
        (c) Declarar como bloqueador crítico (CI quebrada / P0)?
        (d) Esperar `to review` (~10min)?
Usuário: (a)
Agente: Ok, registrado. Retomando #163.
```

```
Usuário: Pera, este Plan vai mesmo precisar tocar arquivo X?
Agente: [Exceção (b): pergunta direta sobre o Plan ativo]
        Sim, arquivo X faz parte do escopo declarado porque {razão}.
        Continuando a implementação.
```

### Incorreto

```
Usuário: Antes de continuar, dá pra você também atualizar essa Lex aqui?
Agente: Claro, deixa eu fazer isso primeiro.        # FORBIDDEN — context switch silencioso
        [edita arquivo não-relacionado, contamina diff do PR]
```

```
Usuário: Aproveita e arruma esse outro bug também
Agente: [silenciosamente expande o escopo sem registrar]    # FORBIDDEN — scope creep silencioso
```

## Validação Automatizada

- **Ferramenta:** auto-verificação do agente antes de aceitar nova instrução durante Plan ativo; auditoria de Argos durante review de PR detectando arquivos modificados fora do escopo declarado do Plan (compara diff do PR com escopo no corpo da sub-issue)
- **Momento:** a cada nova instrução recebida durante Plan em `status: development`; review do PR pelo Argos
- **Métrica:** 0 PRs com arquivos modificados fora do escopo declarado do Plan; 100% das requisições não-relacionadas recusadas com referência explícita ao Plan ativo
