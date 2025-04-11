# import logging
# from dataclasses import dataclass
# from app.routes.web.components.tab_builder import TabBuilder, TabSection, TabEntry
#
# logger = logging.getLogger(__name__)
#
#
# @dataclass
# class GeneralSettingsTab(TabBuilder):
#     tab_name: str = "General"
#
#     def __post_init__(self):
#         self.section_method_order = [
#             self._app_settings_section,
#         ]
#         super().__post_init__()
#
#     def _app_settings_section(self):
#         return TabSection(
#             section_name="Application Settings",
#             entries=[
#                 TabEntry(
#                     entry_name="debug",
#                     label="Enable Debug Mode",
#                     type="switch",
#                     value=self.entity.get("debug", False),
#                     help_text="Activates Flask debug mode (not for production).",
#                 ),
#                 TabEntry(
#                     entry_name="maintenance_mode",
#                     label="Maintenance Mode",
#                     type="switch",
#                     value=self.entity.get("maintenance_mode", False),
#                     help_text="Displays a maintenance banner to all users.",
#                 ),
#             ],
#         )
#
#
# @dataclass
# class LoggingSettingsTab(TabBuilder):
#     tab_name: str = "Logging"
#
#     def __post_init__(self):
#         self.section_method_order = [
#             self._log_settings_section,
#         ]
#         super().__post_init__()
#
#     def _log_settings_section(self):
#         return TabSection(
#             section_name="Logging Configuration",
#             entries=[
#                 TabEntry(
#                     entry_name="log_level",
#                     label="Log Level",
#                     type="select",
#                     value=self.entity.get("log_level", "INFO"),
#                     options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
#                     help_text="Controls the verbosity of the application logs.",
#                 ),
#                 TabEntry(
#                     entry_name="log_to_file",
#                     label="Log to File",
#                     type="switch",
#                     value=self.entity.get("log_to_file", True),
#                     help_text="Enable or disable file-based logging.",
#                 ),
#             ],
#         )
#
#
# @dataclass
# class FeatureFlagsTab(TabBuilder):
#     tab_name: str = "Feature Flags"
#
#     def __post_init__(self):
#         self.section_method_order = [
#             self._flags_section,
#         ]
#         super().__post_init__()
#
#     def _flags_section(self):
#         return TabSection(
#             section_name="Experimental Features",
#             entries=[
#                 TabEntry(
#                     entry_name="enable_beta_ui",
#                     label="Enable Beta UI",
#                     type="switch",
#                     value=self.entity.get("enable_beta_ui", False),
#                     help_text="Toggle access to the new user interface.",
#                 ),
#                 TabEntry(
#                     entry_name="enable_ai_suggestions",
#                     label="AI Suggestions",
#                     type="switch",
#                     value=self.entity.get("enable_ai_suggestions", True),
#                     help_text="Enable AI-based help across the app.",
#                 ),
#             ],
#         )
#
#
# SETTINGS_TABS = [GeneralSettingsTab, LoggingSettingsTab, FeatureFlagsTab]
