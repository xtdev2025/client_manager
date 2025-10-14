from bson import ObjectId
from flask import Blueprint, current_app, flash, redirect, request, send_file, url_for
from flask_login import login_required

from app.controllers.auth import admin_required
from app.controllers.crud_mixin import CrudControllerMixin
from app.models.template import Template
from app.repositories.base import ModelCrudRepository
from app.schemas.crud import TemplateCreateSchema, TemplateUpdateSchema
from app.views.template_view import TemplateView
from app.utils.crud import CrudOperationResult
from app.services.audit_helper import log_change

template = Blueprint("template", __name__, url_prefix="/templates")


class TemplateCrudController(CrudControllerMixin):
    entity_name = "Template"
    audit_entity = "template"
    list_endpoint = "template.list_templates"
    detail_endpoint = "template.view_template"
    create_schema = TemplateCreateSchema
    update_schema = TemplateUpdateSchema
    view = TemplateView

    def perform_update(self, template_id: str, schema: TemplateUpdateSchema | None) -> CrudOperationResult:
        base_payload = schema.to_payload() if schema else {}
        pages = self._extract_pages_from_request()
        base_payload["pages"] = pages

        log_summary = {
            "name": base_payload.get("name"),
            "status": base_payload.get("status"),
            "pages_count": len(pages),
        }
        self.set_audit_payload({k: v for k, v in log_summary.items() if v is not None})

        current_app.logger.info(f"Updating template {template_id} with {len(pages)} pages")
        current_app.logger.debug(f"Template data: {base_payload}")

        return self.repository.update(template_id, base_payload)

    def perform_create(self, schema: TemplateCreateSchema | None, **route_kwargs) -> CrudOperationResult:
        payload = schema.to_payload() if schema else {}
        self.set_audit_payload(payload)
        return self.repository.create(payload)

    def update_success_message(self, result: CrudOperationResult) -> str:
        return result.message or "Template atualizado com sucesso!"

    def after_update_redirect(self, template_id: str, result: CrudOperationResult):
        return redirect(url_for("template.edit_template", template_id=template_id))

    def _extract_pages_from_request(self):
        pages = []
        page_index = 0
        has_home = False

        while True:
            page_id = request.form.get(f"pages[{page_index}][id]")
            if page_id is None:
                break

            page_name = (request.form.get(f"pages[{page_index}][name]", "") or "").strip()
            page_type_raw = request.form.get(f"pages[{page_index}][type]")
            page_type = page_type_raw.strip() if page_type_raw else ""
            page_content = request.form.get(f"pages[{page_index}][content]", "")
            page_order = request.form.get(f"pages[{page_index}][order]", str(page_index + 1))
            page_fixed = request.form.get(f"pages[{page_index}][fixed]") == "true"
            page_slug_raw = (request.form.get(f"pages[{page_index}][slug]", "") or "").strip()
            normalized_slug = (
                Template.generate_slug(page_slug_raw)
                if page_slug_raw
                else Template.generate_slug(page_name)
                if page_name
                else ""
            )

            page_index += 1

            if not page_name:
                continue

            if page_type == "home":
                if has_home:
                    page_type = "custom"
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

        return pages


template_crud = TemplateCrudController(ModelCrudRepository(Template))


@template.route("/")
@login_required
@admin_required
def list_templates():
    """List all templates"""
    return template_crud.list_view()


@template.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_template():
    """Create a new template"""
    return template_crud.create_view()


@template.route("/edit/<template_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_template(template_id):
    """Edit template information"""
    return template_crud.edit_view(template_id)

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
        log_change("template", "download", template_id, payload={"name": template_data.get("name")})

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
        log_change(
            "template",
            "clone",
            new_id,
            payload={
                "original_id": template_id,
                "new_name": new_name,
                "pages_cloned": len(clone_data.get("pages", [])),
            },
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
    return template_crud.delete_view(template_id)


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
