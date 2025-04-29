# app/routes/web/contacts.py
from app.models.pages.contact import Contact
from app.routes.web.blueprint_factory import create_crud_blueprint

contacts_bp = create_crud_blueprint(Contact)
