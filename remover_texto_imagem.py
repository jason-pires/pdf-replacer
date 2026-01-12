# 🎨 Remover Texto de Placeholders da Imagem (Mantendo Background)

import cv2
import numpy as np
from PIL import Image
import pytesseract

def remover_placeholders_com_inpaint(caminho_imagem, caminho_saida):
    """
    Remove placeholders {xxx} da imagem mantendo o fundo intacto
    Usa OCR para detectar onde estão os placeholders
    """
    
    # 1. Carregar imagem
    img = cv2.imread(caminho_imagem)
    if img is None:
        print(f"❌ Erro: Não conseguiu carregar {caminho_imagem}")
        return False
    
    altura, largura = img.shape[:2]
    print(f"📊 Imagem: {largura}x{altura}px")
    
    # 2. Converter para escala de cinza
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 3. Detectar texto (pytesseract)
    print("🔍 Detectando placeholders com OCR...")
    try:
        # Usar pytesseract com detecção de caixas
        dados = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Criar máscara para remover
        mask = np.zeros(gray.shape, dtype=np.uint8)
        
        # Encontrar todas as instâncias de texto que contém "{"
        placeholders_encontrados = 0
        for i, texto in enumerate(dados['text']):
            if '{' in texto and '}' in texto:
                x = dados['left'][i]
                y = dados['top'][i]
                w = dados['width'][i]
                h = dados['height'][i]
                
                # Adicionar margem para garantir remoção completa
                margem = 5
                x_min = max(0, x - margem)
                y_min = max(0, y - margem)
                x_max = min(largura, x + w + margem)
                y_max = min(altura, y + h + margem)
                
                # Marcar na máscara (branco = remover)
                cv2.rectangle(mask, (x_min, y_min), (x_max, y_max), 255, -1)
                
                placeholders_encontrados += 1
                print(f"  ✓ Encontrado: {texto} em ({x}, {y})")
        
        if placeholders_encontrados == 0:
            print("⚠️  Nenhum placeholder encontrado!")
            return False
        
        print(f"\n✓ Total encontrado: {placeholders_encontrados} placeholders")
        
        # 4. Aplicar inpainting (reconstruir fundo)
        print("🎨 Reconstruindo fundo com inpainting...")
        resultado = cv2.inpaint(
            img,
            mask,
            inpaintRadius=3,
            flags=cv2.INPAINT_TELEA
        )
        
        # 5. Salvar resultado
        cv2.imwrite(caminho_saida, resultado)
        print(f"✅ Imagem salva: {caminho_saida}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def remover_texto_manual(caminho_imagem, caminho_saida, regioes):
    """
    Remove texto de regiões específicas (se souber as coordenadas exatas)
    
    regioes: lista de tuplas (x, y, largura, altura)
    Exemplo: [(100, 200, 300, 50), (100, 300, 300, 50)]
    """
    
    img = cv2.imread(caminho_imagem)
    if img is None:
        print(f"❌ Erro ao carregar imagem")
        return False
    
    altura, largura = img.shape[:2]
    mask = np.zeros((altura, largura), dtype=np.uint8)
    
    print("📝 Marcando regiões para remoção...")
    for i, (x, y, w, h) in enumerate(regioes, 1):
        # Adicionar margem
        margem = 3
        x_min = max(0, x - margem)
        y_min = max(0, y - margem)
        x_max = min(largura, x + w + margem)
        y_max = min(altura, y + h + margem)
        
        cv2.rectangle(mask, (x_min, y_min), (x_max, y_max), 255, -1)
        print(f"  ✓ Região {i}: ({x}, {y}, {w}, {h})")
    
    print("🎨 Removendo com inpaint...")
    resultado = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    
    cv2.imwrite(caminho_saida, resultado)
    print(f"✅ Salvo: {caminho_saida}")
    
    return True


def limpar_texto_com_dilatacao(caminho_imagem, caminho_saida):
    """
    Remove TODO texto dilatando a máscara
    Útil se houver muito texto para limpar
    """
    
    img = cv2.imread(caminho_imagem)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold para detectar texto
    _, mask = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Dilatar para pegar todo o texto
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    # Inpaint
    resultado = cv2.inpaint(img, mask, 5, cv2.INPAINT_TELEA)
    
    cv2.imwrite(caminho_saida, resultado)
    print(f"✅ Texto removido: {caminho_saida}")
    
    return True


# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

if __name__ == '__main__':
    
    # OPÇÃO 1: Detectar placeholders automaticamente com OCR
    print("="*80)
    print("OPÇÃO 1: Remover Placeholders com OCR Automático")
    print("="*80)
    
    remover_placeholders_com_inpaint(
        'templates/Contrato_Medico-04_procedimentos.jpg',
        'contratos/contrato_sem_placeholders_ocr.jpg'
    )
    
    # OPÇÃO 2: Remover regiões específicas manualmente
    print("\n" + "="*80)
    print("OPÇÃO 2: Remover Regiões Específicas")
    print("="*80)
    
    # Defina as coordenadas onde estão os placeholders
    # Formato: (x, y, largura, altura)
    regioes = [
        (220, 240, 150, 50),   # {dd}
        (220, 295, 150, 50),   # {mm}
        (220, 350, 150, 50),   # {aaaa}
        (280, 450, 300, 50),   # nome_da_medica_ou_clinica
        (280, 620, 300, 50),   # nome_paciente
    ]
    
    # remover_texto_manual(
    #     'Contrato_Medico-04_procedimentos.jpg',
    #     'contrato_sem_placeholders_manual.jpg',
    #     regioes
    # )
    
    # OPÇÃO 3: Remover TODO texto (mais agressivo)
    print("\n" + "="*80)
    print("OPÇÃO 3: Remover TODO Texto (Agressivo)")
    print("="*80)
    
    # limpar_texto_com_dilatacao(
    #     'Contrato_Medico-04_procedimentos.jpg',
    #     'contrato_limpo.jpg'
    # )
    
    print("\n✅ Processamento concluído!")
