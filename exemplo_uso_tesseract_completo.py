from pdf_placeholder_processor_pytesseract import PDFPlaceholderProcessor

placeholders_valores = {
    # Data
    "{dd}": "15",
    "{mm}": "01",
    "{aaaa}": "2026",
    
    # Profissional
    "{nome_da_medica_ou_clinica}": "Clínica Estética Silva",
    "{emailmedicacli}": "email@clinica.com.br",
    
    # Paciente
    "{nome_paciente}": "João Pedro Santos",
    "{cpfpaciente}": "123.456.789-00",
    "{celpaciente}": "(11) 98765-4321",
    "{enderecopaciente2}": "Rua das Flores, 123 - Apto 45",
    
    # Procedimentos (preencha conforme necessário)
    "{procedimento_1}": "Limpeza de Pele Profunda",
    "{procedimento_1_descricao1}": "Microagulhagem com RF",
    "{procedimento_1_descricao2}": "Peeling Químico",
    "{procedimento_1_descricao3}": "Laser de CO2 Fracionado",
}

pdf_path = "./templates/Contrato_Medico-04_procedimentos_teste.pdf"
v_caminho_saida = "./contratos_gerados/Contrato_Preenchido_2026.pdf"

processador = PDFPlaceholderProcessor(pdf_path, dpi=300)
processador.processar_completo(placeholders_valores, v_caminho_saida)