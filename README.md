# 🛡️ DUAT - Development Universal Artificial Technology
> **Residência em IA — Instituto Eldorado**  
> *Projeto focado em análise, explicabilidade e promoção do pensamento crítico sobre confiabilidade da informação.*

---

## 📌 1. Visão Geral do Projeto (Challenge Statement)
O objetivo principal deste projeto é desenvolver um sistema inteligente que analisa dados textuais/noticiosos e exibe métricas claras de transparência para **auxiliar o usuário a avaliar a confiabilidade da informação**, diferenciando desinformação (intencional) de desinformação acidental/erro (misinformation vs. disinformation) e fomentando a autonomia crítica.

O sistema **não atua como "árbitro da verdade" absoluto**; em vez disso, fornece pistas contextuais, checagem de fontes e destaques textuais para guiar a reflexão do próprio usuário.

---

## 🎯 2. Escopo & Entregas do Challenge

| Entrega | Descrição | Status |
|---|---|---|
| **Algoritmo de Classificação** | Pipeline de IA com modelos supervisionados (KNN, SVM, Random Forest) e não supervisionados (K-Means, DBSCAN, Apriori). | `Em Definição` |
| **Protótipo Funcional / Produto Educacional** | Interface/dashboard para interação direta do usuário. | `Em Definição` |
| **Validação com Usuários Reais** | Testes empíricos com público-alvo (16–60 anos) e coleta de feedback. | `Pendente` |
| **Evidências de Impacto** | Análise de métricas de uso e ganho no senso crítico dos usuários. | `Pendente` |
| **Documentação Completa** | Registro de todas as fases, decisões arquiteturais e relatórios. | `Em Progresso` |

---

## 🧠 3. Pipeline de Inteligência Artificial & Dados

### 3.1. Dados & Pré-processamento
- **Fonte dos Dados:** [Fake.br Corpus](https://github.com/roneysco/Fake.br-Corpus) — dataset público de notícias em português com rótulos de veracidade.
- **Metodologia de Limpeza de Dados:**
  - Remoção de duplicatas.
  - Validação dos dados.
  - Remoção de outliers.
  - Padronização de proporções (4 casas decimais).
  - Undersampling para balanceamento de classes.

### 3.2. Modelagem & Algoritmos
- **Aprendizado Supervisionado:**
  - **KNN (K-Nearest Neighbors):** Baseline simples e interpretável.
  - **SVM (Support Vector Machine):** Eficaz em alta dimensionalidade com TF-IDF.
  - **Random Forest:** Robusto a overfitting e captura de relações não-lineares.
- **Aprendizado Não Supervisionado:**
  - **K-Means:** Agrupamento de notícias similares.
  - **DBSCAN:** Identificação de clusters densos e outliers.
  - **Apriori:** Descoberta de regras de associação entre features.

### 3.3. Métricas de Avaliação
- **Classificação:** Acurácia, Precisão, Recall, F1-score, Matriz de Confusão.
- **Regressão:** MAE (Mean Absolute Error).
- **Clustering:** Métricas internas de qualidade de agrupamento (a definir).

---

## 📊 4. Visualização de Dados & UX
Para garantir interpretabilidade e clareza aos usuários, o sistema integrará pelo menos **3 técnicas de visualização**:
1. **Histogramas:** Distribuição de variáveis numéricas (ex.: número de palavras, proporção de types).
2. **Gráficos de Barras:** Comparação de métricas entre classes (ex.: precisão por modelo).
3. **Matriz de Confusão:** Visualização de VP, VN, FP, FN para cada modelo.

* **Bibliotecas/Frameworks previstos:** Matplotlib, Seaborn, Plotly (a definir).

---

## 👥 5. Impacto Social, Ética e Pensamento Crítico

* **Comunidade Atendida:** 16–60 anos.
* **Promoção do Pensamento Crítico:** O sistema não emite veredito absoluto; apresenta critérios calculáveis (ex.: credibilidade da fonte, estrutura textual, proporção de palavras sensacionalistas) para que o usuário tome sua própria decisão.
* **Ética & Transparência (XAI):**
  * Uso de explicabilidade (XAI) para justificar a pontuação gerada.
  * Preservação da privacidade dos dados e conformidade com a LGPD.
  * Mitigação ativa de vieses ideológicos, regionais e algorítmicos.

---

## ⚙️ 6. Metodologia & Gestão de Projeto
* **Metodologia Ágil:** Scrum com sprints semanais (7 sprints no total), adaptado com quadro Kanban no GitHub Projects (To Do, In Progress, Review, Done).
* **Controle de Versão:** GitHub.
* **Linguagem Principal:** Python 3.14.7.

---

## 🚀 7. Como Executar o Projeto

```bash
# 1. Clonar o repositório
git clone [https://github.com/minneh8/Residence_AI_Challenge-1](https://github.com/minneh8/Residence_AI_Challenge-1)

# 2. Acessar a pasta
cd Residence_AI_Challenge-1

# 3. Criar e ativar ambiente virtual
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Rodar a aplicação / protótipo
python main.py
```

---

## 📁 8. Estrutura do Repositório

```text
Residence_AI_Challenge-1/
│
├── dataset_duat_final.csv
├── montar_dataset_duat.py
├── README.md
├── LICENSE
└── .gitignore
```

### Descrição dos Arquivos

| Arquivo | Descrição |
|---|---|
| `dataset_duat_final.csv` | Dataset final utilizado nos experimentos. |
| `montar_dataset_duat.py` | Script Python responsável pela montagem e preparação do dataset. |
| `README.md` | Documentação do projeto. |
| `LICENSE` | Licença de uso do projeto. |
| `.gitignore` | Arquivos e pastas ignorados pelo Git. |

---

## 📚 9. Referências

1. Fake.br Corpus. Disponível em: [https://github.com/roneysco/Fake.br-Corpus](https://github.com/roneysco/Fake.br-Corpus).
2. TJPR - O perigo das Fake News. Disponível em: [https://www.tjpr.jus.br](https://www.tjpr.jus.br).
3. FLESCH, Rudolf. *A new readability yardstick*. Journal of Applied Psychology, 1948.
4. Textstat (Python Package). Disponível em: [https://pypi.org/project/textstat/](https://pypi.org/project/textstat/).
5. SILVA, R. M. et al. *Fake.br-Corpus: um corpus para detecção de notícias falsas em português*. GitHub / USP, 2018.
6. MONTEIRO, R. A. et al. *Contributions to Natural Language Processing applied to Fake News Detection*. Information Sciences, 2018.
7. Biber, D. *Análise multidimensional: os números na Linguística*.
8. NLPNet (GitHub). Disponível em: [https://github.com/erickrf/nlpnet](https://github.com/erickrf/nlpnet).

---

## 👨‍💻 10. Equipe

**Integrantes:**
- Guilherme Leal
- Leonardo Varela Vacari
- Luís Comenale
- Lucas Marassi
- Lucas Minneh
- Murillo Caravita
- Pedro Henrique Bonetto da Costa

**Repositório:** [https://github.com/minneh8/Residence_AI_Challenge-1](https://github.com/minneh8/Residence_AI_Challenge-1)

---

## 📝 11. Status Atual

- ✅ Dataset inicial documentado e criterios definido.
- ✅ Técnicas de limpeza de dados definidas (undersampling, one-hot, TF-IDF).
- ✅ Algoritmos supervisionados testados (KNN, SVM, Random Forest).
- ✅ Algoritmos não supervisionados selecionados (K-Means, DBSCAN, Apriori).
- ⏳ Ajuste fino de hiperparâmetros em andamento.
- ⏳ Protótipo funcional em desenvolvimento.
- ⏳ Validação com usuários reais pendente.
