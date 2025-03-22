from flask import request, jsonify
from app.routes.api import api_table_config_bp
from app.models.table_config import TableConfig
import logging

logger = logging.getLogger(__name__)

@api_table_config_bp.route('/<string:table_name>', methods=['GET'])
def get_config(table_name):
    """Get the table configuration for the given table name."""
    logger.debug(f"Fetching configuration for table: {table_name}")
    config = TableConfig.get_config(table_name)
    logger.info(f"Configuration for table '{table_name}' fetched successfully.")
    return jsonify(config)


@api_table_config_bp.route('/<string:table_name>', methods=['POST'])
def save_config(table_name):
    """Save the table configuration for the given table name."""
    config_data = request.json

    if not config_data:
        logger.warning("No configuration data provided for saving.")
        return jsonify({'error': 'No configuration data provided'}), 400

    TableConfig.set_config(table_name, config_data)
    logger.info(f"Configuration for table '{table_name}' saved successfully.")
    return jsonify({'success': True})


@api_table_config_bp.route('/<string:table_name>/reset', methods=['POST'])
def reset_config(table_name):
    """Reset the table configuration to default for the given table name."""
    logger.debug(f"Resetting configuration to default for table: {table_name}")

    default_configs = {
        'users': [
            {'field': 'id', 'headerName': 'ID', 'hide': False, 'width': 60, 'comparator': 'number'},
            {'field': 'username', 'headerName': 'Username', 'hide': False, 'width': 120},
            {'field': 'name', 'headerName': 'Name', 'hide': False, 'width': 200},
            {'field': 'email', 'headerName': 'Email', 'hide': False, 'width': 200},
            {'field': 'created_at', 'headerName': 'Created', 'hide': False, 'width': 150, 'comparator': 'date'}
        ],
        'companies': [
            {'field': 'id', 'headerName': 'ID', 'hide': False, 'width': 60, 'comparator': 'number'},
            {'field': 'name', 'headerName': 'Name', 'hide': False, 'width': 200},
            {'field': 'description', 'headerName': 'Description', 'hide': False, 'width': 300},
            {'field': 'created_at', 'headerName': 'Created', 'hide': False, 'width': 150, 'comparator': 'date'}
        ],
        'contacts': [
            {'field': 'id', 'headerName': 'ID', 'hide': False, 'width': 60, 'comparator': 'number'},
            {'field': 'first_name', 'headerName': 'First Name', 'hide': False, 'width': 150},
            {'field': 'last_name', 'headerName': 'Last Name', 'hide': False, 'width': 150},
            {'field': 'email', 'headerName': 'Email', 'hide': False, 'width': 200},
            {'field': 'phone', 'headerName': 'Phone', 'hide': False, 'width': 150},
            {'field': 'company_id', 'headerName': 'Company', 'hide': False, 'width': 200},
            {'field': 'created_at', 'headerName': 'Created', 'hide': False, 'width': 150, 'comparator': 'date'}
        ],
        'opportunities': [
            {'field': 'id', 'headerName': 'ID', 'hide': False, 'width': 60, 'comparator': 'number'},
            {'field': 'name', 'headerName': 'Name', 'hide': False, 'width': 200},
            {'field': 'description', 'headerName': 'Description', 'hide': False, 'width': 300},
            {'field': 'opportunityStage', 'headerName': 'Stage', 'hide': False, 'width': 120}, # Changed from 'status'
            {'field': 'value', 'headerName': 'Value', 'hide': False, 'width': 120, 'valueFormatter': 'money',
             'comparator': 'number', 'filter': 'agNumberColumnFilter'}, # Added filter type
            {'field': 'company_id', 'headerName': 'Company', 'hide': False, 'width': 200, 'valueFormatter': 'company'},
            {'field': 'created_at', 'headerName': 'Created', 'hide': False, 'width': 150, 'comparator': 'date'}
        ]
    }

    if table_name not in default_configs:
        logger.error(f"No default configuration found for table '{table_name}'.")
        return jsonify({'error': f'No default configuration found for {table_name}'}), 404

    TableConfig.set_config(table_name, default_configs[table_name])
    logger.info(f"Configuration for table '{table_name}' reset to default successfully.")
    return jsonify({'success': True})