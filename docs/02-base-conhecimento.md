# Base de Conhecimento

## Dados Utilizados

| Arquivo/Fonte | Formato | Papel na Aura |
|---|---|---|
| `data/transacoes.csv` | CSV | Entender padrao de gastos e saldo do periodo |
| `data/historico_atendimento.csv` | CSV | Dar continuidade ao contexto de relacionamento |
| `data/perfil_investidor.json` | JSON | Personalizar o nivel de explicacao e o foco das respostas |
| `data/produtos_financeiros.json` | JSON | Explicar produtos financeiros disponiveis de forma educativa |
| Selic aberta do Banco Central | API oficial | Trazer referencia oficial de taxa basica de juros |
| `data/selic_bacen.json` | JSON | Snapshot local da Selic oficial para reprodutibilidade |
| `data/tesouro_direto_produtos.json` | JSON | Snapshot local dos produtos do Tesouro Direto |
| Produtos do Tesouro Direto | Pagina oficial | Enriquecer a explicacao de titulos publicos |

## Estrategia de Integracao

### Dados locais
Os arquivos mockados da DIO sao carregados com Python e Pandas para garantir consistencia de leitura e facilitar os calculos de diagnostico.

### Fontes oficiais
- Selic: consulta programatica no endpoint oficial do Banco Central associado a serie 11
- Tesouro Direto: uso de snapshot local estruturado a partir da pagina oficial, porque a rota publica pode bloquear fetch automatizado por script

### Regra de confianca
Se a fonte oficial nao estiver acessivel no momento da execucao:
- a Aura continua funcionando com os dados locais;
- o app sinaliza a indisponibilidade;
- nenhuma resposta passa a "inventar" dado de mercado.

## Exemplo de Contexto Montado

```text
CLIENTE:
- Nome: Joao Silva
- Perfil investidor: moderado
- Objetivo principal: construir reserva de emergencia
- Renda mensal: R$ 5.000,00

RESUMO FINANCEIRO:
- Entradas: R$ 5.000,00
- Saidas: R$ 2.488,90
- Saldo do periodo: R$ 2.511,10
- Maior categoria de gasto: moradia

PRODUTOS DISPONIVEIS PARA EDUCACAO:
- Tesouro Selic
- CDB Liquidez Diaria
- LCI/LCA
- Fundo Imobiliario (FII)
- Fundo de Acoes

FONTES OFICIAIS:
- Selic oficial mais recente disponivel
- Titulos encontrados no Tesouro Direto
```

## Decisao de Projeto
As fontes oficiais foram adicionadas e snapshotadas em `data/` para elevar a credibilidade e a reprodutibilidade da demo. Isso reforca a proposta de um agente educativo que trabalha com contexto real e rastreavel, nao apenas com texto gerado.
