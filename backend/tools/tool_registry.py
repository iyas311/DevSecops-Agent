"""
tool_registry.py – Central registry for all Cloud Identity Security Assistant tools.

The ``ToolRegistry`` is a simple in-memory store that maps tool *names*
to ``BaseTool`` instances.  It provides convenience methods for:

* **Registering** tools (with duplicate-name guard).
* **Looking up** a single tool by name.
* **Listing** all registered tools.
* **Exporting** every tool as a Bedrock Converse API ``toolSpec``.
* **Executing** a tool by name (delegates to the tool's ``execute``).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .base_tool import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Holds references to all available ``BaseTool`` instances.

    Usage
    -----
    >>> registry = ToolRegistry()
    >>> registry.register(ListIAMUsersTool())
    >>> specs = registry.get_bedrock_tool_specs()
    >>> result = await registry.execute_tool("list_iam_users", aws_profile="prod")
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    # ------------------------------------------------------------------ #
    #  Registration                                                       #
    # ------------------------------------------------------------------ #

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance.

        Parameters
        ----------
        tool : BaseTool
            The tool to register.  Its ``name`` must be unique within
            this registry.

        Raises
        ------
        ValueError
            If a tool with the same name is already registered.
        """
        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered. "
                "Each tool name must be unique."
            )
        self._tools[tool.name] = tool
        logger.info("Registered tool: %s", tool.name)

    # ------------------------------------------------------------------ #
    #  Look-up                                                            #
    # ------------------------------------------------------------------ #

    def get_tool(self, name: str) -> BaseTool:
        """Return the tool registered under *name*.

        Raises
        ------
        KeyError
            If no tool with that name exists.
        """
        try:
            return self._tools[name]
        except KeyError:
            available = ", ".join(sorted(self._tools)) or "(none)"
            raise KeyError(
                f"Tool '{name}' not found. Available tools: {available}"
            ) from None

    def get_all_tools(self) -> List[BaseTool]:
        """Return an ordered list of all registered tools."""
        return list(self._tools.values())

    # ------------------------------------------------------------------ #
    #  Bedrock helpers                                                    #
    # ------------------------------------------------------------------ #

    def get_bedrock_tool_specs(self) -> List[Dict[str, Any]]:
        """Return Bedrock Converse API ``toolSpec`` dicts for every registered tool."""
        return [tool.to_bedrock_spec() for tool in self._tools.values()]

    # ------------------------------------------------------------------ #
    #  Execution                                                          #
    # ------------------------------------------------------------------ #

    async def execute_tool(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """Look up a tool by *name* and execute it.

        Parameters
        ----------
        name : str
            The tool name (must already be registered).
        **kwargs
            Forwarded to the tool's ``execute`` method.

        Returns
        -------
        dict
            The structured result from the tool.

        Raises
        ------
        KeyError
            If the tool name is not registered.
        """
        tool = self.get_tool(name)
        logger.info("Executing tool: %s with args: %s", name, kwargs)
        return await tool.execute(**kwargs)

    # ------------------------------------------------------------------ #
    #  Dunder helpers                                                     #
    # ------------------------------------------------------------------ #

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ToolRegistry tools={list(self._tools.keys())}>"
