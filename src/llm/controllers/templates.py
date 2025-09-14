"""
Controllers for managing templates in the LLM application.
"""

import logging
from pathlib import Path
from string import Template
from typing import Any, Dict, Optional

from llm.models.enums.locales import Locale


class TemplateController:
    """
    Controller for managing templates in the LLM application.
    """

    def __init__(self, primary_lang: Locale, fallback_lang: Locale):
        """Initialize the TemplateController.

        Args:
            primary_lang (Locale): The primary language for templates.
            fallback_lang (Locale): The fallback language for templates.
        """
        self.base_templates_dir = Path(__file__).parent.parent / "templates"
        self.logger = logging.getLogger(self.__class__.__name__)
        self.primary_lang = primary_lang
        self.fallback_lang = fallback_lang
        self.logger.info(
            "TemplateController initialized with primary_lang=%s, fallback_lang=%s",
            primary_lang.value,
            fallback_lang.value,
        )
        self.logger.info("Base templates directory: %s", self.base_templates_dir)
        if not self.base_templates_dir.exists():
            self.logger.error(
                "Templates directory does not exist: %s", self.base_templates_dir
            )

        self.locales_dir = self.base_templates_dir / "locales"
        if not self.locales_dir.exists():
            self.logger.error("Locales directory does not exist: %s", self.locales_dir)

    def _get_locale_dir(self, locale: Locale) -> Optional[Path]:
        """Get the directory for a specific locale.

        Args:
            locale (Locale): The locale to get the directory for.

        Returns:
            Optional[Path]: The path to the locale directory, or None if it doesn't exist.
        """
        locale_dir = self.locales_dir / locale.value
        if not locale_dir.exists():
            self.logger.warning(
                "Locale directory does not exist: %s. Falling back to: %s.",
                locale_dir,
                self.fallback_lang.value,
            )
        return locale_dir

    def get_template(
        self,
        group: str,
        key: str,
        variables: Optional[Dict[str, Any]] = None,
        locale: Optional[Locale] = None,
    ) -> Optional[str]:
        """
        Retrieve a template string based on locale, group, and key.

        Args:
            group (str): The group the template belongs to.
            key (str): The key of the template.
            variables (Dict[str, Any]): Variables to format the template with. Optional.
            locale (Locale): The locale to retrieve the template for. Optional; \
                defaults to primary language.

        Returns:
            Optional[str]: The rendered template string, or None if not found.
        """
        if locale is None:
            locale = self.primary_lang
        locale_dir = self._get_locale_dir(locale)
        if locale_dir is None and locale != self.fallback_lang:
            locale_dir = self._get_locale_dir(self.fallback_lang)
        if locale_dir is None:
            return None

        template_path = locale_dir / f"{group}.py"
        if not template_path.exists():
            self.logger.warning("Template not found: %s", template_path)
            return None

        module = __import__(
            f"llm.templates.locales.{locale.value}.{group}", fromlist=[group]
        )
        template: Optional[Template] = getattr(module, key, None)

        if not template:
            self.logger.warning("Template key '%s' not found in %s", key, template_path)
            return None

        return template.substitute(variables) if variables else template.template
