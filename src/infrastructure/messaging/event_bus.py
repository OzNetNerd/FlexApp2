"""
Event bus implementation for domain events.

This module provides a simple event bus implementation for publishing
and subscribing to domain events across the application.
"""

from typing import Dict, List, Type, Callable, Any
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Type alias for event handlers
EventHandler = Callable[[Any], None]


class EventBus:
    """
    Event bus for publishing and subscribing to domain events.

    The event bus allows components to communicate through events
    without direct coupling.
    """

    def __init__(self, async_execution: bool = False, max_workers: int = 5):
        """
        Initialize the event bus.

        Args:
            async_execution: Whether to execute handlers asynchronously
            max_workers: Maximum number of worker threads for async execution
        """
        self._handlers: Dict[Type, List[EventHandler]] = {}
        self._async_execution = async_execution
        self._executor = ThreadPoolExecutor(max_workers=max_workers) if async_execution else None

    def subscribe(self, event_type: Type, handler: EventHandler) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: The type of event to subscribe to
            handler: The handler function to call when event is published
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logger.debug(f"Handler {handler.__name__} subscribed to {event_type.__name__}")

    def unsubscribe(self, event_type: Type, handler: EventHandler) -> None:
        """
        Unsubscribe a handler from an event type.

        Args:
            event_type: The type of event to unsubscribe from
            handler: The handler function to unsubscribe
        """
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.debug(f"Handler {handler.__name__} unsubscribed from {event_type.__name__}")

    def publish(self, event: Any) -> None:
        """
        Publish an event to all subscribed handlers.

        Args:
            event: The event instance to publish
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        if not handlers:
            logger.debug(f"No handlers registered for event type {event_type.__name__}")
            return

        logger.debug(f"Publishing event {event_type.__name__} to {len(handlers)} handlers")

        if self._async_execution and self._executor:
            for handler in handlers:
                self._executor.submit(self._execute_handler, handler, event)
        else:
            for handler in handlers:
                self._execute_handler(handler, event)

    def _execute_handler(self, handler: EventHandler, event: Any) -> None:
        """
        Execute a handler with error handling.

        Args:
            handler: The handler to execute
            event: The event to pass to the handler
        """
        try:
            handler(event)
        except Exception as e:
            logger.error(f"Error in event handler {handler.__name__}: {str(e)}")

    def shutdown(self) -> None:
        """
        Shutdown the event bus and cleanup resources.
        """
        if self._async_execution and self._executor:
            self._executor.shutdown(wait=True)