# pdf_processor_v2_com_fonte.py
# VERSÃO MELHORADA - Função 4 com suporte a fonte Plus Jakarta Sans

import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class PlaceholderInfo:
    """Armazena informações de um placeholder encontrado"""
    nome: str
    valor: str
    bbox: Tuple[float, float, float, float]
    page: int
    font: str
    size: float
    color: tuple


# ============================================================================
# FUNÇÃO AUXILIAR: ENCONTRAR ARQUIVO DE FONTE
# ============================================================================

def encontrar_arquivo_fonte(nome_fonte: str = "PlusJakartaSans-Regular") -> str:
    """
    Procura pela fonte em vários locais padrão
    
    Args:
        nome_fonte: nome da fonte (ex: "PlusJakartaSans-Regular")
    
    Returns:
        str: caminho da fonte ou None
    """
    
    # Locais onde a fonte pode estar
    locais_possiveis = [
        # Diretório local
        f"./fonts/{nome_fonte}.ttf",
        f"./fonts/{nome_fonte}.otf",
        
        # Sistema Windows
        f"C:\\Windows\\Fonts\\{nome_fonte}.ttf",
        
        # Sistema Linux
        f"/usr/share/fonts/truetype/{nome_fonte.lower()}/{nome_fonte}.ttf",
        f"/usr/share/fonts/opentype/{nome_fonte.lower()}/{nome_fonte}.otf",
        
        # Sistema macOS
        f"/Library/Fonts/{nome_fonte}.ttf",
        f"/System/Library/Fonts/{nome_fonte}.ttf",
        
        # Python - fontes instaladas via pip
        f"./venv/Lib/site-packages/fonts/{nome_fonte}.ttf",
    ]
    
    for caminho in locais_possiveis:
        if os.path.exists(caminho):
            return caminho
    
    return None


# ============================================================================
# FUNÇÃO 4 MELHORADA: INSERIR TEXTOS COM FONTE
# ============================================================================

def inserir_textos_com_fonte(imagem_input, placeholders_info: List[PlaceholderInfo],
                             page_num: int, cores_extraidas: Dict[str, tuple],
                             dpi: int = 300, output_dir: str = "./output",
                             fonts_dir: str = "./fonts") -> np.ndarray:
    """
    Insere textos dos placeholders na imagem inpaintada COM FONTE PERSONALIZADA
    
    NOVO: Suporta Plus Jakarta Sans com fallback para fontes padrão
    
    Args:
        imagem_input: caminho ou array NumPy da imagem inpaintada
        placeholders_info: saída de obter_coordenadas()
        page_num: número da página
        cores_extraidas: saída de remover_textos()
        dpi: resolução original
        output_dir: pasta para salvar
        fonts_dir: diretório com as fontes TTF
    
    Returns:
        np.ndarray: imagem com textos inseridos
    """
    
    print("="*80)
    print(f"FUNÇÃO 4: INSERIR TEXTOS COM FONTE (Página {page_num+1})")
    print("="*80)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Carregar imagem
    if isinstance(imagem_input, str):
        img = cv2.imread(imagem_input)
    else:
        img = imagem_input.copy()
    
    # Converter para PIL para usar ImageDraw com suporte a fonte
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    dpi_scale = dpi / 72.0
    
    # Filtrar placeholders dessa página
    page_placeholders = [p for p in placeholders_info if p.page == page_num]
    
    print(f"✍️  Inserindo {len(page_placeholders)} texto(s)...\n")
    
    # Dicionário de fontes carregadas (cache)
    fontes_carregadas = {}
    
    for ph in page_placeholders:
        x0, y0, x1, y1 = ph.bbox
        
        # Converter PDF points → pixels
        x0_px = int(x0 * dpi_scale)
        y0_px = int(y0 * dpi_scale)
        
        # Recuperar cor extraída (BGR → RGB para PIL)
        cor_bgr = cores_extraidas.get(ph.nome, (0, 0, 0))
        cor_rgb = (cor_bgr[2], cor_bgr[1], cor_bgr[0])  # Converter BGR para RGB
        
        # Calcular tamanho de fonte proporcional
        font_size = max(8, int(ph.size * dpi_scale * 0.8))
        
        # Tentar carregar fonte Plus Jakarta Sans
        chave_fonte = f"{ph.font}_{font_size}"
        
        if chave_fonte not in fontes_carregadas:
            # Determinar qual variação usar baseado no nome original
            if "Bold" in ph.font:
                fonte_ttf = "PlusJakartaSans-Bold"
            elif "Medium" in ph.font:
                fonte_ttf = "PlusJakartaSans-Medium"
            elif "SemiBold" in ph.font:
                fonte_ttf = "PlusJakartaSans-SemiBold"
            else:
                fonte_ttf = "PlusJakartaSans-Regular"
            
            # Procurar fonte
            caminho_fonte = None
            
            # 1. Procurar no diretório local
            if os.path.exists(fonts_dir):
                for arquivo in os.listdir(fonts_dir):
                    if fonte_ttf.lower() in arquivo.lower() and arquivo.endswith(('.ttf', '.otf')):
                        caminho_fonte = os.path.join(fonts_dir, arquivo)
                        break
            
            # 2. Procurar em locais padrão
            if not caminho_fonte:
                caminho_fonte = encontrar_arquivo_fonte(fonte_ttf)
            
            # 3. Usar fallback se não encontrar
            if caminho_fonte:
                try:
                    fonte = ImageFont.truetype(caminho_fonte, font_size)
                    print(f"  📝 Fonte carregada: {fonte_ttf} ({font_size}pt)")
                except:
                    print(f"  ⚠️  Erro ao carregar {fonte_ttf}, usando padrão")
                    fonte = ImageFont.load_default()
            else:
                print(f"  ⚠️  Fonte {fonte_ttf} não encontrada, usando padrão")
                fonte = ImageFont.load_default()
            
            fontes_carregadas[chave_fonte] = fonte
        else:
            fonte = fontes_carregadas[chave_fonte]
        
        # Inserir texto com PIL (melhor qualidade que cv2.putText)
        draw.text(
            (x0_px, y0_px + font_size),
            ph.valor,
            fill=cor_rgb,
            font=fonte
        )
        
        print(f"  ✓ {ph.nome[:35]}... = '{ph.valor}'")
    
    # Converter PIL de volta para OpenCV
    img_final = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    # Salvar resultado
    imagem_path = os.path.join(output_dir, f"page_{page_num+1}_final.png")
    cv2.imwrite(imagem_path, img_final)
    
    print(f"\n✅ Textos inseridos com fonte personalizada")
    print(f"💾 Salvo: {imagem_path}")
    print("="*80 + "\n")
    
    return img_final


# ============================================================================
# FUNÇÃO PARA INSTALAR FONTE AUTOMATICAMENTE
# ============================================================================

def instalar_fonte_local(url_fonte: str = None, fonts_dir: str = "./fonts") -> bool:
    """
    Download automático da fonte Plus Jakarta Sans do Google Fonts
    
    Args:
        url_fonte: URL da fonte (opcional)
        fonts_dir: diretório para salvar
    
    Returns:
        bool: sucesso da instalação
    """
    
    print("\n" + "="*80)
    print("INSTALADOR DE FONTE - Plus Jakarta Sans")
    print("="*80)
    
    import urllib.request
    import zipfile
    
    os.makedirs(fonts_dir, exist_ok=True)
    
    # URL oficial do Google Fonts
    if not url_fonte:
        url_fonte = "https://fonts.google.com/download?family=Plus%20Jakarta%20Sans"
    
    print(f"\n📥 Baixando fonte de: {url_fonte}")
    print(f"💾 Salvando em: {fonts_dir}\n")
    
    try:
        # Download
        zip_path = os.path.join(fonts_dir, "plus_jakarta_sans.zip")
        urllib.request.urlretrieve(url_fonte, zip_path)
        
        print(f"✅ Download concluído: {zip_path}")
        
        # Extrair
        print(f"📦 Extraindo arquivos...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(fonts_dir)
        
        # Limpar ZIP
        os.remove(zip_path)
        
        # Listar fontes
        print(f"\n✅ Fonte instalada com sucesso!\n")
        print(f"📋 Arquivos disponíveis em {fonts_dir}:")
        for arquivo in os.listdir(fonts_dir):
            if arquivo.endswith(('.ttf', '.otf')):
                print(f"   ✓ {arquivo}")
        
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao instalar fonte: {e}")
        print("💡 Baixe manualmente de: https://fonts.google.com/specimen/Plus+Jakarta+Sans")
        print("="*80 + "\n")
        return False
