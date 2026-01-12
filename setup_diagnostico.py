#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico e instalação automática do Tesseract
Detecta seu SO e ajuda na instalação
"""

import os
import sys
import platform
import subprocess

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def check_tesseract():
    """Verifica se Tesseract está instalado"""
    try:
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            return True, version_line
    except FileNotFoundError:
        pass
    return False, None

def check_python_packages():
    """Verifica pacotes Python necessários"""
    packages = {
        'PIL': 'Pillow',
        'pytesseract': 'pytesseract',
        'psycopg2': 'psycopg2-binary'
    }
    
    missing = []
    for import_name, package_name in packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    return missing

def get_os_type():
    """Detecta o sistema operacional"""
    system = platform.system()
    if system == 'Linux':
        return 'linux'
    elif system == 'Darwin':
        return 'macos'
    elif system == 'Windows':
        return 'windows'
    return 'unknown'

def install_tesseract_linux():
    """Instruções para Linux"""
    print_header("INSTALAÇÃO: LINUX (Ubuntu/Debian)")
    print("""
    Execute estes comandos no terminal:
    
    # 1. Atualizar repositório
    sudo apt-get update
    
    # 2. Instalar Tesseract
    sudo apt-get install tesseract-ocr -y
    
    # 3. Verificar instalação
    tesseract --version
    
    # 4. Reinicie o terminal/IDE
    """)
    
    print("\n💡 Dica: Se quiser instalar tudo de uma vez:")
    print("""
    sudo apt-get update && sudo apt-get install tesseract-ocr -y
    """)

def install_tesseract_macos():
    """Instruções para macOS"""
    print_header("INSTALAÇÃO: macOS")
    print("""
    Execute estes comandos no terminal:
    
    # 1. Instalar Homebrew (se não tiver)
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # 2. Instalar Tesseract
    brew install tesseract
    
    # 3. Verificar instalação
    tesseract --version
    
    # 4. Reinicie o terminal/IDE
    """)

def install_tesseract_windows():
    """Instruções para Windows"""
    print_header("INSTALAÇÃO: Windows")
    print("""
    ⚠️  ATENÇÃO: Siga exatamente estes passos!
    
    1. Acesse: https://github.com/UB-Mannheim/tesseract/wiki
    
    2. Baixe o instalador:
       tesseract-ocr-w64-setup-v5.3.0.exe (ou versão mais recente)
    
    3. Execute o instalador:
       - Clique em: Next → Next → Install
       - Aceite o local padrão:
         C:\\Program Files\\Tesseract-OCR
    
    4. MUITO IMPORTANTE: Reinicie o computador COMPLETAMENTE
    
    5. Após reiniciar, abra o terminal e execute:
       tesseract --version
    
    6. Se funcionar, execute seu código:
       python exemplo_pratico_completo.py
    
    ---
    
    Se o instalador não funcionar, tente Chocolatey:
    
    # Abra PowerShell como Admin:
    choco install tesseract
    """)

def install_python_packages():
    """Instala pacotes Python necessários"""
    print_header("INSTALANDO PACOTES PYTHON")
    
    try:
        print("⏳ Instalando: Pillow pytesseract psycopg2-binary...")
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 
             'Pillow', 'pytesseract', 'psycopg2-binary'],
            check=True
        )
        print_success("Pacotes Python instalados!")
        return True
    except subprocess.CalledProcessError:
        print_error("Erro ao instalar pacotes Python")
        print("Execute manualmente: pip install Pillow pytesseract psycopg2-binary")
        return False

def main():
    """Função principal"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  🔧 DIAGNÓSTICO E INSTALAÇÃO AUTOMÁTICA DO TESSERACT".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # 1. Detectar SO
    print_header("1️⃣  DETECTANDO SISTEMA OPERACIONAL")
    os_type = get_os_type()
    print_info(f"Sistema: {platform.system()}")
    print_info(f"Versão: {platform.release()}")
    
    # 2. Verificar Tesseract
    print_header("2️⃣  VERIFICANDO TESSERACT")
    has_tesseract, version = check_tesseract()
    
    if has_tesseract:
        print_success(f"Tesseract já está instalado!")
        print_info(f"Versão: {version}")
    else:
        print_error("Tesseract NÃO está instalado")
        print_info("Será necessário instalar para usar OCR")
    
    # 3. Verificar pacotes Python
    print_header("3️⃣  VERIFICANDO PACOTES PYTHON")
    missing_packages = check_python_packages()
    
    if not missing_packages:
        print_success("Todos os pacotes Python estão instalados!")
    else:
        print_error(f"Pacotes faltando: {', '.join(missing_packages)}")
        print_info("Iniciando instalação automática...")
        
        if install_python_packages():
            print_success("Pacotes instalados com sucesso!")
        else:
            print_error("Não foi possível instalar automaticamente")
            print_info("Execute manualmente:")
            print("pip install Pillow pytesseract psycopg2-binary")
    
    # 4. Recomendações
    print_header("4️⃣  PRÓXIMOS PASSOS")
    
    if has_tesseract and not missing_packages:
        print_success("✨ Tudo está instalado! Você está pronto para começar!")
        print_info("Execute: python exemplo_pratico_completo.py")
    else:
        if not has_tesseract:
            print_error("Você precisa instalar o Tesseract (OCR)")
            
            if os_type == 'linux':
                install_tesseract_linux()
            elif os_type == 'macos':
                install_tesseract_macos()
            elif os_type == 'windows':
                install_tesseract_windows()
            else:
                print_error("SO não detectado. Visite:")
                print("https://github.com/UB-Mannheim/tesseract/wiki")
    
    # 5. Teste final
    print_header("5️⃣  TESTE FINAL")
    print("""
    Depois de instalar tudo, rode este comando para testar:
    
    python exemplo_pratico_completo.py
    
    Se funcionar, você verá:
    ✓ Template carregado
    ✓ PDFs gerados em: contratos/
    """)
    
    print_header("RESUMO")
    print(f"✓ SO: {platform.system()}")
    print(f"{'✓' if has_tesseract else '✗'} Tesseract: {'Instalado' if has_tesseract else 'Não instalado'}")
    print(f"{'✓' if not missing_packages else '✗'} Pacotes Python: {'OK' if not missing_packages else f'Faltam {len(missing_packages)}'}")
    
    if has_tesseract and not missing_packages:
        print("\n✅ VOCÊ ESTÁ 100% PRONTO! 🚀\n")
    else:
        print("\n⚠️  COMPLETE A INSTALAÇÃO ANTES DE RODAR O CÓDIGO\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Instalação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        sys.exit(1)
