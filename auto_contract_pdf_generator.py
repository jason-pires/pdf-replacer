"""
SOLUÇÃO FINAL: Detectar Coordenadas Automaticamente + Substituir Texto

✅ Encontra placeholders {xxx} na imagem automaticamente
✅ Substitui apenas o texto (sem desenhar nada)
✅ Zero configuração manual de coordenadas
✅ Funciona com qualquer template

Como funciona:
1. OCR detecta onde os placeholders {xxx} estão na imagem
2. Sobrescreve apenas o texto encontrado
3. Gera PDF com dados preenchidos
"""

from PIL import Image, ImageDraw, ImageFont
import pytesseract  # OCR para detectar texto
from typing import Dict, Tuple, List
import re
import logging
import os

logger = logging.getLogger(__name__)

# ============================================================================
# SOLUÇÃO: Auto-Detect de Placeholders + Substituição de Texto
# ============================================================================

class AutoContractPDFGenerator:
    """Gera PDF automaticamente detectando placeholders na imagem"""
    
    def __init__(self, image_path: str, use_ocr: bool = True):
        """
        Args:
            image_path: Caminho para imagem JPG/PNG
            use_ocr: Se True, usa OCR para detectar texto (recomendado)
        """
        self.image_path = image_path
        self.image = None
        self.use_ocr = use_ocr
        self.detected_placeholders = {}
        self.load_image()
    
    def load_image(self):
        """Carrega a imagem"""
        try:
            self.image = Image.open(self.image_path)
            logger.info(f"✓ Imagem carregada: {self.image_path}")
            logger.info(f"  Tamanho: {self.image.size[0]}x{self.image.size[1]} pixels")
        except Exception as e:
            logger.error(f"✗ Erro ao carregar imagem: {e}")
            raise
    
    def detect_placeholders_with_ocr(self) -> Dict[str, Dict]:
        """
        Detecta placeholders {xxx} na imagem usando OCR
        
        Retorna: {'placeholder_name': {'x': x, 'y': y, 'width': w, 'height': h}, ...}
        """
        try:
            logger.info("\n🔍 Detectando placeholders com OCR...")
            
            # Usar Tesseract para detectar texto com coordenadas
            data = pytesseract.image_to_data(self.image, output_type=pytesseract.Output.DICT)
            
            placeholders = {}
            
            # Processar cada bloco de texto detectado
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                
                # Procurar por padrão {xxx}
                if '{' in text and '}' in text:
                    match = re.search(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', text)
                    if match:
                        placeholder_name = match.group(1)
                        
                        placeholders[placeholder_name] = {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i],
                            'full_text': text
                        }
                        
                        logger.info(f"  ✓ Encontrado: {{{placeholder_name}}} em ({data['left'][i]}, {data['top'][i]})")
            
            if not placeholders:
                logger.warning("⚠ Nenhum placeholder encontrado com OCR")
            
            self.detected_placeholders = placeholders
            return placeholders
        
        except ImportError:
            logger.error("✗ Tesseract não instalado!")
            logger.error("  Instale: pip install pytesseract")
            logger.error("  E também: apt-get install tesseract-ocr (Linux) ou baixe para Windows")
            raise
        except Exception as e:
            logger.error(f"✗ Erro ao detectar placeholders: {e}")
            raise
    
    def detect_placeholders_simple(self) -> Dict[str, Dict]:
        """
        Versão simplificada SEM OCR (manual)
        Use isto se não quiser instalar Tesseract
        """
        logger.info("\n📝 Modo manual: define placeholders manualmente")
        
        # VOCÊ PREENCHE ISTO COM BASE NA IMAGEM
        placeholders = {
            # Formato: 'nome_placeholder': {'x': coluna_esquerda, 'y': linha_topo, 'width': largura}
            
            # EXEMPLO - EDITE COM SEUS VALORES:
            'nome_da_medica_ou_clinica': {'x': 180, 'y': 140, 'width': 400},
            'cpfcnpjmedicacli': {'x': 180, 'y': 165, 'width': 300},
            'celmedicacli': {'x': 180, 'y': 190, 'width': 300},
            'emailmedicacli': {'x': 180, 'y': 215, 'width': 300},
            'enderecomedical': {'x': 180, 'y': 240, 'width': 400},
            'enderecomedica2': {'x': 180, 'y': 265, 'width': 400},
            
            'nome_paciente': {'x': 180, 'y': 350, 'width': 400},
            'cpfpaciente': {'x': 180, 'y': 375, 'width': 300},
            'celpaciente': {'x': 180, 'y': 400, 'width': 300},
            'emailpaciente': {'x': 180, 'y': 425, 'width': 300},
            'enderecopacientel': {'x': 180, 'y': 450, 'width': 400},
            'enderecopaciente2': {'x': 180, 'y': 475, 'width': 400},
            
            'DD/MM/AAAA': {'x': 450, 'y': 550, 'width': 150},
            'valor': {'x': 450, 'y': 575, 'width': 200},
        }
        
        self.detected_placeholders = placeholders
        return placeholders
    
    def replace_text_only(
        self,
        data: Dict[str, str],
        placeholders: Dict[str, Dict] = None,
        font_path: str = None,
        text_color: Tuple[int, int, int] = (0, 0, 0),
        debug: bool = False
    ) -> Image.Image:
        """
        Substitui APENAS o texto dos placeholders (sem desenhar retângulos)
        
        Args:
            data: Dados para preencher {'placeholder': 'valor'}
            placeholders: Mapa de placeholders (se None, usa detectados)
            font_path: Caminho para fonte TTF
            text_color: Cor RGB do texto
            debug: Mostra logs detalhados
        
        Returns:
            Image.Image: Imagem preenchida
        """
        if placeholders is None:
            placeholders = self.detected_placeholders
        
        # Fazer cópia
        result_image = self.image.copy()
        draw = ImageDraw.Draw(result_image)
        
        # Carregar fonte
        try:
            if font_path:
                font = ImageFont.truetype(font_path, 12)
            else:
                # Tentar encontrar fonte padrão
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 12)
                except:
                    try:
                        font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 12)
                    except:
                        font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Substituir cada placeholder
        for placeholder_name, config in placeholders.items():
            if placeholder_name in data:
                x = config['x']
                y = config['y']
                value = str(data[placeholder_name])
                
                # ✅ APENAS DESENHAR TEXTO (sem retângulo branco)
                draw.text((x, y), value, fill=text_color, font=font)
                
                if debug:
                    logger.info(f"  ✓ {placeholder_name}: '{value}' em ({x}, {y})")
        
        return result_image
    
    def generate_pdf(
        self,
        data: Dict[str, str],
        output_path: str,
        auto_detect: bool = True,
        text_color: Tuple[int, int, int] = (0, 0, 0),
        debug: bool = False
    ) -> bytes:
        """
        Gera PDF completo
        
        Args:
            data: Dados para preencher
            output_path: Onde salvar o PDF
            auto_detect: Se True, detecta placeholders automaticamente
            text_color: Cor do texto
            debug: Mostra logs
        
        Returns:
            bytes: PDF em bytes
        """
        logger.info("\n" + "="*80)
        logger.info(f"📄 Gerando PDF...")
        logger.info("="*80)
        
        # 1. Detectar placeholders
        if auto_detect:
            logger.info("\n🔍 Detectando placeholders automaticamente...")
            try:
                placeholders = self.detect_placeholders_with_ocr()
            except:
                logger.warning("⚠ OCR falhou, usando modo manual")
                placeholders = self.detect_placeholders_simple()
        else:
            placeholders = self.detect_placeholders_simple()
        
        # 2. Validar dados
        missing = [p for p in placeholders.keys() if p not in data]
        if missing:
            logger.warning(f"⚠ Placeholders sem valores: {missing}")
        
        # 3. Substituir texto
        logger.info(f"\n✏️  Substituindo {len(data)} valores...")
        filled_image = self.replace_text_only(
            data,
            placeholders,
            text_color=text_color,
            debug=debug
        )
        
        # 4. Converter para PDF
        logger.info(f"\n📤 Convertendo para PDF...")
        if filled_image.mode != 'RGB':
            filled_image = filled_image.convert('RGB')
        
        filled_image.save(output_path, 'PDF')
        logger.info(f"✓ PDF salvo em: {output_path}")
        
        # 5. Retornar bytes
        with open(output_path, 'rb') as f:
            pdf_bytes = f.read()
        
        logger.info(f"✓ Tamanho final: {len(pdf_bytes)/1024:.2f} KB")
        logger.info("="*80)
        
        return pdf_bytes


# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    # Seus dados
    dados = {
        'nome_da_medica_ou_clinica': 'Dra. Maria Silva - Clínica Premium',
        'cpfcnpjmedicacli': '12.345.678/0001-90',
        'celmedicacli': '(21) 99999-8888',
        'emailmedicacli': 'contato@clinica.com.br',
        'enderecomedical': 'Avenida Paulista, 1000',
        'enderecomedica2': 'São Paulo, SP 01311-100',
        
        'nome_paciente': 'João da Silva Santos',
        'cpfpaciente': '123.456.789-00',
        'celpaciente': '(11) 98765-4321',
        'emailpaciente': 'joao.silva@example.com',
        'enderecopacientel': 'Rua das Flores, 123',
        'enderecopaciente2': 'São Paulo, SP 01310-100',
        
        'DD/MM/AAAA': '15/01/2026',
        'valor': 'R$ 5.000,00',
    }
    
    # OPÇÃO 1: Com OCR Automático (Recomendado)
    print("\n" + "="*80)
    print("OPÇÃO 1: Com OCR Automático (Detecta tudo sozinho)")
    print("="*80)
    
    try:
        generator = AutoContractPDFGenerator('Contrato_Medico-04_procedimentos.jpg')
        
        pdf_bytes = generator.generate_pdf(
            data=dados,
            output_path='contrato_saida_auto.pdf',
            auto_detect=True,  # ← Detecta automaticamente!
            debug=True
        )
        
        print("\n✓ Sucesso! PDF gerado com placeholders detectados automaticamente!")
        
    except ImportError:
        print("\n⚠ Tesseract não instalado. Use Opção 2 (manual)")
    except Exception as e:
        print(f"\n✗ Erro: {e}")
    
    # OPÇÃO 2: Sem OCR (Manual - funciona sempre)
    print("\n" + "="*80)
    print("OPÇÃO 2: Sem OCR (Modo Manual - Sempre Funciona)")
    print("="*80)
    
    try:
        generator = AutoContractPDFGenerator('Contrato_Medico-04_procedimentos.jpg')
        
        pdf_bytes = generator.generate_pdf(
            data=dados,
            output_path='contrato_saida_manual.pdf',
            auto_detect=False,  # ← Usa modo manual
            debug=True
        )
        
        print("\n✓ PDF gerado em modo manual!")
        
    except Exception as e:
        print(f"\n✗ Erro: {e}")

