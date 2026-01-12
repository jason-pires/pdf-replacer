# placeholders_valores_completo.py
# Dicionário com TODOS os placeholders do PDF
# Baseado em análise do Contrato_Medico-04_procedimentos_teste.pdf

placeholders_valores = {
    # ========================================================================
    # DATA
    # ========================================================================
    "{dd}": "15",
    "{mmm}": "JAN",
    "{aaaa}": "2026",
    
    # ========================================================================
    # CLÍNICA / PROFISSIONAL
    # ========================================================================
    "{nome_da_medica_ou_clinica}": "Clínica Estética Silva",
    "{cpfcnpjmedicacli}": "12.345.678/0001-90",
    "{emailmedicacli}": "clinica@estética.com.br",
    "{celmedicacli}": "(11) 3456-7890",
    "{enderecomedica1}": "Avenida Paulista, 1000",
    "{enderecomedica2}": "São Paulo - SP - 01311-100",
    
    # ========================================================================
    # PACIENTE
    # ========================================================================
    "{nome_paciente}": "João Pedro Santos Silva",
    "{cpfpaciente}": "123.456.789-00",
    "{emailpaciente}": "joao.santos@email.com",
    "{celpaciente}": "(11) 98765-4321",
    "{enderecopaciente1}": "Rua das Flores, 123",
    "{enderecopaciente2}": "São Paulo - SP - 01234-567",
    
    # ========================================================================
    # PROCEDIMENTO 1
    # ========================================================================
    "{procedimento_1}": "Limpeza de Pele Profunda",
    "{procedimento_1_imagem}": "[Imagem do procedimento 1]",
    
    # ========================================================================
    # PROCEDIMENTO 2 - MICROAGULHAGEM COM RF
    # ========================================================================
    "{procedimento_2}": "Microagulhagem com RF",
    "{procedimento_2_descricao1}": "Procedimento de rejuvenescimento facial com radiofrequência",
    "{procedimento_2_descricao2}": "Firmeza, lift e colágeno - sem tempo de inatividade",
    "{procedimento_2_descricao3}": "Resultados visíveis em 30 dias - 4 sessões recomendadas",
    
    # ========================================================================
    # PROCEDIMENTO 3 - PEELING QUÍMICO
    # ========================================================================
    "{procedimento_3}": "Peeling Químico",
    "{procedimento_3_descricao1}": "Renovação de pele com ácidos profissionais",
    "{procedimento_3_descricao2}": "Elimina manchas, acne e rugas superficiais",
    "{procedimento_3_descricao3}": "Protocolos personalizados conforme tipo de pele",
    
    # ========================================================================
    # PAGAMENTO - PÁGINA 2
    # ========================================================================
    "{DD/MM/AAAA}": "VENCIMENTO DIA 15/01/2026",
    "{valor}": "5.000,00",
    "{espec_pagto}": "Cartão de Crédito",
    
    # ========================================================================
    # PARCELAMENTO
    # ========================================================================
    "{xx_parcelas_de_RS_yyyyyy}": "3 parcelas de R$ 1.666,67",
    "{xx_restantes_de_RS_yyyyyy}": "Saldo de R$ 1.000,00 a vencer",
}

# ============================================================================
# INFORMAÇÕES SOBRE O DICIONÁRIO
# ============================================================================

"""
Total de placeholders: 32

Distribuição por página:
- Página 1: 27 placeholders (data, clínica, paciente, procedimentos)
- Página 2: 5 placeholders (pagamento)
- Página 3: 0 placeholders (assinatura/certificado)

Categorias:
- Data: 3 placeholders
- Clínica/Profissional: 6 placeholders
- Paciente: 6 placeholders
- Procedimento 1: 2 placeholders
- Procedimento 2: 4 placeholders
- Procedimento 3: 3 placeholders
- Pagamento: 5 placeholders

Notas:
1. Placeholders com espaços mantêm o padrão {nome           }
2. Valores inseridos respeitam o tamanho dos campos
3. Campos com CPF/CNPJ usam formato brasileiro
4. Campos com email/telefone usam exemplos realistas
5. Valores monetários seguem padrão brasileiro (R$ e virgula)
6. Descrições de procedimentos são descritivas e profissionais
"""
