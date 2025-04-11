# import logging
# from dataclasses import dataclass
# from app.routes.web.components.tab_builder import TabBuilder, TabSection, TabEntry, InsightsTab
#
# logger = logging.getLogger(__name__)
#
#
# @dataclass
# class AboutTab(TabBuilder):
#     tab_name: str = "About"
#
#     def __post_init__(self):
#         self.section_method_order = [
#             self._company_details_section,
#         ]
#
#         super().__post_init__()
#
#     def _company_details_section(self):
#         section_name = "Company Details"
#         return TabSection(
#             section_name=section_name,
#             entries=[
#                 TabEntry(entry_name="name", label="Name", type="text", required=True, value=self.entity.get("name")),
#                 TabEntry(entry_name="description", label="Description", type="text", value=self.entity.get("description")),
#             ],
#         )
#
#
# @dataclass
# class RelationshipsTab(TabBuilder):
#     tab_name: str = "Relationships"
#
#     def __post_init__(self):
#         self.section_method_order = [
#             self._relationships_section,
#         ]
#
#         super().__post_init__()
#
#     def _relationships_section(self):
#         section_name = "Mappings"
#         return TabSection(
#             section_name=section_name,
#             entries=[
#                 TabEntry(entry_name="users", label="Users", type="custom", value=self.entity.get("users")),
#                 TabEntry(entry_name="companies", label="Companies", type="custom", value=self.entity.get("companies")),
#             ],
#         )
#
#
# # Constant list of tabs for a company
# COMPANIES_TABS = [AboutTab, InsightsTab, RelationshipsTab]
