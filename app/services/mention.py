# import re
# from app.models import User, Company
# from flask import current_app
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# def process_mentions(text):
#     """
#     Process text content to replace mentions with HTML links.
#
#     Supports:
#     - @username for users
#     - #company for companies
#
#     Returns tuple: (processed_text, mentioned_users, mentioned_companies)
#     """
#     if not text:
#         logger.warning("Empty text provided to process_mentions.")
#         return text, [], []
#
#     mentioned_users = []
#     mentioned_companies = []
#
#     # Process user mentions (@username)
#     def replace_user(match):
#         username = match.group(1)
#         user = User.query.filter_by(username=username).first()
#         if user:
#             mentioned_users.append(user)
#             return f'<a href="/users/{user.id}" class="mention user-mention">@{username}</a>'
#         logger.debug(f"User '{username}' not found.")
#         return match.group(0)
#
#     # Process company mentions (#company)
#     def replace_company(match):
#         company_name = match.group(1)
#         company = Company.query.filter(Company.name.ilike(company_name)).first()
#         if company:
#             mentioned_companies.append(company)
#             return f'<a href="/companies/{company.id}" class="mention company-mention">#{company_name}</a>'
#         logger.debug(f"Company '{company_name}' not found.")
#         return match.group(0)
#
#     # Apply replacements
#     processed = re.sub(r"@(\w+)", replace_user, text)
#     processed = re.sub(r"#(\w+)", replace_company, processed)
#
#     logger.info(f"Processed text: {processed}")
#     return processed, mentioned_users, mentioned_companies
#
#
# def search_mentions(query, mention_type):
#     """
#     Search for users or companies based on query string.
#
#     Args:
#         query: The search query string
#         mention_type: Either 'user' (@) or 'company' (#)
#
#     Returns:
#         List of matching results
#     """
#     if not query:
#         logger.warning("Empty query provided to search_mentions.")
#         return []
#
#     logger.debug(f"Searching for mentions of type '{mention_type}' with query '{query}'.")
#
#     if mention_type == "user":
#         return User.search_by_username(query)
#     elif mention_type == "company":
#         return Company.search_by_name(query)
#
#     logger.error(f"❌ Invalid mention_type: '{mention_type}'")
#     return []
