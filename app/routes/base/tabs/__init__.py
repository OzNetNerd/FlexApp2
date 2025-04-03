from app.routes.base.tabs.contacts import CONTACTS_TABS
from app.routes.base.tabs.companies import COMPANIES_TABS
from app.routes.base.tabs.opportunities import OPPORTUNITIES_TABS
from app.routes.base.tabs.users import USERS_TABS
from app.routes.base.tabs.tasks import TASKS_TABS

# In your tabs module or a dedicated registry file
UI_TAB_MAPPING = {
    'Contact': CONTACTS_TABS,
    'Company': COMPANIES_TABS,
    'Opportunity': OPPORTUNITIES_TABS,
    'User': USERS_TABS,
    'Task': TASKS_TABS,
}

