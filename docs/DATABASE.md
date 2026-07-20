# Silver — Database documentation | توثيق قاعدة البيانات

SQLite in the MVP (`data/silver.db`), schema designed to port directly to PostgreSQL.
المخطط مصمم ليُنقل مباشرة إلى PostgreSQL دون تغيير هيكلي.

## Core tables | الجداول الأساسية

| Table | Purpose (EN) | الغرض |
|---|---|---|
| `users` | accounts, roles, status, credentials (PBKDF2-SHA256, per-user salt) | الحسابات والأدوار والحالة |
| `profiles` | display name, bio, city, avatar, privacy flag | بيانات الملف الشخصي |
| `follows` | follower → followee edges; mutual follow = "friends" | المتابعة؛ المتابعة المتبادلة = صداقة |
| `categories` | interest/stream categories (ar+en names, admin-managed) | التصنيفات |
| `user_interests` | user ↔ category | اهتمامات المستخدم |
| `social_sections` | the five fixed sections (circle/front/interests/communities/nearby) | الأقسام الخمسة |
| `posts` | all content: text/image/video/short_video; `hidden` = moderation | المنشورات |
| `post_audiences` | adaptive post: one post → many sections | جمهور المنشور المتكيف |
| `post_variants` | optional public/private text variants | نسختا المنشور |
| `media` | uploaded files linked to posts/stories | الوسائط |
| `stories` | 24h stories with audience + featured flag | القصص |
| `story_views` | who viewed which story | مشاهدات القصص |
| `comments`, `reactions`, `saved_posts` | engagement | التفاعل |
| `communities`, `community_members` | groups with kinds (public/approval/invite) and roles (owner/manager/moderator/member) | المجتمعات والأدوار |
| `conversations`, `conversation_members`, `messages` | DMs; `is_request` marks message requests; messages can reference a story or shared post | الرسائل الخاصة |
| `notifications` | per-kind, gated by `user_settings` toggles | الإشعارات |
| `live_streams`, `live_guests`, `live_viewers`, `live_comments` | public live streams: metadata, guest requests, viewers, chat, pinned comments | البث المباشر العام |
| `reports` | reports on post/comment/user/stream/message with status workflow | البلاغات |
| `blocks`, `mutes` | user-level block/mute | الحظر والكتم |
| `moderation_actions` | every moderator decision | إجراءات الإشراف |
| `user_settings` | language, who-can-message, notification toggles, like-count visibility | إعدادات المستخدم |
| `audit_logs` | admin/system audit trail | سجل التدقيق |

## Key relationships | العلاقات الرئيسية

- `posts.author_id → users.id`; `post_audiences.post_id → posts.id` (a post appears in every section listed).
- Section visibility rules live in `silver/services.py` (`feed_*` functions):
  - **circle**: audience `circle` + author is a mutual follow.
  - **front**: audience `front` + author is followed.
  - **interests**: audience `interests`/`front` + category ∈ viewer's interests.
  - **communities**: post's community ∈ viewer's active memberships.
  - **nearby**: audience `nearby`/`front` + same city (approximate location only; exact location is never stored).
- Blocking removes both follow edges and filters all feeds/search both ways.

## Environment variables | متغيرات البيئة

| Variable | Default | Purpose |
|---|---|---|
| `SILVER_DATA_DIR` | `./data` | database + media location |
| `SILVER_ADMIN_USERNAME` | `admin` | bootstrap admin username |
| `SILVER_ADMIN_EMAIL` | `admin@silver.local` | bootstrap admin email |
| `SILVER_ADMIN_PASSWORD` | `ChangeMe_123` | bootstrap admin password — **change in production** |

The admin account is created only once (first run with no admin present).
