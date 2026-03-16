# Playbook: Search Help Testing

## Objective
Test the "F4" flow from trigger to selection to source field update.

## 1. Confirm Field Eligibility
- Check if the target field has the `F4` property enabled in `sap_inspect_control`.

## 2. Trigger and Detect
- Trigger search help (usually via keyboard or clicking the icon).
- **Validation**: Run `sap_get_screen_summary`.
  - Is the `ActiveWindow` a dialog/popup?
  - Does it contain a hit list (grid or list)?

## 3. Selection Method (`sap_search_help_select`)
- Prefer `value` over `row` index for repeatability.
- If multiple columns exist, ensure the value is unique or specify the correct row.

## 4. Confirm Handover
This is the most common failure point.
**Check sequence**:
1. Does the popup close?
2. Does focus return to the source field?
3. **Validation**: Does the source field now contain the value chosen from the hit list?

## 5. Ambiguity Handling
- If the search help opens a "Restrictions" screen first (Search Criteria):
  1. Fill the criteria.
  2. Press Enter to get the hit list.
  3. Then select.

## 6. Search Help Failure Modes
- **Popup Not Detected**: Script timed out before modal appeared.
- **Value Not Transferred**: Selection technical success but field remains empty.
- **Multiple Results**: Selection was ambiguous and SAP stayed on the hit list.
