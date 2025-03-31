from app.models import Opportunity, Company, db
from app.routes.web import opportunities_bp
from app.routes.web.generic import GenericWebRoutes
import logging
from app.routes.ui.opportunities import get_opportunity_tabs


logger = logging.getLogger(__name__)


class OpportunityCRUDRoutes(GenericWebRoutes):
    """
    Custom CRUD routes for Opportunity model.
    """

    def _preprocess_form_data(self, form_data):
        if hasattr(form_data, 'form'):  # Check if it's a Request object
            # Safely extract data from form
            form_dict = {}
            for k, v in form_data.form.items():
                if isinstance(v, list) and len(v) > 0:
                    form_dict[k] = v[0]
                else:
                    form_dict[k] = v

            # Process company name
            company_name = form_dict.get("company.name", "").strip()

            if company_name:
                company = Company.query.filter_by(name=company_name).first()
                if not company:
                    logger.info(f"Creating new company: {company_name}")
                    company = Company(name=company_name)
                    db.session.add(company)
                    db.session.commit()
                form_dict["company_id"] = company.id

            # Remove 'company.name' as it's not a valid model field
            form_dict.pop("company.name", None)
            return form_dict
        else:
            # Regular dictionary processing
            company_name = form_data.get("company_name", "").strip()
            if company_name:
                company = Company.query.filter_by(name=company_name).first()
                if not company:
                    logger.info(f"Creating new company: {company_name}")
                    company = Company(name=company_name)
                    db.session.add(company)
                    db.session.commit()
                form_data["company_id"] = company.id

            # Remove 'company_name' as it's not a valid model field
            form_data.pop("company_name", None)
            return form_data


opportunity_routes = OpportunityCRUDRoutes(
    blueprint=opportunities_bp,
    model=Opportunity,
    index_template="entity_tables/opportunities.html",
    required_fields=["name"],
    unique_fields=[],
    get_tabs_function=get_opportunity_tabs,
)
