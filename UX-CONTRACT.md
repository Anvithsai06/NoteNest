# NoteNest UX Contract

## Product context

- Audience: verified college students and authorised administrators.
- Primary jobs: find, upload, save, download, report, and moderate academic notes.
- Accessibility target: WCAG 2.2 AA.
- Runtime source of truth: FastAPI routes in `backend/app/api/v1`; visual tokens in `frontend/src/styles.css`.

## Canonical UI Map

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
|---|---|---|---|---|
| Forms | `Field`, `PasswordField`, page forms | FastAPI schemas + this contract | create / edit | TypeScript build + browser form flow |
| Select/Listbox | native `select` | this contract | browser-owned popup | keyboard navigation |
| Scrollbar | global stylesheet | `frontend/src/styles.css` | none | visual review |
| Toast | `ToastRegion` | this contract | success / error / info | live region |
| CRUD | `api` helper and route state | FastAPI routes | return to owning list | API response handling |
| Dialog | `Confirm` | this contract | destructive delete | Escape, Cancel, focus restore |

## Flow ledger

| Operation | Pending | Success | Failure |
|---|---|---|---|
| Upload | disabled submit + progress state | My uploads + toast | retain selected file and inline error |
| Update note | disabled submit | return to My uploads + toast | preserve fields and inline error |
| Delete note | confirmation dialog | refresh My uploads | pending-deletion state / error toast |
| Save / remove saved | action disabled | refresh local collection | error toast |
| Search | loading grid | replace results | stable error panel + retry |

## Navigation and permissions

Public visitors see the landing page at `/`; authenticated visitors reach `/app`. Admin navigation is hidden for non-admin users, but backend authorization remains decisive. A direct unavailable route is redirected to the appropriate home state.

## Async and feedback

Mutations are pessimistic. Duplicate submits are prevented while requests are in progress. Search is explicit through submit or filter selection. Toasts appear bottom-right; errors persist until dismissed. Delete confirmation uses an app-owned dialog—never browser dialogs.
