from typing import List, Tuple

from app.core.services.report_service import ReportService
from app.core.state.session import session
from app.utils.log_utils import log_exception, log_operation


class ReportController:
    """
    Controller for report operations.

    Coordinates between views and services for:
    - Submitting reports for photos and comments (delegates to service)
    - Listing reports for admin review (direct model access — no business logic)
    - Retrieving a single report's details
    - Resolving (deleting) a report
    """

    @staticmethod
    def get_reason_labels() -> List[str]:
        """
        Return the list of valid report-reason labels for dropdown population.

        Returns:
            list[str]: Ordered list of reason label strings.
        """
        return ReportService.get_reason_labels()

    @staticmethod
    def report_photo(photo_id: int, reason: str) -> Tuple[bool, str]:
        """
        Submit a report against a photo.

        Args:
            photo_id: The ID of the photo being reported.
            reason: The reason label chosen by the reporter.
        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            Exception: Any unexpected error during report submission is caught and logged.
        """
        user_id = session.user_id
        if user_id is None:
            log_operation(
                "report.report_photo", "validation_error", "Unable to identify user"
            )
            return False, "Unable to identify user"

        try:
            success, message = ReportService.submit_report(
                reporter_id=user_id, reason=reason, photo_id=photo_id
            )
            if success:
                log_operation(
                    "report.report_photo",
                    "success",
                    f"Photo {photo_id} reported for: {reason}",
                    user_id=user_id,
                )
            else:
                log_operation(
                    "report.report_photo", "validation_error", message, user_id=user_id
                )
            return success, message
        except Exception as e:
            log_exception(
                "report.report_photo",
                e,
                user_id=user_id,
                context={"photo_id": photo_id, "reason": reason},
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def report_comment(comment_id: int, reason: str) -> Tuple[bool, str]:
        """
        Submit a report against a comment.

        Args:
            comment_id: The ID of the comment being reported.
            reason: The reason label chosen by the reporter.

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            Exception: Any unexpected error during report submission is caught and logged.
        """
        user_id = session.user_id
        if user_id is None:
            log_operation(
                "report.report_comment", "validation_error", "Unable to identify user"
            )
            return False, "Unable to identify user"

        try:
            success, message = ReportService.submit_report(
                reporter_id=user_id, reason=reason, comment_id=comment_id
            )
            if success:
                log_operation(
                    "report.report_comment",
                    "success",
                    f"Comment {comment_id} reported for: {reason}",
                    user_id=user_id,
                )
            else:
                log_operation(
                    "report.report_comment",
                    "validation_error",
                    message,
                    user_id=user_id,
                )
            return success, message
        except Exception as e:
            log_exception(
                "report.report_comment",
                e,
                user_id=user_id,
                context={"comment_id": comment_id, "reason": reason},
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def get_all_reports() -> List[dict]:
        """
        Admin-only: return all reports (raw rows).

        Returns:
            List[dict]: List of report dicts, or empty list for non-admins.
        """
        return ReportService.get_all_reports()

    @staticmethod
    def get_report(report_id: int) -> dict | None:
        """
        Admin-only: return a single report's raw data.

        Args:
            report_id: The ID of the report to retrieve.

        Returns:
            dict | None: The report data if found, else None.
        """
        return ReportService.get_report(report_id)

    @staticmethod
    def resolve_report(report_id: int) -> Tuple[bool, str]:
        """
        Admin-only: resolve a report by deleting it.

        Args:
            report_id: The ID of the report to resolve.

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            Exception: Any unexpected error during report resolution is caught and logged.
        """
        try:
            if ReportService.resolve_report(report_id):
                log_operation(
                    "report.resolve_report",
                    "success",
                    f"Report {report_id} resolved",
                    user_id=session.user_id,
                )
                return True, "Report resolved and removed"
            log_operation(
                "report.resolve_report",
                "validation_error",
                f"Report {report_id} not found",
                user_id=session.user_id,
            )
            return False, "Report not found"
        except Exception as e:
            log_exception(
                "report.resolve_report",
                e,
                user_id=session.user_id,
                context={"report_id": report_id},
            )
            return False, "Something went wrong. Please try again later."
