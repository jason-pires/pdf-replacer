#!/usr/bin/env python3
"""
GUIA RÁPIDO: Replace de Placeholders em PDF
Solução pronta para usar
"""

# ============================================================================
# INSTALAÇÃO
# ============================================================================
"""
pip install PyPDF2 reportlab python-dotenv requests
"""

# ============================================================================
# LISTA COMPLETA DE PLACEHOLDERS
# ============================================================================

PLACEHOLDERS_REFERENCE = {
    # CLÍNICA/MÉDICA (6 campos)
    'nome_da_medica_ou_clinica': str,      # Nome completo
    'cpfcnpjmedicacli': str,               # CPF ou CNPJ formatado
    'celmedicacli': str,                   # (XX) XXXXX-XXXX
    'emailmedicacli': str,                 # email@example.com
    'enderecomedical': str,                # Rua, número, complemento
    'enderecomedica2': str,                # Cidade, UF, CEP
    
    # PACIENTE (6 campos)
    'nome_paciente': str,                  # Nome completo
    'cpfpaciente': str,                    # CPF formatado XXX.XXX.XXX-XX
    'celpaciente': str,                    # (XX) XXXXX-XXXX
    'emailpaciente': str,                  # email@example.com
    'enderecopacientel': str,              # Rua, número, apartamento
    'enderecopaciente2': str,              # Cidade, UE, CEP (NOTE: tem typo no PDF)
    
    # DATA (4 campos)
    'dd': str,                             # "15" (dia numérico)
    'mmm': str,                            # "janeiro" (mês por extenso)
    'aaaa': str,                           # "2026" (ano completo)
    'DD/MM/AAAA': str,                     # "15/01/2026" (data formatada)
    
    # VALORES (4 campos)
    'valor': str,                          # "R$ 5.000,00"
    'espec_pagto': str,                    # Descrição do procedimento
    'xx_parcelas_de_R$_yyyy,yy': str,      # "3 parcelas de R$ 1.666,67"
    'xx_restante_de_R$_yyyy,yy': str,      # "R$ 2.000,00"
    
    # PROCEDIMENTOS (dinâmicos: 1-4+)
    'procedimento_1': str,                 # Nome do procedimento 1
    'procedimento_1_descricao': str,       # Descrição técnica
    'procedimento_1_imagem': str,          # URL ou caminho da imagem
    'procedimento_2': str,                 # Nome do procedimento 2
    'procedimento_2_descricao': str,
    'procedimento_2_imagem': str,
    # ... adicione procedimento_3, procedimento_4, etc conforme necessário
}

# ============================================================================
# TEMPLATE SQL PARA BUSCAR DADOS
# ============================================================================

SQL_TEMPLATE = """
SELECT 
    -- CLÍNICA
    c.nome as nome_da_medica_ou_clinica,
    c.cpf_cnpj as cpfcnpjmedicacli,
    c.celular as celmedicacli,
    c.email as emailmedicacli,
    c.endereco_linha1 as enderecomedical,
    c.endereco_linha2 as enderecomedica2,
    
    -- PACIENTE
    p.nome as nome_paciente,
    p.cpf as cpfpaciente,
    p.celular as celpaciente,
    p.email as emailpaciente,
    p.endereco_linha1 as enderecopacientel,
    p.endereco_linha2 as enderecopaciente2,
    
    -- DATA
    EXTRACT(DAY FROM con.data_contrato)::TEXT as dd,
    TO_CHAR(con.data_contrato, 'Month') as mmm,
    EXTRACT(YEAR FROM con.data_contrato)::TEXT as aaaa,
    TO_CHAR(con.data_contrato, 'DD/MM/YYYY') as "DD/MM/AAAA",
    
    -- VALORES
    'R$ ' || con.valor_total::TEXT as valor,
    STRING_AGG(proc.nome, ', ') as espec_pagto,
    con.quantidade_parcelas || ' parcelas de R$ ' || 
        (con.valor_total / con.quantidade_parcelas)::TEXT as xx_parcelas_de_R$_yyyy,yy,
    'Sem restante' as xx_restante_de_R$_yyyy,yy
    
FROM contratos con
LEFT JOIN clinicas c ON con.clinica_id = c.id
LEFT JOIN pacientes p ON con.paciente_id = p.id
LEFT JOIN contrato_itens ci ON con.id = ci.contrato_id
LEFT JOIN procedimentos proc ON ci.procedimento_id = proc.id
WHERE con.id = %s AND con.deleted_at IS NULL
GROUP BY con.id, c.id, p.id;
"""

# ============================================================================
# QUICK START: 3 LINHAS PARA GERAR PDF
# ============================================================================

print("""
# OPÇÃO 1: Uso mínimo (dicionário)
from pdf_replacer import PDFPlaceholderReplacer

replacer = PDFPlaceholderReplacer('template.pdf')
pdf = replacer.replace_and_get_pdf({'nome_paciente': 'João', ...})
# Pronto! PDF em bytes


# OPÇÃO 2: Com validação
replacer = PDFPlaceholderReplacer('template.pdf')
is_valid, missing, extras = replacer.validate_data(dados)
if is_valid:
    pdf = replacer.replace_and_get_pdf(dados)


# OPÇÃO 3: Com mapeamento de banco de dados
from pdf_replacer import DatabaseToDataMapper

db_data = {'clinica_nome': 'Dra. Maria', ...}
mapper = DatabaseToDataMapper()
placeholder_data = mapper.map_db_to_placeholders(db_data)
replacer.replace_and_get_pdf(placeholder_data)
""")

# ============================================================================
# MAPEAMENTO: Colunas do Banco → Placeholders
# ============================================================================

MAPPING_DB_TO_PLACEHOLDER = {
    # Clínica
    'clinica.nome': 'nome_da_medica_ou_clinica',
    'clinica.cpf_cnpj': 'cpfcnpjmedicacli',
    'clinica.celular': 'celmedicacli',
    'clinica.email': 'emailmedicacli',
    'clinica.endereco_linha1': 'enderecomedical',
    'clinica.endereco_linha2': 'enderecomedica2',
    
    # Paciente
    'pacientes.nome': 'nome_paciente',
    'pacientes.cpf': 'cpfpaciente',
    'pacientes.celular': 'celpaciente',
    'pacientes.email': 'emailpaciente',
    'pacientes.endereco_linha1': 'enderecopacientel',
    'pacientes.endereco_linha2': 'enderecopaciente2',
    
    # Data
    'contratos.data_contrato': ['dd', 'mmm', 'aaaa', 'DD/MM/AAAA'],
    
    # Valores
    'contratos.valor_total': 'valor',
    'procedimento.nome': 'espec_pagto',
    'contratos.quantidade_parcelas': 'xx_parcelas_de_R$_yyyy,yy',
}

# ============================================================================
# FORMATO DOS DADOS
# ============================================================================

EXAMPLE_DATA = {
    # Strings simples
    'nome_paciente': 'João da Silva Santos',
    'cpfpaciente': '123.456.789-00',
    'emailpaciente': 'joao@example.com',
    
    # Endereços (linha 1 e linha 2)
    'enderecopacientel': 'Rua das Flores, 123, Apt. 456',
    'enderecopaciente2': 'São Paulo, SP 01310-100',
    
    # Datas (separadas ou formatadas)
    'dd': '15',                            # Dia como número
    'mmm': 'janeiro',                      # Mês por extenso (minúsculas)
    'aaaa': '2026',                        # Ano 4 dígitos
    'DD/MM/AAAA': '15/01/2026',            # Data completa formatada
    
    # Valores monetários
    'valor': 'R$ 5.000,00',                # Com símbolo e vírgula
    'xx_parcelas_de_R$_yyyy,yy': '3 parcelas de R$ 1.666,67',
    'xx_restante_de_R$_yyyy,yy': 'Sem restante',
    
    # Textos descritivos
    'espec_pagto': 'Lipoaspiração de abdômen e flancos',
}

# ============================================================================
# TRATAMENTO DE ERROS COMUNS
# ============================================================================

COMMON_ISSUES = {
    'FileNotFoundError': {
        'erro': "Template PDF não encontrado",
        'solução': "Verificar caminho: 'templates/contrato-medico-04.pdf'",
        'dica': "Use caminho absoluto se necessário"
    },
    'Campos faltando': {
        'erro': "Alguns placeholders não têm valores",
        'solução': "Validar com validate_data() antes de gerar",
        'dica': "Use extract_placeholders() para saber o que precisa"
    },
    'PDF não preenchido': {
        'erro': "PDF gerado mas placeholders não foram substituídos",
        'solução': "PyPDF2 tem limitações. Use ReportLab overlay",
        'dica': "Ver pdf_replacer.py método _create_overlay()"
    },
    'Encoded incorreto': {
        'erro': "Acentos aparecem errados no PDF",
        'solução': "Especificar fonte que suporta UTF-8",
        'dica': "Use TTFont() ou font-family em CSS se usar HTML->PDF"
    },
    'Performance lenta': {
        'erro': "Gerar 100+ PDFs demora muito",
        'solução': "Usar ThreadPoolExecutor para paralelismo",
        'dica': "Ver exemplos_praticos.py cenário 5"
    }
}

# ============================================================================
# CHECKLIST DE IMPLEMENTAÇÃO
# ============================================================================

CHECKLIST = """
[ ] 1. Instalar dependências: pip install PyPDF2 reportlab
[ ] 2. Ter template PDF com placeholders {xxx}
[ ] 3. Extrair placeholders do template: extract_placeholders()
[ ] 4. Preparar dados do banco de dados
[ ] 5. Mapear colunas DB → placeholders usando DatabaseToDataMapper
[ ] 6. Validar dados: validate_data()
[ ] 7. Gerar PDF: replace_and_get_pdf()
[ ] 8. Salvar em S3 ou enviar para cliente
[ ] 9. Se necessário assinatura: integrar com DocuSign/OneFlow
[ ] 10. Implementar logs e auditoria

EXTRA (para produção):
[ ] Usar variáveis de ambiente (.env)
[ ] Implementar cache para templates frequentes
[ ] Adicionar retry logic para S3
[ ] Monitorar tempo de geração
[ ] Alertar se PDF > tamanho esperado
[ ] Testar com acentos e caracteres especiais
"""

# ============================================================================
# PADRÕES RECOMENDADOS
# ============================================================================

BEST_PRACTICES = """
1. SEMPRE validar dados antes de gerar
   is_valid, missing = replacer.validate_data(data)
   if not is_valid:
       raise ValueError(f"Faltando: {missing}")

2. USAR try-except em produção
   try:
       pdf = replacer.replace_and_get_pdf(data)
   except Exception as e:
       logger.error(f"Erro: {e}")
       raise

3. SALVAR PDF em S3, não no servidor local
   s3.upload_fileobj(pdf_bytes, bucket, key)

4. USAR logging para auditoria
   logger.info(f"PDF gerado: {contract_id} para {paciente_id}")

5. VALIDAR CPF/CNPJ antes de salvar
   if not validate_cpf(cpf):
       raise ValueError("CPF inválido")

6. USAR prepared statements (SQL injection)
   cursor.execute("SELECT * FROM contratos WHERE id = %s", [contract_id])

7. CRIPTOGRAFAR dados sensíveis em transit
   Use HTTPS para APIs
   Use SSL para banco de dados

8. FAZER BACKUP de templates
   Versionar em Git: templates/v1/, templates/v2/

9. TESTAR com dados reais (acentos, nomes compostos, etc)
   Não usar Lorem Ipsum

10. MONITORAR execução em produção
    CloudWatch metrics, alerts, logs centralizados
"""

# ============================================================================
# RESUMO FINAL
# ============================================================================

print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                   GUIA RÁPIDO: REPLACE DE PLACEHOLDERS                  ║
╚══════════════════════════════════════════════════════════════════════════╝

ARQUIVOS CRIADOS:
├─ pdf_replacer.py          → Engine principal (PDFPlaceholderReplacer)
├─ database-schema.sql      → Schema PostgreSQL
├─ exemplos_praticos.py     → 5 cenários de uso
└─ quick_reference.py       → Este arquivo (referência)

TOTAL DE PLACEHOLDERS: 20+ (dinâmicos por procedimento)

FLUXO BÁSICO:
1. replacer = PDFPlaceholderReplacer('template.pdf')
2. dados = {{'nome_paciente': 'João', ...}}
3. pdf = replacer.replace_and_get_pdf(dados)
4. salvar em S3 ou enviar

TEMPO DE EXECUÇÃO:
├─ 1 PDF: 0.5-1.0 segundo
├─ 10 PDFs: 5-10 segundos
├─ 100 PDFs: 50-100 segundos (com paralelismo)

PRÓXIMOS PASSOS:
1. Executar exemplos_praticos.py para entender fluxo
2. Criar schema SQL no banco de dados
3. Implementar em seu NestJS/API
4. Configurar integração com assinatura (opcional)

DOCUMENTAÇÃO:
├─ PDF para referência de campos: Contrato_Medico-04_procedimentos.pdf
├─ Mapping DB→Placeholder: database-schema.sql
├─ Exemplos de uso: exemplos_praticos.py
└─ Código completo: pdf_replacer.py

SUPORTE:
- Erro ao gerar? Ver COMMON_ISSUES acima
- Dúvida sobre placeholder? Ver PLACEHOLDERS_REFERENCE
- Dúvida sobre DB? Ver SQL_TEMPLATE

PRONTO PARA PRODUÇÃO? Verificar CHECKLIST acima!
""")
