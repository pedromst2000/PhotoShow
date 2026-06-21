"""
Unit tests for the Bayesian weighted-rating helper.

Formula: weighted = (v / (v+m)) * R + (m / (v+m)) * C
Where R = photo avg, v = vote count, C = global avg, m = MIN_VOTES_THRESHOLD.
"""

from app.core.services.helpers.weighted_rating import (
    MIN_VOTES_THRESHOLD,
    calculate_weighted_rating,
)


class TestCalculateWeightedRating:
    def test_zero_votes_returns_global_average(self):
        """With no votes the result should equal the global average."""
        result = calculate_weighted_rating(avg_rating=4.5, vote_count=0, global_avg=3.0)
        assert result == 3.0

    def test_nonzero_votes_result_is_between_avg_and_global(self):
        """Weighted rating must be strictly between avg and global avg."""
        avg, global_avg = 5.0, 2.0
        result = calculate_weighted_rating(
            avg_rating=avg, vote_count=5, global_avg=global_avg
        )
        assert global_avg < result < avg

    def test_very_many_votes_converges_to_photo_avg(self):
        """With 1 000 votes the result is very close to the photo's average."""
        result = calculate_weighted_rating(
            avg_rating=5.0, vote_count=1000, global_avg=2.0
        )
        assert result >= 4.9

    def test_result_rounded_to_one_decimal(self):
        """Return value must carry at most 1 decimal place."""
        result = calculate_weighted_rating(
            avg_rating=4.333, vote_count=3, global_avg=3.0
        )
        assert result == round(result, 1)

    def test_at_min_votes_threshold_weight_is_fifty_fifty(self):
        """At exactly MIN_VOTES_THRESHOLD votes the ratio is 0.5 / 0.5."""
        m = MIN_VOTES_THRESHOLD
        result = calculate_weighted_rating(avg_rating=4.0, vote_count=m, global_avg=2.0)
        expected = round(0.5 * 4.0 + 0.5 * 2.0, 1)
        assert result == expected

    def test_equal_avg_and_global_returns_that_value(self):
        """When avg == global the result equals that value regardless of votes."""
        result = calculate_weighted_rating(
            avg_rating=3.0, vote_count=10, global_avg=3.0
        )
        assert result == 3.0
