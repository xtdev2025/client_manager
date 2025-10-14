from bson import ObjectId
from flask import Blueprint, abort, current_app, flash, redirect, request, url_for, send_file
from flask_login import current_user, login_required

from app.controllers.auth import admin_required
from app.models.template import Template
from app.services.audit_service import AuditService
from app.views.template_view import TemplateView

template = Blueprint("template", __name__, url_prefix="/templates")


@template.route("/")
@login_required
@admin_required
def list_templates():
    """List all templates"""
    templates = Template.get_all()
    return TemplateView.render_list(templates)


@template.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_template():
    """Create a new template"""
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        content = request.form.get("content", "{}")
        status = request.form.get("status", "active")

        if not name:
            flash("Please fill all required fields", "danger")
            return TemplateView.render_create_form(
                form_data={
                    "name": name,
                    "description": description,
                    "content": content,
                    "status": status,
                }
            )

        # Create template
        success, message = Template.create(name, description, content, status)

        if success:
            # Log template creation in audit trail
            AuditService.log_template_action(
                "create", message, {"name": name, "description": description, "status": status}
            )
            flash("Template created successfully", "success")
            return redirect(url_for("template.list_templates"))
        else:
            flash(f"Error creating template: {message}", "danger")

    return TemplateView.render_create_form()


@template.route("/edit/<template_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_template(template_id):
    """Edit template information"""
    template_data = Template.get_by_id(template_id)
    if not template_data:
        flash("Template not found", "danger")
        return redirect(url_for("template.list_templates"))

    if request.method == "POST":
        # Build the data object with all fields including slug
        data = {
            "name": request.form.get("name"),
            "slug": request.form.get("slug"),  # Capture slug from form
            "description": request.form.get("description"),
            "status": request.form.get("status", "active"),
        }

        # Pages configuration
        pages = []
        page_index = 0
        has_home = False

        while True:
            page_id = request.form.get(f"pages[{page_index}][id]")
            if page_id is None:
                break

            page_name = request.form.get(f"pages[{page_index}][name]", "").strip()
            page_type_raw = request.form.get(f"pages[{page_index}][type]")
            page_type = page_type_raw.strip() if page_type_raw else ""
            page_content = request.form.get(f"pages[{page_index}][content]", "")
            page_order = request.form.get(f"pages[{page_index}][order]", str(page_index + 1))
            page_fixed = request.form.get(f"pages[{page_index}][fixed]") == "true"
            page_slug_raw = request.form.get(f"pages[{page_index}][slug]", "").strip()
            normalized_slug = Template.generate_slug(page_slug_raw) if page_slug_raw else Template.generate_slug(page_name) if page_name else ""

            # Skip empty pages
            if not page_name:
                page_index += 1
                continue

            # Validate only one home page
            if page_type == "home":
                if has_home:
                    page_type = "custom"  # Force to custom if there's already a home
                else:
                    has_home = True

            page_data = {
                "id": page_id,
                "slug": normalized_slug,
                "name": page_name,
                "content": page_content,
                "order": int(page_order),
                "fixed": page_fixed,
            }

            if page_type:
                page_data["type"] = page_type

            pages.append(page_data)
            page_index += 1

        # Always include pages in data, even if empty
        data["pages"] = pages

        # Debug logging
        current_app.logger.info(f"Updating template {template_id} with {len(pages)} pages")
        current_app.logger.debug(f"Template data: {data}")

        # Update template
        success, message = Template.update(template_id, data)

        if success:
            # Log template update in audit trail
            AuditService.log_template_action(
                "update",
                template_id,
                {
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "status": data.get("status"),
                    "pages_count": len(pages),
                },
            )
            flash("Template atualizado com sucesso!", "success")
            # Permanece na mesma página de edição
            return redirect(url_for("template.edit_template", template_id=template_id))
        else:
            flash(f"Erro ao atualizar template: {message}", "danger")

    return TemplateView.render_edit_form(template_data)

@template.route("/download/<template_id>")
@login_required
@admin_required
def download_template(template_id):
    """Download a template backup (e.g., as a JSON file)"""
    template_data = Template.get_by_id(template_id)
    if not template_data:
        flash("Template não encontrado para download.", "danger")
        return redirect(url_for("template.list_templates"))

    try:
        # 1. Converte o objeto template (que pode conter BSON types) para um dict JSON-serializável.
        # Você precisará de uma função auxiliar para converter BSON/ObjectId para string se usar
        # a serialização JSON padrão do Python/Flask.
        # Ex: template_data.pop("_id", None) # Remove _id para facilitar a importação futura
        # Ou usar uma função de serialização JSON que lide com BSON.
        
        # Exemplo simples (assumindo que a maioria dos campos já é serializável)
        data_to_export = template_data.copy()
        
        # Converte o ObjectId e remove campos desnecessários para backup/restauração
        # É crucial que sua classe Template tenha um método para exportar dados limpos
        if '_id' in data_to_export and isinstance(data_to_export['_id'], ObjectId):
             data_to_export['_id'] = str(data_to_export['_id'])
        data_to_export.pop("createdAt", None)
        data_to_export.pop("updatedAt", None)

        import json
        from io import BytesIO

        # 2. Cria o conteúdo do arquivo JSON
        json_content = json.dumps(data_to_export, indent=4, ensure_ascii=False)
        buffer = BytesIO(json_content.encode('utf-8'))
        
        filename = f"template_{template_data.get('slug', template_id)}_backup.json"

        # 3. Retorna o arquivo para o download
        AuditService.log_template_action("download", template_id, {"name": template_data.get('name')})
        
        return send_file(
            buffer,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        current_app.logger.error(f"Erro ao gerar backup do template {template_id}: {e}")
        flash("Erro interno ao gerar o arquivo de backup.", "danger")
        return redirect(url_for("template.list_templates"))

@template.route("/clone/<template_id>", methods=["POST"])
@login_required
@admin_required
def clone_template(template_id):
    """Clone an existing template, including all its subdocuments (pages, versions, etc.)."""
    
    # 1. Busca o template original
    original_template = Template.get_by_id(template_id)
    if not original_template:
        flash("Template não encontrado para clonagem.", "danger")
        return redirect(url_for("template.list_templates"))

    # Para uso no log e flash message
    original_name = original_template.get('name', 'Template Original')

    # 2. Prepara os dados para o novo template (clone)
    # Copia os dados, que agora incluem 'pages', 'versions', etc.
    clone_data = original_template.copy()
    
    # Remove campos específicos do MongoDB (_id, createdAt, updatedAt)
    # Estes serão regenerados na inserção
    clone_data.pop("_id", None)
    clone_data.pop("createdAt", None)
    clone_data.pop("updatedAt", None)
    
    # Define um novo nome e slug para o clone
    new_name = f"{original_name} (Cópia)"
    clone_data["name"] = new_name
    
    # É uma boa prática limpar o slug ou gerar um novo, se o modelo o utiliza
    clone_data.pop("slug", None) 
    
    # 3. Cria o novo template usando o dicionário completo
    # É crucial que este novo método no seu modelo lide com a inserção
    # de todos os campos no MongoDB/banco de dados.
    success, new_id = Template.insert_from_dict(clone_data)

    if success:
        # 4. Log template creation in audit trail
        AuditService.log_template_action(
            "clone", 
            new_id, 
            {"original_id": template_id, "new_name": new_name, "pages_cloned": len(clone_data.get('pages', []))}
        )
        flash(f"Template '{original_name}' clonado com sucesso como '{new_name}'.", "success")
        return redirect(url_for("template.edit_template", template_id=new_id))
    else:
        flash(f"Erro ao clonar template: {new_id}", "danger")
        return redirect(url_for("template.list_templates"))

@template.route("/delete/<template_id>", methods=["POST"])
@login_required
@admin_required
def delete_template(template_id):
    """Delete a template"""
    if request.method == "POST":
        # Get template data before deletion for audit log
        template_data = Template.get_by_id(template_id)
        template_name = template_data.get("name", "unknown") if template_data else "unknown"

        success, message = Template.delete(template_id)

        if success:
            # Log template deletion in audit trail
            AuditService.log_template_action("delete", template_id, {"name": template_name})
            flash("Template deleted successfully", "success")
        else:
            flash(f"Error deleting template: {message}", "danger")

    return redirect(url_for("template.list_templates"))


@template.route("/view/<template_id>")
@login_required
@admin_required
def view_template(template_id):
    """View template details"""
    template_data = Template.get_by_id(template_id)
    if not template_data:
        flash("Template not found", "danger")
        return redirect(url_for("template.list_templates"))

    return TemplateView.render_view(template_data)
