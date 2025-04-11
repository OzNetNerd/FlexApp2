# from flask import jsonify, request, Blueprint
# import logging
# from app.services.crud_service import CRUDService
#
# logger = logging.getLogger(__name__)
#
#
# def register_api_crud_routes(blueprint: Blueprint, service: CRUDService, entity_name: str):
#     """
#     Register standard CRUD API routes on a blueprint.
#
#     Args:
#         blueprint: Flask Blueprint to register routes on
#         service: CRUD service instance for data operations
#         entity_name: Name of the entity (for error messages)
#     """
#     entity_title = entity_name.capitalize()
#
#     @blueprint.route("/", methods=["GET"])
#     def get_all():
#         items = service.get_all()
#         return jsonify([item.to_dict() for item in items])
#
#     @blueprint.route("/<int:entity_id>", methods=["GET"])
#     def get_one(entity_id):
#         item = service.get_by_id(entity_id)
#         if not item:
#             return jsonify({"error": f"{entity_title} not found"}), 404
#         return jsonify(item.to_dict())
#
#     @blueprint.route("/", methods=["POST"])
#     def create():
#         data = request.get_json()
#         result = service.create(data)
#         if "error" in result:
#             return jsonify(result), 400
#         return jsonify(result), 201
#
#     @blueprint.route("/<int:entity_id>", methods=["PUT"])
#     def update(entity_id):
#         data = request.get_json()
#         result = service.update(entity_id, data)
#         if "error" in result:
#             return jsonify(result), 400
#         return jsonify(result)
#
#     @blueprint.route("/<int:entity_id>", methods=["DELETE"])
#     def delete(entity_id):
#         result = service.delete(entity_id)
#         if "error" in result:
#             return jsonify(result), 400
#         return jsonify(result)
#
#     logger.info(f"Registered API CRUD routes for {entity_name}")
