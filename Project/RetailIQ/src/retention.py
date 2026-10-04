"""
RetailIQ - Retention & Win-Back Recommendations

Turns each RFM segment into concrete, actionable business advice -
especially for "At Risk" and "Lost Customers", where the whole point
is giving the business a real chance to win them back rather than
just labeling them and moving on.

This is rule-based business logic (standard CRM/lifecycle-marketing
playbook), not a model - it needs no training data and works on any
dataset the same way the rest of RetailIQ does.
"""

import pandas as pd

SEGMENT_RECOMMENDATIONS = {
    "Champions": {
        "tone": "reward",
        "headline": "Your best customers - protect this relationship.",
        "tips": [
            "Give early access to new products or limited-stock drops.",
            "Set up a loyalty/VIP perk (points, free shipping, birthday reward).",
            "Ask for reviews or referrals - they're your most credible advocates.",
            "Surprise-and-delight occasionally (small free gift, handwritten note) - low cost, high loyalty payoff.",
        ],
    },
    "Loyal Customers": {
        "tone": "grow",
        "headline": "Reliable buyers - grow their basket, don't lose their habit.",
        "tips": [
            "Recommend complementary products based on past purchases (cross-sell).",
            "Offer a small volume/subscription discount to increase order frequency.",
            "Invite them into a loyalty program if they aren't in one yet.",
        ],
    },
    "Regular Customers": {
        "tone": "nudge",
        "headline": "Middle-of-the-pack - a small nudge can move them up a tier.",
        "tips": [
            "Send personalized recommendations to increase purchase frequency.",
            "Offer a modest limited-time discount to prompt an earlier repeat purchase.",
            "Highlight loyalty program benefits they haven't unlocked yet.",
        ],
    },
    "New Customers": {
        "tone": "onboard",
        "headline": "First impression window - the next 30-60 days decide if they stay.",
        "tips": [
            "Send a welcome series: how to use/care for what they bought, plus related picks.",
            "Make the return/support policy easy to find - reduces first-purchase anxiety.",
            "Offer a second-purchase incentive (e.g. 10% off within 30 days) to build the repeat habit early.",
        ],
    },
    "At Risk": {
        "tone": "urgent",
        "headline": "Still recoverable - act before they become Lost.",
        "tips": [
            "Send a personalized \"we miss you\" email or push notification.",
            "Offer a time-limited win-back discount (e.g. 10-15% off, expiring in 7 days).",
            "Show what's new since their last purchase in categories they bought before.",
            "Ask directly for feedback - a short \"what could we do better?\" survey.",
        ],
    },
    "Lost Customers": {
        "tone": "critical",
        "headline": "Longest gap and lowest engagement - needs the strongest incentive to return.",
        "tips": [
            "Run a dedicated win-back campaign with a bigger incentive (e.g. 20%+ off or free shipping).",
            "Send a short survey asking why they left - price, product fit, service, competitor?",
            "Retarget with ads showing bestsellers or new arrivals since they left.",
            "Remind them of unused loyalty points or store credit, if any exist.",
            "If they don't respond after 2-3 attempts, deprioritize - further discounting rarely pays back below this point.",
        ],
    },
}


def get_segment_summary(rfm: pd.DataFrame, segment: str) -> dict:
    """Customer count + historical revenue at stake for one segment."""
    subset = rfm[rfm["Segment"] == segment]
    return {
        "count": len(subset),
        "total_monetary": float(subset["Monetary"].sum()) if len(subset) else 0.0,
        "avg_recency": float(subset["Recency"].mean()) if len(subset) else 0.0,
    }


def get_recommendations(segment: str) -> dict:
    """Return the tone/headline/tips dict for a segment, with a safe fallback."""
    return SEGMENT_RECOMMENDATIONS.get(segment, {
        "tone": "neutral",
        "headline": "No specific playbook for this segment yet.",
        "tips": ["Review this segment's RFM values to decide on an approach."],
    })
