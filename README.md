# Disponibilidade de um serviço replicado

Projeto dos Exercícios 1.1 e 1.2 de Computação Distribuída.

## Modelo matemático

Considere n servidores independentes. Cada servidor está disponível com probabilidade p. O serviço funciona quando pelo menos k servidores estão disponíveis. Se X é o número de servidores disponíveis, então X segue uma distribuição Binomial(n,p).

A disponibilidade é:

A(n,k,p) = soma de i=k até n de C(n,i) p^i (1-p)^(n-i)

Casos importantes:

- Consulta, k=1: A(n,1,p) = 1 - (1-p)^n.
- Atualização, k=n: A(n,n,p) = p^n.
- Maioria: k = ceil(n/2).

## Implementação

O arquivo src/disponibilidade.py implementa a fórmula analítica, a maioria e a simulação Monte Carlo. Em cada rodada, o programa sorteia a disponibilidade de todos os servidores e verifica se pelo menos k estão ativos.

Para executar:

1. Instale Python 3.10 ou superior e NumPy.
2. Execute python scripts/gerar_resultados.py.
3. Consulte os CSVs e gráficos SVG da pasta resultados.

Os resultados experimentais se aproximam dos analíticos quando o número de rodadas aumenta. A semente aleatória pode ser fixada para reproduzir os resultados.

## Testes

Execute python -m unittest discover -s tests -v.

## Conclusões

Aumentar o número de réplicas melhora o caso k=1, pois basta uma réplica funcionar. No caso k=n, aumentar n reduz a disponibilidade, pois todas precisam funcionar. O caso de maioria fica entre esses extremos e depende de p.

## Estrutura

- src/: modelo analítico e simulador.
- scripts/: geração de tabelas e gráficos.
- tests/: testes automatizados.
- resultados/: resultados produzidos pela execução.
