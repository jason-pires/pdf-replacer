# exemplo_uso.py
# Exemplo completo de como usar o PDFPlaceholderProcessor com keras-ocr

from pdf_placeholder_processor import PDFPlaceholderProcessor
import json
from datetime import datetime

# ============================================================================
# PASSO 1: Definir os valores para todos os placeholders
# ============================================================================

placeholders_valores = {
    # Data
    "{dd}": "15",
    "{mm}": "01",
    "{aaaa}": "2026",
    
    # Profissional
    "{nome_da_medica_ou_clinica____}": "Clínica Estética Silva",
    "{emailmedicacli______________}": "email@clinica.com.br",
    
    # Paciente
    "{nome_paciente________________}": "João Pedro Santos",
    "{cpfpaciente____}": "123.456.789-00",
    "{celpaciente___}": "(11) 98765-4321",
    "{enderecopaciente2__________}": "Rua das Flores, 123 - Apto 45",
    
    # Procedimentos (preencha conforme necessário)
    "{procedimento_1______}": "Limpeza de Pele Profunda",
    "{procedimento_1_descricao1__________}": "Microagulhagem com RF",
    "{procedimento_1_descricao2_________}": "Peeling Químico",
    "{procedimento_1_descricao3_________}": "Laser de CO2 Fracionado",
}

# ============================================================================
# PASSO 2: Criar o processador
# ============================================================================

print("="*60)
print("PROCESSADOR DE PDF COM KERAS-OCR")
print("="*60)

pdf_path = "./templates/Contrato_Medico-04_procedimentos_teste.pdf"

processador = PDFPlaceholderProcessor(
    pdf_path,
    dpi=300  # Alta qualidade (300 DPI)
)

# ============================================================================
# PASSO 3: Executar processamento completo
# ============================================================================

v_caminho_saida = "./contratos_gerados/Contrato_Preenchido_2026.pdf"

sucesso = processador.processar_completo(
    placeholders_valores=placeholders_valores,
    caminho_saida=v_caminho_saida,
)

# ============================================================================
# RESULTADO
# ============================================================================

if sucesso:
    print("\n✅ SUCESSO! Arquivo gerado: Contrato_Preenchido_2026.pdf")
    
    # Salvar relatório dos placeholders detectados
    relatorio = {
        "data_processamento": datetime.now().isoformat(),
        "pdf_entrada": "Contrato_Medico-04_procedimentos.pdf",
        "pdf_saida": "Contrato_Preenchido_2026.pdf",
        "total_paginas": len(processador.pages_metadata),
        "placeholders_processados": [],
    }
    
    for page_data in processador.pages_metadata:
        for ph in page_data['placeholders']:
            relatorio["placeholders_processados"].append({
                "pagina": page_data['page'] + 1,
                "placeholder": ph['text'],
                "valor_inserido": placeholders_valores.get(ph['text'], "NÃO INFORMADO"),
                "posicao": f"({ph['x']}, {ph['y']})",
            })
    
    # Salvar relatório em JSON
    with open("relatorio_processamento.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print("\n📋 Relatório salvo: relatorio_processamento.json")
    
else:
    print("\n❌ Erro no processamento")

# ============================================================================
# OPCIONAL: Exibir metadados detalhados
# ============================================================================

print("\n" + "="*60)
print("METADADOS DOS PLACEHOLDERS DETECTADOS")
print("="*60)

for page_num, page_data in enumerate(processador.pages_metadata):
    print(f"\n📄 Página {page_num + 1}:")
    print(f"   Total de placeholders: {len(page_data['placeholders'])}")
    
    for placeholder in page_data['placeholders']:
        print(f"\n   • {placeholder['text']}")
        print(f"     Posição: ({placeholder['x']}, {placeholder['y']})")
        print(f"     Dimensões: {placeholder['width']}x{placeholder['height']} px")
        print(f"     Tamanho fonte: ~{placeholder['font_size']}px")
        print(f"     Cor (RGB): {placeholder['color']}")
        print(f"     Confiança: {placeholder['confidence']:.0%}")
