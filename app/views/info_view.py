from app.models.domain import Domain
from app.models.template import Template
from app.views.base_view import BaseView


class InfoView(BaseView):
    """
    View class for info-related templates.
    """

    @staticmethod
    def render_list(infos):
        """
        Render the info list page for admins.

        Args:
            infos (list): List of info dictionaries

        Returns:
            str: Rendered info list template
        """
        return BaseView.render("infos/list.html", infos=infos)

    @staticmethod
    def render_client_list(client, infos):
        """
        Render the info list page for a specific client.

        Args:
            client (dict): Client data
            infos (list): List of info dictionaries

        Returns:
            str: Rendered client info list template
        """
        # Enrich infos with template and domain information
        for info_data in infos:
            # Enrich with template info
            if "template_id" in info_data and info_data["template_id"]:
                template = Template.get_by_id(info_data["template_id"])
                if template:
                    info_data["template_name"] = template["name"]
                else:
                    info_data["template_name"] = "No Template"
            else:
                info_data["template_name"] = "No Template"

            # Enrich with domain info
            if "domain_id" in info_data and info_data["domain_id"]:
                domain = Domain.get_by_id(info_data["domain_id"])
                if domain:
                    info_data["domain_name"] = domain["name"]
                else:
                    info_data["domain_name"] = "No Domain"
            else:
                info_data["domain_name"] = "No Domain"

        return BaseView.render("infos/client_list.html", client=client, infos=infos)

    @staticmethod
    def render_create_form(client, templates, domains, form_data=None, errors=None):
        """
        Render the info creation form.

        Args:
            client (dict): Client data
            templates (list): List of available templates
            domains (list): List of available domains for the client
            form_data (dict, optional): Form data in case of validation error
            errors (list, optional): Validation errors

        Returns:
            str: Rendered info creation form
        """
        return BaseView.render(
            "infos/create.html",
            client=client,
            templates=templates,
            domains=domains,
            form_data=form_data,
            errors=errors,
        )

    @staticmethod
    def render_edit_form(client, info_data, templates, domains, form_data=None, errors=None):
        """
        Render the info edit form.

        Args:
            client (dict): Client data
            info_data (dict): Info data to edit
            templates (list): List of available templates
            domains (list): List of available domains for the client
            form_data (dict, optional): Form data in case of validation error
            errors (list, optional): Validation errors

        Returns:
            str: Rendered info edit form
        """
        return BaseView.render(
            "infos/edit.html",
            client=client,
            info=info_data,
            templates=templates,
            domains=domains,
            form_data=form_data,
            errors=errors,
        )

    @staticmethod
    def render_view(info_data):
        """
        Render the info view page.

        Args:
            info_data (dict): Info data to view

        Returns:
            str: Rendered info view template
        """
        return BaseView.render("infos/view.html", info=info_data)
