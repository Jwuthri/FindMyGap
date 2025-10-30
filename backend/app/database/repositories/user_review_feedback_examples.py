"""
Example usage of UserReviewFeedbackRepository.

This demonstrates how to manage user access to reviews using the junction table.
"""

from sqlalchemy.orm import Session
from app.database.repositories.user_review_feedback import UserReviewFeedbackRepository
from app.database.repositories.review import ReviewRepository


def example_grant_user_access_to_review(db: Session, user_id: int, review_id: int):
    """
    Example: Grant a user access to a specific review.
    
    Use case: When a user uploads their own reviews or when reviews are shared with them.
    """
    repo = UserReviewFeedbackRepository()
    
    # Grant access with ownership
    user_review = repo.create(
        db=db,
        user_id=user_id,
        review_id=review_id,
        is_owner=True,
        access_type="uploaded",
        notes="User uploaded this review"
    )
    
    print(f"Granted user {user_id} access to review {review_id}")
    return user_review


def example_bulk_grant_access(db: Session, user_id: int, review_ids: list[int]):
    """
    Example: Grant a user access to multiple reviews at once.
    
    Use case: When ingesting a batch of reviews uploaded by a user.
    """
    repo = UserReviewFeedbackRepository()
    
    count = repo.bulk_grant_access(
        db=db,
        user_id=user_id,
        review_ids=review_ids,
        is_owner=True,
        access_type="uploaded"
    )
    
    print(f"Granted user {user_id} access to {count} reviews")
    return count


def example_get_user_reviews(db: Session, user_id: int):
    """
    Example: Get all reviews a user has access to.
    
    Use case: Display all reviews available to a user in their dashboard.
    """
    repo = UserReviewFeedbackRepository()
    
    reviews = repo.get_user_reviews(db=db, user_id=user_id, skip=0, limit=100)
    
    print(f"User {user_id} has access to {len(reviews)} reviews")
    for review in reviews:
        print(f"  - Review {review.id}: {review.text[:50]}...")
    
    return reviews


def example_check_access(db: Session, user_id: int, review_id: int):
    """
    Example: Check if a user has access to a specific review.
    
    Use case: Before allowing a user to view or analyze a review.
    """
    repo = UserReviewFeedbackRepository()
    
    has_access = repo.check_user_access(db=db, user_id=user_id, review_id=review_id)
    
    if has_access:
        print(f"User {user_id} has access to review {review_id}")
    else:
        print(f"User {user_id} does NOT have access to review {review_id}")
    
    return has_access


def example_share_review(db: Session, from_user_id: int, to_user_id: int, review_id: int):
    """
    Example: Share a review from one user to another.
    
    Use case: Collaboration features where users can share reviews.
    """
    repo = UserReviewFeedbackRepository()
    
    # First check if the from_user has access
    if not repo.check_user_access(db, from_user_id, review_id):
        print(f"User {from_user_id} doesn't have access to review {review_id}")
        return None
    
    # Grant access to the other user
    user_review = repo.grant_access(
        db=db,
        user_id=to_user_id,
        review_id=review_id,
        access_type="shared"
    )
    
    if user_review:
        print(f"Shared review {review_id} from user {from_user_id} to user {to_user_id}")
    else:
        print(f"User {to_user_id} already has access to review {review_id}")
    
    return user_review


def example_revoke_access(db: Session, user_id: int, review_id: int):
    """
    Example: Revoke a user's access to a review.
    
    Use case: When removing shared access or cleaning up permissions.
    """
    repo = UserReviewFeedbackRepository()
    
    success = repo.revoke_access(db=db, user_id=user_id, review_id=review_id)
    
    if success:
        print(f"Revoked user {user_id}'s access to review {review_id}")
    else:
        print(f"User {user_id} didn't have access to review {review_id}")
    
    return success


def example_ingest_reviews_workflow(db: Session, user_id: int, review_texts: list[str], company_id: int):
    """
    Example: Complete workflow for ingesting reviews and granting user access.
    
    Use case: When a user uploads a CSV of reviews.
    """
    review_repo = ReviewRepository()
    user_review_repo = UserReviewFeedbackRepository()
    
    review_ids = []
    
    # Step 1: Create reviews in the main reviews_feedback table
    for text in review_texts:
        review = review_repo.create(
            db=db,
            company_id=company_id,
            text=text
        )
        review_ids.append(review.id)
    
    print(f"Created {len(review_ids)} reviews")
    
    # Step 2: Grant user access to all created reviews
    count = user_review_repo.bulk_grant_access(
        db=db,
        user_id=user_id,
        review_ids=review_ids,
        is_owner=True,
        access_type="uploaded"
    )
    
    print(f"Granted user {user_id} access to {count} reviews")
    
    return review_ids


def example_get_owned_reviews(db: Session, user_id: int):
    """
    Example: Get only reviews owned by a user (not shared with them).
    
    Use case: Display user's own uploaded reviews separately from shared ones.
    """
    repo = UserReviewFeedbackRepository()
    
    owned_reviews = repo.get_user_owned_reviews(db=db, user_id=user_id)
    
    print(f"User {user_id} owns {len(owned_reviews)} reviews")
    return owned_reviews


def example_count_user_reviews(db: Session, user_id: int):
    """
    Example: Count total reviews accessible to a user.
    
    Use case: Display statistics in user dashboard.
    """
    repo = UserReviewFeedbackRepository()
    
    count = repo.count_user_reviews(db=db, user_id=user_id)
    
    print(f"User {user_id} has access to {count} total reviews")
    return count
