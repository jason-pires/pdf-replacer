-- ============================================================================
-- SCHEMA DO BANCO DE DADOS PARA GESTÃO DE CONTRATOS
-- ============================================================================
-- 
-- Este schema inclui:
-- 1. Tabelas de clínicas e médicas
-- 2. Tabelas de pacientes
-- 3. Tabelas de contratos
-- 4. Tabelas de procedimentos
-- 5. Tabelas de pagamento
-- 6. Tabela de auditoria

-- ============================================================================
-- 1. TABELAS BASE
-- ============================================================================

CREATE TABLE clinicas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    cpf_cnpj VARCHAR(20) NOT NULL UNIQUE,
    celular VARCHAR(20),
    email VARCHAR(255),
    endereco_linha1 VARCHAR(255),
    endereco_linha2 VARCHAR(255),
    uf VARCHAR(2),
    cep VARCHAR(10),
    ativa BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE medicas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinica_id UUID NOT NULL REFERENCES clinicas(id),
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(20) NOT NULL UNIQUE,
    crm VARCHAR(20) NOT NULL UNIQUE,
    especialidade VARCHAR(255),
    celular VARCHAR(20),
    email VARCHAR(255),
    ativa BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pacientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(20) NOT NULL UNIQUE,
    celular VARCHAR(20),
    email VARCHAR(255),
    endereco_linha1 VARCHAR(255),
    endereco_linha2 VARCHAR(255),
    uf VARCHAR(2),
    cep VARCHAR(10),
    data_nascimento DATE,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 2. TABELAS DE PROCEDIMENTOS
-- ============================================================================

CREATE TABLE procedimentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    valor_padrao DECIMAL(10,2),
    tempo_estimado_minutos INT,
    imagem_url VARCHAR(512),
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 3. TABELA DE CONTRATOS (PRINCIPAL)
-- ============================================================================

CREATE TABLE contratos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Referências
    clinica_id UUID NOT NULL REFERENCES clinicas(id),
    medica_id UUID NOT NULL REFERENCES medicas(id),
    paciente_id UUID NOT NULL REFERENCES pacientes(id),
    
    -- Status
    status VARCHAR(50) DEFAULT 'rascunho', 
    -- rascunho, gerado, enviado_assinatura, assinado, cancelado
    
    -- Datas
    data_contrato DATE NOT NULL,
    vencimento_pagamento DATE,
    
    -- Valores
    valor_total DECIMAL(10,2) NOT NULL,
    taxa_agendamento DECIMAL(10,2),
    
    -- Pagamento
    forma_pagamento VARCHAR(50), -- cartao, boleto, pix, etc
    quantidade_parcelas INT DEFAULT 1,
    juros_mensal DECIMAL(5,2) DEFAULT 1.0,
    multa_atraso DECIMAL(5,2) DEFAULT 10.0,
    
    -- Assinatura
    pdf_original_url VARCHAR(512),
    pdf_preenchido_url VARCHAR(512),
    pdf_assinado_url VARCHAR(512),
    signature_request_id VARCHAR(255),
    signature_provider VARCHAR(50), -- docusign, oneflow, adobe
    assinado_em TIMESTAMP,
    
    -- Observações
    observacoes TEXT,
    termo_consentimento_aceito BOOLEAN DEFAULT false,
    
    -- Rastreamento
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_contratos_clinica ON contratos(clinica_id);
CREATE INDEX idx_contratos_paciente ON contratos(paciente_id);
CREATE INDEX idx_contratos_status ON contratos(status);
CREATE INDEX idx_contratos_data ON contratos(data_contrato);

-- ============================================================================
-- 4. TABELA DE ITENS DO CONTRATO (procedimentos contratados)
-- ============================================================================

CREATE TABLE contrato_itens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contrato_id UUID NOT NULL REFERENCES contratos(id) ON DELETE CASCADE,
    procedimento_id UUID NOT NULL REFERENCES procedimentos(id),
    
    -- Dados do procedimento no momento do contrato
    procedimento_nome VARCHAR(255) NOT NULL,
    procedimento_descricao TEXT,
    procedimento_imagem_url VARCHAR(512),
    
    -- Valor
    valor DECIMAL(10,2) NOT NULL,
    
    -- Status do procedimento
    status VARCHAR(50) DEFAULT 'agendado', 
    -- agendado, realizado, cancelado, refinamento
    
    data_execucao DATE,
    observacoes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_contrato_itens_contrato ON contrato_itens(contrato_id);

-- ============================================================================
-- 5. TABELA DE PAGAMENTOS
-- ============================================================================

CREATE TABLE pagamentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contrato_id UUID NOT NULL REFERENCES contratos(id) ON DELETE CASCADE,
    
    numero_parcela INT,
    data_vencimento DATE,
    data_pagamento DATE,
    
    valor DECIMAL(10,2) NOT NULL,
    valor_pago DECIMAL(10,2),
    
    status VARCHAR(50) DEFAULT 'pendente',
    -- pendente, pago, atrasado, cancelado
    
    metodo_pagamento VARCHAR(50),
    -- cartao, boleto, pix, transferencia
    
    juros_cobrado DECIMAL(10,2) DEFAULT 0,
    multa_cobrada DECIMAL(10,2) DEFAULT 0,
    
    observacoes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pagamentos_contrato ON pagamentos(contrato_id);
CREATE INDEX idx_pagamentos_status ON pagamentos(status);
CREATE INDEX idx_pagamentos_data ON pagamentos(data_vencimento);

-- ============================================================================
-- 6. TABELA DE AUDITORIA
-- ============================================================================

CREATE TABLE auditoria_contratos (
    id SERIAL PRIMARY KEY,
    contrato_id UUID NOT NULL REFERENCES contratos(id) ON DELETE CASCADE,
    
    acao VARCHAR(100), -- criado, preenchido, enviado, assinado, cancelado, etc
    usuario_id VARCHAR(255),
    ip_address INET,
    
    dados_anteriores JSONB,
    dados_novos JSONB,
    
    mensagem TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_auditoria_contrato ON auditoria_contratos(contrato_id);
CREATE INDEX idx_auditoria_data ON auditoria_contratos(created_at);

-- ============================================================================
-- 7. TABELA DE ASSINATURAS
-- ============================================================================

CREATE TABLE assinaturas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contrato_id UUID NOT NULL REFERENCES contratos(id) ON DELETE CASCADE,
    
    tipo VARCHAR(50), -- paciente, medica, outro_responsavel
    nome_assinante VARCHAR(255),
    email_assinante VARCHAR(255),
    cpf_assinante VARCHAR(20),
    
    provider VARCHAR(50), -- docusign, oneflow, adobe
    request_id VARCHAR(255),
    
    status VARCHAR(50) DEFAULT 'pendente',
    -- pendente, assinado, rejeitado, expirado
    
    assinado_em TIMESTAMP,
    expira_em TIMESTAMP,
    
    dados_assinatura JSONB, -- armazena dados da assinatura (timestamp, IP, etc)
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assinaturas_contrato ON assinaturas(contrato_id);
CREATE INDEX idx_assinaturas_status ON assinaturas(status);

-- ============================================================================
-- VIEWS ÚTEIS
-- ============================================================================

-- View: Contratos com dados principais
CREATE VIEW v_contratos_resumo AS
SELECT 
    c.id,
    c.clinica_id,
    c.paciente_id,
    cli.nome as clinica_nome,
    p.nome as paciente_nome,
    m.nome as medica_nome,
    c.data_contrato,
    c.valor_total,
    c.status,
    COUNT(ci.id) as total_procedimentos,
    MAX(c.updated_at) as ultima_atualizacao
FROM contratos c
LEFT JOIN clinicas cli ON c.clinica_id = cli.id
LEFT JOIN pacientes p ON c.paciente_id = p.id
LEFT JOIN medicas m ON c.medica_id = m.id
LEFT JOIN contrato_itens ci ON c.id = ci.contrato_id
WHERE c.deleted_at IS NULL
GROUP BY c.id, c.clinica_id, c.paciente_id, cli.nome, p.nome, m.nome;

-- View: Pagamentos com status
CREATE VIEW v_pagamentos_status AS
SELECT 
    c.id as contrato_id,
    p.nome as paciente_nome,
    COUNT(pa.id) as total_parcelas,
    SUM(CASE WHEN pa.status = 'pago' THEN 1 ELSE 0 END) as parcelas_pagas,
    SUM(CASE WHEN pa.status = 'pendente' THEN pa.valor ELSE 0 END) as valor_pendente,
    SUM(CASE WHEN pa.status = 'atrasado' THEN pa.valor ELSE 0 END) as valor_atrasado,
    MAX(pa.data_vencimento) as ultimo_vencimento
FROM contratos c
LEFT JOIN pacientes p ON c.paciente_id = p.id
LEFT JOIN pagamentos pa ON c.id = pa.contrato_id
WHERE c.deleted_at IS NULL
GROUP BY c.id, p.nome;

-- ============================================================================
-- FUNÇÕES ÚTEIS
-- ============================================================================

-- Função: Buscar dados do contrato para preencher template
CREATE OR REPLACE FUNCTION get_contract_data_for_template(contract_id UUID)
RETURNS TABLE (
    nome_da_medica_ou_clinica VARCHAR,
    cpfcnpjmedicacli VARCHAR,
    celmedicacli VARCHAR,
    emailmedicacli VARCHAR,
    enderecomedical VARCHAR,
    enderecomedica2 VARCHAR,
    nome_paciente VARCHAR,
    cpfpaciente VARCHAR,
    celpaciente VARCHAR,
    emailpaciente VARCHAR,
    enderecopacientel VARCHAR,
    enderecopaciente2 VARCHAR,
    dd VARCHAR,
    mmm VARCHAR,
    aaaa VARCHAR,
    valor VARCHAR,
    espec_pagto VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cli.nome::VARCHAR,
        cli.cpf_cnpj::VARCHAR,
        cli.celular::VARCHAR,
        cli.email::VARCHAR,
        cli.endereco_linha1::VARCHAR,
        cli.endereco_linha2::VARCHAR,
        p.nome::VARCHAR,
        p.cpf::VARCHAR,
        p.celular::VARCHAR,
        p.email::VARCHAR,
        p.endereco_linha1::VARCHAR,
        p.endereco_linha2::VARCHAR,
        EXTRACT(DAY FROM c.data_contrato)::TEXT,
        TO_CHAR(c.data_contrato, 'Month')::VARCHAR,
        EXTRACT(YEAR FROM c.data_contrato)::TEXT,
        c.valor_total::TEXT,
        STRING_AGG(ci.procedimento_nome, ', ')::VARCHAR
    FROM contratos c
    LEFT JOIN clinicas cli ON c.clinica_id = cli.id
    LEFT JOIN pacientes p ON c.paciente_id = p.id
    LEFT JOIN contrato_itens ci ON c.id = ci.contrato_id
    WHERE c.id = contract_id AND c.deleted_at IS NULL
    GROUP BY c.id, cli.id, p.id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DADOS DE EXEMPLO (OPCIONAL)
-- ============================================================================

-- Inserir clínica de exemplo
INSERT INTO clinicas (nome, cpf_cnpj, celular, email, endereco_linha1, endereco_linha2, uf, cep)
VALUES (
    'Dra. Maria Silva - Clínica Estética',
    '12.345.678/0001-90',
    '(21) 99999-8888',
    'contato@clinicamaria.com.br',
    'Av. Paulista, 1000',
    'São Paulo, SP 01311-100',
    'SP',
    '01311-100'
);

-- Inserir procedimentos de exemplo
INSERT INTO procedimentos (nome, descricao, valor_padrao, tempo_estimado_minutos)
VALUES 
    ('Lipoaspiração', 'Remoção de gordura localizada', 5000.00, 120),
    ('Abdominoplastia', 'Cirurgia de abdômen', 8000.00, 180),
    ('Rinoplastia', 'Cirurgia de nariz', 6000.00, 90);

-- ============================================================================
-- ÍNDICES ADICIONAIS PARA PERFORMANCE
-- ============================================================================

CREATE INDEX idx_contratos_medica ON contratos(medica_id);
CREATE INDEX idx_contratos_assinado ON contratos(assinado_em);
CREATE INDEX idx_pagamentos_vencimento ON pagamentos(data_vencimento);
CREATE INDEX idx_assinaturas_request_id ON assinaturas(request_id);
CREATE INDEX idx_contrato_itens_status ON contrato_itens(status);

-- ============================================================================
-- COMMENTS PARA DOCUMENTAÇÃO
-- ============================================================================

COMMENT ON TABLE contratos IS 'Tabela principal de contratos médicos';
COMMENT ON COLUMN contratos.status IS 'Status do contrato: rascunho, gerado, enviado_assinatura, assinado, cancelado';
COMMENT ON COLUMN contratos.signature_provider IS 'Provedor de assinatura: docusign, oneflow, adobe';

COMMENT ON TABLE pagamentos IS 'Registro de parcelas e pagamentos';
COMMENT ON COLUMN pagamentos.status IS 'Status da parcela: pendente, pago, atrasado, cancelado';

COMMENT ON TABLE auditoria_contratos IS 'Log de todas as mudanças nos contratos para compliance';
COMMENT ON TABLE assinaturas IS 'Rastreamento de assinaturas eletrônicas de cada signatário';
