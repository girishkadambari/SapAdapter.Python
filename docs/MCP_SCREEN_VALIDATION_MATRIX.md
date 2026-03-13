# SAP Screen Validation Matrix

Use this matrix to guide your validation efforts for different SAP GUI screen types.

| Screen Type | Primary Tools | Verification Points | Common Failure Modes |
|-------------|---------------|---------------------|----------------------|
| **Search / Initial** | `observe_screen` | Check if search fields (`GuiCTextField`) are missing. | Search button not mapped correctly. |
| **Simple Form** | `extract_entity` | Verify values match the physical screen. | Labels not associated with fields correctly. |
| **Grid (ALV)** | `observe_screen` | Ensure `GuiGridView` is detected. Count columns. | Grid too large causes timeout. |
| **Table Control** | `observe_screen` | Check `GuiTableControl` row count. | Invisible rows (beyond scroll) not extracted. |
| **Menu / Easy Access** | `observe_screen` | Verify `GuiTree` nodes match the hierarchy. | Tree depth exceeds recursion limit. |
| **Modal Dialog** | `observe_screen` | `observation.modal` should NOT be null. | Modal detected but title/buttons missing. |
| **Shell Container** | `observe_screen` | Verify high-level metadata (e.g., Toolbar buttons). | Shell nested in another shell causes loss of target. |

## Validation Steps per Screen
1. **Position SAP**: Manually navigate SAP GUI to the desired transaction.
2. **Observe**: Run `observe_screen` and verify the `screen_type` classification is correct.
3. **Validate Shapes**:
   - For **Grids**: Ensure `columns` list is non-empty.
   - For **Modals**: Ensure the action buttons are available in the `controls` list.
4. **Action Test**: Perform a non-destructive action (e.g., selecting a tab) and re-observe to check for state change.
