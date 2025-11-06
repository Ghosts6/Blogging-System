import pytest
from service.tasks import send_comment_notification_email
import logging

logger = logging.getLogger(__name__)

def test_send_comment_notification_email(mocker):
    """Test the send_comment_notification_email Celery task."""
    mock_logger_info = mocker.patch.object(logging.getLogger('service.tasks'), 'info')
    
    author_email = "author@example.com"
    article_title = "Test Article Title"
    
    result = send_comment_notification_email(author_email, article_title)
    
    assert result == f"Email sent to {author_email}"
    mock_logger_info.assert_called_once_with(f"Simulating sending email to {author_email}: A new comment has been posted on your article: '{article_title}'")
