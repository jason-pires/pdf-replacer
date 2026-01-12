"""
EXEMPLO PRÁTICO: Como fazer o replace de placeholders com PyMuPDF
Método Novo: Busca Automática de Coordenadas ✅

Dados reais → PDF preenchido (com posicionamento automático!)
"""

import json
from pdf_replacer_pymupdf import PDFPlaceholderReplacerMuPDF, DatabaseToDataMapperMuPDF

# ============================================================================
# CENÁRIO 1: Dados diretos em dicionário (teste local)
# ============================================================================

print("\n" + "="*80)
print("CENÁRIO 1: Replace com dados diretos (dicionário) - NOVO COM PYMUPDF")
print("="*80)

# Dados do contrato (vindo do banco de dados)
dados_contrato = {
    # Dados da clínica
    'nome_da_medica_ou_clinica': 'Dra. Maria Silva - Clínica Estética Premium',
    'cpfcnpjmedicacli': '12.345.678/0001-90',
    'celmedicacli': '(21) 99999-8888',
    'emailmedicacli': 'contato@clinicamaria.com.br',
    'enderecomedical': 'Avenida Paulista, 1000 - Apt 3000',
    'enderecomedica2': 'São Paulo, SP 01311-100 - Brasil',
    
    # Dados da paciente
    'nome_paciente': 'João da Silva Santos',
    'cpfpaciente': '123.456.789-00',
    'celpaciente': '(11) 98765-4321',
    'emailpaciente': 'joao.silva@example.com',
    'enderecopaciente2': 'São Paulo, SP 01310-100',
    
    # Data do contrato
    'dd': '15',
    'mmm': 'janeiro',
    'aaaa': '2026',
    'DD/MM/AAAA': '15/01/2026',

    # Procedimentos
    'procedimento_4': 'Preenchimento Facial com Ácido Hialurônico',
    'procedimento_4_imagem': 'IMAGEM_DO_PROCEDIMENTO_04.png',
    'procedimento_4_descricao': 'Preenchimento para harmonização facial, melhorando contornos e volume.',
}

print(f"\nDados carregados: {len(dados_contrato)} campos")
print("\nExemplos:")
for key, value in list(dados_contrato.items())[:5]:
    print(f"  {key}: {value}")

try:
    # ✅ NOVO: Usar PDFPlaceholderReplacerMuPDF
    replacer = PDFPlaceholderReplacerMuPDF('templates/contrato-medico-04.pdf')
    
    # # Step 1: Extrair placeholders (encontra automaticamente!)
    # print("\n📍 Encontrando placeholders no PDF...")
    # placeholders = replacer.extract_placeholders()
    # print(f"✓ Encontrados {len(placeholders)} placeholders únicos:")
    # for placeholder in list(placeholders.keys()):
    #     print(f"  - {placeholder}")
    
    # # Step 2: Validar dados
    # print("\n✓ Validando dados...")
    # is_valid, missing, extras = replacer.validate_data(dados_contrato)
    
    # if is_valid:
    #     print("✓ Validação passou!")
    # else:
    #     print(f"⚠ Faltando campos: {missing}")
    #     print(f"⚠ Campos extras: {extras}")
    
    # Step 3: Gerar PDF (com posicionamento automático!)
    print("\n📄 Gerando PDF com PyMuPDF (busca automática)...")
    pdf_bytes = replacer.replace_and_get_pdf(
        data=dados_contrato,
        output_path='contratos_gerados/contrato_joao_silva.pdf',
        font_size=10,
        text_color=(0, 0, 0)  # Preto
    )
    
    print(f"✓ PDF gerado com sucesso!")
    print(f"  Tamanho: {len(pdf_bytes)/1024:.2f} KB")
    print(f"  Textos no lugar CERTO! ✅")
    
except FileNotFoundError:
    print("\n⚠ Template PDF não encontrado.")
    print("  Execute o exemplo com um PDF válido.")
except Exception as e:
    print(f"\n✗ Erro: {e}")
