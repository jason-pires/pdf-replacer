# exemplo_v2_com_fonte.py
# Script de uso - PDF Processor V2 COM FONTE PLUS JAKARTA SANS (VERSÃO COMPLETA)

from pdf_processor_v2_com_fonte_completo import processar_pdf_completo
from placeholders_valores_completo import placeholders_valores

# ============================================================================
# EXECUTAR PIPELINE COMPLETO COM FONTE
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*80)
    print("PDF PROCESSOR V2 - VERSÃO COM FONTE PLUS JAKARTA SANS")
    print("="*80)
    print(f"\n📋 Total de placeholders: {len(placeholders_valores)}")
    print("✅ Usando fonte Plus Jakarta Sans para melhor qualidade visual\n")

    v_pdf_path = "./templates/Contrato_Medico-04_procedimentos_teste.pdf"
    v_output_pdf="./output/Contrato_Preenchido.pdf"
    
    sucesso = processar_pdf_completo(
        pdf_path=v_pdf_path,
        placeholders_valores=placeholders_valores,
        output_pdf=v_output_pdf,
        dpi=600,  # 300 = profissional, 600 = ultra alta qualidade
        fonts_dir="./fonts"  # Pasta com os arquivos TTF
    )
    
    if sucesso:
        print("\n" + "🎉 "*40)
        print("PDF GERADO COM SUCESSO!")
        print("Verifique a pasta ./output/")
        print("Arquivo: Contrato_Preenchido_Com_Fonte.pdf")
        print("🎉 "*40 + "\n")
    else:
        print("\n❌ Erro ao processar PDF\n")
