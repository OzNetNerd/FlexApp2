from app.app import create_app
from app.models import db, User, Company, Contact, CapabilityCategory, Capability, CompanyCapability
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


def create_or_update(model, match_by: dict, data: dict):
    instance = model.query.filter_by(**match_by).first()
    if instance:
        for key, value in data.items():
            setattr(instance, key, value)
        logger.info(f"Updated existing {model.__name__}: {match_by}")
    else:
        instance = model(**{**match_by, **data})
        db.session.add(instance)
        logger.info(f"Created new {model.__name__}: {match_by}")
    return instance


def seed_users():
    users = [
        ("alice", "Alice Johnson", "alice@example.com"),
        ("bob", "Bob Smith", "bob@example.com"),
        ("carol", "Carol White", "carol@example.com"),
        ("dave", "Dave Black", "dave@example.com"),
        ("eve", "Eve Grey", "eve@example.com"),
    ]

    for username, name, email in users:
        create_or_update(
            User,
            {"username": username},
            {
                "name": name,
                "email": email,
                "password_hash": generate_password_hash("password"),
                "is_admin": False,
            },
        )
    db.session.commit()
    print("✅ Users seeded.")


def seed_companies():
    companies = [
        ("FlexTech", "A flexible software consultancy."),
        ("CloudCorp", "Leaders in scalable cloud infrastructure."),
        ("DataSolve", "Data-driven business intelligence solutions."),
        ("CyberTrust", "Next-gen cybersecurity solutions."),
        ("GreenGrid", "Sustainable smart grid technology provider."),
    ]

    for name, description in companies:
        create_or_update(Company, {"name": name}, {"description": description})
    db.session.commit()
    print("✅ Companies seeded.")


def seed_contacts():
    companies = Company.query.all()
    users = User.query.all()
    first_names = ["Liam", "Noah", "Olivia", "Emma", "Ava"]
    last_names = ["Walker", "Lee", "Davis", "Martin", "Lopez"]

    for i in range(5):
        company = companies[i % len(companies)]
        create_or_update(
            Contact,
            {
                "first_name": first_names[i],
                "last_name": last_names[i],
                "email": f"{first_names[i].lower()}@{company.name.lower()}.com",
            },
            {
                "phone": f"0400{i}12345",
                "company": company,
            },
        )
    db.session.commit()
    print("✅ Contacts seeded.")


def seed_capabilities_and_categories():
    categories = ["Security", "Data", "Infrastructure", "DevOps", "AI"]
    for category in categories:
        create_or_update(CapabilityCategory, {"name": category}, {})
    db.session.commit()

    capability_map = {
        "Security": ["Penetration Testing", "Risk Assessment"],
        "Data": ["ETL", "Data Warehousing"],
        "Infrastructure": ["Load Balancing"],
        "DevOps": ["CI/CD Pipelines"],
        "AI": ["ML Model Training"]
    }

    for category_name, capability_names in capability_map.items():
        category = CapabilityCategory.query.filter_by(name=category_name).first()
        for cap_name in capability_names:
            create_or_update(Capability, {"name": cap_name}, {"category": category})
    db.session.commit()
    print("✅ Capabilities and categories seeded.")


def seed_company_capabilities():
    companies = Company.query.all()
    capabilities = Capability.query.all()

    for i, company in enumerate(companies):
        cap = capabilities[i % len(capabilities)]
        existing = CompanyCapability.query.filter_by(company_id=company.id, capability_id=cap.id).first()
        if not existing:
            db.session.add(CompanyCapability(company=company, capability=cap))
    db.session.commit()
    print("✅ CompanyCapabilities seeded.")


def seed_demo_data():
    app = create_app()
    with app.app_context():
        try:
            seed_users()
            seed_companies()
            seed_contacts()
            seed_capabilities_and_categories()
            seed_company_capabilities()
            print("🎉 All demo data seeded successfully.")
        except IntegrityError as e:
            db.session.rollback()
            print(f"❌ IntegrityError: {e}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error seeding data: {e}")


if __name__ == "__main__":
    seed_demo_data()