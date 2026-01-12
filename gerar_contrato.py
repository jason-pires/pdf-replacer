from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

def gerar_contrato(dados, caminho_template, caminho_saida):
    # 1. Carregar a imagem base
    try:
        imagem = Image.open(caminho_template).convert("RGB")
        draw = ImageDraw.Draw(imagem)
        largura_img, altura_img = imagem.size
    except FileNotFoundError:
        print(f"Erro: Arquivo {caminho_template} não encontrado.")
        return

    # 2. Configuração de Fontes (Tente usar uma fonte TTF do sistema para ficar bonito)
    # Se não tiver 'arial.ttf', substitua pelo caminho de uma fonte como Montserrat ou Roboto
    try:
        font_padrao = "arial.ttf" 
        # Função auxiliar para carregar fonte com tamanho específico
        def get_font(tamanho):
            return ImageFont.truetype(font_padrao, size=tamanho)
    except OSError:
        # Fallback se não encontrar a fonte
        print("Aviso: Fonte Arial não encontrada, usando padrão.")
        def get_font(tamanho):
            return ImageFont.load_default()

    # Cores (baseadas na imagem)
    cor_texto_escuro = (50, 50, 50)   # Cinza escuro/Preto
    cor_texto_roxo = (108, 92, 231)   # Roxo do título (aproximado)
    cor_texto_branco = (255, 255, 255) # Branco

    # 3. Mapeamento de Coordenadas (X, Y)
    # IMPORTANTE: Estes valores são ESTIMATIVAS baseadas na imagem visual.
    # Você terá que ajustar esses números (x, y) trial-and-error para alinhar perfeitamente.
    mapa_campos = {
        # Data (Topo Centro-Direita)
        'dd':   {'pos': (620, 240), 'tamanho': 24, 'cor': cor_texto_roxo},
        'mmm':  {'pos': (620, 265), 'tamanho': 24, 'cor': cor_texto_roxo},
        'aaaa': {'pos': (620, 290), 'tamanho': 24, 'cor': cor_texto_roxo},

        # Seção Médica (Esquerda - Roxo Escuro)
        'nome_da_medica_ou_clinica': {'pos': (100, 370), 'tamanho': 22, 'cor': cor_texto_escuro, 'bold': True},
        # Ícones de contato médica (estimados abaixo do nome)
        'celmedicacli':    {'pos': (130, 420), 'tamanho': 16, 'cor': cor_texto_escuro}, # Ícone Telefone
        'emailmedicacli':  {'pos': (330, 420), 'tamanho': 16, 'cor': cor_texto_escuro}, # Ícone Email
        'enderecomedical': {'pos': (330, 450), 'tamanho': 16, 'cor': cor_texto_escuro}, # Ícone Pin
        # Nota: O CPF/CNPJ médica costuma ir na assinatura ou abaixo do nome
        'cpfcnpjmedicacli':{'pos': (130, 470), 'tamanho': 14, 'cor': cor_texto_escuro}, 

        # Seção Paciente (Esquerda - Roxo Escuro - Abaixo)
        'nome_paciente':   {'pos': (100, 530), 'tamanho': 22, 'cor': cor_texto_escuro, 'bold': True},
        'cpfpaciente':     {'pos': (100, 560), 'tamanho': 16, 'cor': cor_texto_escuro},
        'celpaciente':     {'pos': (130, 590), 'tamanho': 16, 'cor': cor_texto_escuro}, # Ícone telefone
        'emailpaciente':   {'pos': (330, 560), 'tamanho': 16, 'cor': cor_texto_escuro}, # Ícone email
        'enderecopaciente2':{'pos':(330, 590), 'tamanho': 16, 'cor': cor_texto_escuro}, # Ícone pin

        # Procedimento 4 (Caixa Roxa Inferior Direita)
        'procedimento_4':           {'pos': (530, 860), 'tamanho': 20, 'cor': cor_texto_branco, 'center': True, 'width': 400},
        'procedimento_4_descricao': {'pos': (530, 940), 'tamanho': 14, 'cor': cor_texto_branco, 'center': True, 'width': 400},
    }

    # 4. Iterar e desenhar textos
    for chave, config in mapa_campos.items():
        if chave in dados:
            texto = dados[chave]
            fonte = get_font(config['tamanho'])
            pos_x, pos_y = config['pos']
            cor = config['cor']

            # Verifica se precisa centralizar ou quebrar texto (wrap)
            if config.get('center'):
                # Simples lógica de centralização baseada numa largura de caixa
                largura_caixa = config.get('width', 300)
                
                # Quebrar texto se for longo
                linhas = textwrap.wrap(texto, width=40) # Ajuste width conforme o tamanho da fonte
                
                offset_y = 0
                for linha in linhas:
                    # Calcular largura da linha para centralizar
                    bbox = draw.textbbox((0, 0), linha, font=fonte)
                    largura_texto = bbox[2] - bbox[0]
                    novo_x = pos_x + (largura_caixa - largura_texto) / 2
                    
                    draw.text((novo_x, pos_y + offset_y), linha, font=fonte, fill=cor)
                    offset_y += config['tamanho'] + 5
            else:
                draw.text((pos_x, pos_y), texto, font=fonte, fill=cor)

    # 5. Inserir Imagem do Procedimento (Overlay)
    # A chave é 'procedimento_4_imagem', que contém o nome do arquivo
    nome_arq_img_proc = dados.get('procedimento_4_imagem')
    
    # Coordenadas onde a imagem deve entrar (Caixa inferior direita, lado esquerdo dela ou fundo)
    # Ajuste aqui a posição e tamanho da miniatura
    pos_img_x, pos_img_y = 520, 900 
    tamanho_img = (80, 80) # Tamanho da miniatura

    if nome_arq_img_proc:
        try:
            # Tenta abrir a imagem do procedimento (se existir no disco)
            # Para teste, se não existir, cria um quadrado cinza
            if os.path.exists(nome_arq_img_proc):
                img_proc = Image.open(nome_arq_img_proc).convert("RGBA")
                img_proc = img_proc.resize(tamanho_img)
                imagem.paste(img_proc, (pos_img_x, pos_img_y), img_proc)
            else:
                print(f"Aviso: Imagem '{nome_arq_img_proc}' não encontrada. Pulando overlay.")
        except Exception as e:
            print(f"Erro ao inserir imagem: {e}")

    # 6. Salvar resultado
    imagem.save(caminho_saida)
    print(f"Contrato gerado com sucesso: {caminho_saida}")

# --- DADOS DE ENTRADA (Do seu prompt) ---
dados_input = {
    'nome_da_medica_ou_clinica': 'Dra. Maria Silva - Clínica Estética Premium',
    'cpfcnpjmedicacli': '12.345.678/0001-90',
    'celmedicacli': '(21) 99999-8888',
    'emailmedicacli': 'contato@clinicamaria.com.br',
    'enderecomedical': 'Avenida Paulista, 1000',
    'enderecomedica2': 'São Paulo, SP 01311-100',
    'nome_paciente': 'João da Silva Santos',
    'cpfpaciente': '123.456.789-00',
    'celpaciente': '(11) 98765-4321',
    'emailpaciente': 'joao.silva@example.com',
    'enderecopaciente2': 'São Paulo, SP 01310-100',
    'dd': '15',
    'mmm': 'janeiro',
    'aaaa': '2026',
    'procedimento_4': 'Preenchimento Facial com Ácido Hialurônico',
    'procedimento_4_imagem': 'IMAGEM_DO_PROCEDIMENTO_04.png',
    'procedimento_4_descricao': 'Preenchimento para harmonização facial, melhorando contornos.',
}

template_path = 'templates/Contrato_Medico-04_procedimentos.jpg'
output_path = 'contratos/Contrato_Preenchido.jpg'
# EXECUÇÃO
# Certifique-se de ter o arquivo 'Contrato_Medico-04_procedimentos.jpg' na mesma pasta
gerar_contrato(dados_input, template_path, output_path)