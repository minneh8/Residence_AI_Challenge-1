# DUAT — Development of Universal Architecture Technology

**DUAT (Development of Universal Architecture Technology)** é um sistema de inteligência artificial desenvolvido para o **Residence AI Challenge**. O projeto combina um backend em Python/Flask, responsável pelo processamento dos dados e inferência dos modelos, com uma interface web leve e intuitiva construída em HTML, CSS e JavaScript.

---

## Visão geral

O DUAT foi estruturado para receber entradas do usuário pela interface web, transformá-las em features utilizáveis pelos modelos e gerar uma resposta/predição por meio do pipeline de inferência.

A arquitetura é dividida em duas camadas:

- **Backend** — API Flask que coordena o pipeline, a extração de features e o carregamento dos modelos.
- **Frontend** — interface web estática que consome a API e apresenta os resultados de forma clara.

---

## Arquitetura

```text
┌──────────────┐        requisição         ┌──────────────────┐
│   Frontend   │ ────────────────────────► │   Backend Flask  │
│  HTML/CSS/JS │                           │                  │
└──────────────┘ ◄──────────────────────── └──────────────────┘
                        resposta                    │
                                                    ▼
                                        ┌────────────────────────┐
                                        │  Extração de features  │
                                        └────────────────────────┘
                                                    │
                                                    ▼
                                        ┌────────────────────────┐
                                        │     Núcleo DUAT        │
                                        └────────────────────────┘
                                                    │
                                                    ▼
                                        ┌────────────────────────┐
                                        │   Modelos treinados    │
                                        └────────────────────────┘
```

---

## Estrutura do projeto

```text
DUAT/
├── backend/
│   ├── app.py                  # API Flask e rotas principais
│   ├── duat_core.py            # Núcleo de processamento e inferência
│   ├── extracao_features.py    # Extração e preparação de features
│   └── modelos/                # Modelos e artefatos treinados
├── frontend/
│   ├── index.html              # Página principal
│   ├── app.js                  # Lógica da interface e chamadas à API
│   ├── styles.css              # Estilização
│   └── assets/                 # Recursos estáticos
├── requirements.txt            # Dependências Python
├── LICENSE
└── README.md
```

---

## Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/minneh8/Residence_AI_Challenge-1.git
cd Residence_AI_Challenge-1
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Inicie o backend

```bash
cd backend
python app.py
```

A API normalmente ficará disponível em:

```text
http://127.0.0.1:5000
```

### 5. Abra o frontend

Você pode abrir diretamente:

```text
frontend/index.html
```

Ou servir a pasta com um servidor estático:

```bash
cd frontend
python -m http.server 5500
```

E acessar:

```text
http://127.0.0.1:5500
```

---

## Fluxo de funcionamento

1. O usuário interage com a interface no frontend.
2. O frontend envia os dados para a API Flask.
3. O backend processa a entrada e extrai as features necessárias.
4. O núcleo DUAT coordena o pipeline de inferência.
5. O modelo treinado é utilizado para gerar o resultado.
6. A resposta é retornada ao frontend e exibida ao usuário.

---

## Principais módulos

| Módulo | Responsabilidade |
|---|---|
| `backend/app.py` | API Flask, rotas e integração com o frontend |
| `backend/duat_core.py` | Lógica central e pipeline de inferência do DUAT |
| `backend/extracao_features.py` | Tratamento dos dados e extração de features |
| `backend/modelos/` | Armazenamento dos modelos treinados |
| `frontend/app.js` | Controle da interface e comunicação com a API |
| `frontend/index.html` | Estrutura visual da aplicação |
| `frontend/styles.css` | Estilização e identidade visual |

---

## Tecnologias

- Python
- Flask
- Machine Learning
- HTML5
- CSS3
- JavaScript

---

## Licença

Este projeto está licenciado sob os termos do arquivo [LICENSE](./LICENSE).
