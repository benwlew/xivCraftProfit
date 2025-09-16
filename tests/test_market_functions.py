import pytest
from market import split_listings_by_quality, filter_outliers, calculate_market_stats

def test_split_listings_by_quality(sample_listings):
    """Test that listings are correctly split by quality."""
    nq_listings, hq_listings = split_listings_by_quality(sample_listings)
    
    # Verify all NQ listings are actually NQ
    assert all(not listing['hq'] for listing in nq_listings)
    
    # Verify all HQ listings are actually HQ
    assert all(listing['hq'] for listing in hq_listings)



def test_calculate_market_stats(sample_listings):
    """Test market statistics calculation."""
    stats = calculate_market_stats(sample_listings)
    
    # Check that we have both HQ and NQ stats
    assert 'hq' in stats
    assert 'nq' in stats
    
    # Check HQ stats
    hq_stats = stats['hq']
    assert 'medianPrice' in hq_stats
    assert 'minPrice' in hq_stats
    assert len(hq_stats['listings']) <= 5  # Should have max 5 listings
    assert hq_stats['total_listings'] == 3  # Excluding mannequin
    
    # Check NQ stats
    nq_stats = stats['nq']
    assert 'medianPrice' in nq_stats
    assert 'minPrice' in nq_stats
    assert len(nq_stats['listings']) <= 5
    assert nq_stats['total_listings'] == 3
    
    # Verify min prices are correct
    assert hq_stats['minPrice'] == 950  # Lowest non-mannequin HQ price
    assert nq_stats['minPrice'] == 750  # 100 should be filtered as outlier