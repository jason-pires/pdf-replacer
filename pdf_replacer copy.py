"""
SUBSTITUIDOR DE PLACEHOLDERS EM PDF
Substitui todos os placeholders {xxx} por valores reais do banco de dados

Uso:
    replacer = PDFPlaceholderReplacer('template.pdf')
    dados = {
        'nome_paciente': 'João Silva',
        'cpfpaciente': '123.456.789-00',
        ...
    }
    pdf_bytes = replacer.replace_and_get_pdf(dados)
"""

import re
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFPlaceholderReplacerBKP:
    """
    Substitui placeholders {xxx} em PDF por valores reais
    Mantém a formatação original do PDF
    """
    
    # Mapeamento de placeholders para leitura amigável
    PLACEHOLDER_MAPPING = {
        # Dados da clínica
        'nome_da_medica_ou_clinica': 'Nome da Médica/Clínica',
        'cpfcnpjmedicacli': 'CPF/CNPJ Médica/Clínica',
        'celmedicacli': 'Celular Médica/Clínica',
        'emailmedicacli': 'Email Médica/Clínica',
        'enderecomedical': 'Endereço Médica (Linha 1)',
        'enderecomedica2': 'Endereço Médica (Linha 2)',
        
        # Dados da paciente
        'nome_paciente': 'Nome da Paciente',
        'cpfpaciente': 'CPF da Paciente',
        'celpaciente': 'Celular da Paciente',
        'emailpaciente': 'Email da Paciente',
        'enderecopacientel': 'Endereço Paciente (Linha 1)',
        'enderecopaciente2': 'Endereço Paciente (Linha 2)',
        
        # Datas
        'dd': 'Dia',
        'mmm': 'Mês (texto)',
        'aaaa': 'Ano',
        'DD/MM/AAAA': 'Data completa',
        
        # Valores
        'valor': 'Valor total',
        'espec_pagto': 'Especificação do pagamento',
        'xx_parcelas_de_R$_yyyy,yy': 'Descrição das parcelas',
        'xx_restante_de_R$_yyyy,yy': 'Descrição do restante',
        
        # Procedimentos (padrão 1-4, expandível)
        'procedimento': 'Descrição do procedimento',
        'procedimento_imagem': 'Imagem do procedimento',
        'procedimento_descricao': 'Descrição técnica do procedimento',
    }
    
    def __init__(self, template_path: str):
        """
        Inicializa replacer com template PDF
        
        Args:
            template_path: Caminho do arquivo PDF template
        """
        self.template_path = template_path
        self.pattern = re.compile(r'\{([^}]+)\}')
    
    def extract_placeholders(self) -> Dict[str, int]:
        """
        Extrai todos os placeholders do PDF e conta quantas vezes aparecem
        
        Returns:
            Dict com placeholder: quantidade_de_ocorrências
        """
        try:
            with open(self.template_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
            
            matches = self.pattern.findall(text)
            
            # Contar ocorrências
            count_dict = {}
            for match in matches:
                count_dict[match] = count_dict.get(match, 0) + 1
            
            return count_dict
        
        except Exception as e:
            logger.error(f"Erro ao extrair placeholders: {e}")
            return {}
    
    def validate_data(self, data: Dict[str, str]) -> Tuple[bool, List[str], List[str]]:
        """
        Valida se todos os placeholders têm valores correspondentes
        
        Args:
            data: Dicionário com valores reais
        
        Returns:
            (válido: bool, faltando: List, extras: List)
        """
        placeholders = self.extract_placeholders()
        placeholder_names = set(placeholders.keys())
        provided_keys = set(data.keys())
        
        missing = placeholder_names - provided_keys
        extras = provided_keys - placeholder_names
        
        is_valid = len(missing) == 0
        
        return is_valid, list(missing), list(extras)
    
    def replace_and_get_pdf(self, data: Dict[str, str], output_path: str = None) -> bytes:
        """
        Substitui placeholders e retorna PDF em bytes
        
        Método: Extrai texto, substitui, cria overlay com ReportLab
        
        Args:
            data: Dict com {placeholder: valor_real}
            output_path: (opcional) onde salvar o PDF
        
        Returns:
            PDF em bytes (pronto para S3, email, etc)
        """
        
        # Validar dados
        is_valid, missing, extras = self.validate_data(data)
        
        if not is_valid:
            logger.warning(f"Campos faltando: {missing}")
            logger.warning(f"Campos extras (ignorados): {extras}")
        
        try:
            # 1. Carregar PDF original
            with open(self.template_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                writer = PyPDF2.PdfWriter()
                
                # 2. Para cada página do template
                for page_num, page in enumerate(reader.pages):
                    # 3. Extrair texto da página para encontrar posições aproximadas
                    page_text = page.extract_text() or ""
                    
                    # 4. Criar overlay com ReportLab
                    packet = BytesIO()
                    can = canvas.Canvas(packet, pagesize=letter)
                    can.setFont("Helvetica", 10)
                    
                    # Substituir cada placeholder no overlay
                    y_position = 750  # Começa perto do topo
                    
                    for placeholder, value in data.items():
                        # Encontrar placeholder no texto
                        if f"{{{placeholder}}}" in page_text:
                            # Desenhar valor
                            can.drawString(100, y_position, str(value))
                            y_position -= 15
                    
                    can.save()
                    packet.seek(0)
                    
                    # 5. Mesclar overlay com página original
                    overlay_pdf = PyPDF2.PdfReader(packet)
                    if len(overlay_pdf.pages) > 0:
                        page.merge_page(overlay_pdf.pages[0])
                    
                    writer.add_page(page)
                
                # 6. Salvar resultado
                output = BytesIO()
                writer.write(output)
                output.seek(0)
                result_bytes = output.getvalue()
                
                # 7. Salvar em arquivo se path fornecido
                if output_path:
                    with open(output_path, 'wb') as f:
                        f.write(result_bytes)
                    logger.info(f"PDF salvo em: {output_path}")
                
                return result_bytes
        
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {e}")
            raise


class DatabaseToDataMapper:
    """
    Mapeia dados do banco de dados para o dicionário de placeholders
    
    Exemplo:
        db_data = {
            'nome': 'João Silva',
            'cpf': '123.456.789-00',
            ...
        }
        mapper = DatabaseToDataMapper()
        placeholder_data = mapper.map_db_to_placeholders(db_data)
    """
    
    def __init__(self):
        """
        Define o mapeamento de colunas DB → placeholders
        Customize conforme seu schema
        """
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
            
            # Datas (se vindo de DB como objeto date)
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
    
    def map_db_to_placeholders(self, db_data: Dict) -> Dict[str, str]:
        """
        Converte dados do DB para placeholders
        
        Args:
            db_data: Dicionário com dados do banco
        
        Returns:
            Dicionário com placeholder: valor
        """
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
    
    print("\n" + "="*70)
    print("EXEMPLO 1: Extrair placeholders do template")
    print("="*70)
    
    replacer = PDFPlaceholderReplacer('templates/contrato-medico-04.pdf')
    
    placeholders = replacer.extract_placeholders()
    print(f"\nEncontrados {len(placeholders)} placeholders únicos:")
    for placeholder, count in sorted(placeholders.items()):
        desc = PDFPlaceholderReplacer.PLACEHOLDER_MAPPING.get(
            placeholder, 
            "Desconhecido"
        )
        print(f"  {placeholder:40} → {count}x  ({desc})")
    
    
    print("\n" + "="*70)
    print("EXEMPLO 2: Validar dados antes de gerar")
    print("="*70)
    
    # Dados do banco de dados
    dados_db = {
        # Clínica
        'clinica_nome': 'Dra. Maria Silva - Clínica Estética',
        'clinica_cpf_cnpj': '12.345.678/0001-90',
        'clinica_celular': '(21) 99999-8888',
        'clinica_email': 'contato@clinicamaria.com.br',
        'clinica_endereco_linha1': 'Av. Paulista, 1000 - São Paulo, SP',
        'clinica_endereco_linha2': 'CEP 01311-100',
        
        # Paciente
        'paciente_nome': 'João da Silva Santos',
        'paciente_cpf': '123.456.789-00',
        'paciente_celular': '(11) 98765-4321',
        'paciente_email': 'joao@example.com',
        'paciente_endereco_linha1': 'Rua das Flores, 123 - Apt. 456',
        'paciente_endereco_linha2': 'São Paulo, SP 01310-100',
        
        # Data
        'data_dia': '15',
        'data_mes_nome': 'janeiro',
        'data_ano': '2026',
        'data_completa': '15/01/2026',
        
        # Valores
        'valor_total': '5000.00',
        'pagamento_especificacao': 'Cirurgia de lipoaspiração',
        'pagamento_parcelas': '3 parcelas de R$ 1.666,67',
        'pagamento_restante': 'Sem restante',
    }
    
    # Mapear dados do DB para placeholders
    mapper = DatabaseToDataMapper()
    dados_placeholders = mapper.map_db_to_placeholders(dados_db)
    
    # Validar
    is_valid, missing, extras = replacer.validate_data(dados_placeholders)
    
    if is_valid:
        print("✓ Dados válidos! Pronto para gerar PDF")
    else:
        print(f"✗ Campos faltando: {missing}")
        if extras:
            print(f"  Campos extras (ignorados): {extras}")
    
    
    print("\n" + "="*70)
    print("EXEMPLO 3: Gerar PDF com dados reais")
    print("="*70)
    
    try:
        pdf_bytes = replacer.replace_and_get_pdf(
            data=dados_placeholders,
            output_path='output_contrato_preenchido.pdf'
        )
        
        print(f"✓ PDF gerado com sucesso!")
        print(f"  Tamanho: {len(pdf_bytes)/1024:.2f} KB")
        print(f"  Salvo em: output_contrato_preenchido.pdf")
        
    except Exception as e:
        print(f"✗ Erro ao gerar: {e}")
    
    
    print("\n" + "="*70)
    print("EXEMPLO 4: Integração com API (para usar no NestJS)")
    print("="*70)
    
    print("""
    # No seu NestJS, você faria:
    
    const replacer = new PDFPlaceholderReplacer('./templates/contrato-medico-04.pdf');
    const mapper = new DatabaseToDataMapper();
    
    // Buscar dados do paciente no BD
    const dbData = await database.query(`
        SELECT 
            clinica_nome,
            clinica_cpf_cnpj,
            paciente_nome,
            paciente_cpf,
            valor_total,
            data_completa
        FROM contratos WHERE id = $1
    `, [contractId]);
    
    // Mapear para placeholders
    const placeholderData = mapper.map_db_to_placeholders(dbData);
    
    // Gerar PDF
    const pdfBytes = replacer.replace_and_get_pdf(placeholderData);
    
    // Salvar em S3 e retornar
    await s3.upload({
        Bucket: 'contratos',
        Key: `${contractId}.pdf`,
        Body: pdfBytes
    });
    """)
