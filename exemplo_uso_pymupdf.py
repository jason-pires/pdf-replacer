# exemplo_uso_pymupdf.py
# Exemplo de uso com PyMuPDF (100% preciso, sem OCR)

from pdf_placeholder_processor_pymupdf import PDFPlaceholderProcessorPyMuPDF

# ============================================================================
# PASSO 1: Definir os valores dos placeholders
# ============================================================================

placeholders_valores = {
    # Data
    "{dd}": "15",
    "{mmm}": "01",
    "{aaaa}": "2026",
    
    # Clínica/Profissional
    "{nome_da_medica_ou_clinica}": "Clínica Estética Silva",
    
    # Paciente
    "{nome_paciente}": "João Pedro Santos",
    "{cpfpaciente}": "123.456.789-00",
    "{celepaciente}": "(11) 98765-4321",
    "{endereceopaciente2}": "Rua das Flores, 123 - Apto 45",
    
    # Procedimentos
    "{procedimento_1}": "Limpeza de Pele Profunda",
    "{procedimento_2}": "Microagulhagem com RF",
    "{procedimento_3}": "Peeling Químico",
    "{procedimento_4}": "Laser de CO2 Fracionado",
}

# ============================================================================
# PASSO 2: Processar PDF
# ============================================================================

print("="*60)
print("PROCESSADOR DE PDF - PyMuPDF (100% Preciso)")
print("="*60)

v_pdf_path = "./templates/Contrato_Medico-04_procedimentos_teste.pdf"
v_caminho_saida = "./contratos_gerados/Contrato_Preenchido_2026.pdf"

# Criar processador (PyMuPDF)
processador = PDFPlaceholderProcessorPyMuPDF(
    pdf_path=v_pdf_path,
    dpi=300  # 300 = qualidade profissional, 600 = ultra alta
)

# Executar processamento completo
sucesso = processador.processar_completo(
    placeholders_valores=placeholders_valores,
    caminho_saida=v_caminho_saida
)

# ============================================================================
# RESULTADO
# ============================================================================

if sucesso:
    print("\n✅ SUCESSO!")
    print("📄 PDF gerado: Contrato_Preenchido_PyMuPDF.pdf")
    print("\n💡 Vantagens do PyMuPDF:")
    print("   • 100% preciso (sem OCR)")
    print("   • Coordenadas exatas")
    print("   • Mantém fonte/cor original")
    print("   • Muito rápido (~3s)")
else:
    print("\n❌ Erro no processamento")

# ============================================================================
# METADADOS (opcional)
# ============================================================================

print("\n" + "="*60)
print("METADADOS DOS PLACEHOLDERS PROCESSADOS")
print("="*60)

for page_num, page_data in enumerate(processador.pages_metadata):
    print(f"\n📄 Página {page_num + 1}:")
    print(f"   Total de placeholders: {len(page_data['placeholders'])}")
    
    for ph in page_data['placeholders']:
        valor = placeholders_valores.get(ph['text'], "NÃO INFORMADO")
        x0, y0, x1, y1 = ph['bbox']
        print(f"\n   • {ph['text']}")
        print(f"     Posição: ({x0:.1f}, {y0:.1f})")
        print(f"     Tamanho: {ph['size']:.1f}pt")
        print(f"     Fonte: {ph['font']}")
        print(f"     Valor: '{valor}'")
