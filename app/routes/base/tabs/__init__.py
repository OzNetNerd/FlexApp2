from app.routes.base.tabs.contacts import CONTACTS_TABS
from app.routes.base.tabs.companies import COMPANIES_TABS

# In your tabs module or a dedicated registry file
UI_TAB_MAPPING = {
    'Contact': CONTACTS_TABS,
    'Company': COMPANIES_TABS,
}


