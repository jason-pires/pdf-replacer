"""
EXEMPLO PRÁTICO: Como fazer o replace de placeholders
Dados reais → PDF preenchido
"""

import json
from pdf_replacer import PDFPlaceholderReplacer, DatabaseToDataMapper


# ============================================================================
# CENÁRIO 1: Dados diretos em dicionário (teste local)
# ============================================================================

print("\n" + "="*80)
print("CENÁRIO 1: Replace com dados diretos (dicionário)")
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
for key, value in list(dados_contrato.items()):
    print(f"  {key}: {value}")

try:
    replacer = PDFPlaceholderReplacer('contrato-medico-04.pdf')
    places = replacer.extract_placeholders()
    print(f"\nPlaceholders encontrados no template: {len(places)}")
    print("Exemplos:")
    for ph in places:
        print(f"  {ph}")
    
    # Validar dados
    is_valid, missing, extras = replacer.validate_data(dados_contrato)
    
    if is_valid:
        print("\n✓ Validação passou!")
    else:
        print(f"\n⚠ Faltando campos: {missing}")
    
    # Gerar PDF
    pdf_bytes = replacer.replace_and_get_pdf(
        data=dados_contrato,
        output_path='contratos_gerados/contrato_joao_silva.pdf'
    )
    
    print(f"\n✓ PDF gerado com sucesso!")
    print(f"  Tamanho: {len(pdf_bytes)/1024:.2f} KB")

except FileNotFoundError:
    print("\n⚠ Template PDF não encontrado. Execute o exemplo 2 para usar dados reais do BD.")