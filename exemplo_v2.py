# exemplo_v2.py
# Script de uso - PDF Processor V2
# Implementação completa das 5 funções


from pdf_processor_v2 import processar_pdf_completo

# ============================================================================
# CONFIGURAÇÃO - Placeholders e Valores
# ============================================================================
from placeholders_valores_completo import placeholders_valores

# ============================================================================
# EXECUTAR PIPELINE COMPLETO
# ============================================================================

if __name__ == "__main__":

    v_pdf_path = "./templates/Contrato_Medico-04_procedimentos_teste.pdf"
    v_output_pdf="./output/Contrato_Preenchido.pdf"
    
    sucesso = processar_pdf_completo(
        pdf_path=v_pdf_path,
        placeholders_valores=placeholders_valores,
        output_pdf=v_output_pdf,
        dpi=600  # 300 = profissional, 600 = ultra alta qualidade
    )
    
    if sucesso:
        print("\n" + "🎉 "*40)
        print("PDF GERADO COM SUCESSO!")
        print("Verifique a pasta ./output/")
        print("🎉 "*40)
    else:
        print("\n❌ Erro ao processar PDF")
