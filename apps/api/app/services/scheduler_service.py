import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger
from app.models.knowledge import CrawlSchedule, KnowledgeSource, ScheduleType
from app.services.crawler_service import CrawlerService

logger = get_logger(__name__)


class SchedulerService:
    """Background scheduler for automatic crawls"""
    
    _scheduler: Optional[AsyncIOScheduler] = None
    _running = False
    
    @classmethod
    def start(cls):
        """Start the background scheduler"""
        if cls._running:
            logger.warning("Scheduler already running")
            return
        
        cls._scheduler = AsyncIOScheduler()
        
        # Run check_schedules every hour
        cls._scheduler.add_job(
            cls.check_schedules,
            CronTrigger(minute=0),  # Every hour at minute 0
            id='check_schedules',
            replace_existing=True
        )
        
        cls._scheduler.start()
        cls._running = True
        logger.info("Crawl scheduler started")
    
    @classmethod
    def stop(cls):
        """Stop the background scheduler"""
        if cls._scheduler and cls._running:
            cls._scheduler.shutdown()
            cls._running = False
            logger.info("Crawl scheduler stopped")
    
    @classmethod
    async def check_schedules(cls):
        """Check for schedules that need to run"""
        logger.info("Checking for scheduled crawls...")
        
        async with AsyncSessionLocal() as db:
            try:
                now = datetime.now(timezone.utc)
                
                # Find schedules where next_crawl_at <= now and is_active = true
                result = await db.execute(
                    select(CrawlSchedule, KnowledgeSource)
                    .join(KnowledgeSource, CrawlSchedule.knowledge_source_id == KnowledgeSource.id)
                    .where(
                        and_(
                            CrawlSchedule.is_active == True,
                            CrawlSchedule.next_crawl_at <= now
                        )
                    )
                )
                
                schedules = result.all()
                
                if not schedules:
                    logger.info("No schedules to run")
                    return
                
                logger.info(f"Found {len(schedules)} schedules to execute")
                
                for schedule, knowledge_source in schedules:
                    try:
                        logger.info(f"Triggering crawl for knowledge source {knowledge_source.id}")
                        
                        # Start crawl in background
                        asyncio.create_task(
                            CrawlerService.start_crawl(
                                knowledge_source_id=str(knowledge_source.id),
                                base_url=knowledge_source.source_url,
                                max_pages=500,
                                is_recrawl=True
                            )
                        )
                        
                        # Calculate next crawl time
                        next_crawl = cls.calculate_next_crawl(schedule)
                        
                        # Update schedule
                        schedule.next_crawl_at = next_crawl
                        await db.commit()
                        
                        logger.info(f"Next crawl scheduled for {next_crawl}")
                        
                    except Exception as e:
                        logger.error(f"Error triggering crawl for schedule {schedule.id}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error checking schedules: {e}")
    
    @classmethod
    def calculate_next_crawl(cls, schedule: CrawlSchedule) -> datetime:
        """Calculate the next crawl time based on schedule type"""
        now = datetime.now(timezone.utc)
        preferred_hour = schedule.preferred_hour
        
        if schedule.schedule_type == ScheduleType.DAILY:
            # Next occurrence at preferred_hour
            next_time = now.replace(hour=preferred_hour, minute=0, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
            return next_time
        
        elif schedule.schedule_type == ScheduleType.WEEKLY:
            # Next occurrence on day_of_week at preferred_hour
            target_weekday = schedule.day_of_week or 0  # Default to Monday
            current_weekday = now.weekday()
            
            days_ahead = target_weekday - current_weekday
            if days_ahead < 0:  # Target day already happened this week
                days_ahead += 7
            elif days_ahead == 0:  # Today is the target day
                next_time = now.replace(hour=preferred_hour, minute=0, second=0, microsecond=0)
                if next_time <= now:
                    days_ahead = 7
            
            next_time = now.replace(hour=preferred_hour, minute=0, second=0, microsecond=0)
            next_time += timedelta(days=days_ahead)
            return next_time
        
        elif schedule.schedule_type == ScheduleType.MONTHLY:
            # Next occurrence on the same day of next month at preferred_hour
            next_time = now.replace(hour=preferred_hour, minute=0, second=0, microsecond=0)
            
            # Move to next month
            if next_time.month == 12:
                next_time = next_time.replace(year=next_time.year + 1, month=1)
            else:
                next_time = next_time.replace(month=next_time.month + 1)
            
            # Handle day overflow (e.g., Jan 31 -> Feb 28)
            while True:
                try:
                    next_time = next_time.replace(day=now.day)
                    break
                except ValueError:
                    # Day doesn't exist in target month, use last day
                    next_time = next_time.replace(day=1) + timedelta(days=32)
                    next_time = next_time.replace(day=1) - timedelta(days=1)
                    break
            
            if next_time <= now:
                # If still in the past, add another month
                if next_time.month == 12:
                    next_time = next_time.replace(year=next_time.year + 1, month=1)
                else:
                    next_time = next_time.replace(month=next_time.month + 1)
            
            return next_time
        
        else:  # MANUAL
            # No automatic scheduling
            return None
    
    @classmethod
    async def create_or_update_schedule(
        cls,
        db: AsyncSession,
        knowledge_source_id: str,
        schedule_type: ScheduleType,
        day_of_week: Optional[int] = None,
        preferred_hour: int = 2,
        is_active: bool = True
    ) -> CrawlSchedule:
        """Create or update a crawl schedule"""
        
        # Check if schedule exists
        result = await db.execute(
            select(CrawlSchedule).where(
                CrawlSchedule.knowledge_source_id == knowledge_source_id
            )
        )
        schedule = result.scalar_one_or_none()
        
        if schedule:
            # Update existing
            schedule.schedule_type = schedule_type
            schedule.day_of_week = day_of_week
            schedule.preferred_hour = preferred_hour
            schedule.is_active = is_active
        else:
            # Create new
            schedule = CrawlSchedule(
                knowledge_source_id=knowledge_source_id,
                schedule_type=schedule_type,
                day_of_week=day_of_week,
                preferred_hour=preferred_hour,
                is_active=is_active
            )
            db.add(schedule)
        
        # Calculate next crawl time if not manual
        if schedule_type != ScheduleType.MANUAL and is_active:
            schedule.next_crawl_at = cls.calculate_next_crawl(schedule)
        else:
            schedule.next_crawl_at = None
        
        await db.commit()
        await db.refresh(schedule)
        
        return schedule

