# Projeto ENEM - Análise de Microdados

Este repositório demonstra um pipeline completo para:

1. Download e processamento de microdados do ENEM
2. Simulação de cálculos estatísticos com NumPy
3. Análises específicas por estado com enfoque em fatores socioeconômicos
4. Cruzamento de variáveis para investigar desigualdades educacionais

## 📁 Estrutura do Projeto

```
projeto_enem/
│
├── enem_lib/                    # Pacote com módulos reutilizáveis
│   ├── __init__.py
│   ├── downloader.py           # Classe para download dos microdados
│   ├── numpy_ops.py            # Operações com NumPy (álgebra linear, simulações)
│   ├── analysis.py             # Análises genéricas dos dados do ENEM
│   └── paraiba_analysis.py     # Análises específicas para a Paraíba
│
├── main.py                     # Script principal que orquestra o pipeline
├── analyze_enem.py             # Funções de análise estatística
├── explore_data.py             # Scripts exploratórios dos dados
├── import_sys.py               # Ajustes de ambiente e paths
├── requirements.txt            # Dependências do projeto
├── README.md                   # Este arquivo
└── .gitignore                  # Arquivos a serem ignorados pelo Git
```

## 🚀 Como Usar

### 1. Pré-requisitos

- Python 3.8 ou superior
- Gerenciador de pacotes pip

### 2. Configuração do Ambiente

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual (Windows)
.venv\Scripts\activate

# Ativar ambiente virtual (Linux/Mac)
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Execução do Pipeline Principal

```bash
python main.py
```

O script irá:
- Solicitar os anos do ENEM a serem baixados (ex: 2019,2020 ou 2019:2021)
- Perguntar qual UF deseja analisar (ex: PB, SP, RJ)
- Baixar e processar os microdados
- Realizar análises de correlação entre fatores socioeconômicos e desempenho
- Gerar exemplos de uso do NumPy para álgebra linear e simulações

### 4. Exploração dos Dados

```bash
# Explorar estrutura dos arquivos baixados
python explore_data.py

# Executar análises específicas
python analyze_enem.py
```

## 📊 Funcionalidades Principais

### Download de Microdados
- Sistema de tentativas com retry automático
- Conversão eficiente de CSV para Parquet
- Verificação de integridade dos dados

### Análises Implementadas
- Correlação entre educação dos pais e desempenho no ENEM
- Relação entre situação ocupacional dos pais e notas
- Análise de renda familiar vs desempenho
- Bootstrap para estimar intervalos de confiança
- Estatísticas descritivas por grupo socioeconômico

### Exemplos NumPy
- Álgebra linear: autovalores, autovetores, matriz de covariância
- Simulação de dados com numpy.random
- Geração de distribuições normais para notas do ENEM

## 📋 Requirements

```
requests>=2.28.0
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
tqdm>=4.64.0
pyarrow>=10.0.0
fastparquet>=0.8.0
```

## 🔍 Variáveis Analisadas

### Questões Socioeconômicas
- **Q002**: Educação do pai
- **Q003**: Educação da mãe  
- **Q006**: Renda familiar (categorizada de A a Q)
- **Q007**: Renda mensal da família (valores específicos)

### Desempenho Acadêmico
- **NU_NOTA_CN**: Ciências da Natureza
- **NU_NOTA_CH**: Ciências Humanas
- **NU_NOTA_LC**: Linguagens e Códigos
- **NU_NOTA_MT**: Matemática
- **NU_NOTA_REDACAO**: Redação

## 💡 Exemplos de Uso

### Análise para múltiplos anos
```
Digite os anos para baixar (ex: 2014:2024 ou 2014,2015,2016): 2019:2021
Digite a UF que deseja analisar (ex: PB, SP, RJ): PB
```

### Análise para anos específicos
```
Digite os anos para baixar (ex: 2014:2024 ou 2014,2015,2016): 2017,2019,2021
Digite a UF que deseja analisar (ex: PB, SP, RJ): SP
```

## ⚠️ Observações Importantes

1. O download dos microdados pode demorar devido ao tamanho dos arquivos
2. Recomenda-se executar inicialmente com poucos anos para teste
3. Os dados são armazenados na pasta `dados_enem/` (não versionada)
4. Algumas variáveis podem ter nomenclaturas diferentes entre anos

## 📈 Resultados Esperados

- Estatísticas descritivas por grupo socioeconômico
- Correlações entre variáveis de renda/educação e desempenho
- Visualizações de distribuição de notas
- Exemplos de operações com NumPy aplicadas aos dados do ENEM

## 🔄 Próximas Melhorias

- [ ] Dividir apropriadamente o script em raw, bronze, silver e gold
- [ ] Filtar os dados a nível municipal != estadual 
- [ ] Adicionar mais visualizações gráficas
- [ ] Implementar modelos preditivos de desempenho
- [ ] Adicionar análise longitudinal (variação temporal)
- [ ] Criar interface web para exploração dos dados

## 📝 Licença

Este projeto é para fins educacionais e de pesquisa. Os dados do ENEM são disponibilizados pelo INEP sob licença aberta.

---

Para dúvidas ou sugestões, entre em contato ou abra uma issue no repositório.
