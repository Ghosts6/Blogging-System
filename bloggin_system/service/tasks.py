from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_comment_notification_email(author_email, article_title):
    """
    Simulates sending an email to the author of an article when a new comment is posted.
    """
    message = f"A new comment has been posted on your article: '{article_title}'"
    logger.info(f"Simulating sending email to {author_email}: {message}")
    return f"Email sent to {author_email}"