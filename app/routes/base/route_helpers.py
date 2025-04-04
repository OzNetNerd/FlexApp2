def register_standard_routes(blueprint, crud_service, model_name):
    """
    Register standard CRUD routes on a blueprint.

    Args:
        blueprint: Flask Blueprint to register routes on
        crud_service: Instance of CRUDService for data operations
        model_name: Name of the model (for error messages)
    """

    @blueprint.route("/", methods=["GET"])
    def get_all():
        items = crud_service.get_all()
        return jsonify([item.to_dict() for item in items])

    @blueprint.route("/<int:item_id>", methods=["GET"])
    def get_one(item_id):
        item = crud_service.get_by_id(item_id)
        if not item:
            return jsonify({"error": f"{model_name} not found"}), 404
        return jsonify(item.to_dict())

    @blueprint.route("/", methods=["POST"])
    def create():
        data = request.get_json()
        result = crud_service.create(data)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result), 201

    @blueprint.route("/<int:item_id>", methods=["PUT"])
    def update(item_id):
        data = request.get_json()
        result = crud_service.update(item_id, data)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)

    @blueprint.route("/<int:item_id>", methods=["DELETE"])
    def delete(item_id):
        result = crud_service.delete(item_id)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)