# pdf_processor_v2_com_fonte_inteligente.py
# VERSÃO INTELIGENTE - Detecta brilho do fundo e escolhe cor automática (preta ou branca)

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
# FUNÇÃO AUXILIAR: DETECTAR BRILHO DO FUNDO
# ============================================================================

def detectar_brilho_fundo(imagem_bgr: np.ndarray, bbox: Tuple[float, float, float, float], 
                         dpi_scale: float) -> Tuple[float, str]:
    """
    Detecta o brilho do fundo em uma região e retorna:
    - Valor de brilho (0-255)
    - Cor recomendada para texto ('preto' ou 'branco')
    
    Usa a fórmula de luminância relativa: Y = 0.299*R + 0.587*G + 0.114*B
    """
    
    x0, y0, x1, y1 = bbox
    
    x0_px = max(0, int(x0 * dpi_scale) - 5)
    y0_px = max(0, int(y0 * dpi_scale) - 5)
    x1_px = min(imagem_bgr.shape[1], int(x1 * dpi_scale) + 5)
    y1_px = min(imagem_bgr.shape[0], int(y1 * dpi_scale) + 5)
    
    regiao = imagem_bgr[y0_px:y1_px, x0_px:x1_px]
    
    if regiao.size == 0:
        return 128, 'preto'
    
    # Extrair canais BGR
    b, g, r = cv2.split(regiao)
    
    # Calcular luminância (converter para escala 0-1 para cálculo)
    r_norm = r.astype(float) / 255.0
    g_norm = g.astype(float) / 255.0
    b_norm = b.astype(float) / 255.0
    
    # Fórmula de luminância relativa (RGB)
    luminancia = 0.299 * r_norm + 0.587 * g_norm + 0.114 * b_norm
    
    # Brilho médio (0-255)
    brilho_medio = np.mean(luminancia) * 255.0
    
    # Limiar: se brilho > 128, é claro (usar texto preto), senão usar branco
    cor_texto = 'preto' if brilho_medio > 128 else 'branco'
    
    return brilho_medio, cor_texto


def obter_cor_contraste(cor_texto: str) -> Tuple[int, int, int]:
    """Retorna cor RGB para melhor contraste"""
    if cor_texto == 'preto':
        return (0, 0, 0)  # RGB preto
    else:
        return (255, 255, 255)  # RGB branco


# ============================================================================
# FUNÇÃO AUXILIAR: ENCONTRAR ARQUIVO DE FONTE
# ============================================================================

def encontrar_arquivo_fonte(nome_fonte: str = "PlusJakartaSans-Regular", fonts_dir: str = "./fonts") -> str:
    """Procura pela fonte em vários locais"""
    
    locais_possiveis = [
        f"{fonts_dir}/{nome_fonte}.ttf",
        f"{fonts_dir}/{nome_fonte}.otf",
        f"C:\\Windows\\Fonts\\{nome_fonte}.ttf",
        f"/usr/share/fonts/truetype/{nome_fonte.lower()}/{nome_fonte}.ttf",
        f"/Library/Fonts/{nome_fonte}.ttf",
    ]
    
    for caminho in locais_possiveis:
        if os.path.exists(caminho):
            return caminho
    
    return None


# ============================================================================
# FUNÇÃO 1: OBTER COORDENADAS
# ============================================================================

def obter_coordenadas(pdf_path: str, placeholders_valores: Dict[str, str]) -> List[PlaceholderInfo]:
    """Extrai coordenadas exatas de todos os placeholders no PDF"""
    
    print("\n" + "="*80)
    print("FUNÇÃO 1: OBTER COORDENADAS")
    print("="*80)
    
    doc = fitz.open(pdf_path)
    placeholders_encontrados = []
    
    print(f"📄 PDF: {pdf_path} ({len(doc)} página(s))")
    print(f"🔍 Procurando placeholders...\n")
    
    placeholders_limpos = {}
    for k, v in placeholders_valores.items():
        chave_limpa = k.strip().strip('{}')
        placeholders_limpos[chave_limpa] = v
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_count = 0
        
        try:
            blocos = page.get_text("dict")["blocks"]
        except:
            print(f"  ⚠️  Página {page_num+1}: erro ao extrair blocos")
            continue
        
        for bloco in blocos:
            if "lines" not in bloco:
                continue
            
            for linha in bloco["lines"]:
                for span in linha["spans"]:
                    texto = span["text"]
                    
                    if '{' in texto and '}' in texto:
                        match = re.search(r'{(.*?)}', texto)
                        if not match:
                            continue
                        
                        nome_completo = match.group(1)
                        nome_limpo = nome_completo.strip()
                        
                        for chave_entrada, valor in placeholders_limpos.items():
                            if chave_entrada in nome_limpo or nome_limpo.startswith(chave_entrada):
                                bbox = span["bbox"]
                                font = span.get("font", "Arial")
                                size = span.get("size", 12.0)
                                color = span.get("color", 0)
                                
                                ph = PlaceholderInfo(
                                    nome=texto,
                                    valor=valor,
                                    bbox=bbox,
                                    page=page_num,
                                    font=font,
                                    size=size,
                                    color=color
                                )
                                
                                placeholders_encontrados.append(ph)
                                page_count += 1
                                
                                x0, y0, x1, y1 = bbox
                                print(f"  ✓ Pág {page_num+1}: '{texto[:40]}{'...' if len(texto) > 40 else ''}'")
                                print(f"    → Valor: '{valor}' | Bbox: ({x0:.1f}, {y0:.1f})")
                                break
        
        if page_count > 0:
            print(f"\n  📊 Página {page_num+1}: {page_count} placeholder(s) encontrado(s)")
        else:
            print(f"  📊 Página {page_num+1}: nenhum placeholder")
    
    doc.close()
    
    print(f"\n✅ Total encontrado: {len(placeholders_encontrados)} placeholder(s)")
    print("="*80 + "\n")
    
    return placeholders_encontrados


# ============================================================================
# FUNÇÃO 2: GERAR IMAGEM COM DESTAQUE
# ============================================================================

def gerar_imagem(pdf_path: str, placeholders_info: List[PlaceholderInfo], 
                 dpi: int = 300, output_dir: str = "./output") -> Dict[int, np.ndarray]:
    """Renderiza PDF em imagens com destaque dos placeholders"""
    
    print("="*80)
    print("FUNÇÃO 2: GERAR IMAGEM COM DESTAQUE")
    print("="*80)
    
    os.makedirs(output_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    dpi_scale = dpi / 72.0
    imagens = {}
    
    print(f"🖼️  Renderizando {len(doc)} página(s) em DPI {dpi}...\n")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        mat = fitz.Matrix(dpi_scale, dpi_scale)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        
        page_placeholders = [p for p in placeholders_info if p.page == page_num]
        
        print(f"📄 Página {page_num+1}: {len(page_placeholders)} placeholder(s)")
        
        for ph in page_placeholders:
            x0, y0, x1, y1 = ph.bbox
            
            x0_px = int(x0 * dpi_scale)
            y0_px = int(y0 * dpi_scale)
            x1_px = int(x1 * dpi_scale)
            y1_px = int(y1 * dpi_scale)
            
            cv2.rectangle(img_cv, (x0_px, y0_px), (x1_px, y1_px), 
                         (0, 255, 255), 1)
        
        imagem_path = os.path.join(output_dir, f"page_{page_num+1}_destaque.png")
        cv2.imwrite(imagem_path, img_cv)
        
        imagens[page_num] = img_cv
        
        print(f"  💾 Salvo: {imagem_path}\n")
    
    doc.close()
    
    print(f"✅ Total de imagens: {len(imagens)}")
    print("="*80 + "\n")
    
    return imagens


# ============================================================================
# FUNÇÃO 3: REMOVER TEXTOS COM INPAINTING
# ============================================================================

def remover_textos(imagem_input, placeholders_info: List[PlaceholderInfo],
                   page_num: int, dpi: int = 300,
                   output_dir: str = "./output") -> Tuple[np.ndarray, Dict[str, tuple]]:
    """Remove textos usando inpainting (algoritmo Telea)"""
    
    print("="*80)
    print(f"FUNÇÃO 3: REMOVER TEXTOS (Página {page_num+1})")
    print("="*80)
    
    os.makedirs(output_dir, exist_ok=True)
    
    if isinstance(imagem_input, str):
        img = cv2.imread(imagem_input)
    else:
        img = imagem_input.copy()
    
    img_original = img.copy()
    dpi_scale = dpi / 72.0
    
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    page_placeholders = [p for p in placeholders_info if p.page == page_num]
    
    print(f"🎨 Aplicando inpainting em {len(page_placeholders)} área(s)...\n")
    
    cores_extraidas = {}
    
    for ph in page_placeholders:
        x0, y0, x1, y1 = ph.bbox
        
        x0_px = int(x0 * dpi_scale)
        y0_px = int(y0 * dpi_scale)
        x1_px = int(x1 * dpi_scale)
        y1_px = int(y1 * dpi_scale)
        
        margin = 3
        x0_px = max(0, x0_px - margin)
        y0_px = max(0, y0_px - margin)
        x1_px = min(img.shape[1], x1_px + margin)
        y1_px = min(img.shape[0], y1_px + margin)
        
        regiao = img_original[y0_px:y1_px, x0_px:x1_px]
        if regiao.size > 0:
            cor_media_bgr = cv2.mean(regiao)[:3]
            cores_extraidas[ph.nome] = tuple(int(c) for c in cor_media_bgr)
        else:
            cores_extraidas[ph.nome] = (0, 0, 0)
        
        cv2.rectangle(mask, (x0_px, y0_px), (x1_px, y1_px), 255, -1)
        
        print(f"  ✓ Máscara criada para: {ph.nome[:40]}...")
    
    print("\n  🔧 Executando inpainting Telea...")
    img_inpainted = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    
    imagem_path = os.path.join(output_dir, f"page_{page_num+1}_inpainted.png")
    cv2.imwrite(imagem_path, img_inpainted)
    
    print(f"\n✅ Inpainting concluído")
    print(f"💾 Salvo: {imagem_path}")
    print("="*80 + "\n")
    
    return img_inpainted, cores_extraidas


# ============================================================================
# FUNÇÃO 4: INSERIR TEXTOS COM DETECÇÃO INTELIGENTE DE COR
# ============================================================================

def inserir_textos_inteligente(imagem_input, placeholders_info: List[PlaceholderInfo],
                               page_num: int, cores_extraidas: Dict[str, tuple],
                               dpi: int = 300, output_dir: str = "./output",
                               fonts_dir: str = "./fonts") -> np.ndarray:
    """
    Insere textos dos placeholders com DETECÇÃO AUTOMÁTICA de cor
    
    🧠 INTELIGENTE: Detecta brilho do fundo e escolhe preto ou branco
    """
    
    print("="*80)
    print(f"FUNÇÃO 4: INSERIR TEXTOS COM DETECÇÃO INTELIGENTE (Página {page_num+1})")
    print("="*80)
    
    os.makedirs(output_dir, exist_ok=True)
    
    if isinstance(imagem_input, str):
        img = cv2.imread(imagem_input)
    else:
        img = imagem_input.copy()
    
    # Converter BGR (OpenCV) → RGB (PIL)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(img_pil)
    
    dpi_scale = dpi / 72.0
    
    page_placeholders = [p for p in placeholders_info if p.page == page_num]
    
    print(f"✍️  Inserindo {len(page_placeholders)} texto(s) com cor inteligente...\n")
    
    fontes_carregadas = {}
    
    for ph in page_placeholders:
        x0, y0, x1, y1 = ph.bbox
        
        x0_px = int(x0 * dpi_scale)
        y0_px = int(y0 * dpi_scale)
        
        # 🧠 DETECÇÃO INTELIGENTE: Analisar brilho do fundo
        brilho, cor_texto = detectar_brilho_fundo(img, ph.bbox, dpi_scale)
        cor_rgb = obter_cor_contraste(cor_texto)
        
        font_size = max(8, int(ph.size * dpi_scale * 0.8))
        
        chave_fonte = f"{ph.font}_{font_size}"
        
        if chave_fonte not in fontes_carregadas:
            if "Bold" in ph.font:
                fonte_ttf = "PlusJakartaSans-Bold"
            elif "Medium" in ph.font:
                fonte_ttf = "PlusJakartaSans-Medium"
            elif "SemiBold" in ph.font:
                fonte_ttf = "PlusJakartaSans-SemiBold"
            else:
                fonte_ttf = "PlusJakartaSans-Regular"
            
            caminho_fonte = None
            
            if os.path.exists(fonts_dir):
                for arquivo in os.listdir(fonts_dir):
                    if fonte_ttf.lower() in arquivo.lower() and arquivo.endswith(('.ttf', '.otf')):
                        caminho_fonte = os.path.join(fonts_dir, arquivo)
                        break
            
            if not caminho_fonte:
                caminho_fonte = encontrar_arquivo_fonte(fonte_ttf, fonts_dir)
            
            if caminho_fonte:
                try:
                    fonte = ImageFont.truetype(caminho_fonte, font_size)
                except:
                    fonte = ImageFont.load_default()
            else:
                fonte = ImageFont.load_default()
            
            fontes_carregadas[chave_fonte] = fonte
        else:
            fonte = fontes_carregadas[chave_fonte]
        
        # Inserir texto com cor inteligente
        draw.text(
            (x0_px, y0_px + font_size),
            ph.valor,
            fill=cor_rgb,
            font=fonte
        )
        
        cor_nome = "PRETO" if cor_texto == 'preto' else "BRANCO"
        print(f"  ✓ {ph.nome[:30]}... = '{ph.valor}'")
        print(f"    → Brilho fundo: {brilho:.0f} | Cor: {cor_nome}")
    
    # Converter de volta para BGR (OpenCV)
    img_final = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    imagem_path = os.path.join(output_dir, f"page_{page_num+1}_final_inteligente.png")
    cv2.imwrite(imagem_path, img_final)
    
    print(f"\n✅ Textos inseridos com detecção inteligente de cor")
    print(f"💾 Salvo: {imagem_path}")
    print("="*80 + "\n")
    
    return img_final


# ============================================================================
# FUNÇÃO 5: GERAR PDF
# ============================================================================

def gerar_pdf(imagens_dict: Dict[int, np.ndarray],
              output_pdf: str = "./output/Contrato_Final.pdf") -> bool:
    """Converte imagens em PDF"""
    
    print("="*80)
    print("FUNÇÃO 5: GERAR PDF")
    print("="*80)
    
    os.makedirs(os.path.dirname(output_pdf) or ".", exist_ok=True)
    
    try:
        doc = fitz.open()
        
        print(f"📄 Convertendo {len(imagens_dict)} imagem(s) em PDF...\n")
        
        for page_num in sorted(imagens_dict.keys()):
            img_cv = imagens_dict[page_num]
            
            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            
            img_pil = Image.fromarray(img_rgb)
            
            img_array = np.array(img_pil)
            
            pix = fitz.Pixmap(fitz.csRGB, img_array)
            
            page = doc.new_page(width=pix.width, height=pix.height)
            
            page.insert_image(page.rect, pixmap=pix)
            
            print(f"  ✓ Página {page_num+1} inserida ({pix.width}×{pix.height}px)")
        
        doc.save(output_pdf, garbage=4, deflate=True)
        doc.close()
        
        tamanho_mb = os.path.getsize(output_pdf) / 1024 / 1024
        
        print(f"\n✅ PDF gerado com sucesso!")
        print(f"📄 {output_pdf}")
        print(f"   Tamanho: {tamanho_mb:.2f} MB")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar PDF: {e}")
        return False


# ============================================================================
# FUNÇÃO AUXILIAR: PIPELINE COMPLETO COM DETECÇÃO INTELIGENTE
# ============================================================================

def processar_pdf_inteligente(pdf_path: str, placeholders_valores: Dict[str, str],
                              output_pdf: str = "./output/Contrato_Final.pdf",
                              dpi: int = 300, fonts_dir: str = "./fonts"):
    """Executa o pipeline completo com detecção inteligente de cor"""
    
    print("\n" + "🚀 "*35)
    print("PIPELINE COMPLETO - PDF PROCESSOR V2 COM DETECÇÃO INTELIGENTE")
    print("🚀 "*35 + "\n")
    
    placeholders_info = obter_coordenadas(pdf_path, placeholders_valores)
    
    if not placeholders_info:
        print("❌ Nenhum placeholder encontrado!")
        return False
    
    imagens_com_destaque = gerar_imagem(pdf_path, placeholders_info, dpi)
    
    imagens_finais = {}
    
    for page_num in sorted(imagens_com_destaque.keys()):
        img_com_destaque = imagens_com_destaque[page_num]
        
        page_placeholders = [p for p in placeholders_info if p.page == page_num]
        
        if not page_placeholders:
            print(f"\n⚠️  Página {page_num+1}: sem placeholders (copiando original)")
            imagens_finais[page_num] = img_com_destaque
        else:
            img_inpainted, cores = remover_textos(
                img_com_destaque, placeholders_info, page_num, dpi
            )
            
            img_final = inserir_textos_inteligente(
                img_inpainted, placeholders_info, page_num, cores, dpi, 
                fonts_dir=fonts_dir
            )
            
            imagens_finais[page_num] = img_final
    
    sucesso = gerar_pdf(imagens_finais, output_pdf)
    
    print("✅ "*35)
    if sucesso:
        print("PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print(f"📄 Arquivo final: {output_pdf}")
        print("🧠 Com detecção inteligente de cor (preto em fundos claros, branco em escuros)")
    else:
        print("PROCESSAMENTO FALHOU!")
    print("✅ "*35 + "\n")
    
    return sucesso
