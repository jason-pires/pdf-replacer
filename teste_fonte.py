# teste_fonte.py
# Script para verificar e testar a instalação da fonte Plus Jakarta Sans

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2


def verificar_fontes():
    """Verifica se as fontes estão instaladas"""
    
    print("\n" + "="*80)
    print("📋 VERIFICAÇÃO DE FONTES - PLUS JAKARTA SANS")
    print("="*80 + "\n")
    
    fontes_esperadas = [
        "PlusJakartaSans-Regular.ttf",
        "PlusJakartaSans-Medium.ttf",
        "PlusJakartaSans-Bold.ttf",
        "PlusJakartaSans-SemiBold.ttf",
    ]
    
    if not os.path.exists("./fonts"):
        print("❌ Pasta ./fonts/ NÃO encontrada")
        return False
    
    print("✅ Pasta ./fonts/ encontrada\n")
    
    arquivos = os.listdir("./fonts")
    fontes_ttf = [f for f in arquivos if f.endswith(('.ttf', '.otf'))]
    
    print(f"📝 Total de arquivos: {len(fontes_ttf)}\n")
    
    if len(fontes_ttf) == 0:
        print("❌ Nenhum arquivo .ttf ou .otf encontrado!")
        return False
    
    print("📦 Fontes disponíveis:")
    for fonte in sorted(fontes_ttf):
        tamanho_kb = os.path.getsize(f"./fonts/{fonte}") / 1024
        print(f"  ✓ {fonte} ({tamanho_kb:.1f} KB)")
    
    print(f"\n✅ Total: {len(fontes_ttf)} arquivo(s)")
    
    return len(fontes_ttf) > 0


def testar_carregamento_fonte(nome_fonte="PlusJakartaSans-Regular.ttf", tamanho=24):
    """Testa se consegue carregar a fonte"""
    
    print("\n" + "="*80)
    print("🔧 TESTE DE CARREGAMENTO DE FONTE")
    print("="*80 + "\n")
    
    caminho = f"./fonts/{nome_fonte}"
    
    if not os.path.exists(caminho):
        print(f"❌ Arquivo não encontrado: {caminho}")
        return False
    
    try:
        fonte = ImageFont.truetype(caminho, tamanho)
        print(f"✅ Fonte carregada com sucesso!")
        print(f"   Arquivo: {nome_fonte}")
        print(f"   Tamanho: {tamanho}pt")
        return True
    except Exception as e:
        print(f"❌ Erro ao carregar fonte: {e}")
        return False


def testar_renderizacao_texto():
    """Testa a renderização de texto com a fonte"""
    
    print("\n" + "="*80)
    print("🎨 TESTE DE RENDERIZAÇÃO - GERAR IMAGEM COM TEXTO")
    print("="*80 + "\n")
    
    try:
        # Criar imagem branca
        img = Image.new('RGB', (800, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # Variações de fonte
        variações = [
            ("PlusJakartaSans-Regular.ttf", "Regular"),
            ("PlusJakartaSans-Medium.ttf", "Medium"),
            ("PlusJakartaSans-Bold.ttf", "Bold"),
        ]
        
        y_pos = 30
        
        for arquivo, label in variações:
            caminho = f"./fonts/{arquivo}"
            
            if not os.path.exists(caminho):
                print(f"⚠️  {label}: arquivo não encontrado ({arquivo})")
                continue
            
            try:
                fonte = ImageFont.truetype(caminho, 32)
                texto = f"Plus Jakarta Sans - {label}"
                
                draw.text((50, y_pos), texto, fill='black', font=fonte)
                print(f"✅ {label}: renderizado com sucesso")
                
                y_pos += 80
                
            except Exception as e:
                print(f"❌ {label}: erro ao renderizar - {e}")
        
        # Adicionar exemplo de valores de placeholder
        y_pos += 20
        try:
            fonte_pequena = ImageFont.truetype("./fonts/PlusJakartaSans-Regular.ttf", 14)
            draw.text((50, y_pos), 
                     "Exemplo: João Pedro Santos (CPF: 123.456.789-00)",
                     fill='#333333', font=fonte_pequena)
            print(f"✅ Exemplo de placeholder: renderizado com sucesso")
        except:
            pass
        
        # Salvar imagem
        img.save("./fonts/teste_fonte.png")
        
        print(f"\n✅ Imagem de teste salva: ./fonts/teste_fonte.png")
        print("   Abra em um visualizador de imagens para confirmar")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao renderizar: {e}")
        return False


def gerar_relatorio():
    """Gera relatório completo"""
    
    print("\n" + "🎯 "*40)
    print("RELATÓRIO FINAL - ESTADO DA FONTE")
    print("🎯 "*40 + "\n")
    
    # Verificação 1: Pasta e arquivos
    print("1️⃣  VERIFICAÇÃO DE INSTALAÇÃO")
    print("-" * 80)
    paso1 = verificar_fontes()
    
    if not paso1:
        print("\n❌ FONTE NÃO INSTALADA CORRETAMENTE")
        print("   Solução: Download do Google Fonts e extraia em ./fonts/")
        return False
    
    # Verificação 2: Carregamento
    print("\n\n2️⃣  CARREGAMENTO DE FONTE")
    print("-" * 80)
    paso2 = testar_carregamento_fonte()
    
    if not paso2:
        print("\n❌ ERRO AO CARREGAR FONTE")
        print("   Verifique se o arquivo .ttf não está corrompido")
        return False
    
    # Verificação 3: Renderização
    print("\n\n3️⃣  RENDERIZAÇÃO DE TEXTO")
    print("-" * 80)
    paso3 = testar_renderizacao_texto()
    
    if not paso3:
        print("\n❌ ERRO AO RENDERIZAR")
        return False
    
    # Relatório final
    print("\n" + "✅ "*40)
    print("TUDO PRONTO!")
    print("✅ "*40)
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("-" * 80)
    print("1. Use a função 4 melhorada:")
    print("   from pdf_processor_v2_com_fonte import inserir_textos_com_fonte")
    print("\n2. Ou continue com a versão original:")
    print("   from pdf_processor_v2 import inserir_textos")
    print("\n3. Execute o exemplo completo:")
    print("   python exemplo_v2_completo.py")
    print("-" * 80 + "\n")
    
    return True


if __name__ == "__main__":
    
    sucesso = gerar_relatorio()
    
    if sucesso:
        print("\n" + "🚀 "*20)
        print("FONTE INSTALADA COM SUCESSO!")
        print("Você está pronto para processar PDFs com Plus Jakarta Sans")
        print("🚀 "*20 + "\n")
    else:
        print("\n" + "⚠️ "*20)
        print("PROBLEMA DETECTADO - Verifique as mensagens acima")
        print("⚠️ "*20 + "\n")
