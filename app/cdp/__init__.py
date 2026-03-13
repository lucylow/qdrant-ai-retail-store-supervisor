"""Customer Data Platform: unified 360 profiles, real-time/historical features, GDPR."""

from app.cdp.customer_profile import CustomerProfile, CustomerSegment
from app.cdp.gdpr_compliance import GDPRCompliance
from app.cdp.historical_features import HistoricalFeatures, compute_historical_features
from app.cdp.real_time_features import RealTimeFeatures, compute_real_time_features

__all__ = [
    "CustomerProfile",
    "CustomerSegment",
    "GDPRCompliance",
    "HistoricalFeatures",
    "RealTimeFeatures",
    "compute_historical_features",
    "compute_real_time_features",
]
