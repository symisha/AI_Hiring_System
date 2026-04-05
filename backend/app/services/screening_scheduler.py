import asyncio
import logging

from app.database.db_connection import supabase
from app.services.resume_extractor import screen_new_applications_for_job
from app.services.shortlisting_resume import shortlist_and_update_status

logger = logging.getLogger(__name__)

SCHEDULER_INTERVAL_SECONDS = 30 * 60


async def screening_scheduler_loop():
    logger.info("[scheduler] Screening scheduler started (30-minute interval)")

    while True:
        try:
            jobs = (
                supabase.table("jobs")
                .select("id,company_id,status")
                .in_("status", ["open", "active"])
                .execute()
                .data
            ) or []

            logger.info(f"[scheduler] Open/active jobs found: {len(jobs)}")

            for job in jobs:
                job_id = str(job.get("id"))
                company_id = str(job.get("company_id"))

                try:
                    screen_result = screen_new_applications_for_job(job_id=job_id, company_id=company_id)
                    shortlist_result = shortlist_and_update_status(job_id=job_id, company_id=company_id)

                    logger.info(
                        "[scheduler] job=%s screen(new=%s, processed=%s, failed=%s) shortlist(shortlisted=%s, rejected=%s)",
                        job_id,
                        screen_result.get("new_applications"),
                        screen_result.get("processed"),
                        screen_result.get("failed"),
                        shortlist_result.get("shortlisted"),
                        shortlist_result.get("rejected"),
                    )
                except Exception as job_error:
                    logger.exception(f"[scheduler] Failed processing job {job_id}: {job_error}")

        except Exception as loop_error:
            logger.exception(f"[scheduler] Loop error: {loop_error}")

        await asyncio.sleep(SCHEDULER_INTERVAL_SECONDS)
