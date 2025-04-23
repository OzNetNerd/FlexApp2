from flask import Blueprint, request, jsonify
from app.models import User, Company, Opportunity

from app.utils.app_logging import get_logger

logger = get_logger()

search_bp = Blueprint("search_bp", __name__, url_prefix="/api/search")


@search_bp.route("/")
def search():
    query = request.args.get("q", "").strip()
    if not query or len(query) < 2:
        logger.warning("Search query is too short or empty.")
        return jsonify([])

    results = []

    logger.debug(f"Searching for users with query: {query}")
    users = User.query.filter(User.username.ilike(f"%{query}%") | User.name.ilike(f"%{query}%")).limit(5).all()
    results.extend(
        [
            {
                "id": user.id,
                "text": user.name,
                "type": "user",
                "url": f"/users/{user.id}",
            }
            for user in users
        ]
    )

    logger.debug(f"Searching for companies with query: {query}")
    companies = Company.query.filter(Company.name.ilike(f"%{query}%")).limit(5).all()
    results.extend(
        [
            {
                "id": company.id,
                "text": company.name,
                "type": "company",
                "url": f"/companies/{company.id}",
            }
            for company in companies
        ]
    )

    logger.debug(f"Searching for opportunities with query: {query}")
    opportunities = Opportunity.query.filter(Opportunity.name.ilike(f"%{query}%")).limit(5).all()
    results.extend(
        [
            {
                "id": opportunity.id,
                "text": opportunity.name,
                "type": "opportunity",
                "url": f"/opportunities/{opportunity.id}",
            }
            for opportunity in opportunities
        ]
    )

    logger.info(f"Returning {len(results)} search results.")
    return jsonify(results)


@search_bp.route("/mentions")
def mentions_search():
    query = request.args.get("q", "").strip()
    mention_type = request.args.get("type", "user")

    logger.debug(f"Searching for mentions with query: {query} and type: {mention_type}")
    results = []
    # Commented out as it seems this function might not exist yet
    # entities = search_mentions(query, mention_type)

    # Temporary implementation
    if mention_type == "user":
        entities = (
            User.query.filter(
                User.username.ilike(f"%{query}%")
                | User.name.ilike(f"%{query}%")
                | User.first_name.ilike(f"%{query}%")
                | User.last_name.ilike(f"%{query}%")
            )
            .limit(10)
            .all()
        )

        for entity in entities:
            results.append(
                {
                    "id": entity.id,
                    "username": entity.username,
                    "name": entity.name,
                    "text": f"@{entity.username}",
                }
            )
    elif mention_type == "company":
        entities = Company.query.filter(Company.name.ilike(f"%{query}%")).limit(10).all()

        for entity in entities:
            results.append(
                {
                    "id": entity.id,
                    "name": entity.name,
                    "text": f"#{entity.name}",
                }
            )

    logger.info(f"Returning {len(results)} mention results.")
    return jsonify(results)


@search_bp.route("/users")
def users_data():
    query = request.args.get("q", "").strip()

    if query:
        logger.debug(f"Searching for users with query: {query}")
        users = (
            User.query.filter(
                User.username.ilike(f"%{query}%")
                | User.name.ilike(f"%{query}%")
                | User.first_name.ilike(f"%{query}%")
                | User.last_name.ilike(f"%{query}%")
                | User.email.ilike(f"%{query}%")
            )
            .order_by(User.name)
            .limit(10)
            .all()
        )
    else:
        users = User.query.order_by(User.name).limit(30).all()

    data = [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "name": user.name or f"{user.first_name} {user.last_name}".strip(),
        }
        for user in users
    ]
    return jsonify({"data": data})


@search_bp.route("/companies")
def companies_data():
    query = request.args.get("q", "").strip()

    if query:
        logger.debug(f"Searching for companies with query: {query}")
        companies = Company.query.filter(Company.name.ilike(f"%{query}%")).order_by(Company.name).limit(10).all()
    else:
        companies = Company.query.order_by(Company.name).limit(30).all()

    data = [
        {
            "id": company.id,
            "name": company.name,
        }
        for company in companies
    ]
    return jsonify({"data": data})
