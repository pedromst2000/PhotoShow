from app.controllers.explore_controller import ExploreController


def load_feature_photos(username: str) -> list:
    """
    Return the top-3 photos for *username* sorted by combined interactions.

    Interaction score = likes + comments + round(weighted_rating * 5).

    Args:
        username: The profile owner's username.

    Returns:
        list: List of up to 3 photo dictionaries, or empty list on error.
    """
    if not username:
        return []
    try:
        all_photos = ExploreController.get_catalog(sort_by="likes", username=username)
        all_photos.sort(
            key=lambda p: (
                p.get("likes", 0)
                + p.get("comments", 0)
                + round(p.get("weighted_rating", 0) * 5)
            ),
            reverse=True,
        )
        return all_photos[:3]
    except Exception:
        return []
