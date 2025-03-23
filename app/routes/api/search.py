from flask import Blueprint, request, jsonify
from app.models import User, Company, Opportunity
from app.services.mention import search_mentions
import logging

logger = logging.getLogger(__name__)

search_bp = Blueprint("search", __name__, url_prefix="/api/search")


@search_bp.route("/")
def search():
    """
    Perform a global search across users, companies, and opportunities.

    Query Parameters:
        q (str): The search string (must be at least 2 characters).

    Returns:
        Response: A JSON array of results. Each result includes:
            - id (int): The entity's ID.
            - text (str): The display name.
            - type (str): One of 'user', 'company', or 'opportunity'.
            - url (str): A URL to the entity's detail page.
    """
    query = request.args.get("q", "").strip()
    if not query or len(query) < 2:
        logger.warning("Search query is too short or empty.")
        return jsonify([])

    results = []

    logger.debug(f"Searching for users with query: {query}")
    users = (
        User.query.filter(
            User.username.ilike(f"%{query}%") | User.name.ilike(f"%{query}%")
        )
        .limit(5)
        .all()
    )
    results.extend([
        {
            "id": user.id,
            "text": user.name,
            "type": "user",
            "url": f"/users/{user.id}",
        }
        for user in users
    ])

    logger.debug(f"Searching for companies with query: {query}")
    companies = Company.query.filter(Company.name.ilike(f"%{query}%")).limit(5).all()
    results.extend([
        {
            "id": company.id,
            "text": company.name,
            "type": "company",
            "url": f"/companies/{company.id}",
        }
        for company in companies
    ])

    logger.debug(f"Searching for opportunities with query: {query}")
    opportunities = Opportunity.query.filter(Opportunity.name.ilike(f"%{query}%")).limit(5).all()
    results.extend([
        {
            "id": opportunity.id,
            "text": opportunity.name,
            "type": "opportunity",
            "url": f"/opportunities/{opportunity.id}",
        }
        for opportunity in opportunities
    ])

    logger.info(f"Returning {len(results)} search results.")
    return jsonify(results)


@search_bp.route("/mentions")
def mentions_search():
    """
    Search for users or companies to mention using @ or #.

    Query Parameters:
        q (str): The partial search query.
        type (str): 'user' or 'company'. Defaults to 'user'.

    Returns:
        Response: A JSON array of mention suggestions.
    """
    query = request.args.get("q", "").strip()
    mention_type = request.args.get("type", "user")

    logger.debug(f"Searching for mentions with query: {query} and type: {mention_type}")
    results = []
    items = search_mentions(query, mention_type)

    for item in items:
        if mention_type == "user":
            results.append({
                "id": item.id,
                "username": item.username,
                "name": item.name,
                "text": f"@{item.username}",
            })
        elif mention_type == "company":
            results.append({
                "id": item.id,
                "name": item.name,
                "text": f"#{item.name}",
            })

    logger.info(f"Returning {len(results)} mention results.")
    return jsonify(results)
