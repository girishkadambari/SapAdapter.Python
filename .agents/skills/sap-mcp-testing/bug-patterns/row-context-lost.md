# Bug Pattern: Row Context Lost

## Symptom
Operations on row $N$ affect row $M$, or throw "Row out of bounds".

## Likely Root Causes
1. **Scrolling Interaction**: The script scrolled the table but didn't update the logical index mapping.
2. **Sorting/Filtering**: The user sorted the grid, changing the row positions while the agent still uses old indices.
3. **Lazy Loading**: SAP only loaded 20 rows; row 50 "doesn't exist" yet.

## Diagnosis Steps
- Check `VisibleRowCount` vs `RowCount` in `inspect_control`.
- Verify scroll position (`VerticalScrollbar` property).
- Run `find_row_by_text` to re-synchronize the row index after any table-wide action (Sort/Filter).

## Recommended Fix in Test
- Use semantic identifiers (e.g., "Find the row with Material TG11") instead of hardcoded indices.
- Re-inspect the table after any scrolling or sorting.
