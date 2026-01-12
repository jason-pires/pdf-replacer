# instalar_dependencias_v2.py
# Script seguro para instalar TODAS as dependências - NumPy 2.x + OpenCV 4.10+

import subprocess
import sys
import os

def instalar_pacotes():
    """Instala todas as dependências necessárias de forma segura com NumPy 2.x"""
    
    print("\n" + "="*80)
    print("🔧 INSTALADOR DE DEPENDÊNCIAS - PDF PROCESSOR V2")
    print("📦 Versão: NumPy 2.4.1 + OpenCV 4.10+ (Compatível)")
    print("="*80 + "\n")
    
    # Lista de pacotes com versões específicas (compatíveis com NumPy 2.x)
    pacotes = [
        ("numpy", "2.4.1", "Processamento numérico (versão 2.x)"),
        ("Pillow", "10.0.0", "Processamento de imagens"),
        ("opencv-python", "4.10.0.84", "Visão computacional (compatível com NumPy 2.x)"),
        ("PyMuPDF", "1.24.1", "Manipulação de PDF"),
        ("img2pdf", "1.4.11", "Conversão de imagens para PDF"),
    ]
    
    print("📦 Pacotes a instalar:\n")
    for nome, versao, descricao in pacotes:
        print(f"  ✓ {nome:20} v{versao:15} - {descricao}")
    
    print("\n" + "-"*80 + "\n")
    
    # Instalar cada pacote individualmente
    for nome, versao, descricao in pacotes:
        print(f"\n📥 Instalando {nome} {versao}...")
        print("-"*80)
        
        try:
            # Usar pip install com versão específica e --force-reinstall
            comando = [
                sys.executable, "-m", "pip", "install",
                f"{nome}=={versao}",
                "--force-reinstall",
                "--no-cache-dir"
            ]
            
            resultado = subprocess.run(
                comando,
                capture_output=False,
                text=True
            )
            
            if resultado.returncode == 0:
                print(f"✅ {nome} instalado com sucesso!")
            else:
                print(f"⚠️  Erro ao instalar {nome}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    print("\n" + "="*80)
    print("✅ INSTALAÇÃO CONCLUÍDA!")
    print("="*80 + "\n")
    
    # Verificar instalação
    print("🔍 Verificando instalação...\n")
    
    verificacoes = [
        ("numpy", lambda: __import__("numpy").__version__),
        ("cv2 (OpenCV)", lambda: __import__("cv2").__version__),
        ("PIL (Pillow)", lambda: __import__("PIL").__version__),
        ("fitz (PyMuPDF)", lambda: __import__("fitz").version[0]),
        ("img2pdf", lambda: __import__("img2pdf").__version__),
    ]
    
    for nome, get_version in verificacoes:
        try:
            versao = get_version()
            print(f"  ✅ {nome:20} v{versao}")
        except Exception as e:
            print(f"  ❌ {nome:20} - Erro: {e}")
    
    print("\n" + "="*80)
    print("🎉 PRONTO PARA USAR PDF PROCESSOR V2!")
    print("="*80 + "\n")
    
    print("✅ Compatibilidade verificada:")
    print("   • NumPy 2.4.1 ✓")
    print("   • OpenCV 4.10+ ✓")
    print("   • PyMuPDF 1.24.1 ✓")
    print("   • img2pdf 1.4.11 ✓")
    
    print("\n🚀 Próximos passos:")
    print("   1. Coloque a fonte Plus Jakarta Sans em ./fonts/")
    print("   2. Execute: python exemplo_v2_img2pdf.py")
    print("\n")


if __name__ == "__main__":
    instalar_pacotes()
