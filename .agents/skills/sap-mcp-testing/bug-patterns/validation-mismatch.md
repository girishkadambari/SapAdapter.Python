# Bug Pattern: Validation Mismatch

## Symptom
Agent thinks it succeeded because no error occurred, but the business result is wrong (e.g., Order saved with 0 price).

## Likely Root Causes
1. **Silent Warnings**: SAP issued a warning that didn't block navigation but resulted in incomplete data.
2. **Missing Field Validation**: The agent missed an "Incompletion" log item.
3. **Logic Gap**: The test didn't check the *calculated* values (Net Value, Tax, Scrapped).

## Diagnosis Steps
- Always run `get_status_and_incompletion` before final Save.
- Check for "Pricing error" or "Missing mandatory field" in the response.

## Recommended Fix in Test
- Add a "Business Validation" step to every scenario.
- Match "Calculated Values" against "Expected Values" defined in the test data.
