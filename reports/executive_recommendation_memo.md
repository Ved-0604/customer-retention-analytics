# Executive Recommendation Memo: Customer Retention & Churn Optimization
**To:** Head of Growth & Chief Marketing Officer (CMO)  
**From:** Senior Analytics Engineering & BI Team  
**Date:** January 5, 2026  
**Subject:** Customer Retention Economics, Churn Hazard Analysis, and Targeted Retention Strategy  

---

### 1. Executive Summary & Business Problem
Over the 2024–2025 operating period, our e-commerce platform generated **\$21.79M in net revenue** across **108,184 completed orders** from **15,000 acquired customers**. While top-line acquisition expanded rapidly (culminating in a peak Q4 2025 holiday run-rate of \$2.51M/month), our retention efficiency is severely impaired:
- **Overall Customer Churn Rate:** **58.1%** (8,722 customers inactive for > 90 days as of December 31, 2025).
- **One-Time Buyer Ratio:** **44.3%** of all acquired users never place a second order.
- **Revenue Concentration Risk:** The top **20% of customers (Champions & Loyalists) generate 74.0% of all platform revenue (\$16.13M)**. Concurrently, **980 high-spending customers (\$956.7K in historical spend) have entered the "At Risk" and "Cannot Lose Them" dormancy zones**.

Without targeted retention interventions, the company risks churning high-LTV accounts and running on a costly acquisition treadmill where Customer Acquisition Costs (CAC) in paid channels are depleted on low-repeat cohorts.

---

### 2. Key Analytical Findings

1. **Cohort Decay Dynamics:**
   - Month 1 retention across organic and paid cohorts averages **41.8%**, decaying to **31.2% by Month 3** and **22.5% by Month 12**.
   - Q4 holiday cohorts experience an initial repeat boost (M1 retention of 48.3%), but suffer sharp post-holiday cliffs as promotional shoppers lapse.
2. **RFM Segment Disparities:**
   - **Champions (4,845 users / 32.3%):** Highly active, generating \$16.13M with an AOV of \$201.39, average frequency of 16.5 orders, and average recency of 28 days.
   - **At Risk & Cannot Lose Them (980 users / 6.5%):** Former high-frequency spenders who have now been inactive for an average of 184 days, placing **\$956.7K in annualized revenue at immediate risk of permanent loss**.
   - **Lost & Hibernating (6,504 users / 43.4%):** Primarily one-time or early two-time buyers representing low lifetime value (\$197 average spend).
3. **Acquisition Channel Unit Economics (LTV/CAC Disparities):**
   - **Direct & Organic Search:** Exceptional unit economics (Organic CAC \$12.50 vs Estimated CLV \$1,610.40; **128.8x LTV/CAC**; 62.4% repeat rate).
   - **Email Marketing:** Extremely profitable retention channel (CAC \$4.20 vs CLV \$1,485.60; **353.7x LTV/CAC**; 59.1% repeat rate).
   - **Paid Social (Meta/TikTok):** Highest churn hazard (**52.8% churn**; 47.2% repeat rate; CAC \$55.00 vs CLV \$985.20; **17.9x LTV/CAC**).
4. **Multivariate Churn Drivers (Logistic Regression):**
   - **Discount Dependency (Odds Ratio: 1.11x):** Customers whose orders exceed 20% discount rates have an 11% higher propensity to churn once promotional subsidies cease.
   - **Cohort Age / Inactivity Decay (Odds Ratio: 1.59x):** Inactivity past day 60 is the steepest inflection point leading to permanent defection.

---

### 3. Root Cause Analysis

```
┌────────────────────────────────┐    ┌────────────────────────────────┐    ┌────────────────────────────────┐
│   Post-Purchase Disengagement  │    │      Bargain Hunter Churn      │    │  High-Spender Silent Attrition │
│  44.3% one-time buyers lack an │    │ Paid Social discounts attract  │    │ VIPs experiencing delayed gaps │
│ automated onboarding sequence  │    │ promo-driven buyers who defect │    │ without proactive outreach     │
└───────────────┬────────────────┘    └───────────────┬────────────────┘    └───────────────┬────────────────┘
                │                                     │                                     │
                ▼                                     ▼                                     ▼
        Month 1 Cliff Drop                    LTV Dilution on Paid CAC              $956.7K Revenue at Risk
```

---

### 4. Revenue & Retention Implications
If the current 58.1% churn rate continues unchecked:
- The business must acquire **~8,700 new customers every year** simply to maintain baseline revenue.
- Losing just 25% of the currently identified "At Risk" accounts (\$956.7K at stake) represents an unrecoverable **\$239,000 annual margin loss**.
- Paid Social ROAS will continue to deteriorate as CPA rises, making organic and owned retention essential for EBITDA health.

---

### 5. Targeted Retention Strategies

#### Strategy 1: High-Value VIP "Concierge Save" Program
- **Target Customer Segment:** "At Risk" (977 accounts) & "Cannot Lose Them" (3 accounts) who have been inactive 60–120 days.
- **Identified Business Problem:** VIPs who previously spent \$900–\$4,000+ are slipping into permanent churn without human touchpoints or personalized incentives.
- **Proposed Intervention:** 
  1. Trigger automated high-priority CRM alert when a Tier-1 customer reaches 60 days of inactivity.
  2. Deliver personalized executive outreach with a dedicated concierge preview of new category arrivals and an exclusive credit (e.g., \$50 off \$200), avoiding public coupon codes.
- **Expected Business Impact:** Re-activating 15–20% of at-risk VIP accounts would defend an estimated **\$140,000–\$190,000 in gross margin**.
- **Measurement KPI:** 60-day Reactivation Rate of At-Risk Accounts (Target: > 18%) and Incremental Revenue per Saved Customer.
- **Implementation Priority:** **P0 (Immediate – High Revenue Leverage)**.

#### Strategy 2: "Second-Order Acceleration" Onboarding Engine
- **Target Customer Segment:** "New Customers" (1-order buyers, recency ≤ 45 days).
- **Identified Business Problem:** 44.3% one-time buyer drop-off occurs within the first 30–60 days after first purchase.
- **Proposed Intervention:**
  1. Deploy a 4-part automated email & SMS lifecycle sequence timed at Day 7 (delivery satisfaction & cross-sell guide), Day 14 (category replenishment recommendation based on bought item), and Day 28 (limited-time second-order incentive).
  2. Implement category-specific onboarding (e.g., Electronics buyers receive setup tutorials; Beauty buyers receive 30-day regimen guides).
- **Expected Business Impact:** A 3.0 percentage point reduction in one-time buyer drop-off would convert ~450 additional customers into repeat buyers annually, generating an estimated **\$180,000 in incremental first-year revenue**.
- **Measurement KPI:** Day-60 Repeat Purchase Rate (Target: increase from 42.2% to 46.0%).
- **Implementation Priority:** **P1 (Near-Term – Structural Foundation)**.

#### Strategy 3: Paid Social "Full-Price Margin Protection" Restructuring
- **Target Customer Segment:** Paid Social (Meta/TikTok) prospective customers.
- **Identified Business Problem:** Paid Social customers show the highest churn (52.8%) and lowest repeat rate (47.2%), driven by promotional discounting that attracts bargain hunters with poor retention elasticity.
- **Proposed Intervention:**
  1. Shift ad creatives from discount-led offers ("Get 25% Off") to product value and bundle-oriented offers ("Starter Kits" and "Essential Bundles" with free shipping thresholds > \$75).
  2. Build Lookalike Audiences derived exclusively from our **"Champions" and "Loyal Customers"** cohorts rather than all site visitors.
- **Expected Business Impact:** Improves cohort quality at acquisition, lifting Paid Social M3 retention while preserving unit margins.
- **Measurement KPI:** Paid Social 90-day Retention Rate and 6-Month Realized ROAS (Target: 1.25x increase).
- **Implementation Priority:** **P2 (Medium-Term – Channel Economics)**.

---

### 6. Executive Success Metrics & Governance
We recommend establishing an **Executive Retention Scorecard** reviewed bi-weekly:
1. **Gross Margin Churn Rate:** Track churn weighted by gross profit dollars, not just customer headcount.
2. **Cohort M1 & M3 Retention:** Early leading indicator of retention health.
3. **At-Risk Account Reactivation Rate:** Operational measure of VIP outreach efficiency.
4. **Blended LTV/CAC Ratio:** Maintain overall ratio > 5.0x (and paid channels > 3.0x).

---

### 7. Next Steps & Execution Roadmap
- **Week 1–2:** Ingest and automate the SQL At-Risk list into the marketing CRM (Klaviyo / Braze / Salesforce) for immediate Concierge pilot.
- **Week 3–4:** Deploy A/B test on the Second-Order Acceleration lifecycle sequence across 50% holdout group.
- **Week 5–6:** Audit Paid Social ad sets and deploy Champions Lookalike audiences.
- **Quarterly Review:** Evaluate cohort retention uplift in the Power BI dashboard at 90 days.
