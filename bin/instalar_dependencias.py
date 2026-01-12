# instalar_dependencias.py
# Script seguro para instalar TODAS as dependências sem conflitos

import subprocess
import sys
import os

def instalar_pacotes():
    """Instala todas as dependências necessárias de forma segura"""
    
    print("\n" + "="*80)
    print("🔧 INSTALADOR DE DEPENDÊNCIAS - PDF PROCESSOR V2")
    print("="*80 + "\n")
    
    # Lista de pacotes com versões específicas (compatíveis)
    pacotes = [
        ("numpy", "1.24.3", "Processamento numérico"),
        ("Pillow", "10.0.0", "Processamento de imagens"),
        ("opencv-python", "4.8.1.78", "Visão computacional (inpainting)"),
        ("PyMuPDF", "1.23.8", "Manipulação de PDF"),
        ("img2pdf", "1.4.11", "Conversão de imagens para PDF"),
    ]
    
    print("📦 Pacotes a instalar:\n")
    for nome, versao, descricao in pacotes:
        print(f"  ✓ {nome:20} v{versao:10} - {descricao}")
    
    print("\n" + "-"*80 + "\n")
    
    # Instalar cada pacote individualmente
    for nome, versao, descricao in pacotes:
        print(f"\n📥 Instalando {nome} {versao}...")
        print("-"*80)
        
        try:
            # Usar pip install com versão específica
            comando = [sys.executable, "-m", "pip", "install", f"{nome}=={versao}"]
            
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
    
    modulos = ["numpy", "cv2", "PIL", "fitz", "img2pdf"]
    
    for modulo in modulos:
        try:
            if modulo == "cv2":
                import cv2
                print(f"  ✅ OpenCV (cv2) v{cv2.__version__}")
            elif modulo == "fitz":
                import fitz
                print(f"  ✅ PyMuPDF (fitz) v{fitz.version[0]}")
            elif modulo == "PIL":
                from PIL import __version__
                print(f"  ✅ Pillow (PIL) v{__version__}")
            elif modulo == "img2pdf":
                import img2pdf
                print(f"  ✅ img2pdf v{img2pdf.__version__}")
            else:
                exec(f"import {modulo}")
                print(f"  ✅ {modulo}")
        except Exception as e:
            print(f"  ❌ {modulo}: {e}")
    
    print("\n" + "="*80)
    print("🎉 PRONTO PARA USAR PDF PROCESSOR V2!")
    print("="*80 + "\n")
    
    print("🚀 Próximos passos:")
    print("   1. Coloque a fonte Plus Jakarta Sans em ./fonts/")
    print("   2. Execute: python exemplo_v2_img2pdf.py")
    print("\n")


if __name__ == "__main__":
    instalar_pacotes()
