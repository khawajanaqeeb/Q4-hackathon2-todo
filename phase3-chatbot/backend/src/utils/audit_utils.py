from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import Session, select
from ..models.audit_log import AuditLog
from ..models.user import User
import time


class AuditUtils:
    """Audit utilities for tracking API usage and maintaining audit trails."""

    @staticmethod
    async def log_api_call(
        session: Session,
        user_id: Optional[str],
        action_type: str,
        resource_type: Optional[str],
        resource_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        response_time_ms: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        Log an API call to the audit trail.

        Args:
            session: Database session
            user_id: User ID associated with the call
            action_type: Type of action performed
            resource_type: Type of resource operated on
            resource_id: ID of the specific resource
            metadata: Additional metadata about the operation
            success: Whether the operation succeeded
            response_time_ms: Response time in milliseconds
            ip_address: IP address of the requester
            user_agent: User agent string
            error_message: Error message if operation failed

        Returns:
            Created AuditLog object
        """
        audit_log = AuditLog(
            user_id=user_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
            success=success,
            response_time_ms=response_time_ms,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message,
            timestamp=datetime.utcnow()
        )

        session.add(audit_log)
        session.commit()
        session.refresh(audit_log)

        return audit_log

    @staticmethod
    async def track_api_usage(
        session: Session,
        user_id: str,
        provider: str,
        action: str,
        cost: float = 0.0,
        tokens_used: int = 0
    ) -> AuditLog:
        """
        Track API usage and costs.

        Args:
            session: Database session
            user_id: User ID
            provider: Provider name
            action: Action performed
            cost: Cost of the operation
            tokens_used: Number of tokens used

        Returns:
            Created AuditLog object
        """
        metadata = {
            "provider": provider,
            "action": action,
            "cost": cost,
            "tokens_used": tokens_used
        }

        return await AuditUtils.log_api_call(
            session=session,
            user_id=user_id,
            action_type="API_USAGE",
            resource_type="API_CALL",
            metadata=metadata,
            success=True
        )

    @staticmethod
    async def generate_usage_report(
        session: Session,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action_types: Optional[list] = None
    ) -> list[AuditLog]:
        """
        Generate audit reports for API usage.

        Args:
            session: Database session
            user_id: Optional user ID to filter by
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            action_types: Optional list of action types to filter by

        Returns:
            List of audit logs matching the criteria
        """
        statement = select(AuditLog)

        if user_id:
            statement = statement.where(AuditLog.user_id == user_id)

        if start_date:
            statement = statement.where(AuditLog.timestamp >= start_date)

        if end_date:
            statement = statement.where(AuditLog.timestamp <= end_date)

        if action_types:
            statement = statement.where(AuditLog.action_type.in_(action_types))

        audit_logs = session.exec(statement).all()
        return audit_logs

    @staticmethod
    async def get_user_api_stats(
        session: Session,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get user API usage statistics.

        Args:
            session: Database session
            user_id: User ID
            days: Number of days to look back

        Returns:
            Dictionary with API usage statistics
        """
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Count total API calls
        total_calls_stmt = select(AuditLog).where(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= cutoff_date
        )
        total_calls = len(session.exec(total_calls_stmt).all())

        # Count successful API calls
        success_stmt = select(AuditLog).where(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= cutoff_date,
            AuditLog.success == True
        )
        successful_calls = len(session.exec(success_stmt).all())

        # Count failed API calls
        failed_stmt = select(AuditLog).where(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= cutoff_date,
            AuditLog.success == False
        )
        failed_calls = len(session.exec(failed_stmt).all())

        # Get most common action types
        action_stmt = select(AuditLog).where(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= cutoff_date
        )
        all_logs = session.exec(action_stmt).all()

        action_counts = {}
        total_cost = 0.0
        total_tokens = 0

        for log in all_logs:
            action_type = log.action_type
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

            # Sum up costs and tokens if available in metadata
            if log.metadata:
                cost = log.metadata.get("cost", 0)
                tokens = log.metadata.get("tokens_used", 0)
                total_cost += cost
                total_tokens += tokens

        return {
            "total_api_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
            "action_distribution": action_counts,
            "total_cost": total_cost,
            "total_tokens_used": total_tokens,
            "report_period_days": days
        }

    @staticmethod
    async def log_security_event(
        session: Session,
        user_id: Optional[str],
        event_type: str,
        severity: str = "medium",  # low, medium, high, critical
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log a security-related event.

        Args:
            session: Database session
            user_id: User ID associated with the event
            event_type: Type of security event
            severity: Severity level of the event
            details: Additional details about the event
            ip_address: IP address of the requester
            user_agent: User agent string

        Returns:
            Created AuditLog object
        """
        metadata = {
            "event_type": event_type,
            "severity": severity,
            "details": details or {}
        }

        return await AuditUtils.log_api_call(
            session=session,
            user_id=user_id,
            action_type="SECURITY_EVENT",
            resource_type="SECURITY",
            metadata=metadata,
            success=True,  # Logging the event itself is successful
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    async def check_rate_limit_violations(
        session: Session,
        user_id: str,
        action_type: str,
        time_window_minutes: int = 1,
        max_attempts: int = 10
    ) -> bool:
        """
        Check if a user has violated rate limits.

        Args:
            session: Database session
            user_id: User ID to check
            action_type: Action type to check for
            time_window_minutes: Time window in minutes
            max_attempts: Maximum number of attempts allowed in the time window

        Returns:
            True if rate limit is violated, False otherwise
        """
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)

        # Count actions of this type for this user in the time window
        stmt = select(AuditLog).where(
            AuditLog.user_id == user_id,
            AuditLog.action_type == action_type,
            AuditLog.timestamp >= cutoff_time
        )
        recent_actions = session.exec(stmt).all()

        return len(recent_actions) > max_attempts

    @staticmethod
    async def get_recent_activity(
        session: Session,
        user_id: str,
        limit: int = 50
    ) -> list[AuditLog]:
        """
        Get recent activity for a user.

        Args:
            session: Database session
            user_id: User ID
            limit: Maximum number of records to return

        Returns:
            List of recent audit logs
        """
        stmt = select(AuditLog).where(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.timestamp.desc()).limit(limit)

        return session.exec(stmt).all()