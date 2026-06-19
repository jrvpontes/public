# Workspace Manager Linux Mint

## Objetivo

Desenvolver um Workspace Manager utilizando:

- Python
- PyWinCtl
- wmctrl
- xprop
- xrandr

Arquivo único:

```text
/wks/paimon/wks-workspace.json
```

## Estado Atual

### Save

Funcionando de forma aceitável.

Responsável por salvar:

- janelas abertas
- posição
- tamanho
- monitor
- estado (maximizada/minimizada)
- WM_CLASS
- launch_command

### Open

Funcionando de forma aceitável.

Validado com:

- Eclipse
- Chrome
- Brave
- VSCode
- Sublime
- Tilix

Requisitos já atendidos:

- evitar abertura duplicada
- restaurar todas as janelas
- preservar compatibilidade com Eclipse
- corrigir abertura do Tilix

## Pendência

### Close

Necessita melhorias.

Problemas identificados:

- PID salvo não é confiável para fechamento posterior
- provável necessidade de fechamento por `window_id`
- possível divergência de formato entre `window_id` salvo e retornado pelo `wmctrl`
- o terminal que executa o script não deve ser fechado

## Regra Principal

Não alterar a arquitetura atual do `save` e do `open`.
O foco desta conversa é exclusivamente evoluir o script `close`.