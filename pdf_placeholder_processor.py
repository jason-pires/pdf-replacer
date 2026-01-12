# pdf_placeholder_processor.py
# Processa PDF: detecta, remove e reinsere placeholders com valores
# Usa keras-ocr para melhor detecção de texto

# ```python
import cv2
import numpy as np
from keras_ocr import pipeline
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
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
    Usa keras-ocr para melhor detecção de texto
    
    Fluxo:
    1. Converte PDF em imagens
    2. Detecta placeholders {xxx} com keras-ocr
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
        self.pages_images = []  # Lista de PIL Images
        self.pages_metadata = []  # Lista com metadados de cada página
        self.ocr_pipeline = None  # Pipeline keras-ocr (carregado sob demanda)
        
    def carregar_ocr_pipeline(self):
        """Carrega o pipeline keras-ocr na primeira necessidade"""
        if self.ocr_pipeline is None:
            print("📚 Carregando pipeline keras-ocr (primeira vez demora ~30s)...")
            self.ocr_pipeline = pipeline.Pipeline()
            print("✅ Pipeline carregado")
        return self.ocr_pipeline
    
    def converter_pdf_para_imagens(self) -> List[Image.Image]:
        """
        Converte todas as páginas do PDF em imagens PIL
        
        Returns:
            Lista de imagens PIL (RGB)
        """
        print(f"📄 Convertendo PDF para imagens... DPI={self.dpi}")
        
        try:
            images = convert_from_path(
                self.pdf_path, 
                dpi=self.dpi,
                first_page=None,
                last_page=None
            )
            
            self.pages_images = images
            print(f"✅ {len(images)} página(s) convertida(s)")
            return images
            
        except Exception as e:
            print(f"❌ Erro ao converter PDF: {e}")
            return []
    
    def detectar_placeholders_keras_ocr(self, pil_image: Image.Image) -> List[PlaceholderMetadata]:
        """
        Detecta todos os placeholders {xxx} em uma imagem usando keras-ocr
        
        Args:
            pil_image: Imagem PIL
            
        Returns:
            Lista de PlaceholderMetadata
        """
        ocr_pipeline = self.carregar_ocr_pipeline()
        
        # Converter PIL para numpy array para keras-ocr
        img_array = np.array(pil_image)
        
        # Executar OCR
        print("  🔍 Executando OCR com keras-ocr...")
        results = ocr_pipeline.recognize([img_array])
        
        placeholders = []
        
        if results and len(results) > 0:
            images, texts = results
            
            # texts é lista de (texto, caixa_delimitadora)
            for text_data in texts:
                if len(text_data) >= 1:
                    texto = text_data[0]
                    
                    # Filtrar apenas placeholders {xxx}
                    if '{' in texto and '}' in texto:
                        # Extrair coordenadas da bounding box
                        # keras-ocr retorna coordenadas normalizadas
                        if len(text_data) > 1:
                            box = text_data[1]
                            
                            # Converter coordenadas para pixels
                            x_coords = [point[0] for point in box]
                            y_coords = [point[1] for point in box]
                            
                            x = int(min(x_coords))
                            y = int(min(y_coords))
                            w = int(max(x_coords) - x)
                            h = int(max(y_coords) - y)
                        else:
                            x, y, w, h = 0, 0, 50, 20
                        
                        # Estimar tamanho da fonte baseado na altura
                        font_size = max(8, int(h * 0.7))
                        
                        # Detectar cor dominante da região
                        try:
                            roi = np.array(pil_image.crop((
                                max(0, x-5), 
                                max(0, y-5),
                                min(pil_image.width, x+w+5),
                                min(pil_image.height, y+h+5)
                            )))
                            
                            if roi.size > 0:
                                if len(roi.shape) == 3:
                                    color_value = int(np.mean(roi[:,:,0]))
                                else:
                                    color_value = int(np.mean(roi))
                            else:
                                color_value = 0
                        except:
                            color_value = 0
                        
                        color = (color_value, color_value, color_value)
                        confidence = 0.95  # keras-ocr não retorna confiança por padrão
                        
                        placeholder = PlaceholderMetadata(
                            text=texto,
                            x=x, y=y,
                            width=w, height=h,
                            font_size=font_size,
                            color=color,
                            confidence=confidence
                        )
                        
                        placeholders.append(placeholder)
                        print(f"  ✓ Encontrado: '{texto}' em ({x}, {y})")
        
        if not placeholders:
            print("  ⚠️  Nenhum placeholder encontrado")
        
        return placeholders
    
    def remover_placeholder_em_imagem(self, pil_image: Image.Image, 
                                     metadata: PlaceholderMetadata,
                                     margem: int = 5) -> Image.Image:
        """
        Remove um placeholder específico da imagem usando inpainting
        
        Args:
            pil_image: Imagem PIL original
            metadata: Metadados do placeholder
            margem: pixels de margem ao redor do texto
            
        Returns:
            Imagem PIL com placeholder removido
        """
        # Converter para OpenCV
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Criar máscara
        mask = np.zeros(cv_image.shape[:2], dtype=np.uint8)
        
        # Adicionar margem
        x1 = max(0, metadata.x - margem)
        y1 = max(0, metadata.y - margem)
        x2 = min(cv_image.shape[1], metadata.x + metadata.width + margem)
        y2 = min(cv_image.shape[0], metadata.y + metadata.height + margem)
        
        # Marcar região para remover (branco = remover)
        mask[y1:y2, x1:x2] = 255
        
        # Aplicar inpainting (reconstruir fundo)
        resultado = cv2.inpaint(cv_image, mask, 3, cv2.INPAINT_TELEA)
        
        # Converter de volta para PIL
        resultado_pil = Image.fromarray(cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB))
        
        return resultado_pil
    
    def processar_pagina(self, page_num: int) -> Tuple[Image.Image, List[PlaceholderMetadata]]:
        """
        Processa uma página completa:
        1. Detecta placeholders
        2. Remove cada um
        3. Armazena metadados
        
        Args:
            page_num: Número da página (0-indexed)
            
        Returns:
            (imagem_processada, lista_de_metadados)
        """
        print(f"\n📖 Processando página {page_num + 1}...")
        
        pil_image = self.pages_images[page_num]
        
        # 1. Detectar com keras-ocr
        print("  🔍 Detectando placeholders com keras-ocr...")
        placeholders = self.detectar_placeholders_keras_ocr(pil_image)
        
        if not placeholders:
            print("  ⚠️  Nenhum placeholder encontrado nesta página")
            return pil_image, []
        
        # 2. Remover cada um
        print(f"  ✂️  Removendo {len(placeholders)} placeholder(s)...")
        imagem_limpa = pil_image.copy()
        
        for placeholder in placeholders:
            imagem_limpa = self.remover_placeholder_em_imagem(imagem_limpa, placeholder)
        
        # 3. Armazenar metadados
        self.pages_metadata.append({
            'page': page_num,
            'placeholders': [p.to_dict() for p in placeholders]
        })
        
        print(f"  ✅ Página {page_num + 1} processada com {len(placeholders)} placeholder(s) removido(s)")
        
        return imagem_limpa, placeholders
    
    def processar_todas_paginas(self) -> List[Image.Image]:
        """
        Processa todas as páginas do PDF
        
        Returns:
            Lista de imagens processadas
        """
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
        """
        Reinsere os valores nos placeholders removidos
        
        Args:
            imagens_limpas: Lista de imagens sem placeholders
            placeholders_valores: Dict {"{placeholder}": "valor"}
            
        Returns:
            Lista de imagens com valores inseridos
        """
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
                
                # Procurar o valor
                if placeholder_key in placeholders_valores:
                    valor = placeholders_valores[placeholder_key]
                    
                    x = placeholder_info['x']
                    y = placeholder_info['y']
                    font_size = placeholder_info['font_size']
                    color = tuple(placeholder_info['color'])
                    
                    # Tentar usar fonte True Type (fallback para default)
                    try:
                        # Tenta diferentes caminhos possíveis para Arial
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
                    
                    # Desenhar texto
                    draw.text(
                        (x, y),
                        valor,
                        fill=color,
                        font=fonte
                    )
                    
                    print(f"  ✓ {placeholder_key} → '{valor}'")
                else:
                    print(f"  ⚠️  Valor não informado para {placeholder_key}")
            
            imagens_finais.append(imagem_final)
        
        return imagens_finais
    
    def salvar_pdf(self, imagens: List[Image.Image], caminho_saida: str):
        """
        Reconstrói PDF a partir das imagens
        
        Args:
            imagens: Lista de imagens PIL
            caminho_saida: Caminho do PDF de saída
        """
        print("\n" + "="*60)
        print("RECONSTRUINDO PDF")
        print("="*60)
        
        try:
            # Converter para RGB se necessário
            imagens_rgb = [
                img.convert('RGB') if img.mode != 'RGB' else img 
                for img in imagens
            ]
            
            # Salvar como PDF
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
        """
        Executa o fluxo completo:
        A. PDF → Imagens
        B. Detectar, remover placeholders
        C. Reinserer valores
        D. Salvar PDF
        
        Args:
            placeholders_valores: Dict {"{placeholder}": "valor"}
            caminho_saida: Caminho do PDF de saída
        """
        tempo_inicio = datetime.now()
        
        print("\n" + "🚀 "*30)
        print("INICIANDO PROCESSAMENTO COMPLETO")
        print("🚀 "*30 + "\n")
        
        # PASSO A: Converter PDF para imagens
        self.converter_pdf_para_imagens()
        
        if not self.pages_images:
            print("❌ Erro: Nenhuma imagem convertida")
            return False
        
        # PASSO B: Processar (detectar e remover)
        imagens_limpas = self.processar_todas_paginas()
        
        # PASSO C: Reinserer valores
        imagens_finais = self.reinserer_valores(imagens_limpas, placeholders_valores)
        
        # PASSO D: Salvar PDF
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

# ```python
# # 1. Definir valores dos placeholders
# placeholders_valores = {
#     "{dd}": "15",
#     "{mm}": "01",
#     "{aaaa}": "2026",
#     "{nome_da_medica_ou_clinica}": "Dra. Maria Silva",
#     "{nome_paciente}": "João Santos",
#     # ... adicione todos os placeholders
# }

# # 2. Criar processador
# processador = PDFPlaceholderProcessor(
#     pdf_path="Contrato_Medico-04_procedimentos.pdf",
#     dpi=300  # Alta qualidade
# )

# # 3. Executar processamento completo
# processador.processar_completo(
#     placeholders_valores=placeholders_valores,
#     caminho_saida="Contrato_Preenchido.pdf"
# )
# ```

# ---

# ## 📦 Dependências Necessárias

# ```bash
# pip install keras-ocr pdf2image pillow opencv-python
# ```

# ---

# ## ✅ Melhorias com keras-ocr

# ✅ **Melhor detecção** de texto em diferentes fontes
# ✅ **Mais robusto** a diferentes resoluções
# ✅ **Suporta múltiplos idiomas**
# ✅ **Reconhece** placeholders mesmo com formatações complexas
# ✅ **Mais preciso** que pytesseract em muitos casos
