"""
RESUMO VISUAL: PLACEHOLDERS DO CONTRATO MEDICO-04

Documento analisado: Contrato_Medico-04_procedimentos.pdf
Total de placeholders encontrados: 20 (+ dinâmicos por procedimento)
"""

# ============================================================================
# VISÃO GERAL: SEÇÕES E CAMPOS
# ============================================================================

CONTRATOS_LAYOUT = """
┌─────────────────────────────────────────────────────────────────────────┐
│                    CABEÇALHO - DADOS DA CLÍNICA/MÉDICA                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  MÉDICA/CLÍNICA CONTRATADA                                            │
│  {nome_da_medica_ou_clinica}                                          │
│  {cpfcnpjmedicacli}                                                    │
│  {celmedicacli}  |  {emailmedicacli}                                   │
│  {enderecomedical}                                                      │
│  {enderecomedica2}                                                      │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                  PACIENTE/CONTRATANTE                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  {nome_paciente}                                                        │
│  CPF: {cpfpaciente}  |  Celular: {celpaciente}                         │
│  Email: {emailpaciente}                                                 │
│  {enderecopacientel}                                                     │
│  {enderecopaciente2}                                                     │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│           PROCEDIMENTOS CONTRATADOS (repetido para cada um)             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Procedimento: {procedimento_1}                                        │
│  Imagem: {procedimento_1_imagem}                                       │
│  Descrição: {procedimento_1_descricao}                                 │
│  [VER TERMO DE CONSENTIMENTO]                                          │
│                                                                         │
│  Procedimento: {procedimento_2}                                        │
│  Imagem: {procedimento_2_imagem}                                       │
│  Descrição: {procedimento_2_descricao}                                 │
│  [VER TERMO DE CONSENTIMENTO]                                          │
│                                                                         │
│  (... continua até 4+ procedimentos)                                   │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                   DATA E ASSINATURA                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Resende, {dd} de {mmm} de {aaaa}                                       │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                    VALORES E PAGAMENTO                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Descrição: {espec_pagto}                                              │
│  Valor Total: {valor}                                                   │
│                                                                         │
│  Forma de Pagamento: {xx_parcelas_de_R$_yyyy,yy}                       │
│  Saldo Restante: {xx_restante_de_R$_yyyy,yy}                           │
│                                                                         │
│  Vencimento: {DD/MM/AAAA}                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
"""

# ============================================================================
# MATRIZ DE PLACEHOLDERS POR CATEGORIA
# ============================================================================

PLACEHOLDERS_BY_CATEGORY = {
    "CLÍNICA/MÉDICA (6 campos)": {
        "{nome_da_medica_ou_clinica}": "Nome da clínica ou médica responsável",
        "{cpfcnpjmedicacli}": "CPF ou CNPJ (formatado ou não)",
        "{celmedicacli}": "Telefone celular da clínica",
        "{emailmedicacli}": "Email de contato da clínica",
        "{enderecomedical}": "Endereço linha 1 (rua, número, complemento)",
        "{enderecomedica2}": "Endereço linha 2 (cidade, UF, CEP)",
    },
    
    "PACIENTE (6 campos)": {
        "{nome_paciente}": "Nome completo do paciente",
        "{cpfpaciente}": "CPF formatado ou não",
        "{celpaciente}": "Telefone celular do paciente",
        "{emailpaciente}": "Email do paciente",
        "{enderecopacientel}": "Endereço linha 1 (com typo no original 'pacientel')",
        "{enderecopaciente2)": "Endereço linha 2 (tem parêntese sobrando no original)",
    },
    
    "DATA DO CONTRATO (4 campos)": {
        "{dd}": "Dia do mês (numérico: 01-31)",
        "{mmm}": "Mês por extenso (janeiro, fevereiro, etc)",
        "{aaaa}": "Ano completo (2026, 2027, etc)",
        "{DD/MM/AAAA}": "Data completa formatada (15/01/2026)",
    },
    
    "VALORES E PAGAMENTO (4 campos)": {
        "{valor}": "Valor total do contrato (R$ 5.000,00)",
        "{espec_pagto}": "Especificação/descrição do pagamento ou procedimento",
        "{xx_parcelas_de_R$_yyyy,yy}": "Descrição das parcelas (3 parcelas de R$ 1.666,67)",
        "{xx_restante_de_R$_yyyy,yy}": "Descrição do saldo restante ou restante",
    },
    
    "PROCEDIMENTOS (DINÂMICOS - pode ser 1-4+ campos cada)": {
        "{procedimento_1}": "Nome do 1º procedimento",
        "{procedimento_1_imagem}": "Imagem/foto do 1º procedimento",
        "{procedimento_1_descricao}": "Descrição técnica do 1º procedimento",
        "{procedimento_2}": "Nome do 2º procedimento (se houver)",
        "{procedimento_2_imagem}": "Imagem do 2º procedimento",
        "{procedimento_2_descricao}": "Descrição do 2º procedimento",
        "...": "Adicione procedimento_3, procedimento_4, etc conforme necessário",
    }
}

# ============================================================================
# EXEMPLOS DE VALORES PARA CADA PLACEHOLDER
# ============================================================================

EXAMPLES_BY_FIELD = {
    "{nome_da_medica_ou_clinica}": [
        "Dra. Maria Silva",
        "Dr. João Carlos - Clínica Estética",
        "Centro de Estética e Bem-estar Premium",
    ],
    
    "{cpfcnpjmedicacli}": [
        "12.345.678/0001-90",  # CNPJ
        "123.456.789-00",      # CPF
    ],
    
    "{celmedicacli}": [
        "(11) 99999-8888",
        "(21) 98765-4321",
        "+55 11 99999-8888",
    ],
    
    "{emailmedicacli}": [
        "clinica@example.com",
        "contato@clinica.com.br",
        "atendimento@estética.med.br",
    ],
    
    "{enderecomedical}": [
        "Avenida Paulista, 1000 - Sala 3000",
        "Rua das Flores, 123 - Bloco A",
        "Av. Brasil, 500 - Centro Médico",
    ],
    
    "{enderecomedica2}": [
        "São Paulo, SP 01311-100",
        "Rio de Janeiro, RJ 20040-020",
        "Belo Horizonte, MG 30130-100",
    ],
    
    "{nome_paciente}": [
        "João da Silva Santos",
        "Maria Clara de Oliveira",
        "Pedro Roberto Costa",
    ],
    
    "{cpfpaciente}": [
        "123.456.789-00",
        "987.654.321-00",
    ],
    
    "{celpaciente}": [
        "(11) 98765-4321",
        "(21) 99999-8888",
    ],
    
    "{emailpaciente}": [
        "joao@example.com",
        "maria.silva@empresa.com.br",
    ],
    
    "{enderecopacientel}": [
        "Rua das Flores, 123 - Apartamento 456",
        "Avenida Atlântica, 500 - Sala 200",
        "Rua Principal, 999 - Casa 1",
    ],
    
    "{enderecopaciente2}": [  # Note: tem typo no original
        "São Paulo, SP 01310-100",
        "Rio de Janeiro, RJ 22040-020",
    ],
    
    "{dd}": [
        "01", "15", "31",
    ],
    
    "{mmm}": [
        "janeiro",
        "fevereiro",
        "dezembro",
    ],
    
    "{aaaa}": [
        "2025",
        "2026",
        "2027",
    ],
    
    "{DD/MM/AAAA}": [
        "15/01/2026",
        "01/12/2025",
        "31/12/2027",
    ],
    
    "{valor}": [
        "R$ 5.000,00",
        "R$ 10.500,50",
        "R$ 2.999,99",
    ],
    
    "{espec_pagto}": [
        "Lipoaspiração de abdômen",
        "Abdominoplastia com lipoaspiração",
        "Rinoplastia fechada",
        "Cirurgia de aumento de glúteos com enxerto",
    ],
    
    "{xx_parcelas_de_R$_yyyy,yy}": [
        "1 parcela de R$ 5.000,00",
        "3 parcelas de R$ 1.666,67",
        "4 parcelas de R$ 2.500,00",
        "12 parcelas de R$ 416,67",
    ],
    
    "{xx_restante_de_R$_yyyy,yy}": [
        "Sem restante",
        "R$ 500,00",
        "Primeira parcela na assinatura",
    ],
    
    "{procedimento_1}": [
        "Lipoaspiração",
        "Abdominoplastia",
        "Rinoplastia",
        "Aumento de glúteos",
    ],
}

# ============================================================================
# CHECKLIST DE PREENCHIMENTO
# ============================================================================

PREENCHIMENTO_CHECKLIST = """
✓ CLÍNICA (6 campos)
  ├─ [ ] nome_da_medica_ou_clinica
  ├─ [ ] cpfcnpjmedicacli
  ├─ [ ] celmedicacli
  ├─ [ ] emailmedicacli
  ├─ [ ] enderecomedical
  └─ [ ] enderecomedica2

✓ PACIENTE (6 campos)
  ├─ [ ] nome_paciente
  ├─ [ ] cpfpaciente
  ├─ [ ] celpaciente
  ├─ [ ] emailpaciente
  ├─ [ ] enderecopacientel
  └─ [ ] enderecopaciente2

✓ DATA (4 campos - todas necessárias)
  ├─ [ ] dd
  ├─ [ ] mmm
  ├─ [ ] aaaa
  └─ [ ] DD/MM/AAAA

✓ VALORES (4 campos)
  ├─ [ ] valor
  ├─ [ ] espec_pagto
  ├─ [ ] xx_parcelas_de_R$_yyyy,yy
  └─ [ ] xx_restante_de_R$_yyyy,yy

✓ PROCEDIMENTOS (repita para cada procedimento)
  ├─ [ ] procedimento_1
  ├─ [ ] procedimento_1_imagem
  ├─ [ ] procedimento_1_descricao
  ├─ [ ] procedimento_2
  ├─ [ ] procedimento_2_imagem
  ├─ [ ] procedimento_2_descricao
  └─ [ ] ... (adicione procedimento_3, procedimento_4, etc)

TOTAL MÍNIMO: 20 campos
COM 1 PROCEDIMENTO: 23 campos
COM 2 PROCEDIMENTOS: 26 campos
COM 4 PROCEDIMENTOS: 32 campos
"""

# ============================================================================
# ERROS COMUNS E COMO CORRIGIR
# ============================================================================

COMMON_ERRORS = {
    "Placeholder não foi substituído no PDF": {
        "causa": "Nome do placeholder diferente entre código e PDF",
        "solução": "Usar extract_placeholders() para descobrir nomes exatos",
        "exemplo": 
            "❌ {endereco_paciente} não existe"
            "✅ {enderecopacientel} é o correto (tem typo!)"
    },
    
    "Erro: Campo obrigatório faltando": {
        "causa": "Um dos 20 campos obrigatórios não foi fornecido",
        "solução": "Ver checklist acima, preencher todos os campos",
        "dica": "Usar validate_data() para encontrar qual falta"
    },
    
    "Acentos aparecem errados": {
        "causa": "Encoding UTF-8 não configurado",
        "solução": "Especificar charset='utf-8' ao abrir arquivo",
        "código": "open('arquivo.pdf', 'rb', encoding='utf-8')"
    },
    
    "Data em formato errado": {
        "causa": "Colocar '2026' em {dd} ao invés de '15'",
        "solução": "Separar components: dia, mês (nome), ano",
        "exemplo": {
            "❌ dd='15/01/2026'",
            "✅ dd='15', mmm='janeiro', aaaa='2026'",
        }
    },
    
    "Telefone sem formatação": {
        "causa": "Salvar '11987654321' ao invés de '(11) 98765-4321'",
        "solução": "Formatar antes de substituir",
        "codigo": "def format_phone(p): return f'({p[:2]}) {p[2:7]}-{p[7:]}'",
    }
}

# ============================================================================
# RESUMO EXECUTIVO
# ============================================================================

print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                    CONTRATO MÉDICO-04: PLACEHOLDERS                     ║
║                           (RESUMO VISUAL)                               ║
╚══════════════════════════════════════════════════════════════════════════╝

ENCONTRADOS: 20 campos fixos + n procedimentos (dinâmicos)

DISTRIBUIÇÃO:
├─ CLÍNICA:     6 campos (nome, CPF/CNPJ, contato, endereço)
├─ PACIENTE:    6 campos (nome, CPF, contato, endereço)
├─ DATA:        4 campos (dia, mês, ano, completa)
├─ VALORES:     4 campos (total, descrição, parcelas, restante)
└─ PROCEDIMENTOS: 3+ campos por procedimento (nome, imagem, descrição)

TOTAL MÍNIMO PARA GERAR: 20 campos
TEMPO DE SUBSTITUIÇÃO: < 1 segundo
ARQUIVO RESULTADO: PDF pronto para assinatura

PRÓXIMAS AÇÕES:
1. Executar: python -c "from pdf_replacer import PDFPlaceholderReplacer; ..."
2. Testar com dados reais do banco
3. Implementar integração com DocuSign/OneFlow (opcional)
4. Deploy em produção

DOCUMENTAÇÃO:
├─ quick_reference.py  → Este arquivo (referência)
├─ pdf_replacer.py     → Código principal
├─ exemplos_praticos.py → 5 cenários reais
└─ database-schema.sql → Schema SQL pronto

✓ PRONTO PARA USAR!
""")
