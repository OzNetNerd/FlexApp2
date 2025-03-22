from app.routes.web import main_bp
from app.routes.base.components.template_renderer import render_safely

@main_bp.route('/')
def index():
    context = {}
    fallback_message = "Sorry, we couldn't load the homepage. Please try again later."
    return render_safely('index.html', context, fallback_message)