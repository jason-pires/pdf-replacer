"""
EXEMPLO PRÁTICO COMPLETO: Do Zero até PDF em Produção
Passo a passo real com seu template de contrato
"""

import logging
from auto_contract_pdf_generator import AutoContractPDFGenerator
from typing import Dict, Tuple
import psycopg2
from datetime import datetime

# ============================================================================
# CONFIGURAÇÃO INICIAL
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# PASSO 1: Dados de Exemplo (Simulando Banco de Dados)
# ============================================================================

DADOS_EXEMPLO_1 = {
    'nome_da_medica_ou_clinica': 'Dra. Maria Silva - Clínica Estética Premium',
    'cpfcnpjmedicacli': '12.345.678/0001-90',
    'celmedicacli': '(21) 99999-8888',
    'emailmedicacli': 'contato@clinicamaria.com.br',
    'enderecomedical': 'Avenida Paulista, 1000 - Apt 3000',
    'enderecomedica2': 'São Paulo, SP 01311-100 - Brasil',
    
    'nome_paciente': 'João da Silva Santos',
    'cpfpaciente': '123.456.789-00',
    'celpaciente': '(11) 98765-4321',
    'emailpaciente': 'joao.silva@example.com',
    'enderecopacientel': 'Rua das Flores, 123 - Apartamento 456',
    'enderecopaciente2': 'São Paulo, SP 01310-100',
    
    'DD/MM/AAAA': '15/01/2026',
    'valor': 'R$ 5.000,00',
}

DADOS_EXEMPLO_2 = {
    'nome_da_medica_ou_clinica': 'Dr. Carlos Mendes - Cirurgia Plástica',
    'cpfcnpjmedicacli': '98.765.432/0001-12',
    'celmedicacli': '(85) 98888-7777',
    'emailmedicacli': 'contato@drcarlos.com.br',
    'enderecomedical': 'Rua das Acácias, 500',
    'enderecomedica2': 'Fortaleza, CE 60040-531',
    
    'nome_paciente': 'Ana Costa Silva',
    'cpfpaciente': '987.654.321-00',
    'celpaciente': '(85) 99999-2222',
    'emailpaciente': 'ana.costa@example.com',
    'enderecopacientel': 'Avenida Beira Mar, 2000',
    'enderecopaciente2': 'Fortaleza, CE 60060-000',
    
    'DD/MM/AAAA': '20/01/2026',
    'valor': 'R$ 8.500,00',
}

DADOS_EXEMPLO_3 = {
    'nome_da_medica_ou_clinica': 'Dra. Fernanda Oliveira - Dermatologia',
    'cpfcnpjmedicacli': '55.555.666/0001-77',
    'celmedicacli': '(31) 99876-5432',
    'emailmedicacli': 'contato@fernanda-dermatologia.com.br',
    'enderecomedical': 'Savassi Medical Center, Sala 1500',
    'enderecomedica2': 'Belo Horizonte, MG 30140-073',
    
    'nome_paciente': 'Pedro Ferreira Gomes',
    'cpfpaciente': '555.666.777-88',
    'celpaciente': '(31) 98765-4321',
    'emailpaciente': 'pedro.gomes@example.com',
    'enderecopacientel': 'Rua Alagoano, 500 - Apto 201',
    'enderecopaciente2': 'Belo Horizonte, MG 30140-071',
    
    'DD/MM/AAAA': '22/01/2026',
    'valor': 'R$ 3.200,00',
}

# ============================================================================
# PASSO 2: Classe Wrapper com Métodos Práticos
# ============================================================================

class PdfContractManager:
    """Manager para gerar PDFs com fácil integração"""
    
    def __init__(self, template_path: str = 'Contrato_Medico-04_procedimentos.jpg'):
        """Inicializa o gerenciador"""
        self.template_path = template_path
        self.generator = None
        self.load_template()
    
    def load_template(self):
        """Carrega o template da imagem"""
        try:
            self.generator = AutoContractPDFGenerator(self.template_path)
            logger.info(f"✓ Template carregado: {self.template_path}")
        except Exception as e:
            logger.error(f"✗ Erro ao carregar template: {e}")
            raise
    
    def gerar_pdf_simples(
        self,
        dados: Dict,
        output_path: str,
        debug: bool = False
    ) -> Tuple[bool, str]:
        """Gera PDF simples"""
        try:
            logger.info(f"\n📄 Gerando PDF para: {dados.get('nome_paciente', 'Desconhecido')}")
            
            pdf_bytes = self.generator.generate_pdf(
                data=dados,
                output_path=output_path,
                auto_detect=True,
                debug=debug
            )
            
            tamanho = len(pdf_bytes) / 1024
            logger.info(f"✓ PDF gerado com sucesso! ({tamanho:.2f} KB)")
            logger.info(f"  Salvo em: {output_path}")
            
            return True, f"PDF gerado com sucesso! ({tamanho:.2f} KB)"
        
        except ImportError as e:
            msg = "Tesseract não instalado. Use auto_detect=False para modo manual"
            logger.error(f"✗ {msg}")
            return False, msg
        except Exception as e:
            msg = f"Erro ao gerar PDF: {str(e)}"
            logger.error(f"✗ {msg}")
            return False, msg
    
    def gerar_pdf_do_banco(self, contract_id: int) -> Tuple[bool, bytes]:
        """Gera PDF buscando dados do banco PostgreSQL"""
        try:
            logger.info(f"\n🔍 Buscando contrato ID: {contract_id}")
            
            # Conectar ao banco (EDITE ESTES VALORES!)
            conn = psycopg2.connect(
                host="localhost",
                database="clinica_db",
                user="user",
                password="password"
            )
            cursor = conn.cursor()
            
            # Query para buscar dados
            query = """
                SELECT 
                    c.nome as clinica_nome,
                    c.cpf_cnpj as clinica_cpf_cnpj,
                    c.celular as clinica_celular,
                    c.email as clinica_email,
                    c.endereco_linha1 as clinica_endereco1,
                    c.endereco_linha2 as clinica_endereco2,
                    p.nome as paciente_nome,
                    p.cpf as paciente_cpf,
                    p.celular as paciente_celular,
                    p.email as paciente_email,
                    p.endereco_linha1 as paciente_endereco1,
                    p.endereco_linha2 as paciente_endereco2,
                    con.data_contrato,
                    con.valor_total
                FROM contratos con
                JOIN clinicas c ON con.clinica_id = c.id
                JOIN pacientes p ON con.paciente_id = p.id
                WHERE con.id = %s
            """
            
            cursor.execute(query, (contract_id,))
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"⚠ Contrato {contract_id} não encontrado")
                return False, b''
            
            # Montar dados do banco
            dados = {
                'nome_da_medica_ou_clinica': row[0],
                'cpfcnpjmedicacli': row[1],
                'celmedicacli': row[2],
                'emailmedicacli': row[3],
                'enderecomedical': row[4],
                'enderecomedica2': row[5],
                'nome_paciente': row[6],
                'cpfpaciente': row[7],
                'celpaciente': row[8],
                'emailpaciente': row[9],
                'enderecopacientel': row[10],
                'enderecopaciente2': row[11],
                'DD/MM/AAAA': row[12].strftime('%d/%m/%Y'),
                'valor': f"R$ {row[13]:,.2f}",
            }
            
            # Gerar PDF
            output_path = f'contratos/{contract_id}_contrato.pdf'
            
            sucesso, msg = self.gerar_pdf_simples(dados, output_path)
            
            if sucesso:
                with open(output_path, 'rb') as f:
                    pdf_bytes = f.read()
                return True, pdf_bytes
            else:
                return False, b''
        
        except psycopg2.Error as e:
            logger.error(f"✗ Erro no banco de dados: {e}")
            return False, b''
        except Exception as e:
            logger.error(f"✗ Erro: {e}")
            return False, b''
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
    
    def gerar_lote_pdfs(self, lista_dados: list) -> Dict:
        """Gera múltiplos PDFs sequencialmente"""
        logger.info(f"\n📚 Gerando lote de {len(lista_dados)} PDFs...")
        
        resultados = {
            'total': len(lista_dados),
            'sucesso': 0,
            'erro': 0,
            'detalhes': []
        }
        
        for idx, dados in enumerate(lista_dados, 1):
            nome_paciente = dados.get('nome_paciente', f'Paciente {idx}')
            output_path = f"contratos/contrato_{idx:03d}_{nome_paciente.replace(' ', '_')}.pdf"
            
            sucesso, msg = self.gerar_pdf_simples(dados, output_path, debug=False)
            
            if sucesso:
                resultados['sucesso'] += 1
                resultado = '✓'
            else:
                resultados['erro'] += 1
                resultado = '✗'
            
            resultados['detalhes'].append({
                'idx': idx,
                'paciente': nome_paciente,
                'sucesso': sucesso,
                'mensagem': msg
            })
            
            logger.info(f"  [{resultado}] {idx}/{len(lista_dados)} - {nome_paciente}")
        
        # Resumo
        logger.info("\n" + "="*80)
        logger.info("📊 RESUMO DO LOTE")
        logger.info("="*80)
        logger.info(f"✓ Sucesso: {resultados['sucesso']}")
        logger.info(f"✗ Erros: {resultados['erro']}")
        logger.info(f"📊 Taxa: {resultados['sucesso']/len(lista_dados)*100:.1f}%")
        
        return resultados

# ============================================================================
# PASSO 3: Exemplos de Uso Prático
# ============================================================================

if __name__ == "__main__":
    
    # EXEMPLO 1: Um único PDF
    print("\n" + "="*80)
    print("EXEMPLO 1: Gerar Um PDF")
    print("="*80)
    
    manager = PdfContractManager('Contrato_Medico-04_procedimentos.jpg')
    
    sucesso, msg = manager.gerar_pdf_simples(
        dados=DADOS_EXEMPLO_1,
        output_path='contratos/exemplo_1_joao.pdf',
        debug=True  # Mostra logs detalhados
    )
    print(f"\nResultado: {msg}")
    
    # ========================================================================
    
    # EXEMPLO 2: Múltiplos PDFs do mesmo template
    print("\n" + "="*80)
    print("EXEMPLO 2: Gerar Múltiplos PDFs")
    print("="*80)
    
    lista_dados = [DADOS_EXEMPLO_1, DADOS_EXEMPLO_2, DADOS_EXEMPLO_3]
    
    resultados = manager.gerar_lote_pdfs(lista_dados)
    
    print(f"\n✓ Total gerado: {resultados['sucesso']}")
    print(f"✗ Erros: {resultados['erro']}")
    
    # ========================================================================
    
    # EXEMPLO 3: Integrando com Banco de Dados (Comentado - você ativa!)
    print("\n" + "="*80)
    print("EXEMPLO 3: Integração com Banco de Dados")
    print("="*80)
    print("""
    Para usar com banco PostgreSQL:
    
    1. Configure as credenciais em gerar_pdf_do_banco()
    2. Certifique-se que a tabela existe com os campos
    3. Descomente a linha abaixo:
    """)
    
    # sucesso, pdf_bytes = manager.gerar_pdf_do_banco(contract_id=1)
    # if sucesso:
    #     with open('contrato_do_banco.pdf', 'wb') as f:
    #         f.write(pdf_bytes)
    #     print("✓ PDF gerado do banco de dados!")
    
    # ========================================================================
    
    # EXEMPLO 4: Processamento em Paralelo
    print("\n" + "="*80)
    print("EXEMPLO 4: Processamento em Paralelo (Avançado)")
    print("="*80)
    print("""
    Para processar múltiplos PDFs em paralelo:
    
    import concurrent.futures
    
    def gerar_em_paralelo(lista_dados):
        manager = PdfContractManager()
        
        def gerar_um(dados):
            try:
                sucesso, msg = manager.gerar_pdf_simples(
                    dados,
                    f"contratos/{dados['nome_paciente']}.pdf"
                )
                return {'sucesso': sucesso, 'paciente': dados['nome_paciente']}
            except Exception as e:
                return {'sucesso': False, 'erro': str(e)}
        
        # Processar 4 PDFs por vez
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            resultados = list(executor.map(gerar_um, lista_dados))
        
        return resultados
    
    resultados = gerar_em_paralelo(lista_dados)
    """)
    
    # ========================================================================
    
    # EXEMPLO 5: Salvando em S3 (para nuvem)
    print("\n" + "="*80)
    print("EXEMPLO 5: Salvando em AWS S3")
    print("="*80)
    print("""
    Para salvar PDFs em S3:
    
    import boto3
    
    s3 = boto3.client('s3')
    
    manager = PdfContractManager()
    sucesso, msg = manager.gerar_pdf_simples(
        dados=DADOS_EXEMPLO_1,
        output_path='/tmp/contrato.pdf'
    )
    
    if sucesso:
        # Upload para S3
        s3.upload_file(
            '/tmp/contrato.pdf',
            'bucket-name',
            'contratos/contrato_2026_01_15.pdf'
        )
        print("✓ PDF salvo em S3!")
    """)
    
    # ========================================================================
    
    print("\n" + "="*80)
    print("✅ EXEMPLOS CONCLUÍDOS!")
    print("="*80)
    print("""
    Próximas ações:
    1. Editar gerar_pdf_do_banco() com suas credenciais de banco
    2. Testar com seus dados reais
    3. Integrar com sua API/Sistema
    4. Publicar em produção!
    
    Dúvidas? Veja:
    - GUIA_AUTO_DETECT.md
    - QUICK_START_AUTO_DETECT.md
    - auto_contract_pdf_generator.py
    """)

