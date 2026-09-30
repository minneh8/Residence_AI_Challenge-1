# ------------------------------------------------------------
# PÁGINA 2
# ------------------------------------------------------------
# PÁGINA 2: exibida ao clicar em 'Avançar' na página 3; mostra a notícia e a tabela de features
def mostrar_pagina_2(texto_noticia):
    # Apaga tudo o que estava na tela antes de desenhar esta página
    limpar_tela()

    # Logo no canto superior direito
    # Carrega o logo reduzido (máx. 110x80) para o canto superior da página
    imagens["logo_voltar"] = carregar_imagem((110, 80))

    # Se a imagem carregou, usa um Label com a imagem como botão de voltar
    if imagens["logo_voltar"]:
        botao_logo = tk.Label(
            root,
            image=imagens["logo_voltar"],
            bg=COR_FUNDO,
            cursor="hand2"
        )
    # Se a imagem não carregou, usa um Label com o texto 'DUAT' no lugar
    else:
        botao_logo = tk.Label(
            root,
            text="DUAT",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Arial", 18, "bold"),
            cursor="hand2"
        )

    # Posiciona o logo no canto superior direito (relx/rely são proporções da janela)
    botao_logo.place(relx=0.97, rely=0.04, anchor="ne")
    # Ao clicar no logo, volta para a página 1 (tela inicial)
    botao_logo.bind("<Button-1>", lambda event: mostrar_pagina_1())

    # Conteúdo da segunda página
    # Frame que agrupa o título, posicionado no topo e centralizado
    conteudo = tk.Frame(root, bg=COR_FUNDO)
    conteudo.place(relx=0.5, rely=0.1, anchor="center")

    # Título da página
    tk.Label(
        conteudo,
        text="Análise da notícia",
        bg=COR_FUNDO,
        fg=COR_TEXTO,
        font=("Arial", 40, "bold")
    ).pack(pady=(0, 30))

    # --------------------------------------------------------
    # NOTÍCIA ENVIADA
    # Label e caixa ficam lado a lado
    # --------------------------------------------------------
    # Frame que agrupa o rótulo e a caixa com a notícia enviada
    noticia = tk.Frame(root, bg=COR_FUNDO)
    noticia.place(relx=0.5, rely=0.22, anchor="center")

    # Rótulo laranja 'Notícia enviada:' (coluna 0 da grade)
    tk.Label(
        noticia,
        text="Notícia enviada:",
        bg=COR_FUNDO,
        fg=COR_LARANJA,
        font=("Arial", 16, "bold")
    ).grid(row=0, column=0, padx=(0, 20), sticky="e")

    # Caixa com o texto da notícia, já resumido (coluna 1). wraplength quebra a linha aos 700 px
    caixa_noticia = tk.Label(
        noticia,
        text=resumir_noticia(texto_noticia),
        bg=COR_INPUT,
        fg=COR_TEXTO,
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
        root,
        width=LARGURA_TABELA,
        height=ALTURA_TABELA,
        bg=COR_FUNDO,
        highlightthickness=0
    )

    # Centraliza o canvas na janela
    canvas_tabela.place(
        relx=0.5,
        rely=0.65,
        anchor="center"
    )

    # Desenha o retângulo arredondado (raio 20) com fundo azul e borda laranja
    retangulo_arredondado(
        canvas_tabela,
        5,
        5,
        LARGURA_TABELA - 5,
        ALTURA_TABELA - 5,
        20,
        fill=COR_INPUT,
        outline=COR_LARANJA,
        width=3
    )

    # Frame interno que vai receber a tabela
    frame_tabela = tk.Frame(
        canvas_tabela,
        bg=COR_INPUT
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
    background=COR_INPUT,
    foreground="white",
    fieldbackground=COR_INPUT,
    bordercolor=COR_LARANJA,
    borderwidth=1,
    rowheight=35,
    font=("Arial", 11)
    )   

    # Estilo do cabeçalho da tabela: fundo laranja, texto branco e fonte em negrito
    style.configure(
    "Treeview.Heading",
    background=COR_LARANJA,
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

#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------



# ------------------------------------------------------------
# PAGINA 3
# ------------------------------------------------------------

# PÁGINA 3: primeira página após o envio da notícia; mostra apenas a tabela de features
# e um botão 'Avançar' que leva para a página 2
def mostrar_pagina_3(texto_noticia):
    # Apaga tudo o que estava na tela antes de desenhar esta página
    limpar_tela()

    # Logo no canto superior direito
    # Carrega o logo reduzido (máx. 110x80) para o canto superior da página
    imagens["logo_voltar"] = carregar_imagem((110, 80))

    # Se a imagem carregou, usa um Label com a imagem como botão de voltar
    if imagens["logo_voltar"]:
        botao_logo = tk.Label(
            root,
            image=imagens["logo_voltar"],
            bg=COR_FUNDO,
            cursor="hand2"
        )
    # Se a imagem não carregou, usa um Label com o texto 'DUAT' no lugar
    else:
        botao_logo = tk.Label(
            root,
            text="DUAT",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Arial", 18, "bold"),
            cursor="hand2"
        )

    # Posiciona o logo no canto superior direito (relx/rely são proporções da janela)
    botao_logo.place(relx=0.97, rely=0.04, anchor="ne")
    # Ao clicar no logo, volta para a página 1 (tela inicial)
    botao_logo.bind("<Button-1>", lambda event: mostrar_pagina_1())

    # Conteúdo da terceira página
    # Frame que agrupa o título, posicionado no topo e centralizado
    conteudo = tk.Frame(root, bg=COR_FUNDO)
    conteudo.place(relx=0.5, rely=0.1, anchor="center")

    # Título da página
    tk.Label(
        conteudo,
        text="Análise da notícia",
        bg=COR_FUNDO,
        fg=COR_TEXTO,
        font=("Arial", 40, "bold")
    ).pack(pady=(0, 30))

    # --------------------------------------------------------
    # CONTAINER DA TABELA
    # --------------------------------------------------------

    # Tamanho do container da tabela, em pixels
    LARGURA_TABELA = 1100
    ALTURA_TABELA = 550

    # Canvas que serve de fundo para o retângulo arredondado da tabela
    canvas_tabela = tk.Canvas(
        root,
        width=LARGURA_TABELA,
        height=ALTURA_TABELA,
        bg=COR_FUNDO,
        highlightthickness=0
    )

    # Centraliza o canvas na janela
    canvas_tabela.place(
        relx=0.5,
        rely=0.5,
        anchor="center"
    )

    # Desenha o retângulo arredondado (raio 20) com fundo azul e borda laranja
    retangulo_arredondado(
        canvas_tabela,
        5,
        5,
        LARGURA_TABELA - 5,
        ALTURA_TABELA - 5,
        20,
        fill=COR_INPUT,
        outline=COR_LARANJA,
        width=3
    )

    # Frame interno que vai receber a tabela
    frame_tabela = tk.Frame(
        canvas_tabela,
        bg=COR_INPUT
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
    background=COR_INPUT,
    foreground="white",
    fieldbackground=COR_INPUT,
    bordercolor=COR_LARANJA,
    borderwidth=1,
    rowheight=35,
    font=("Arial", 11)
    )   

    # Estilo do cabeçalho da tabela: fundo laranja, texto branco e fonte em negrito
    style.configure(
    "Treeview.Heading",
    background=COR_LARANJA,
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

    # --------------------------------------------------------
    # BOTÃO AVANÇAR
    # --------------------------------------------------------
    # Tamanho do botão e margem para a borda não ser cortada
    largura_avancar = 200
    altura_avancar = ALTURA

    # Canvas onde o botão arredondado é desenhado, posicionado abaixo da tabela
    canvas_avancar = tk.Canvas(
        root,
        width=largura_avancar + 2 * MARGEM,
        height=altura_avancar + 2 * MARGEM,
        bg=COR_FUNDO,
        highlightthickness=0,
        bd=0
    )
    canvas_avancar.place(relx=0.5, rely=0.9, anchor="center")

    # Fundo laranja do botão (guardamos o ID para o efeito de hover)
    forma_avancar = retangulo_arredondado(
        canvas_avancar,
        MARGEM, MARGEM,
        MARGEM + largura_avancar, MARGEM + altura_avancar,
        RAIO,
        fill=COR_LARANJA,
        outline=COR_LARANJA
    )

    # Texto 'Avançar' no centro do botão
    texto_avancar = canvas_avancar.create_text(
        MARGEM + largura_avancar / 2,
        MARGEM + altura_avancar / 2,
        text="Avançar",
        fill=COR_TEXTO,
        font=("Arial", 14, "bold")
    )

    # Ao clicar (na forma ou no texto), vai para a página 2 levando a notícia digitada
    def ir_para_pagina_2(event):
        mostrar_pagina_2(texto_noticia)

    # Mouse sobre o botão: cursor de mãozinha e cor mais escura
    def entrar_avancar(event):
        canvas_avancar.config(cursor="hand2")
        canvas_avancar.itemconfig(
            forma_avancar,
            fill=COR_LARANJA_HOVER,
            outline=COR_LARANJA_HOVER
        )

    # Mouse saiu do botão: volta o cursor e a cor normais
    def sair_avancar(event):
        canvas_avancar.config(cursor="")
        canvas_avancar.itemconfig(
            forma_avancar,
            fill=COR_LARANJA,
            outline=COR_LARANJA
        )

    # Liga os eventos de clique e hover tanto na forma quanto no texto
    canvas_avancar.tag_bind(forma_avancar, "<Button-1>", ir_para_pagina_2)
    canvas_avancar.tag_bind(texto_avancar, "<Button-1>", ir_para_pagina_2)
    canvas_avancar.tag_bind(forma_avancar, "<Enter>", entrar_avancar)
    canvas_avancar.tag_bind(forma_avancar, "<Leave>", sair_avancar)
    canvas_avancar.tag_bind(texto_avancar, "<Enter>", entrar_avancar)
    canvas_avancar.tag_bind(texto_avancar, "<Leave>", sair_avancar)







# ------------------------------------------------------------