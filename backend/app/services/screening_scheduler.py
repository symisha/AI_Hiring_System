import asyncio
import logging

from app.database.db_connection import supabase
from app.services.resume_extractor import screen_new_applications_for_job
# Import the new granular flow functions

import logging

# Configure logging to output to the console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

from app.services.shortlisting_resume import (
    run_resume_to_assessment_flow,
    run_assessment_to_interview_flow
)

logger = logging.getLogger(__name__)

SCHEDULER_INTERVAL_SECONDS = 30

async def screening_scheduler_loop():
    logger.info("[scheduler] Multi-stage screening scheduler started")

    while True:
        try:
            # Fetch active jobs
            jobs = (
                supabase.table("jobs")
                .select("id, company_id, status")
                .in_("status", ["open", "active"])
                .execute()
                .data
            ) or []

            for job in jobs:
                job_id = str(job.get("id"))
                company_id = str(job.get("company_id"))

                try:
                    logger.info(f"--- Processing Job: {job_id} ---")

                    # 1. Screening
                    screen_result = screen_new_applications_for_job(job_id=job_id, company_id=company_id)
                    logger.info(f"Step 1 Complete for {job_id}")

                    # 2. Stage One
                    logger.info(f"Starting Stage 1 Shortlist for {job_id}...")
                    stage_one = run_resume_to_assessment_flow(job_id=job_id)
                    logger.info(f"Step 2 Complete. Shortlisted: {len(stage_one.get('shortlisted', []))}")

                    # 3. Stage Two
                    logger.info(f"Starting Stage 2 Shortlist for {job_id}...")
                    stage_two = run_assessment_to_interview_flow(job_id=job_id)
                    logger.info(f"Step 3 Complete. Shortlisted: {len(stage_two.get('shortlisted', []))}")

                    # Final Summary
                    logger.info(
                        "[scheduler] SUCCESS | job=%s | New=%s | S1=%s | S2=%s",
                        job_id,
                        screen_result.get("processed", 0),
                        len(stage_one.get("shortlisted", [])),
                        len(stage_two.get("shortlisted", []))
                    )

                except Exception as job_error:
                    logger.error(f"CRASH in job loop for {job_id}: {str(job_error)}", exc_info=True)

        except Exception as loop_error:
            logger.exception(f"[scheduler] Loop error: {loop_error}")

        # Sleep for the defined interval
        await asyncio.sleep(SCHEDULER_INTERVAL_SECONDS)