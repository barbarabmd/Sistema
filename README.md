# Relatório de Testes: Sistema de Avaliação Financeira de Clientes

## 1. Introdução

Este documento detalha os testes End-to-End (E2E) e de Carga realizados no sistema de IA para avaliação de clientes de cartão de crédito. O sistema é composto por um frontend (Nginx + HTML/JS/CSS), um backend (FastAPI + Python) que utiliza um modelo de Machine Learning, e é orquestrado via Docker Compose.

**Objetivo dos Testes:**
* **Testes E2E (Selenium):** Verificar a funcionalidade completa do fluxo de avaliação do cliente, desde a inserção de dados no frontend até a exibição do resultado processado pelo backend.
* **Testes de Carga (JMeter):** Avaliar o desempenho e a estabilidade do backend sob múltiplas requisições concorrentes, identificando gargalos e a capacidade de resposta do sistema.

**Importante:** O modelo de Machine Learning `modelo_cluster_cartao_credito.pkl` original não foi fornecido. Para possibilitar os testes do backend e do fluxo completo, um **modelo dummy (simulado)** foi criado. Este modelo dummy retorna um dos cinco clusters de forma aleatória. Portanto, os testes validam a integração e o fluxo do sistema, mas não a lógica de negócio específica do modelo de IA original.

## 2. Metodologia de Testes

### 2.1. Testes End-to-End (E2E) com Selenium

* **Ferramenta:** Selenium WebDriver com Python.
* **Navegador:** Google Chrome.
* **Abordagem:** Simulação da interação do usuário com a interface web da aplicação. O script automatizado preenche o formulário de avaliação, submete os dados e verifica se o resultado é exibido corretamente na tela.
* **Ambiente:** Aplicação rodando localmente via Docker Compose (`http://localhost:80` para o frontend).

### 2.2. Testes de Carga com JMeter

* **Ferramenta:** Apache JMeter.
* **Alvo:** Endpoint POST `/avaliar` do serviço de backend (`http://localhost:8000/avaliar`).
* **Abordagem:** Configuração de um plano de testes para simular múltiplos usuários enviando requisições simultâneas ao backend. Foram coletadas métricas de tempo de resposta, vazão (throughput) e taxa de erros.
* **Tipos de Teste de Carga:**
    * **Teste de Linha de Base:** Carga leve para estabelecer um comportamento padrão.
    * **Teste de Estresse (Conceitual):** Aumento gradual da carga para identificar o ponto de quebra ou degradação significativa de performance. Os scripts fornecidos permitem configurar este tipo de teste.
* **Dados de Teste:** Um arquivo CSV (`client_data.csv`) pode ser usado para fornecer dados variados para as requisições, ou dados fixos podem ser configurados diretamente no JMeter.

## 3. Roteiros de Testes

### 3.1. Roteiro de Teste E2E (Selenium)

**ID do Teste:** E2E_AVALIACAO_001
**Título:** Avaliação de Cliente Bem-Sucedida (Caminho Feliz)

**Pré-condições:**
1.  O ambiente Docker com os containers do frontend e backend deve estar em execução.
2.  O backend deve estar funcional (com o modelo dummy `modelo_cluster_cartao_credito.pkl`).
3.  O navegador Chrome e o ChromeDriver correspondente devem estar instalados e configurados.

**Passos:**
1.  Abrir o navegador e navegar para a URL do frontend: `http://localhost:80/`.
2.  Verificar se a página "Avaliação Financeira" é carregada corretamente com todos os campos do formulário: "Nome do Futuro Cliente", "Limite Restante", "Quantidade em Compras", "Saques", "Limite de Crédito", "Pagamentos" e o botão "Enviar para Análise".
3.  Preencher o campo "Nome do Futuro Cliente" com "Cliente Teste Selenium".
4.  Preencher o campo "Limite Restante" com "1000.50".
5.  Preencher o campo "Quantidade em Compras" com "500.25".
6.  Preencher o campo "Saques" com "100.00".
7.  Preencher o campo "Limite de Crédito" com "5000.00".
8.  Preencher o campo "Pagamentos" com "300.75".
9.  Clicar no botão "Enviar para Análise".

**Resultado Esperado:**
1.  Após a submissão, uma mensagem de resultado deve ser exibida na seção "resultado" da página.
2.  A mensagem deve iniciar com "Resultado: " seguido por uma das seguintes descrições (devido ao modelo dummy):
    * "São clientes que possuem grandes limites totais no cartão, mas não são bons pagadores, logo, não têm muito limite disponível."
    * "Clientes que gastam muito com saques. Compram pouco no crédito e são bons pagadores."
    * "Clientes com maior preferência em usar débito e saques ao invés do crédito."
    * "São os clientes que menos utilizam os serviços financeiros."
    * "Utilizam muito o serviço de crédito e são bons pagadores."

### 3.2. Roteiro de Teste de Carga (JMeter)

**ID do Teste:** CARGA_AVALIACAO_001
**Título:** Teste de Carga Base no Endpoint /avaliar

**Pré-condições:**
1.  O ambiente Docker com o container do backend deve estar em execução e acessível em `http://localhost:8000`.
2.  O Apache JMeter deve estar instalado.

**Configuração do Plano de Testes (JMeter):**
1.  **Thread Group (Grupo de Usuários):**
    * Número de Threads (usuários): 10
    * Ramp-up Period (segundos): 5 (tempo para iniciar todos os usuários)
    * Loop Count (Contador de Repetição): 10 (cada usuário faz 10 requisições)
2.  **HTTP Request Defaults (Padrões de Requisição HTTP - Opcional):**
    * Server Name or IP: `localhost`
    * Port Number: `8000`
3.  **HTTP Request Sampler (Amostra de Requisição HTTP):**
    * Nome: `POST /avaliar`
    * Protocolo: `http`
    * Método: `POST`
    * Path: `/avaliar`
    * Corpo da Requisição (Body Data - JSON):
        ```json
        {
            "name": "Cliente Carga JMeter",
            "balance": 1500.75,
            "purchases": 350.00,
            "cash_advance": 70.00,
            "credit_limit": 3000.00,
            "payments": 200.50
        }
        ```
        *(Opcionalmente, usar CSV Data Set Config para variar os dados)*
4.  **HTTP Header Manager (Gerenciador de Cabeçalhos HTTP):**
    * Adicionar: `Content-Type` com valor `application/json`
5.  **Listeners (Ouvintes):**
    * View Results Tree (Árvore de Resultados) - para depuração.
    * Summary Report (Relatório Sumário) - para métricas agregadas.
    * Aggregate Graph (Gráfico Agregado) - para visualização de tendências.

**Execução:**
1.  Abrir o JMeter e carregar o script JMX (`teste_carga_avaliacao.jmx`).
2.  Iniciar o teste.
3.  Monitorar os listeners para observar o comportamento do sistema.

**Resultado Esperado:**
1.  **Taxa de Erro:** Próxima de 0%.
2.  **Tempo Médio de Resposta:** Dentro de um limite aceitável (ex: < 500ms, a ser definido conforme requisitos não funcionais).
3.  **Throughput (Vazão):** Número de requisições por segundo que o sistema consegue processar.
4.  O sistema deve permanecer estável durante o teste.

## 4. Configuração do Ambiente de Teste

1.  **Docker e Docker Compose:** Necessários para executar a aplicação.
2.  **Python 3.x:** Para executar o script Selenium e o script de criação do modelo dummy.
    * Bibliotecas Python: `selenium`, `webdriver-manager`, `unittest` (para Selenium); `scikit-learn`, `joblib`, `numpy` (para criar o modelo dummy).
3.  **Apache JMeter:** Para executar os testes de carga.
4.  **Navegador Web:** Google Chrome (para testes Selenium).
5.  **ChromeDriver:** Gerenciado automaticamente pelo `webdriver-manager` ou instalado manualmente e adicionado ao PATH do sistema.
6.  **Estrutura de Arquivos (sugerida):**
    ```
    /seu_projeto/
    ├── backend/
    │   ├── Dockerfile
    │   ├── main.py
    │   ├── models.py
    │   ├── requirements.txt
    │   ├── utils.py
    │   ├── create_dummy_model.py  <-- NOVO (para gerar o modelo dummy)
    │   └── modelo_cluster_cartao_credito.pkl <-- GERADO pelo script acima
    ├── frontend/
    │   ├── Dockerfile
    │   └── app/
    │       ├── index.html
    │       ├── css/
    │       │   └── styles.css
    │       └── js/
    │           └── scripts.js
    ├── docker-compose.yml
    ├── .gitignore
    ├── test_e2e_avaliacao.py      <-- SCRIPT SELENIUM
    ├── teste_carga_avaliacao.jmx  <-- SCRIPT JMETER
    └── client_data.csv            <-- DADOS OPCIONAIS PARA JMETER
    ```

**Passos para Configurar e Executar:**

1.  **Criar Modelo Dummy:**
    * Navegue até o diretório `backend`.
    * Execute o script: `python create_dummy_model.py`. Isso criará o arquivo `modelo_cluster_cartao_credito.pkl`.
2.  **Iniciar a Aplicação:**
    * No diretório raiz do projeto (onde está `docker-compose.yml`), execute: `docker-compose up --build -d`.
3.  **Executar Testes E2E (Selenium):**
    * No diretório raiz do projeto, execute: `python test_e2e_avaliacao.py`.
4.  **Executar Testes de Carga (JMeter):**
    * Abra o Apache JMeter.
    * Clique em "File" > "Open" e selecione o arquivo `teste_carga_avaliacao.jmx`.
    * No painel esquerdo, selecione o "Thread Group" para ajustar parâmetros de carga (número de usuários, ramp-up, loops) se necessário.
    * Clique no botão "Start" (ícone de play verde).
    * Acompanhe os resultados nos Listeners configurados (View Results Tree, Summary Report).

## 5. Resultados Encontrados (Exemplo Teórico)

Esta seção descreveria os resultados reais obtidos após a execução dos testes. Como não posso executar o ambiente, apresento um formato de como os resultados seriam reportados.

### 5.1. Resultados dos Testes E2E (Selenium)

| ID do Teste        | Título                               | Status      | Observações                                                                                                |
| ------------------ | ------------------------------------ | ----------- | ---------------------------------------------------------------------------------------------------------- |
| E2E_AVALIACAO_001  | Avaliação de Cliente Bem-Sucedida    | **PASSOU** | O formulário foi preenchido, submetido e uma mensagem de resultado válida foi exibida, conforme esperado.    |
| _(Outros cenários)_ | _(Descrição)_                       | _(PASSOU/FALHOU)_ | _(Detalhes)_                                                                                               |

**Capturas de Tela / Vídeos:** (Opcional, mas recomendado para evidências, especialmente para falhas)

### 5.2. Resultados dos Testes de Carga (JMeter)

**Configuração do Teste de Linha de Base:**
* Threads (Usuários): 10
* Ramp-up: 5 segundos
* Loops: 10
* Duração total aproximada: ~5-10 segundos (dependendo do tempo de resposta)

**Resultados do Teste de Linha de Base (Exemplo):**

| Métrica                     | Valor (Exemplo)             | Unidade    |
| --------------------------- | --------------------------- | ---------- |
| Samples (Total Requisições) | 100                         | -          |
| Average (Tempo Médio Resp.) | 85                          | ms         |
| Median (Tempo Mediana Resp.)| 75                          | ms         |
| 90% Line (Percentil 90)     | 120                         | ms         |
| Min (Tempo Mínimo Resp.)    | 40                          | ms         |
| Max (Tempo Máximo Resp.)    | 210                         | ms         |
| Error % (Taxa de Erro)      | 0.00                        | %          |
| Throughput (Vazão)          | 15.5                        | req/segundo|
| KB/sec (Transferência)      | 5.2                         | KB/s       |

**(Análise para o Teste de Linha de Base):**
* O sistema respondeu rapidamente sob carga leve.
* Nenhum erro foi observado.
* O throughput indica a capacidade atual com essa carga.

**Configuração do Teste de Estresse (Exemplo):**
* Threads (Usuários): Aumentar gradualmente (ex: 50, 100, 200) ou usar um plugin para ramp-up contínuo.
* Duração: Ex: 5 minutos por nível de carga.

**Resultados do Teste de Estresse (Exemplo Hipotético):**
* **Com 50 usuários:** Tempo médio 150ms, Erros 0%, Throughput 30 req/seg.
* **Com 100 usuários:** Tempo médio 350ms, Erros 1%, Throughput 45 req/seg. (Início de degradação)
* **Com 200 usuários:** Tempo médio 800ms, Erros 5%, Throughput 40 req/seg. (Sistema sobrecarregado, throughput cai)

**(Análise para o Teste de Estresse):**
* Identificar o ponto onde o tempo de resposta aumenta significativamente e/ou erros começam a aparecer.
* Observar o comportamento do uso de CPU/memória dos containers do backend durante o teste de estresse (`docker stats`).

**Dados Exportados do JMeter (CSV):**
Os resultados detalhados podem ser exportados do JMeter (via Listeners como Summary Report ou Aggregate Report) para um arquivo CSV para análise posterior. Este arquivo conteria colunas como: `timeStamp`, `elapsed`, `label`, `responseCode`, `responseMessage`, `threadName`, `success`, `bytes`, `sentBytes`, `grpThreads`, `allThreads`, `URL`, `Latency`, `IdleTime`, `Connect`.

## 6. Conclusões e Recomendações

**Conclusões (Exemplo):**
* O fluxo E2E da aplicação, desde a interface do usuário até a resposta do backend, está funcionando conforme o esperado (validado com modelo dummy).
* O backend demonstrou bom desempenho sob a carga de linha de base (10 usuários concorrentes), com tempos de resposta rápidos e sem erros.
* *(Se o teste de estresse fosse executado)* O sistema começou a mostrar sinais de degradação com X usuários, indicando um possível gargalo no [componente específico, ex: processamento da IA, I/O do banco de dados (não aplicável aqui diretamente)].

**Recomendações (Exemplo):**
1.  **Modelo de IA Real:** Para validar a lógica de negócio e a precisão das avaliações, os testes (especialmente E2E) devem ser reexecutados com o modelo de Machine Learning original (`modelo_cluster_cartao_credito.pkl`). Casos de teste E2E específicos para cada cluster esperado deveriam ser criados.
2.  **Monitoramento Avançado:** Implementar monitoramento mais detalhado no backend (ex: com Prometheus/Grafana) para observar o consumo de recursos (CPU, memória), latências internas e outros aspectos durante os testes de carga.
3.  **Validação de Entrada no Backend:** Embora o frontend use campos `type="number"` e `required`, adicionar validação robusta no backend para os tipos de dados e campos obrigatórios é uma boa prática para garantir a integridade dos dados e a segurança.
4.  **Otimização de Performance:** Se os testes de estresse revelarem gargalos, investigar otimizações no código do backend, no modelo de ML (se aplicável), ou considerar escalonamento horizontal (mais réplicas do container backend).
5.  **Testes de Longa Duração (Soak Tests):** Considerar a execução de testes de carga por períodos mais longos (ex: várias horas) para identificar possíveis vazamentos de memória ou outros problemas de estabilidade a longo prazo.

## 7. Anexos

* Código-fonte com modificações: `create_dummy_model.py` (adicionado ao diretório `backend`).
* Script de testes do JMeter: `teste_carga_avaliacao.jmx`.
* Dados de entrada para JMeter (opcional): `client_data.csv`.
* Script de testes do Selenium: `test_e2e_avaliacao.py`.
