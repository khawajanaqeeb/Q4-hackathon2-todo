import asyncio
import time
from typing import Any, Optional, Callable, Dict
from enum import Enum


class ServiceStatus(Enum):
    """Enum for service status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class FallbackService:
    """Maintain functionality during service outages with fallback mechanisms."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        """
        Initialize Fallback Service.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff
            max_delay: Maximum delay for exponential backoff
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.service_status: Dict[str, ServiceStatus] = {}
        self.last_check_time: Dict[str, float] = {}
        self.offline_data_cache: Dict[str, Any] = {}

    async def handle_fallback(
        self,
        service_name: str,
        primary_operation: Callable,
        fallback_operation: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute fallback logic when primary operation fails.

        Args:
            service_name: Name of the service
            primary_operation: Primary operation to attempt
            fallback_operation: Fallback operation to execute if primary fails
            *args: Arguments for the operations
            **kwargs: Keyword arguments for the operations

        Returns:
            Result of either primary or fallback operation
        """
        try:
            # Update service status to healthy if it was degraded
            if self.service_status.get(service_name) == ServiceStatus.DEGRADED:
                self.service_status[service_name] = ServiceStatus.HEALTHY

            # Attempt primary operation
            result = await primary_operation(*args, **kwargs)
            return result
        except Exception as e:
            # Mark service as degraded
            self.service_status[service_name] = ServiceStatus.DEGRADED
            self.last_check_time[service_name] = time.time()

            # If fallback is provided, execute it
            if fallback_operation:
                try:
                    fallback_result = await fallback_operation(*args, **kwargs)
                    return fallback_result
                except Exception as fallback_error:
                    # If fallback also fails, raise the original error
                    raise e
            else:
                # No fallback provided, raise the original error
                raise e

    async def retry_with_backoff(
        self,
        operation: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Retry failed operations with exponential backoff.

        Args:
            operation: Operation to retry
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
            Result of the operation
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt < self.max_retries:
                    # Calculate delay with exponential backoff and jitter
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    # Add jitter to prevent thundering herd
                    jitter = delay * 0.1 * (await self._get_random_factor())
                    actual_delay = delay + jitter

                    await asyncio.sleep(actual_delay)
                else:
                    # All retries exhausted
                    raise last_exception

        raise last_exception

    async def offline_mode(self, service_name: str, cached_data_key: str = None) -> Any:
        """
        Enable offline mode and return cached data if available.

        Args:
            service_name: Name of the service in offline mode
            cached_data_key: Key to retrieve cached data

        Returns:
            Cached data or default response
        """
        self.service_status[service_name] = ServiceStatus.UNAVAILABLE

        if cached_data_key and cached_data_key in self.offline_data_cache:
            return self.offline_data_cache[cached_data_key]

        return {
            "status": "offline",
            "message": f"Service {service_name} is currently unavailable. Operating in offline mode.",
            "timestamp": time.time()
        }

    async def _get_random_factor(self) -> float:
        """Generate a random factor for jitter calculation."""
        import random
        return random.random()

    def store_offline_data(self, key: str, data: Any) -> None:
        """
        Store data for offline access.

        Args:
            key: Key to store the data
            data: Data to store
        """
        self.offline_data_cache[key] = data

    def get_offline_data(self, key: str) -> Optional[Any]:
        """
        Retrieve offline data.

        Args:
            key: Key to retrieve data

        Returns:
            Stored data or None if not found
        """
        return self.offline_data_cache.get(key)

    def is_service_available(self, service_name: str) -> bool:
        """
        Check if a service is available.

        Args:
            service_name: Name of the service

        Returns:
            True if service is available, False otherwise
        """
        status = self.service_status.get(service_name, ServiceStatus.HEALTHY)
        return status != ServiceStatus.UNAVAILABLE

    def get_service_health(self, service_name: str) -> ServiceStatus:
        """
        Get the health status of a service.

        Args:
            service_name: Name of the service

        Returns:
            Service health status
        """
        return self.service_status.get(service_name, ServiceStatus.HEALTHY)

    async def monitor_service(self, service_name: str, health_check: Callable) -> ServiceStatus:
        """
        Monitor service availability.

        Args:
            service_name: Name of the service
            health_check: Function to check service health

        Returns:
            Updated service status
        """
        try:
            is_healthy = await health_check()
            if is_healthy:
                self.service_status[service_name] = ServiceStatus.HEALTHY
            else:
                self.service_status[service_name] = ServiceStatus.UNAVAILABLE
        except Exception:
            self.service_status[service_name] = ServiceStatus.UNAVAILABLE

        return self.service_status[service_name]

    def enable_circuit_breaker(self, service_name: str, failure_threshold: int = 5, timeout: int = 60) -> None:
        """
        Enable circuit breaker pattern for a service.

        Args:
            service_name: Name of the service
            failure_threshold: Number of failures before opening circuit
            timeout: Timeout in seconds before attempting to close circuit
        """
        # This would typically integrate with a circuit breaker library
        # For now, we'll just store the configuration
        if not hasattr(self, 'circuit_breakers'):
            self.circuit_breakers = {}

        self.circuit_breakers[service_name] = {
            'failure_count': 0,
            'failure_threshold': failure_threshold,
            'timeout': timeout,
            'opened_at': None,
            'last_failure': None
        }

    def is_circuit_open(self, service_name: str) -> bool:
        """
        Check if the circuit breaker is open for a service.

        Args:
            service_name: Name of the service

        Returns:
            True if circuit is open, False otherwise
        """
        if not hasattr(self, 'circuit_breakers') or service_name not in self.circuit_breakers:
            return False

        cb_config = self.circuit_breakers[service_name]

        # If circuit is not open, return False
        if cb_config['opened_at'] is None:
            return False

        # Check if timeout has passed to attempt closing the circuit
        if time.time() - cb_config['opened_at'] > cb_config['timeout']:
            # Reset circuit breaker state
            cb_config['opened_at'] = None
            cb_config['failure_count'] = 0
            return False

        return True

    def record_failure(self, service_name: str) -> bool:
        """
        Record a failure and open circuit if threshold reached.

        Args:
            service_name: Name of the service

        Returns:
            True if circuit was opened, False otherwise
        """
        if not hasattr(self, 'circuit_breakers') or service_name not in self.circuit_breakers:
            return False

        cb_config = self.circuit_breakers[service_name]
        cb_config['failure_count'] += 1
        cb_config['last_failure'] = time.time()

        if cb_config['failure_count'] >= cb_config['failure_threshold']:
            cb_config['opened_at'] = time.time()
            self.service_status[service_name] = ServiceStatus.UNAVAILABLE
            return True

        return False