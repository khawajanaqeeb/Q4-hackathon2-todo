import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import Session, select
from ..models.audit_log import AuditLog


class AuditService:
    """Service for tracking API usage and maintaining audit trails."""

    def __init__(self, session: Session):
        """
        Initialize Audit Service.

        Args:
            session: Database session
        """
        self.session = session

    async def log_operation(
        self,
        session: Session,
        user_id: Optional[uuid.UUID],
        action_type: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        response_time_ms: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        Log an operation to the audit trail.

        Args:
            session: Database session
            user_id: User ID associated with the operation
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
            error_message=error_message
        )

        session.add(audit_log)
        session.commit()
        session.refresh(audit_log)

        return audit_log

    async def track_usage(
        self,
        session: Session,
        user_id: uuid.UUID,
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

        return await self.log_operation(
            session=session,
            user_id=user_id,
            action_type="API_USAGE",
            resource_type="API_CALL",
            metadata=metadata,
            success=True
        )

    async def generate_report(
        self,
        session: Session,
        user_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action_types: Optional[list] = None
    ) -> list[AuditLog]:
        """
        Generate audit reports.

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

    async def get_user_activity(
        self,
        session: Session,
        user_id: uuid.UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get user activity summary.

        Args:
            session: Database session
            user_id: User ID
            days: Number of days to look back

        Returns:
            Dictionary with activity summary
        """
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Count total operations
        total_ops_stmt = select(AuditLog).where(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= cutoff_date
        )
        total_operations = len(session.exec(total_ops_stmt).all())

        # Count successful operations
        success_stmt = select(AuditLog).where(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= cutoff_date,
            AuditLog.success == True
        )
        successful_operations = len(session.exec(success_stmt).all())

        # Count failed operations
        failed_stmt = select(AuditLog).where(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= cutoff_date,
            AuditLog.success == False
        )
        failed_operations = len(session.exec(failed_stmt).all())

        # Get most common action types
        action_stmt = select(AuditLog).where(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= cutoff_date
        )
        all_logs = session.exec(action_stmt).all()

        action_counts = {}
        for log in all_logs:
            action_type = log.action_type
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": successful_operations / total_operations if total_operations > 0 else 0,
            "action_distribution": action_counts,
            "report_period_days": days
        }