# start | Getting started

## Walkthrough: get your first answer
1. Select **Open feature** to reach **Home**, then open **Administration → AI Models** in the sidebar.
2. Open **Chat models** and use **Add** on the provider you want.
3. Fill in the provider configuration, choose a model, and select **Save changes**. If Ollama shows no models, check its address and installed models.
4. Open **Chat**, start a new conversation, and send `Reply with one line: Nestor is ready.`
5. If it responds, try a clear deliverable, such as `Write a 100-word email inviting my teammates to a 9 AM meeting.`
6. On failure, read the error, verify the selected model and API key or Ollama connection, and repeat the short test first.

## Which screen do I need?
| Task | Screen |
| --- | --- |
| Ask a question, write a draft, or iterate on an answer | Chat |
| Compare PDFs, Word documents, and spreadsheets with citations | Documents |
| Hand off work that may take several minutes | Tasks |
| Repeat work on a schedule | Automations |
| Write and organize notes | Notebook |

# chat | Chat

## Walkthrough: read an attachment and save the output
1. Open **Chat** and start a fresh conversation for this task.
2. Use **+** to attach a small document. Check that its name appears by the composer and remove any wrong attachment.
3. Open the model selector and choose the configured model. Review session permissions and the selected provider before sending sensitive material.
4. Send `Read the attachment, summarize it in five bullets, and create summary.md.` Review any operation that prompts for approval.
5. Read the summary, open the conversation files panel, and download `summary.md`. If only a chat response appears, ask for a file and its name.
6. To refine it, send `Preserve the numbers and shorten each point to one sentence.` in the same conversation.

## Example
`Read the attached contract. Return a table of obligations, deadlines, responsible parties, and source pages. Mark any details that the contract does not specify.`

## If the result is wrong
- Add a requirement or an example of the desired output, then edit and resend your last message.
- Check whether the selected model can read your files or images. Run OCR in **Documents** before asking about text in an image-only PDF.

# tools | Specialized tools

## Walkthrough: run a tool form
1. In **Tools**, choose a card for your desired output, then read the field labels.
2. Select the correct workflow tab before attaching files. Inputs may belong to just one form.
3. Start with small input. Confirm the uploaded filename, then specify the output format, language, and information that must be preserved.
4. Choose a model, run the form, and review its preview or output. Download or copy it if the tool provides that action.
5. If Run is disabled, check required fields and file formats. For a provider error, test the same model with a short message in **Chat**.

## If the tool fails
- For a model or API key error, review the selected provider in **AI Models**.
- For a file error, open the original file to check it. Run OCR in **Documents** for an image-only PDF.

# tasks | Background tasks

## Walkthrough: assign a task with a clear deliverable
1. In **Tasks**, enter each input, your requested work, and the desired output format.
2. Review permissions. Choose read-only access when the task only needs to inspect and summarize material.
3. Assign it, confirm it appears in the list, and open the task to monitor its status.
4. To stop it, choose **Stop** and wait for the status to update before assigning it again.
5. Review the result against your criteria. If a part is missing, assign that portion with a reference to the completed output.

## Example
`Summarize the reports from the three departments. Return a table of key figures, contradictions, and sources for each conclusion.`

# kanban | Kanban

## Walkthrough: create and assign a card
1. Open **Kanban** and use **+** in the to-do column.
2. Enter a title such as `Review contract A`, add sources and completion criteria, then add the card.
3. Reopen it to check the description. Save any edits before dispatching it.
4. Choose **Assign task**. Reopen the card for its status or follow the link to the agent session when available.
5. For a blocked task, read the error and retry after fixing the cause. For manual work, update the card column as work progresses.

## Example
`Review contract A. Deliver a table of fees, payment dates, and penalties with source pages. Done when all three topics have been checked.`

# automations | Automations

## Walkthrough: schedule a morning report
1. Open **Automations** and create a new automation.
2. Name it `Morning task summary`. In the instructions field, specify the source and output, such as three priorities and open decisions.
3. Choose daily or weekdays and enter the time. Read the schedule description below the controls.
4. Enable result notifications if wanted. In advanced options, select a dedicated model if needed.
5. Save and use **Test run** on the card. Check **Tasks** or **Inbox** for the output.
6. If the output is wrong, edit the instructions and test again. Pause the automation after testing if you are not ready for recurring runs.

## Example
`Every morning, summarize unfinished work into three priorities and list decisions that require my input.`

# inbox | Inbox

## Walkthrough: find a completed result
1. Open **Inbox** when the sidebar shows unread notifications and find the latest entry for your task.
2. Open the notification and follow its task link when available to see the full result or error.
3. Return to the inbox and use **Mark as read** to update the unread count.
4. Save any result names or links you still need before using the action to clear notifications.

# skills | Skills

## Walkthrough: install and test a skill
1. Open **Skills**, then suggestions or the ClawHub discovery tab, and search by task.
2. Read the description and requirements. Set up any required CLI or account following the skill instructions.
3. Install it and open the **Installed** tab. Check the current filter if it is not listed.
4. In **Chat**, reference the skill by name and provide a small sample instead of a large file.
5. To author your own skill, use **Create skill**, enter its instructions, and test in a new conversation.

## Example
`Use the document summarization skill to turn this attachment into a summary, action items, and open questions.`

# notebook | Notebook

## Walkthrough: create a notebook and export Markdown
1. Open **Notebook** and create an entry. Click its title to name it, for example `Project meeting notes`.
2. Type `/` in the editor to open the block menu. Add headings, notes, or a table.
3. To split up the content, insert a subpage, name it, and confirm its creation.
4. Check that changes are saved. If saving fails, retry before leaving the page.
5. Use **Export Markdown** on the notebook toolbar and open the downloaded file to check what will be shared.

## Meeting note example
- Create sections for **Decisions**, **Action items**, and **Open questions**.
- Paste your raw notes and ask chat to organize them while preserving owners and agreed dates.

# documents | Documents and citations

## Walkthrough: question a category and verify the answer
1. In **Documents**, create a category named `Project contracts`.
2. Open it and choose files or a folder. For a first test, use one PDF with selectable text and one small DOCX.
3. The limit is **60 MB per file**. Check each file after upload. Wait while it is indexing. Stored-only files remain available for download.
4. In the right-hand chat, ask `How do the payment deadlines differ? Give the filename, deadline, and a citation for each claim.`
5. Click a citation. Check the file, location, and highlighted text in the left pane. Use its back arrow to return to the list.
6. To inspect a file before asking, click its name or use the original-file action in its menu. Use the download control for the original.
7. For a longer report, return to the list, choose **Analyze documents**, enter a focus, and read the result under **Tasks**.

## Example
`Which contracts in this category require payment within 30 days? Return a table and cite each row.`

## If a source is missing
- For a scanned PDF, use **⋮ → Run OCR**. If results rely on keyword search, try a term from the document and check the embedding settings.
- Word pagination can differ in the browser. Download the original when you need to check the printed layout.

Use the category card menu to rename or delete the category. Deleting a category also deletes its files.

# ocr | OCR for scanned PDFs

## Walkthrough: recognize a scanned PDF
1. Open **Settings → OCR** and check the Tesseract, Vietnamese, and English indicators.
2. If Tesseract is missing, use automatic installation if available. Handle any Windows permission prompt on the host running Nestor. If automatic setup is unavailable, use the manual instructions in that tab.
3. If only languages are missing, use the language download button. After a manual install, choose **Check again** and wait for OCR to be ready.
4. Open a category in **Documents** and upload a scanned PDF. New files process pages without text; choose **Run OCR** from the file menu for an existing file.
5. Wait for indexing, ask about a phrase you can locate visually, and click its citation to check the highlight on the original image.
6. If there is no usable text, read the file status note and check rotation or blur. Try a clearer scan, or rerun OCR after adding language data.

## If recognition is inaccurate
- Check for rotated pages, cut-off text, or a blurry scan. A clear, correctly oriented image usually helps.
- For an existing PDF with unrecognized pages, use **⋮ → Run OCR** after correcting the missing language data. OCR runs on the Nestor host, even when you connect from another computer.

# models | AI models and embeddings

## Walkthrough: download and switch an Ollama embedding model
1. Open **AI Models → Embedding model** and enable semantic search if it is off.
2. Select Ollama and choose a model, such as `bge-m3`.
3. If it is missing, choose automatic download and wait. On failure, copy the manual command and run it on the Ollama host.
4. Once the model is installed, save the selection and check the active model displayed in the status panel.
5. When changing the model for existing data, rebuild the index after saving. Wait for completion and check the indexed passage count.
6. In a familiar document category, ask a question in different words from the source and review the returned citation.

## Configure a chat model
- Add a provider, enter any required credentials, and select a default model. Save and test with a short request.
- For image tasks, choose a model that handles images or configure a vision model in Settings.

## Configure embeddings
- For Ollama, start the service on the Nestor host and use **Download model automatically**. The manual instructions include a command such as `ollama pull bge-m3`. Gemini is the cloud option.
- Wait for the **Installed** badge, then save the selection. Run **Rebuild index** when switching models.
- If the status reports a connection error, check whether Ollama is running and whether the selected model appears in its installed models list.

# extensions | Extensions and connections

## Walkthrough: connect an MCP server
1. Open **Connections → MCP server**, then add a server.
2. Give it a recognizable name. Select the required transport and enter the address or configuration provided by the service.
3. Test when available. For OAuth services, save, complete sign-in, and return to verify status.
4. Try a small read operation in chat and check the tool and result before assigning write operations.
5. On failure, verify the address, account permissions, and sign-in status, then use reconnect.

## If the connection fails
- Check the service address, account permissions, and whether its credentials are still valid.
- Update changed credentials in Nestor before retrying.

# assistant | Profiles, personality, and memory

## Walkthrough: create and test a profile
1. Open **Assistant profiles** and create a profile.
2. Name it after a role, such as `Contract reviewer`, and describe its task, tone, and limits.
3. Select the model and tools in the form. Save and verify the profile appears in the list.
4. Test with a small request. If the format is wrong, edit the profile and add an output example.
5. Use **Personality & memory** for workspace-wide instructions and keep one-time directions in their conversation.

## Example
`Contract reviewer: answer in Vietnamese, prefer tables, cite page numbers, and flag issues that need legal review.`

# monitoring | Usage and system health

## Walkthrough: investigate a failed chat request
1. Note the time and model, then open **Activity** and find entries around that time.
2. Check the model and operation status. If a tool failed, note the tool name and relevant error.
3. Open **System health** and inspect resources and logs around the same time. Check the affected service first if the error is external.
4. After correcting the configuration, send a short request using the same model before repeating the larger task.

# settings | Settings and security

## Walkthrough: change appearance and review a draft
1. In **Settings**, search for Appearance and open its card.
2. Change the theme. It updates immediately. Close and reopen the dialog to check the selection.
3. Open memory and context settings. Change a value you can recognize, then choose **Discard changes** to verify it returns to the saved value.
4. To apply a real change, edit the value and choose **Save changes** in the dialog. Reopen the panel to verify.
5. Search for `ocr` or `embedding` to open those configuration dialogs directly.

## Security example
- If you use Nestor across a local network, set an interface password under **Safety & security**.
- Review shell approvals before granting a chat permission to run commands or write files.

# backup | Backup and restore

## Walkthrough: back up before migrating
1. Open **Settings → Backup & restore**.
2. Download the backup archive. Wait for the download to finish and record its date.
3. Copy it somewhere the new machine can access. If the destination already has data you need, make a separate backup of that machine first.
4. Open backup settings on the destination and use the restore-from-file action. Select the transferred archive and verify its filename at confirmation.
5. Wait for success and reload. Check a conversation, a document category, and the model configuration.
6. If you restored the wrong archive, find the pre-restore backup and verify its date before using it.

## Create a backup
- Under **Settings → Backup & restore**, choose **Download backup** before migrating or making an important configuration change.
- Keep the downloaded file somewhere you can reach if the Nestor host fails. Record the backup date.

## Restore and verify
- Choose the correct backup and read the confirmation. Restoring replaces the current data.
- After the page reloads, check a conversation, a document category, and the model configuration.
- If you restored the wrong file, use the separate backup Nestor created before applying the restore.
