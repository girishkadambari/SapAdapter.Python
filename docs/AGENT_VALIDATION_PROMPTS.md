# Agent Validation Prompts

Use these prompts with an AI agent (like Antigravity) to stress-test the SAP MCP tool interface.

## 1. Environment & Connectivity
> "Analyze the local environment. List all active SAP sessions and tell me which transaction is currently running in each."

## 2. Deep Observation
> "Inspect the current SAP screen. Provide a summary of all input fields, buttons, and tables found. Include a screenshot in your analysis to confirm visual alignment."

## 3. Interaction & Verification Loop
> "I need to set the Username field to 'BROSS' and the Language to 'EN'. Execute these actions and then re-observe the screen to verify that the changes were applied correctly. Report any errors encountered."

## 4. Complex Data Extraction
> "Find the main data table on the screen. Extract all rows and columns, and summarize the total number of entries. If there are multiple pages, tell me how you would navigate them."

## 5. Modal & Error Handling
> "Try to click the 'Exit' button. If a confirmation modal appears, detect it, read its message, and then 'Cancel' the modal to return to the previous screen. Verify that the modal is gone."

## 6. Semantic Extraction (Entity Layer)
> "Identify if the current screen represents a Sales Order. If so, extract the Header Data (Order ID, Date, Sold-to Party) using the entity extraction tool."
