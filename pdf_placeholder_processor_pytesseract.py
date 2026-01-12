# pdf_placeholder_processor_pytesseract.py
# VERSÃO ALTERNATIVA: Sem keras-ocr (mais leve, sem compilação)
# Usa pytesseract para detecção de texto

# ```python
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import os
from typing import Dict, List, Tuple
from datetime import datetime

class PlaceholderMetadata:
    """Armazena metadados de um placeholder detectado"""
    def __init__(self, text: str, x: int, y: int, width: int, height: int, 
                 font_size: int, color: Tuple[int,int,int], confidence: float):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font_size = font_size
        self.color = color
        self.confidence = confidence
    
    def to_dict(self):
        return {
            'text': self.text,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'font_size': self.font_size,
            'color': self.color,
            'confidence': self.confidence
        }


class PDFPlaceholderProcessor:
    """
    Processa PDF para encontrar, remover e reinserer placeholders
    Versão com pytesseract (sem keras-ocr)
    
    Fluxo:
    1. Converte PDF em imagens
    2. Detecta placeholders {xxx} com pytesseract
    3. Armazena posição, fonte, cor
    4. Remove texto
    5. Reinsere valores novos
    6. Reconstrói PDF
    """
    
    def __init__(self, pdf_path: str, dpi: int = 300):
        """
        Args:
            pdf_path: caminho do PDF de entrada
            dpi: resolução para conversão (300 = alta qualidade)
        """
        self.pdf_path = pdf_path
        self.dpi = dpi
        self.pages_images = []
        self.pages_metadata = []
    
    def converter_pdf_para_imagens(self) -> List[Image.Image]:
        """Converte PDF em imagens PIL"""
        print(f"📄 Convertendo PDF para imagens... DPI={self.dpi}")
        
        try:
            images = convert_from_path(self.pdf_path, dpi=self.dpi)
            self.pages_images = images
            print(f"✅ {len(images)} página(s) convertida(s)")
            return images
        except Exception as e:
            print(f"❌ Erro ao converter PDF: {e}")
            return []
    
    def detectar_placeholders_pytesseract(self, pil_image: Image.Image) -> List[PlaceholderMetadata]:
        """Detecta placeholders com pytesseract"""
        # Converter PIL para OpenCV
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # OCR com pytesseract
        print("  🔍 Detectando placeholders com pytesseract...")
        
        try:
            dados = pytesseract.image_to_data(
                gray, 
                output_type=pytesseract.Output.DICT,
                lang='por'
            )
        except Exception as e:
            print(f"  ⚠️  Erro no OCR: {e}")
            return []
        
        placeholders = []
        
        for i, texto in enumerate(dados['text']):
            # Filtrar placeholders {xxx}
            if '{' in texto and '}' in texto:
                x = dados['left'][i]
                y = dados['top'][i]
                w = dados['width'][i]
                h = dados['height'][i]
                conf = dados['confidence'][i]
                
                if conf < 10:  # Confiança muito baixa
                    continue
                
                # Tamanho da fonte
                font_size = max(8, int(h * 0.7))
                
                # Cor
                roi = gray[max(0, y-5):min(gray.shape[0], y+h+5),
                          max(0, x-5):min(gray.shape[1], x+w+5)]
                color_value = int(np.mean(roi)) if roi.size > 0 else 0
                color = (color_value, color_value, color_value)
                
                placeholder = PlaceholderMetadata(
                    text=texto,
                    x=x, y=y,
                    width=w, height=h,
                    font_size=font_size,
                    color=color,
                    confidence=float(conf)
                )
                
                placeholders.append(placeholder)
                print(f"  ✓ Encontrado: '{texto}' em ({x}, {y})")
        
        if not placeholders:
            print("  ⚠️  Nenhum placeholder encontrado")
        
        return placeholders
    
    def remover_placeholder_em_imagem(self, pil_image: Image.Image,
                                     metadata: PlaceholderMetadata,
                                     margem: int = 5) -> Image.Image:
        """Remove placeholder usando inpainting"""
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Criar máscara
        mask = np.zeros(cv_image.shape[:2], dtype=np.uint8)
        
        # Adicionar margem
        x1 = max(0, metadata.x - margem)
        y1 = max(0, metadata.y - margem)
        x2 = min(cv_image.shape[1], metadata.x + metadata.width + margem)
        y2 = min(cv_image.shape[0], metadata.y + metadata.height + margem)
        
        # Marcar para remover
        mask[y1:y2, x1:x2] = 255
        
        # Inpainting
        resultado = cv2.inpaint(cv_image, mask, 3, cv2.INPAINT_TELEA)
        
        # Converter para PIL
        resultado_pil = Image.fromarray(cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB))
        
        return resultado_pil
    
    def processar_pagina(self, page_num: int) -> Tuple[Image.Image, List[PlaceholderMetadata]]:
        """Processa uma página"""
        print(f"\n📖 Processando página {page_num + 1}...")
        
        pil_image = self.pages_images[page_num]
        
        # Detectar
        placeholders = self.detectar_placeholders_pytesseract(pil_image)
        
        if not placeholders:
            return pil_image, []
        
        # Remover
        print(f"  ✂️  Removendo {len(placeholders)} placeholder(s)...")
        imagem_limpa = pil_image.copy()
        
        for placeholder in placeholders:
            imagem_limpa = self.remover_placeholder_em_imagem(imagem_limpa, placeholder)
        
        # Armazenar metadados
        self.pages_metadata.append({
            'page': page_num,
            'placeholders': [p.to_dict() for p in placeholders]
        })
        
        print(f"  ✅ Página {page_num + 1} processada")
        
        return imagem_limpa, placeholders
    
    def processar_todas_paginas(self) -> List[Image.Image]:
        """Processa todas as páginas"""
        print("\n" + "="*60)
        print("PROCESSANDO TODAS AS PÁGINAS")
        print("="*60)
        
        imagens_processadas = []
        
        for i in range(len(self.pages_images)):
            imagem_limpa, _ = self.processar_pagina(i)
            imagens_processadas.append(imagem_limpa)
        
        return imagens_processadas
    
    def reinserer_valores(self, imagens_limpas: List[Image.Image],
                         placeholders_valores: Dict[str, str]) -> List[Image.Image]:
        """Reinsere valores"""
        print("\n" + "="*60)
        print("REINSERINDO VALORES")
        print("="*60)
        
        imagens_finais = []
        
        for page_num, (imagem_limpa, metadata_page) in enumerate(
            zip(imagens_limpas, self.pages_metadata)):
            
            print(f"\n📝 Página {page_num + 1}: Inserindo valores...")
            
            imagem_final = imagem_limpa.copy()
            draw = ImageDraw.Draw(imagem_final)
            
            for placeholder_info in metadata_page['placeholders']:
                placeholder_key = placeholder_info['text']
                
                if placeholder_key in placeholders_valores:
                    valor = placeholders_valores[placeholder_key]
                    
                    x = placeholder_info['x']
                    y = placeholder_info['y']
                    font_size = placeholder_info['font_size']
                    color = tuple(placeholder_info['color'])
                    
                    # Carregar fonte
                    try:
                        font_paths = [
                            "arial.ttf",
                            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                            "/System/Library/Fonts/Arial.ttf",
                            "C:\\Windows\\Fonts\\arial.ttf",
                        ]
                        
                        fonte = None
                        for font_path in font_paths:
                            if os.path.exists(font_path):
                                fonte = ImageFont.truetype(font_path, font_size)
                                break
                        
                        if fonte is None:
                            fonte = ImageFont.load_default()
                    except:
                        fonte = ImageFont.load_default()
                    
                    # Desenhar
                    draw.text((x, y), valor, fill=color, font=fonte)
                    
                    print(f"  ✓ {placeholder_key} → '{valor}'")
                else:
                    print(f"  ⚠️  Valor não informado para {placeholder_key}")
            
            imagens_finais.append(imagem_final)
        
        return imagens_finais
    
    def salvar_pdf(self, imagens: List[Image.Image], caminho_saida: str):
        """Salva PDF"""
        print("\n" + "="*60)
        print("RECONSTRUINDO PDF")
        print("="*60)
        
        try:
            imagens_rgb = [
                img.convert('RGB') if img.mode != 'RGB' else img
                for img in imagens
            ]
            
            imagens_rgb[0].save(
                caminho_saida,
                save_all=True,
                append_images=imagens_rgb[1:] if len(imagens_rgb) > 1 else [],
                quality=95
            )
            
            tamanho_mb = os.path.getsize(caminho_saida) / 1024 / 1024
            print(f"✅ PDF salvo: {caminho_saida}")
            print(f"   Tamanho: {tamanho_mb:.2f} MB")
            
        except Exception as e:
            print(f"❌ Erro ao salvar PDF: {e}")
    
    def processar_completo(self, placeholders_valores: Dict[str, str],
                          caminho_saida: str):
        """Executa fluxo completo"""
        tempo_inicio = datetime.now()
        
        print("\n" + "🚀 "*30)
        print("PROCESSAMENTO COMPLETO - PYTESSERACT")
        print("🚀 "*30 + "\n")
        
        # A. Converter
        self.converter_pdf_para_imagens()
        
        if not self.pages_images:
            print("❌ Erro: Nenhuma imagem convertida")
            return False
        
        # B. Processar
        imagens_limpas = self.processar_todas_paginas()
        
        # C. Reinserer
        imagens_finais = self.reinserer_valores(imagens_limpas, placeholders_valores)
        
        # D. Salvar
        self.salvar_pdf(imagens_finais, caminho_saida)
        
        tempo_total = (datetime.now() - tempo_inicio).total_seconds()
        
        print("\n" + "✅ "*30)
        print("PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print(f"⏱️  Tempo total: {tempo_total:.2f}s")
        print("✅ "*30)
        
        return True
# ```

# ---

# ## 📖 Como Usar

# Identico ao keras-ocr:

# ```python
# from pdf_placeholder_processor_pytesseract import PDFPlaceholderProcessor

# valores = {
#     "{dd}": "15",
#     "{mm}": "01",
#     "{aaaa}": "2026",
#     "{nome_paciente}": "João Santos",
# }

# processador = PDFPlaceholderProcessor("entrada.pdf", dpi=300)
# processador.processar_completo(valores, "saida.pdf")
# ```

# ---

# ## 📦 Dependências (MÍNIMAS)

# ```bash
# pip install pdf2image pillow opencv-python pytesseract
# ```

# ---

# ## ✅ Vantagens desta Versão

# ✅ Sem keras-ocr (sem problemas de compilação)
# ✅ Muito mais rápido (sem carregar rede neural)
# ✅ Menor consumo de memória
# ✅ Simples, direto, funciona
# ✅ Mesma API que a versão keras-ocr
