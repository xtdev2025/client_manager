#!/usr/bin/env python
"""
Script para extrair apenas o conteúdo do <body> dos templates
Remove DOCTYPE, html, head tags, mantém apenas o conteúdo
"""

import re
import sys

def extract_body_content(html_content):
    """
    Extrai apenas o conteúdo entre <body> e </body>
    """
    # Encontrar o conteúdo entre <body> e </body>
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
    
    if body_match:
        return body_match.group(1).strip()
    else:
        # Se não encontrar body, retorna o conteúdo completo
        # (provavelmente já está sem as tags)
        return html_content.strip()

def process_templates_file():
    """
    Processa o arquivo templates_data.py e extrai apenas o body
    """
    input_file = '/home/rootkit/Apps/xPages/client_manager/app/templates_data.py'
    output_file = '/home/rootkit/Apps/xPages/client_manager/app/templates_data_fixed.py'
    
    print("📖 Lendo templates_data.py...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encontrar todos os blocos de content="""..."""
    pattern = r'(content\s*=\s*""")(.*?)(""")'
    
    def replace_content(match):
        prefix = match.group(1)
        html_content = match.group(2)
        suffix = match.group(3)
        
        # Extrair apenas o body
        body_content = extract_body_content(html_content)
        
        return f"{prefix}\n{body_content}\n{suffix}"
    
    # Substituir todos os conteúdos
    new_content = re.sub(pattern, replace_content, content, flags=re.DOTALL)
    
    # Salvar novo arquivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Arquivo processado salvo em: {output_file}")
    print()
    print("Para aplicar as mudanças:")
    print("  mv app/templates_data.py app/templates_data_original.py")
    print("  mv app/templates_data_fixed.py app/templates_data.py")

if __name__ == '__main__':
    process_templates_file()
