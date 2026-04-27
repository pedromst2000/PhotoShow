from typing import Optional, Tuple

from app.core.db.engine import SessionLocal
from app.core.db.models.report import ReportModel
from app.core.db.models.report_reason import ReportReasonModel
from app.core.db.models.user import UserModel
from app.utils.log_utils import log_exception, log_operation


class ReportService:
    """
    Service class for content-report business logic.

    Business rules enforced:
    - Reason label must be non-empty and map to a valid report_reasons row.
    - Admins cannot submit reports.
    - Exactly one of photo_id / comment_id must be provided.
    """

    @staticmethod
    def get_reason_labels() -> list:
        """
        Return the list of valid report-reason labels.

        Returns:
            list[str]: Ordered list of reason label strings.

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
            with SessionLocal() as session:
                labels = ReportReasonModel.get_labels(session)
            log_operation(
                "report.get_reason_labels",
                "success",
                f"Retrieved {len(labels)} report reasons",
            )
            return labels
        except Exception as e:
            log_exception("report.get_reason_labels", e)
            return []

    @staticmethod
    def get_all_reports() -> list:
        """
        Get all reports (admin only, but service doesn't enforce permission).

        Returns:
            list[dict]: List of report dictionaries.

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
            with SessionLocal() as session:
                reports = ReportModel.get_all(session)
            log_operation(
                "report.get_all_reports", "success", f"Retrieved {len(reports)} reports"
            )
            return reports
        except Exception as e:
            log_exception("report.get_all_reports", e)
            return []

    @staticmethod
    def get_report(report_id: int):
        """
        Get a single report by ID.

        Args:
            report_id: The ID of the report to retrieve.

        Returns:
            dict or None: The report data if found, else None.

        Raises:
            Exception: Any database error is caught and logged; None returned.
        """
        try:
            with SessionLocal() as session:
                report = ReportModel.get_by_id(session, report_id)
            if report:
                log_operation(
                    "report.get_report", "success", f"Retrieved report {report_id}"
                )
            return report
        except Exception as e:
            log_exception("report.get_report", e, context={"report_id": report_id})
            return None

    @staticmethod
    def has_user_reported(
        user_id: int,
        photo_id: Optional[int] = None,
        comment_id: Optional[int] = None,
    ) -> bool:
        """
        Check if a user has already reported a specific photo or comment.

        Args:
            user_id: The ID of the user to check.
            photo_id: The ID of the photo to check (mutually exclusive with comment_id).
            comment_id: The ID of the comment to check (mutually exclusive with photo_id).

        Returns:
            bool: True if the user has already reported this content, False otherwise.
        """
        try:
            with SessionLocal() as session:
                return ReportModel.has_user_reported(
                    session, user_id, photo_id=photo_id, comment_id=comment_id
                )
        except Exception as e:
            log_exception("report.has_user_reported", e)
            return False

    @staticmethod
    def resolve_report(report_id: int) -> bool:
        """
        Delete (resolve) a report. Returns True if deleted, False if not found.

        Args:
            report_id: The ID of the report to delete.

        Returns:
            bool: True if the report was found and deleted, False if not found.

        Raises:
            Exception: Any database error is caught and logged; False returned.
        """
        try:
            with SessionLocal() as session:
                result = ReportModel.delete(session, report_id)
                session.commit()
            if result:
                log_operation(
                    "report.resolve_report", "success", f"Resolved report {report_id}"
                )
            else:
                log_operation(
                    "report.resolve_report",
                    "validation_error",
                    f"Report {report_id} not found",
                )
            return result
        except Exception as e:
            log_exception("report.resolve_report", e, context={"report_id": report_id})
            return False

    @staticmethod
    def submit_report(
        reporter_id: int,
        reason: str,
        photo_id: Optional[int] = None,
        comment_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Submit a content report against a photo or comment.

        Business rules enforced:
        - Reason label must be non-empty and map to a valid report_reasons row.
        - Admins cannot submit reports.
        - Exactly one of photo_id / comment_id must be provided.
        - description is required when reason is "Other".

        Args:
            reporter_id: The ID of the user submitting the report.
            reason: The reason label chosen by the reporter.
            photo_id: The ID of the photo being reported (if applicable).
            comment_id: The ID of the comment being reported (if applicable).
            description: Optional detail text (required when reason is "Other").

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            Exception: Any database error is caught and logged; (False, message) returned.
        """
        if not reason or not reason.strip():
            return False, "A reason is required"

        if (photo_id is None) == (comment_id is None):
            return False, "Exactly one of photo or comment must be specified"

        clean_description = (
            description.strip() if description and description.strip() else None
        )

        if reason.strip() == "Other" and not clean_description:
            return False, "Please provide details when selecting 'Other'"

        if clean_description and len(clean_description) > 255:
            return False, "Description must not exceed 255 characters"

        try:
            with SessionLocal() as session:
                reporter = UserModel.get_by_id(session, reporter_id)
                if reporter and reporter.get("roleId") == 1:
                    log_operation(
                        "report.submit_report",
                        "validation_error",
                        "Admins cannot submit reports",
                        user_id=reporter_id,
                    )
                    return False, "Admins cannot submit reports"

                reason_record = ReportReasonModel.get_by_label(session, reason)
                if not reason_record:
                    log_operation(
                        "report.submit_report",
                        "validation_error",
                        f"Invalid reason: {reason}",
                        user_id=reporter_id,
                    )
                    return False, "Invalid reason"

                # Check if user has already reported this photo/comment
                if ReportModel.has_user_reported(
                    session, reporter_id, photo_id=photo_id, comment_id=comment_id
                ):
                    log_operation(
                        "report.submit_report",
                        "validation_error",
                        "User has already reported this content",
                        user_id=reporter_id,
                    )
                    return False, "You have already reported this content"

                ReportModel.create(
                    session,
                    reporter_id=reporter_id,
                    reason_id=reason_record["id"],
                    photo_id=photo_id,
                    comment_id=comment_id,
                    description=clean_description,
                )
                session.commit()
            log_operation(
                "report.submit_report",
                "success",
                f"Report submitted by user {reporter_id}",
                user_id=reporter_id,
            )
            return (
                True,
                "Your report has been submitted and will be reviewed by an admin",
            )
        except Exception as e:
            log_exception(
                "report.submit_report",
                e,
                user_id=reporter_id,
                context={"reason": reason},
            )
            return False, "Failed to submit report. Please try again"
