import logging
from models import CRISPScore
from routes.web import crisp_scores_bp
from routes.web.generic import GenericWebRoutes

logger = logging.getLogger(__name__)

class CRISPScoreCRUDRoutes(GenericWebRoutes):
    """
    CRUD routes for CRISP score records tied to relationships.
    """

crisp_score_routes = CRISPScoreCRUDRoutes(
    blueprint=crisp_scores_bp,
    model=CRISPScore,
    required_fields=['relationship_id', 'c_score', 'r_score', 'i_score', 's_score', 'p_score'],
    index_template='crisp_scores.html',
)
