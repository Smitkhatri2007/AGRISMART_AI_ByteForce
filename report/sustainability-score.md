# AgriSmart AI Sustainability Score

## Overview
The **AgriSmart AI Sustainability Score** is an automated metric (0-100) calculated for every disease diagnosis that requires a treatment plan. It helps farmers gauge the environmental impact of the recommended interventions.

## Calculation Formula

The score begins at a baseline of **100** (representing perfectly sustainable, zero-impact farming) and is adjusted based on the AI's prescribed cure plan.

### 1. Chemical Intervention Penalty
Chemical fungicides and bactericides have varying levels of soil residual impact and non-target toxicity.
- **Has Chemical Treatment**: `-40 points`
*(Note: If the chemical treatment string indicates "None" or "Not required", this penalty is waived).*

### 2. Severity & Urgency Penalty
Higher severity infections require more aggressive, immediate action which typically involves more intensive resource use (water for spraying, labor, immediate containment).
- **Critical Severity**: `-20 points`
- **High Severity**: `-10 points`
- **Moderate / Low Severity**: `-5 points`
- **None (Healthy)**: `0 points`

### 3. Organic Compensation
If a viable organic treatment is recommended alongside or instead of chemical options, a bonus is awarded to encourage regenerative practices.
- **Has Organic Treatment**: `+10 points`

*(Final score is clamped between 0 and 100).*

## Example
**Tomato Late Blight (High Severity)**
- Base: 100
- Chemical Treatment prescribed (Mancozeb): -40
- High Severity: -10
- Organic alternative provided: +10
- **Total Score: 60/100 (Amber/Moderate Sustainability)**
