# Guia de uso — BTG para OFX

Converta extratos e faturas do **BTG Pactual** para OFX e importe no seu app de finanças.

> Leia este guia **antes** de rodar o programa pela primeira vez.

## Privacidade

- **Processamento 100% local** — seus dados bancários não são enviados para nenhum servidor.
- **Não compartilhe** extratos, faturas ou arquivos OFX gerados publicamente.
- O programa **não precisa de internet** para converter.

## O que é OFX?

OFX é um formato de extrato usado por apps como Quicken, GNUCash e outros. Este conversor transforma os arquivos exportados pelo BTG nesse formato.

> **Importante:** testado apenas com exportações do **BTG Pactual**. Não é um produto oficial do banco.

## Dois tipos de arquivo, dois comandos

| Tipo | Extensão | Comando |
| ---- | -------- | ------- |
| Conta corrente (extrato) | `.xls` | `checking` |
| Cartão de crédito (fatura) | `.xlsx` | `card` |

## Extrato conta corrente (.xls)

### Como baixar no BTG

1. Abra o app ou site do BTG e acesse sua **conta corrente**.
2. Exporte o **extrato** do período desejado.
3. Confirme que o arquivo termina em `.xls` (não `.xlsx`).

### Comando

```text
btg-ofx-converter checking Extrato_2026-01.xls
```

Gera `Extrato_2026-01.ofx` na mesma pasta do arquivo original.

## Fatura cartão (.xlsx)

### Como baixar no BTG

1. Abra o app ou site do BTG e acesse o **cartão de crédito**.
2. Baixe a **fatura** do ciclo desejado (ex.: `2026-08-15_Fatura_BTG.xlsx`).
3. Confirme que o arquivo termina em `.xlsx`.

### Remover a senha (obrigatório na maioria das faturas BTG)

A fatura baixada do BTG costuma vir **protegida por senha**. O conversor **não consegue ler** arquivos criptografados.

1. Abra o arquivo no **Excel** ou **LibreOffice Calc**.
2. Digite a senha quando solicitado (o BTG envia por email ou mostra no app).
3. **Salve uma cópia sem senha** — *Arquivo → Salvar como* e deixe os campos de senha vazios.
4. Use essa **cópia sem proteção** no comando `card` abaixo.

Se aparecer o erro `File is not a zip file`, o arquivo ainda está protegido — repita estes passos.

### Comando

```text
btg-ofx-converter card 2026-08-15_Fatura_BTG.xlsx
```

Gera `2026-08-15_Fatura_BTG.ofx` na mesma pasta.

## Exemplos por sistema

### Windows (PowerShell ou CMD)

```text
btg-ofx-converter.exe checking Extrato_2026-01.xls
btg-ofx-converter.exe card 2026-08-15_Fatura_BTG.xlsx
```

### macOS / Linux

```bash
chmod +x btg-ofx-converter-macos-arm64   # uma vez, após baixar
./btg-ofx-converter-macos-arm64 checking Extrato_2026-01.xls
./btg-ofx-converter-macos-arm64 card 2026-08-15_Fatura_BTG.xlsx
```

**macOS:** na primeira execução pode aparecer aviso do Gatekeeper. Use **Ajustes do Sistema → Privacidade e Segurança → Abrir assim mesmo**, ou rode uma vez:

```bash
xattr -cr ./btg-ofx-converter-macos-arm64
```

## Problemas ou sugestões

- Abra uma issue no GitHub: [github.com/joaovictornsv/btg-ofx-converter/issues](https://github.com/joaovictornsv/btg-ofx-converter/issues)
- Ou envie email: [hi@joaovictornsv.dev](mailto:hi@joaovictornsv.dev)

## Solução de problemas

- **Extensão errada:** use `checking` só para `.xls` e `card` só para `.xlsx`.
- **Fatura com senha / `File is not a zip file`:** abra a fatura no Excel ou LibreOffice com a senha do BTG e salve uma **cópia sem senha** antes de converter.
- **Arquivo não encontrado:** confira o caminho; no terminal, navegue até a pasta do arquivo antes de rodar.
- **Erro ao ler o arquivo:** o BTG pode ter alterado o formato — envie um exemplo (com dados sensíveis apagados) numa issue.
- **App não importa o OFX:** alguns apps de cartão exigem layout OFX específico; reporte qual app você usa.
