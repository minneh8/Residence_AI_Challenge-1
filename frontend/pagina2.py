import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import main as mn 
import pagina3 as pg3

try:
    from PIL import Image, ImageTk
    # Pillow está instalada: guardamos essa informação numa flag
    TEM_PIL = True
# Se a Pillow não estiver instalada, o programa continua funcionando sem ela
except ImportError:
    TEM_PIL = False

# ------------------------------------------------------------
# PÁGINA 2
# ------------------------------------------------------------
# PÁGINA 2: exibida ao clicar em 'Avançar' na página 3; mostra a notícia e a tabela de features
def mostrar_pagina_2(texto_noticia):
    # Apaga tudo o que estava na tela antes de desenhar esta página
    mn.limpar_tela()

    # Logo no canto superior direito
    # Carrega o logo reduzido (máx. 110x80) para o canto superior da página
    mn.imagens["logo_voltar"] = mn.carregar_imagem((110, 80))

    # Se a imagem carregou, usa um Label com a imagem como botão de voltar
    if mn.imagens["logo_voltar"]:
        botao_logo = tk.Label(
            mn.root,
            image=mn.imagens["logo_voltar"],
            bg=mn.COR_FUNDO,
            cursor="hand2"
        )
    # Se a imagem não carregou, usa um Label com o texto 'DUAT' no lugar
    else:
        botao_logo = tk.Label(
            mn.root,
            text="DUAT",
            bg=mn.COR_FUNDO,
            fg=mn.COR_TEXTO,
            font=("Arial", 18, "bold"),
            cursor="hand2"
        )

    # Posiciona o logo no canto superior direito (relx/rely são proporções da janela)
    botao_logo.place(relx=0.97, rely=0.04, anchor="ne")
    # Ao clicar no logo, volta para a página 1 (tela inicial)
    botao_logo.bind("<Button-1>", lambda event: mn.mostrar_pagina_1())

    # Conteúdo da segunda página
    # Frame que agrupa o título, posicionado no topo e centralizado
    conteudo = tk.Frame(mn.root, bg=mn.COR_FUNDO)
    conteudo.place(relx=0.5, rely=0.1, anchor="center")

    # Título da página
    tk.Label(
        conteudo,
        text="Análise da notícia",
        bg=mn.COR_FUNDO,
        fg=mn.COR_TEXTO,
        font=("Arial", 40, "bold")
    ).pack(pady=(0, 30))

    # --------------------------------------------------------
    # NOTÍCIA ENVIADA
    # Label e caixa ficam lado a lado
    # --------------------------------------------------------
    # Frame que agrupa o rótulo e a caixa com a notícia enviada
    noticia = tk.Frame(mn.root, bg=mn.COR_FUNDO)
    noticia.place(relx=0.5, rely=0.22, anchor="center")

    # Rótulo laranja 'Notícia enviada:' (coluna 0 da grade)
    tk.Label(
        noticia,
        text="Notícia enviada:",
        bg=mn.COR_FUNDO,
        fg=mn.COR_LARANJA,
        font=("Arial", 16, "bold")
    ).grid(row=0, column=0, padx=(0, 20), sticky="e")

    # Caixa com o texto da notícia, já resumido (coluna 1). wraplength quebra a linha aos 700 px
    caixa_noticia = tk.Label(
        noticia,
        text=mn.resumir_noticia(texto_noticia),
        bg=mn.COR_INPUT,
        fg=mn.COR_TEXTO,
        font=("Arial", 15),
        wraplength=700,
        justify="left",
        anchor="w",
        padx=25,
        pady=20
    )
    caixa_noticia.grid(row=0, column=1, sticky="w")

    # --------------------------------------------------------
    # CONTAINER DA TABELA
    # --------------------------------------------------------

    # Tamanho do container da tabela, em pixels
    LARGURA_TABELA = 1100
    ALTURA_TABELA = 550

    # Canvas que serve de fundo para o retângulo arredondado da tabela
    canvas_tabela = tk.Canvas(
        mn.root,
        width=LARGURA_TABELA,
        height=ALTURA_TABELA,
        bg=mn.COR_FUNDO,
        highlightthickness=0
    )

    # Centraliza o canvas na janela
    canvas_tabela.place(
        relx=0.5,
        rely=0.65,
        anchor="center"
    )

    # Desenha o retângulo arredondado (raio 20) com fundo azul e borda laranja
    mn.retangulo_arredondado(
        canvas_tabela,
        5,
        5,
        LARGURA_TABELA - 5,
        ALTURA_TABELA - 5,
        20,
        fill=mn.COR_INPUT,
        outline=mn.COR_LARANJA,
        width=3
    )

    # Frame interno que vai receber a tabela
    frame_tabela = tk.Frame(
        canvas_tabela,
        bg=mn.COR_INPUT
    )

    # Coloca o frame dentro do canvas, no centro, com 10 px de folga em cada lado
    canvas_tabela.create_window(
        LARGURA_TABELA/2,
        ALTURA_TABELA/2,
        window=frame_tabela,
        width=LARGURA_TABELA-20,
        height=ALTURA_TABELA-20
    )

    # Configuração visual (estilo) da tabela
    style = ttk.Style()
    # O tema 'default' permite personalizar as cores do Treeview
    style.theme_use("default")

    # Estilo do corpo da tabela: cores, borda, altura das linhas e fonte
    style.configure(
    "Treeview",
    background=mn.COR_INPUT,
    foreground="white",
    fieldbackground=mn.COR_INPUT,
    bordercolor=mn.COR_LARANJA,
    borderwidth=1,
    rowheight=35,
    font=("Arial", 11)
    )   

    # Estilo do cabeçalho da tabela: fundo laranja, texto branco e fonte em negrito
    style.configure(
    "Treeview.Heading",
    background=mn.COR_LARANJA,
    foreground="white",
    relief="solid",
    borderwidth=1,
    font=("Arial", 12, "bold")
    )

    # Nomes das duas colunas da tabela
    colunas = ("Features", "Valor")

    # Cria a tabela. show='headings' esconde a coluna extra de árvore; height=8 são as linhas visíveis
    tabela = ttk.Treeview(
        frame_tabela,
        columns=colunas,
        show="headings",
        height=8
    )

    # Define o título, a largura e o alinhamento de cada coluna
    tabela.heading("Features",text="Features")
    tabela.heading("Valor",text="Valor")
    tabela.column("Features",width=500,anchor="center")
    tabela.column("Valor",width=300,anchor="center")
    # Exibe a tabela preenchendo todo o frame, com 10 px de margem
    tabela.pack(fill="both",expand=True,padx=10,pady=10)
    # Insere as linhas da tabela (feature, valor).
    # Atenção: os valores são fixos (exemplo), não são calculados a partir da notícia
    tabela.insert( "","end",values=("tamanho_medio_palavra", "0,2"))
    tabela.insert("","end",values=("pct_erro_ortografico", "0,3"))
    tabela.insert("","end",values=("estudos_previos_proporcao", "0,07"))
    tabela.insert( "","end",values=("fontes_proporcao ", "0,9"))
    tabela.insert("","end",values=("emotividade", "0,55"))
    tabela.insert("","end",values=("sensacionalismo_proporcao", "0,15"))
    tabela.insert( "","end",values=("verbos_proporcao", "0,85"))
    tabela.insert("","end",values=("verbos_subj_imp_proporcao ", "0,55"))
    tabela.insert("","end",values=("substantivos_proporcao", "0,15"))
    tabela.insert( "","end",values=("adjetivos_proporcao", "0,85"))
    tabela.insert("","end",values=("adverbios_proporcao", "0,55"))
    tabela.insert("","end",values=("modais_proporcao", "0,15"))
    tabela.insert( "","end",values=("pronomes_proporcao", "0,2"))
    tabela.insert("","end",values=("pausalidade", "0,3"))
    tabela.insert("","end",values=("indice_legibilidade", "0,07"))
    tabela.insert( "","end",values=("tamanho_medio_frase ", "0,2"))

