# Playbook: Safe Navigation

## Objective
Move between transactions and screens while maintaining state awareness and error trapping.

## 1. Global Navigation (`navigate_tcode`)
- Always use the `/n` prefix (e.g., `/nVA01`) to ensure a clean transaction start.
- **Validation**: After navigation, run `sap_get_screen_summary`.
  - Is the `Title` correct?
  - Did the `Program` name change?
  - Is there an error message in the `StatusBar` (e.g., "Transaction VA01 does not exist")?

## 2. Keyboard Emulation (`send_vkey`)
Common V-Keys and their validation:
- **0 (Enter)**: Check if a new field appeared or the cursor moved. Do NOT assume Enter solved a warning; check the `StatusBar`.
- **11 (Save)**: This is critical. After Save, you MUST look for "Document XXXXXX has been saved" in the `StatusBar`.
- **3 (Back) / 12 (Cancel)**: Verify the `Title` returned to the previous screen or the main menu.

## 3. Handling Blockers
- **Error Popups**: If a modal appears, you must address it before continuing. Do not send more V-Keys blindly.
- **System Messages**: If a "System Message" popup appears, you usually need V-Key 0 to acknowledge it.

## 4. Navigation Success Criteria
- The target screen's `FocusedControl` is ready for input.
- No "E" (Error) type messages in the status bar.
- The `Title` matches the expected step in the test scenario.
