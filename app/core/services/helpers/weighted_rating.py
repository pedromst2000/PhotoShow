MIN_VOTES_THRESHOLD = 3


def calculate_weighted_rating(
    avg_rating: float, vote_count: int, global_avg: float
) -> float:
    """
    Calculate a weighted average rating using Bayesian smoothing.

    Formula: weighted = (v / (v + m)) * R + (m / (v + m)) * C
    Where:
      - R = photo's average rating
      - v = number of votes for the photo
      - C = global average rating (prior)
      - m = MIN_VOTES_THRESHOLD (prior weight)

    Args:
        avg_rating: The photo's raw average rating.
        vote_count: Number of votes for the photo.
        global_avg: Global average rating across all photos.

    References:
    - https://en.wikipedia.org/wiki/Weighted_arithmetic_mean#Bayesian_average_rating

    Returns:
        float: The weighted rating, rounded to 1 decimal place.
    """
    if vote_count > 0:
        weight_ratio = vote_count / (vote_count + MIN_VOTES_THRESHOLD)
        prior_ratio = MIN_VOTES_THRESHOLD / (vote_count + MIN_VOTES_THRESHOLD)
        weighted = weight_ratio * avg_rating + prior_ratio * global_avg
    else:
        weighted = global_avg
    return round(weighted, 1)
