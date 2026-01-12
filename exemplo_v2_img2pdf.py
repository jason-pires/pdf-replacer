# exemplo_v2_img2pdf.py
# Script de uso - PDF Processor V2 COM IMG2PDF

from pdf_processor_v2_com_fonte_inteligente_IMG2PDF import processar_pdf_inteligente
from placeholders_valores_completo import placeholders_valores

# ============================================================================
# EXECUTAR PIPELINE COMPLETO COM IMG2PDF
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*80)
    print("PDF PROCESSOR V2 - VERSÃO COM IMG2PDF")
    print("="*80)
    print(f"\n📋 Total de placeholders: {len(placeholders_valores)}")
    print("✅ Detecção automática de cor:")
    print("   • PRETO em fundos CLAROS (brilho > 128)")
    print("   • BRANCO em fundos ESCUROS (brilho ≤ 128)")
    print("✅ Usando fonte Plus Jakarta Sans para melhor qualidade visual")
    print("📦 Gerando PDF com img2pdf (simples e eficiente)\n")

    v_pdf_path = "./templates/Contrato_Medico-04_procedimentos_teste.pdf"
    v_output_pdf="./output/Contrato_Preenchido.pdf"
    
    sucesso = processar_pdf_inteligente(
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
        print("Arquivo: Contrato_Preenchido_IMG2PDF.pdf")
        print("✨ Textos com COR INTELIGENTE baseada no fundo!")
        print("📦 Convertido com img2pdf")
        print("🎉 "*40 + "\n")
    else:
        print("\n❌ Erro ao processar PDF")
        print("Verifique a mensagem de erro acima\n")
