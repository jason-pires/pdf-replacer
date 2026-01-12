"""
SOLUÇÃO CORRIGIDA: Usando PyMuPDF para ENCONTRAR e SUBSTITUIR placeholders
Com posicionamento AUTOMÁTICO e PRECISO

Instalação:
pip install PyMuPDF
"""

import fitz  # PyMuPDF
from io import BytesIO
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFPlaceholderReplacerMuPDF:
    """
    Substitui placeholders {xxx} usando PyMuPDF com busca automática de coordenadas
    
    DIFERENÇA IMPORTANTE:
    - Método anterior (PyPDF2): Requer mapear posições manualmente
    - Este método (PyMuPDF): Encontra automaticamente onde está cada placeholder
    """
    
    def __init__(self, template_path: str):
        """
        Args:
            template_path: Caminho do template PDF
        """
        self.template_path = template_path
        self.pattern = re.compile(r'\{([^}]+)\}')
    
    def extract_placeholders(self) -> dict:
        """
        Extrai todos os placeholders e suas posições (x, y, width, height)
        
        Returns:
            {placeholder_name: [lista de rects(x0, y0, x1, y1)]}
        """
        try:
            doc = fitz.open(self.template_path)
            placeholders = {}
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                
                # Encontrar todos os placeholders no texto
                matches = self.pattern.findall(text)
                
                for match in matches:
                    placeholder_text = f"{{{match}}}"
                    
                    # Buscar posição exata do placeholder
                    rects = page.search_for(placeholder_text)
                    
                    if rects:
                        if match not in placeholders:
                            placeholders[match] = []
                        
                        for rect in rects:
                            placeholders[match].append({
                                'page': page_num,
                                'x0': rect.x0,
                                'y0': rect.y0,
                                'x1': rect.x1,
                                'y1': rect.y1,
                                'width': rect.width,
                                'height': rect.height,
                            })
                        
                        logger.info(
                            f"Encontrado {placeholder_text} na página {page_num} "
                            f"em ({rect.x0:.1f}, {rect.y0:.1f})"
                        )
            
            doc.close()
            return placeholders
        
        except Exception as e:
            logger.error(f"Erro ao extrair placeholders: {e}")
            return {}
    
    def validate_data(self, data: dict) -> tuple:
        """
        Valida se todos os placeholders têm valores
        
        Returns:
            (válido: bool, faltando: list, extras: list)
        """
        placeholders = self.extract_placeholders()
        placeholder_names = set(placeholders.keys())
        provided_keys = set(data.keys())
        
        missing = placeholder_names - provided_keys
        extras = provided_keys - placeholder_names
        
        is_valid = len(missing) == 0
        
        return is_valid, list(missing), list(extras)
    
    def replace_and_get_pdf(
        self, 
        data: dict, 
        output_path: str = None,
        font_name: str = "helv",
        font_size: int = 10,
        text_color: tuple = (0, 0, 0)
    ) -> bytes:
        """
        Substitui placeholders por valores reais com posicionamento automático
        
        Args:
            data: Dicionário {placeholder: valor}
            output_path: (opcional) onde salvar
            font_name: Nome da fonte ("helv", "times-roman", etc)
            font_size: Tamanho da fonte em pontos
            text_color: Tupla RGB (0-1) ex: (0, 0, 0) = preto
        
        Returns:
            PDF em bytes
        """
        
        # Validar dados
        is_valid, missing, extras = self.validate_data(data)
        
        if not is_valid:
            logger.warning(f"Campos faltando: {missing}")
        
        try:
            doc = fitz.open(self.template_path)
            placeholders = self.extract_placeholders()
            
            # Processar cada placeholder
            for placeholder_name, positions in placeholders.items():
                if placeholder_name not in data:
                    logger.warning(f"Placeholder {placeholder_name} sem valor fornecido")
                    continue
                
                value = str(data[placeholder_name])
                placeholder_text = f"{{{placeholder_name}}}"
                
                # Para cada ocorrência do placeholder
                for pos_info in positions:
                    page_num = pos_info['page']
                    page = doc[page_num]
                    
                    # 1. Remover o placeholder (cobrir com branco)
                    rect = fitz.Rect(
                        pos_info['x0'],
                        pos_info['y0'],
                        pos_info['x1'],
                        pos_info['y1']
                    )
                    
                    # Desenhar retângulo branco (mesmo tamanho do placeholder)
                    page.draw_rect(
                        rect,
                        color=None,
                        fill=(1, 1, 1),  # Branco
                        width=0
                    )
                    
                    # 2. Inserir novo texto na mesma posição
                    # Ajustar para que o texto fique centralizado no espaço do placeholder
                    x = rect.x0
                    y = rect.y0 + (rect.height * 0.75)  # Ajuste vertical
                    
                    page.insert_text(
                        (x, y),
                        value,
                        fontsize=font_size,
                        fontname=font_name,
                        color=text_color,
                    )
                    
                    logger.info(
                        f"✓ Substituído {placeholder_text} por '{value}' "
                        f"na página {page_num}"
                    )
            
            # 3. Salvar resultado
            # output = BytesIO()
            # doc.write(output)
            # output.seek(0)
            # result_bytes = output.getvalue()
            result_bytes = doc.write()
            
            doc.close()
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(result_bytes)
                logger.info(f"PDF salvo em: {output_path}")
            
            return result_bytes
        
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {e}")
            raise
    
    def list_available_fonts(self) -> list:
        """
        Lista todas as fontes disponíveis no PyMuPDF
        """
        return fitz.get_fontnames()


class DatabaseToDataMapperMuPDF:
    """
    Mapeia dados do banco para placeholders (igual ao anterior)
    """
    
    def __init__(self):
        self.mapping = {
            # Clínica
            'clinica_nome': 'nome_da_medica_ou_clinica',
            'clinica_cpf_cnpj': 'cpfcnpjmedicacli',
            'clinica_celular': 'celmedicacli',
            'clinica_email': 'emailmedicacli',
            'clinica_endereco_linha1': 'enderecomedical',
            'clinica_endereco_linha2': 'enderecomedica2',
            
            # Paciente
            'paciente_nome': 'nome_paciente',
            'paciente_cpf': 'cpfpaciente',
            'paciente_celular': 'celpaciente',
            'paciente_email': 'emailpaciente',
            'paciente_endereco_linha1': 'enderecopacientel',
            'paciente_endereco_linha2': 'enderecopaciente2',
            
            # Datas
            'data_dia': 'dd',
            'data_mes_nome': 'mmm',
            'data_ano': 'aaaa',
            'data_completa': 'DD/MM/AAAA',
            
            # Valores
            'valor_total': 'valor',
            'pagamento_especificacao': 'espec_pagto',
            'pagamento_parcelas': 'xx_parcelas_de_R$_yyyy,yy',
            'pagamento_restante': 'xx_restante_de_R$_yyyy,yy',
        }
    
    def map_db_to_placeholders(self, db_data: dict) -> dict:
        """Converte dados do DB para placeholders"""
        placeholder_data = {}
        
        for db_field, placeholder in self.mapping.items():
            if db_field in db_data:
                placeholder_data[placeholder] = str(db_data[db_field])
        
        return placeholder_data
    
    def add_custom_mapping(self, db_field: str, placeholder: str):
        """Adiciona mapeamento customizado"""
        self.mapping[db_field] = placeholder


# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*80)
    print("EXEMPLO 1: Listar placeholders encontrados no PDF")
    print("="*80)
    
    replacer = PDFPlaceholderReplacerMuPDF('templates/contrato-medico-04.pdf')
    
    placeholders = replacer.extract_placeholders()
    
    print(f"\n✓ Encontrados {len(placeholders)} placeholders únicos:\n")
    
    for placeholder, positions in sorted(placeholders.items()):
        print(f"  {placeholder}:")
        for i, pos in enumerate(positions):
            print(f"    - Página {pos['page']}, Posição: ({pos['x0']:.1f}, {pos['y0']:.1f})")
    
    
    print("\n" + "="*80)
    print("EXEMPLO 2: Validar dados antes de gerar")
    print("="*80)
    
    dados_db = {
        'clinica_nome': 'Dra. Maria Silva',
        'clinica_cpf_cnpj': '12.345.678/0001-90',
        'clinica_celular': '(21) 99999-8888',
        'clinica_email': 'contato@clinicamaria.com.br',
        'clinica_endereco_linha1': 'Avenida Paulista, 1000',
        'clinica_endereco_linha2': 'São Paulo, SP 01311-100',
        
        'paciente_nome': 'João da Silva Santos',
        'paciente_cpf': '123.456.789-00',
        'paciente_celular': '(11) 98765-4321',
        'paciente_email': 'joao@example.com',
        'paciente_endereco_linha1': 'Rua das Flores, 123 - Apt. 456',
        'paciente_endereco_linha2': 'São Paulo, SP 01310-100',
        
        'data_dia': '15',
        'data_mes_nome': 'janeiro',
        'data_ano': '2026',
        'data_completa': '15/01/2026',
        
        'valor_total': 'R$ 5.000,00',
        'pagamento_especificacao': 'Lipoaspiração',
        'pagamento_parcelas': '3 parcelas de R$ 1.666,67',
        'pagamento_restante': 'Sem restante',
    }
    
    mapper = DatabaseToDataMapperMuPDF()
    dados_placeholders = mapper.map_db_to_placeholders(dados_db)
    
    is_valid, missing, extras = replacer.validate_data(dados_placeholders)
    
    if is_valid:
        print("✓ Dados válidos! Pronto para gerar PDF")
    else:
        print(f"✗ Campos faltando: {missing}")
    
    
    print("\n" + "="*80)
    print("EXEMPLO 3: Gerar PDF com posicionamento automático")
    print("="*80)
    
    try:
        pdf_bytes = replacer.replace_and_get_pdf(
            data=dados_placeholders,
            output_path='output_contrato_pymupdf.pdf',
            font_size=10,
            text_color=(0, 0, 0)  # Preto
        )
        
        print(f"\n✓ PDF gerado com sucesso!")
        print(f"  Tamanho: {len(pdf_bytes)/1024:.2f} KB")
        print(f"  Salvo em: output_contrato_pymupdf.pdf")
        
    except Exception as e:
        print(f"✗ Erro ao gerar: {e}")
    
    
    print("\n" + "="*80)
    print("EXEMPLO 4: Listar fontes disponíveis")
    print("="*80)
    
    fonts = replacer.list_available_fonts()
    print(f"\nFontes disponíveis no PyMuPDF:")
    for font in sorted(fonts)[:10]:  # Mostrar primeiras 10
        print(f"  - {font}")
    print(f"  ... ({len(fonts)} fontes no total)")
    print(f"\nRecomendado usar: 'helv' (Helvetica) ou 'times-roman'")


# ============================================================================
# IMPORTANTE: COMPARAÇÃO COM ABORDAGEM ANTERIOR
# ============================================================================

print("\n" + "="*80)
print("POR QUE AGORA FUNCIONA MELHOR")
print("="*80)

print("""
❌ ABORDAGEM ANTERIOR (PyPDF2 + ReportLab):
   ├─ Exigia mapeamento manual de posições
   ├─ Coordenadas (100, 750) tinham que ser descobertas manualmente
   ├─ Cada template precisava de ajustes diferentes
   ├─ Textos frequentemente ficavam fora de posição
   └─ Muito frágil e impreciso

✅ ABORDAGEM NOVA (PyMuPDF):
   ├─ Busca automaticamente onde está cada placeholder
   ├─ Encontra as coordenadas exatas com page.search_for()
   ├─ Substitui no exato local onde o placeholder estava
   ├─ Funciona para qualquer template sem ajustes
   ├─ Preciso e confiável
   └─ Textos no lugar exato!

DIFERENÇA:
PyMuPDF.search_for('{nome_paciente}')
↓
Retorna: Rect(x0=100.5, y0=742.3, x1=245.2, y1=759.8)
↓
Usa essas coordenadas para substituir no lugar exato
""")
