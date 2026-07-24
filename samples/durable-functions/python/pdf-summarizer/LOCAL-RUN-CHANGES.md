# Local Run Change Log (Per-File Tables)

This document lists each local-run related change individually, grouped by file, from current git changes.

## `samples/durable-functions/python/pdf-summarizer/function_app.py`

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Added `ManagedIdentityCredential` import and `_openai_credential = DefaultAzureCredential()` | Separates storage and OpenAI auth concerns; enables AAD token acquisition for direct OpenAI REST calls. |
| 2 | Added `_build_storage_credential()` | In Azure-hosted runs, prefers explicit managed identity path to reduce credential-chain ambiguity. |
| 3 | Added `_build_blob_service_client()` | Selects Azurite connection-string mode for local storage and identity-based account URL mode for cloud. |
| 4 | Added local storage detection (`UseDevelopmentStorage`, `127.0.0.1`, `localhost`) | Makes the same code executable in local emulation without cloud identity dependency. |
| 5 | Added `_summarize_with_azure_openai(text)` | Replaces binding abstraction with explicit `chat/completions` HTTP call for deterministic request/response behavior. |
| 6 | Implemented dual OpenAI auth (API key or AAD bearer token) | Supports both secret-based local fallback and managed-identity/AAD-first operation. |
| 7 | Updated blob trigger log string formatting | Improves observability of blob name and size during local debugging. |
| 8 | Removed `generic_input_binding` on `summarize_text` | Eliminates binding-layer failures from the local path and simplifies activity dependencies. |
| 9 | Changed `summarize_text(results, response)` to `summarize_text(results)` | Activity now owns completion call logic directly, reducing coupling to host binding behavior. |

## `samples/durable-functions/python/pdf-summarizer/host.json`

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | `hubName` changed from `"TASKHUB_NAME"` to `"%TASKHUB_NAME%"` | Enables environment-variable expansion so the runtime uses configured task hub instead of a literal value. |

## `samples/durable-functions/python/pdf-summarizer/.gitignore`

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Added `.venv` | Prevents local virtual environment artifacts from entering source control. |
| 2 | Added `*__azurite_db_*__.json` | Excludes Azurite metadata databases generated during local storage emulation. |
| 3 | Added `__blobstorage__/*` | Excludes local blob payload/state written by Azurite. |
| 4 | Added `__queuestorage__/*` | Excludes local queue payload/state written by Azurite. |

## `.gitignore` (repo root)

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Trailing newline-only diff | No functional rule change; formatting-only diff. |

## `samples/durable-functions/python/pdf-summarizer/infra/main.bicep`

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | `chatModel.deploymentVersion` default `2024-08-06` -> `2024-11-20` | Aligns default model API/deployment baseline with newer OpenAI deployment expectations. |
| 2 | Function runtime `python 3.9` -> `python 3.11` | Aligns provisioned runtime with local/runtime code assumptions and dependency compatibility. |
| 3 | Added `storageQueueRoleDefinitionId` | Introduces explicit RBAC role id for queue operations required by runtime paths. |
| 4 | Added `storageTableRoleDefinitionId` | Introduces explicit RBAC role id for table operations required by runtime paths. |
| 5 | Added `storageQueueRoleAssignmentApiUAMI` module | Grants queue permissions to the function's user-assigned managed identity. |
| 6 | Added `storageTableRoleAssignmentApiUAMI` module | Grants table permissions to the function's user-assigned managed identity. |
| 7 | Added `storageQueueRoleAssignmentApi` module | Grants queue permissions to deployment/login principal for operational access parity. |
| 8 | Added `storageTableRoleAssignmentApi` module | Grants table permissions to deployment/login principal for operational access parity. |

## `samples/durable-functions/python/pdf-summarizer/README.md`

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Architecture image path changed to `architecture_v2.png` | Uses sample-local asset path so docs render without external media path dependency. |
| 2 | Python prerequisite `3.9+` -> `3.11+` | Matches runtime/dependency baseline actually used in the local debug workflow. |
| 3 | Orchestration code image path changed to `code.png` | Keeps README visuals resolvable from sample directory. |
| 4 | Dashboard image path changed to `dashboard.png` | Keeps README visuals resolvable from sample directory. |
| 5 | Activity image path changed to `activity.png` | Keeps README visuals resolvable from sample directory. |
| 6 | Sequence image path changed to `sequence.png` | Keeps README visuals resolvable from sample directory. |

## `samples/durable-functions/python/pdf-summarizer/.vscode/tasks.json` (new)

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Added task `func: host start (debugpy)` | Creates a reproducible local host startup command for debugging. |
| 2 | Sets `VIRTUAL_ENV` in start task | Pins execution context to project virtual environment. |
| 3 | Prepends `.venv\\Scripts` to `PATH` | Ensures Python/pip resolution prefers project interpreter binaries. |
| 4 | Sets `languageWorkers__python__defaultExecutablePath` | Forces Azure Functions Python worker to use `.venv` interpreter. |
| 5 | Sets `languageWorkers__python__arguments` to `-m debugpy --listen 9091` | Enables remote attach debugging to worker process. |
| 6 | Added background `problemMatcher` with host-ready `endsPattern` | Allows VS Code debug orchestration to wait until host is ready before attach. |
| 7 | Added task `func: host stop` | Provides deterministic teardown for iterative local debug runs. |

## `samples/durable-functions/python/pdf-summarizer/.vscode/launch.json` (new)

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Added `Functions: Start + Attach (One Click)` config | Combines startup task and debug attach into one repeatable workflow. |
| 2 | Uses `debugpy` attach on `localhost:9091` | Targets Python worker debug endpoint created by the start task. |
| 3 | Sets `preLaunchTask` and `postDebugTask` | Automates lifecycle management and reduces stale host/debug sessions. |
| 4 | Added `Python: Current File` config | Keeps a standalone script-debug option for non-function troubleshooting. |

## `samples/durable-functions/python/pdf-summarizer/local.settings.json-v1` (new)

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | `DURABLE_TASK_SCHEDULER_CONNECTION_STRING` points to `http://localhost:8080` with `Authentication=None` | Configures local DTS emulator mode without cloud auth dependency. |
| 2 | `TASKHUB_NAME=default` | Uses emulator-compatible hub identity. |
| 3 | `AzureWebJobsStorage=UseDevelopmentStorage=true` | Routes storage bindings to Azurite for fully local execution. |

## `samples/durable-functions/python/pdf-summarizer/local.settings.json-v2` (new)

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Added `AZURE_TENANT_ID=16b3c013-d300-468d-ac64-7eda0820b6d3` | Pins Entra tenant resolution to avoid wrong-tenant token selection in local auth chain. |
| 2 | `DURABLE_TASK_SCHEDULER_CONNECTION_STRING` switched to remote durabletask.io endpoint with `Authentication=DefaultAzure` | Moves scheduler backend from emulator to managed remote service with AAD auth. |
| 3 | `TASKHUB_NAME` changed to `taskhub-c3phyppgfoxrm` | Aligns local runtime with remote scheduler's configured hub. |
| 4 | `AzureWebJobsStorage` remains `UseDevelopmentStorage=true` in this snapshot | Keeps storage local while scheduler is remote for mixed-mode testing. |

## `samples/durable-functions/python/pdf-summarizer/run-locally.ps1` (new)

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Added DTS emulator start command | Provides local scheduler backend bootstrap. |
| 2 | Added DTS emulator stop command | Provides local scheduler backend cleanup. |
| 3 | Added Azurite container creation commands (`input`, `output`) | Ensures required blob containers exist before trigger tests. |
| 4 | Added sample blob upload command(s) | Provides reproducible trigger input for E2E validation. |
| 5 | Added sample blob delete command | Simplifies rerun/reset loops during local tests. |
| 6 | Added `azurite --skipApiVersionCheck` command | Stabilizes local storage emulator startup for current CLI/runtime combination. |

## `samples/durable-functions/python/pdf-summarizer/activity.png` (new)

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Added screenshot asset | Supports README monitoring/troubleshooting documentation. |

## `samples/durable-functions/python/pdf-summarizer/architecture_v2.png` (new)

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Added architecture asset | Supports README system design documentation from local asset path. |

## `samples/durable-functions/python/pdf-summarizer/code.png` (new)

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Added orchestration code screenshot | Supports README implementation walkthrough visuals. |

## `samples/durable-functions/python/pdf-summarizer/dashboard.png` (new)

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Added dashboard screenshot | Supports README execution monitoring guidance. |

## `samples/durable-functions/python/pdf-summarizer/sequence.png` (new)

| # | Change | Concise technical explanation |
|---|---|---|
| 1 | Added orchestration sequence screenshot | Supports README timeline/sequence diagnostics explanation. |

## Notes

- `local.settings.json` is normally git-ignored; `local.settings.json-v1` and `local.settings.json-v2` are tracked snapshots used to document configuration transitions.
- This file is organized strictly by file, with one table per file and one row per individual change.
