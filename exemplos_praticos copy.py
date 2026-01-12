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
    'enderecopacientel': 'Rua das Flores, 123 - Apartamento 456',
    'enderecopaciente2': 'São Paulo, SP 01310-100',
    
    # Data do contrato
    'dd': '15',
    'mmm': 'janeiro',
    'aaaa': '2026',
    'DD/MM/AAAA': '15/01/2026',
    
    # Valores
    'valor': 'R$ 5.000,00',
    'espec_pagto': 'Lipoaspiração de abdômen e flancos',
    'xx_parcelas_de_R$_yyyy,yy': '3 parcelas de R$ 1.666,67',
    'xx_restante_de_R$_yyyy,yy': 'Sem restante após assinatura',
    
    # Procedimentos (expandir conforme necessário)
    'procedimento_1': 'Lipoaspiração de abdômen e flancos',
    'procedimento_1_descricao': 'Remoção de gordura localizada usando técnica de lipoaspiração tumescente',
    'procedimento_1_imagem': 'https://example.com/procedimento-1.jpg',
}

print(f"\nDados carregados: {len(dados_contrato)} campos")
print("\nExemplos:")
for key, value in list(dados_contrato.items())[:5]:
    print(f"  {key}: {value}")

try:
    replacer = PDFPlaceholderReplacer('contrato-medico-04.pdf')
    
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


# ============================================================================
# CENÁRIO 2: Dados vindo de um banco de dados (PostgreSQL)
# ============================================================================

print("\n" + "="*80)
print("CENÁRIO 2: Dados vindo do banco de dados")
print("="*80)

print("""
# Exemplo de query SQL para buscar dados:

query = '''
    SELECT 
        -- Clínica
        c.nome as clinica_nome,
        c.cpf_cnpj as clinica_cpf_cnpj,
        c.celular as clinica_celular,
        c.email as clinica_email,
        c.endereco_linha1 as clinica_endereco_linha1,
        c.endereco_linha2 as clinica_endereco_linha2,
        
        -- Paciente
        p.nome as paciente_nome,
        p.cpf as paciente_cpf,
        p.celular as paciente_celular,
        p.email as paciente_email,
        p.endereco_linha1 as paciente_endereco_linha1,
        p.endereco_linha2 as paciente_endereco_linha2,
        
        -- Contrato
        con.data_contrato,
        con.valor_total,
        con.forma_pagamento,
        
        -- Procedimento
        STRING_AGG(proc.nome, ', ') as procedimentos
    FROM contratos con
    LEFT JOIN clinicas c ON con.clinica_id = c.id
    LEFT JOIN pacientes p ON con.paciente_id = p.id
    LEFT JOIN contrato_itens ci ON con.id = ci.contrato_id
    LEFT JOIN procedimentos proc ON ci.procedimento_id = proc.id
    WHERE con.id = %s
    GROUP BY con.id, c.id, p.id
'''

# Executar query
cursor.execute(query, (contract_id,))
db_row = cursor.fetchone()

# Converter resultado para dicionário
db_data = {
    'clinica_nome': db_row['clinica_nome'],
    'clinica_cpf_cnpj': db_row['clinica_cpf_cnpj'],
    'clinica_celular': db_row['clinica_celular'],
    # ... etc
}

# Mapear para placeholders
mapper = DatabaseToDataMapper()
placeholder_data = mapper.map_db_to_placeholders(db_data)

# Gerar PDF
replacer = PDFPlaceholderReplacer('templates/contrato-medico-04.pdf')
pdf_bytes = replacer.replace_and_get_pdf(placeholder_data)
""")


# ============================================================================
# CENÁRIO 3: JSON do cliente (API request)
# ============================================================================

print("\n" + "="*80)
print("CENÁRIO 3: Dados vindo de um JSON (API request)")
print("="*80)

# Simular JSON vindo do frontend/API
request_json = {
    "template_id": "contrato-medico-04",
    "clinica": {
        "nome": "Dra. Maria Silva - Clínica Estética Premium",
        "cpf_cnpj": "12.345.678/0001-90",
        "celular": "(21) 99999-8888",
        "email": "contato@clinicamaria.com.br",
        "endereco": "Avenida Paulista, 1000",
        "endereco2": "São Paulo, SP 01311-100"
    },
    "paciente": {
        "nome": "Ana Costa Silva",
        "cpf": "987.654.321-00",
        "celular": "(21) 98765-4321",
        "email": "ana.costa@example.com",
        "endereco": "Rua Copacabana, 500",
        "endereco2": "Rio de Janeiro, RJ 20040-020"
    },
    "contrato": {
        "data": "15/01/2026",
        "valor_total": "8000.00",
        "forma_pagamento": "cartao_credito",
        "parcelas": 4
    },
    "procedimento": "Abdominoplastia com lipoaspiração"
}

# Converter JSON para formato de placeholder
dados_api = {
    'nome_da_medica_ou_clinica': request_json['clinica']['nome'],
    'cpfcnpjmedicacli': request_json['clinica']['cpf_cnpj'],
    'celmedicacli': request_json['clinica']['celular'],
    'emailmedicacli': request_json['clinica']['email'],
    'enderecomedical': request_json['clinica']['endereco'],
    'enderecomedica2': request_json['clinica']['endereco2'],
    
    'nome_paciente': request_json['paciente']['nome'],
    'cpfpaciente': request_json['paciente']['cpf'],
    'celpaciente': request_json['paciente']['celular'],
    'emailpaciente': request_json['paciente']['email'],
    'enderecopacientel': request_json['paciente']['endereco'],
    'enderecopaciente2': request_json['paciente']['endereco2'],
    
    'DD/MM/AAAA': request_json['contrato']['data'],
    'valor': f"R$ {request_json['contrato']['valor_total']}",
    'xx_parcelas_de_R$_yyyy,yy': f"{request_json['contrato']['parcelas']} parcelas",
    
    'espec_pagto': request_json['procedimento'],
}

print(f"\nJSON recebido com {len(dados_api)} campos")
print("Dados mapeados para placeholders")


# ============================================================================
# CENÁRIO 4: Integração com API NestJS
# ============================================================================

print("\n" + "="*80)
print("CENÁRIO 4: Integração com NestJS API")
print("="*80)

print("""
# Em seu controller NestJS (TypeScript):

@Post('contracts/generate-pdf')
async generatePDF(@Body() request: ContractRequest) {
    try {
        // 1. Buscar dados do banco
        const contractData = await this.contractService.getContractData(
            request.contract_id
        );
        
        // 2. Chamar serviço Python
        const pdfBytes = await this.pdfService.generatePDF({
            template_id: request.template_id,
            client_data: contractData
        });
        
        // 3. Salvar em S3
        const s3Url = await this.s3Service.uploadPDF(
            pdfBytes,
            request.contract_id
        );
        
        // 4. Atualizar banco de dados
        await this.contractService.updatePdfUrl(
            request.contract_id,
            s3Url
        );
        
        // 5. Se configurado, enviar para assinatura
        if (request.send_for_signature) {
            const signatureResult = await this.signatureService.send(
                s3Url,
                request.signer_email,
                request.signer_name
            );
            
            await this.contractService.updateSignatureId(
                request.contract_id,
                signatureResult.request_id
            );
        }
        
        return {
            success: true,
            contract_id: request.contract_id,
            pdf_url: s3Url,
            signature_request_id: signatureResult?.request_id
        };
    } catch (error) {
        throw new BadRequestException(error.message);
    }
}

# Request body:
{
    "contract_id": "uuid-here",
    "template_id": "contrato-medico-04",
    "send_for_signature": true,
    "signer_email": "paciente@example.com",
    "signer_name": "João Silva"
}
""")


# ============================================================================
# CENÁRIO 5: Processamento em lote (batch)
# ============================================================================

print("\n" + "="*80)
print("CENÁRIO 5: Gerar múltiplos PDFs em paralelo")
print("="*80)

print("""
import concurrent.futures
from typing import List

def generate_batch_pdfs(contracts: List[Dict]) -> List[Dict]:
    '''
    Gera múltiplos PDFs em paralelo usando ThreadPoolExecutor
    Muito mais rápido que sequencial
    '''
    replacer = PDFPlaceholderReplacer('templates/contrato-medico-04.pdf')
    results = []
    
    def generate_one(contract_data):
        try:
            pdf_bytes = replacer.replace_and_get_pdf(contract_data)
            return {
                'contract_id': contract_data['contract_id'],
                'success': True,
                'pdf_bytes': pdf_bytes,
                'size_kb': len(pdf_bytes) / 1024
            }
        except Exception as e:
            return {
                'contract_id': contract_data['contract_id'],
                'success': False,
                'error': str(e)
            }
    
    # Usar ThreadPoolExecutor para paralelismo
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(generate_one, contract)
            for contract in contracts
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    return results


# Exemplo de uso:
contracts_to_generate = [
    {'contract_id': '1', 'nome_paciente': 'João', ...},
    {'contract_id': '2', 'nome_paciente': 'Maria', ...},
    {'contract_id': '3', 'nome_paciente': 'Pedro', ...},
    # ... até 100+ contratos
]

results = generate_batch_pdfs(contracts_to_generate)

successful = sum(1 for r in results if r['success'])
failed = sum(1 for r in results if not r['success'])

print(f"✓ Gerados com sucesso: {successful}")
print(f"✗ Falharam: {failed}")
""")


# ============================================================================
# RESUMO
# ============================================================================

print("\n" + "="*80)
print("RESUMO: Como usar o sistema")
print("="*80)

print("""
PASSO 1: Extrair placeholders do template
├─ replacer = PDFPlaceholderReplacer('template.pdf')
└─ placeholders = replacer.extract_placeholders()

PASSO 2: Validar dados antes de gerar
├─ is_valid, missing, extras = replacer.validate_data(dados)
└─ Se válido, prosseguir com geração

PASSO 3: Gerar PDF
├─ pdf_bytes = replacer.replace_and_get_pdf(dados)
└─ Retorna PDF em bytes (pronto para S3, email, etc)

PASSO 4: Opções pós-geração
├─ A) Salvar em S3: s3.upload(pdf_bytes)
├─ B) Enviar para email: send_email(pdf_bytes)
├─ C) Enviar para assinatura: docusign_api.send(pdf_url)
└─ D) Retornar ao cliente: return send_file(pdf_bytes)

DADOS VINDO DE:
├─ Banco de dados (PostgreSQL, MySQL, etc)
├─ JSON (API request)
├─ Planilha (Excel, CSV)
└─ Formulário (web form)

PERFORMANCE:
├─ Um PDF: 0.5-1s
├─ 10 PDFs: 5-10s
├─ 100 PDFs: 50-100s (com paralelismo)
└─ 1000 PDFs: Adicionar Redis cache + async jobs

SEGURANÇA:
├─ Validar dados antes de substituir
├─ Nunca confiar em dados do usuário
├─ Usar prepared statements (SQL injection)
├─ Salvar PDFs em S3 (não no servidor)
└─ Logs de auditoria (quem gerou, quando, para quem)
""")
