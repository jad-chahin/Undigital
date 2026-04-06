import sys
import random
from typing import Literal, TypedDict, cast

import pygame

from game_constants import (
    BOOKTOK_LABELS,
    FORUM_BAD_COMMENTS,
    FORUM_COMMENT_LIFE,
    FORUM_COMMENT_ROW_HEIGHT,
    FORUM_GOOD_COMMENTS,
    FORUM_POST_BODY,
    FORUM_POST_TITLE,
    FORUM_SPAWN_MS,
    FORUM_THREAD_COMMENTS_TOP,
    FORUM_TITLE_TEXT,
    FPS,
    LEVEL_OBJECTIVES,
    LEVEL1_SPAWN_INTERVAL,
    LEVEL3_CLEAR_HOLD_SECONDS,
    LEVEL3_NOTIFICATION_MAX,
    LEVEL3_NOTIFICATION_SPAWN_MS,
    LEVEL3_NOTIFICATION_TEXTS,
    LEVEL3_TASK_COOLDOWN_SECONDS,
    LEVEL3_TASK_HOLD_SECONDS,
    LEVEL3_TASK_SPAWN_SECONDS,
    LEVEL3_TIME_LIMIT,
    LEVEL4_AD_BRANDS,
    LEVEL4_AD_HEADLINES,
    LEVEL4_AD_OFFERS,
    LEVEL4_BASE_FEATURES,
    LEVEL4_CONTACTS,
    LEVEL4_EXTRA_FEATURES,
    LEVEL4_NEWS_ALERTS,
    LEVEL4_NEWS_NUDGES,
    LEVEL4_NEW_FEATURE_MS,
    LEVEL4_POPUP_MS,
    LEVEL4_PROMPT_BENEFITS,
    LEVEL4_PROMPT_CTAS,
    LEVEL4_PROMPT_HOOKS,
    LEVEL4_REENABLE_MS,
    LEVEL4_SOCIAL_PROOF,
    LEVEL4_TEXT_NUDGES,
    LEVEL4_TIME_LIMIT,
    LEVEL4_UPDATE_MESSAGES,
    LEVELS,
    OTHER_LABELS,
    PLAYER_SIZE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from ui_helpers import draw_3d_text, draw_text, draw_text_left, draw_wrapped_text_center


LevelMode = Literal["booktok", "forum", "logoff", "settings", "placeholder"]


class LevelDef(TypedDict):
    name: str
    bg_color: tuple[int, int, int]
    mode: LevelMode


class FallingPost(TypedDict):
    rect: pygame.Rect
    label: str
    is_booktok: bool
    speed: float


class ForumComment(TypedDict):
    rect: pygame.Rect
    text: str
    is_bad: bool
    age: float
    life: float
    approve_rect: pygame.Rect
    disapprove_rect: pygame.Rect


class Level4Feature(TypedDict):
    name: str
    on: bool
    active: bool


class Level4Popup(TypedDict):
    title: str
    id: int
    tag: str
    kind: str
    text: str
    x: int
    y: int
    w: int
    h: int


class PopupCampaign(TypedDict):
    text: str
    title: str
    kind: str
    tag: str


class Level4Layout(TypedDict):
    app_frame: pygame.Rect
    header: pygame.Rect
    list_rect: pygame.Rect
    row_x: int
    row_w: int
    row_h: int
    start_y: int
    gap: int
    content_height: int
    max_scroll: float


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Simple Pygame App")
    clock = pygame.time.Clock()

    player = pygame.Rect(
        (WINDOW_WIDTH - PLAYER_SIZE) // 2,
        (WINDOW_HEIGHT - PLAYER_SIZE) // 2,
        PLAYER_SIZE,
        PLAYER_SIZE,
    )

    title_font = pygame.font.SysFont(None, 56)
    menu_font = pygame.font.SysFont(None, 36)
    hud_font = pygame.font.SysFont(None, 28)
    forum_title_font = pygame.font.SysFont(None, 34)
    forum_text_font = pygame.font.SysFont(None, 24)
    forum_comment_font = pygame.font.SysFont(None, 22)

    game_state = "menu"
    selected_index = 0
    levels: list[LevelDef] = cast(list[LevelDef], LEVELS)
    active_level: LevelDef = levels[selected_index]
    feed_score = 0
    falling_posts: list[FallingPost] = []
    spawn_counter = 0
    feed_ratio = 0.25
    booktok_topic_weights: dict[str, float] = {}
    level1_result: str | None = None
    forum_comments: list[ForumComment] = []
    forum_points = 0
    forum_safety_score = 50
    forum_spawn_timer_ms = 0
    forum_ban_flash = 0.0
    forum_result: str | None = None
    forum_points_delta = 0
    forum_points_delta_timer = 0.0
    forum_points_delta_duration = 0.55
    level3_notifications: list[str] = []
    level3_notification_timer_ms = 0
    level3_stress = 0.0
    level3_break = 0.0
    level3_task_progress = 0.0
    level3_elapsed = 0.0
    level3_result: str | None = None
    level3_pending_tasks: list[str] = []
    level3_task_cooldowns: dict[str, float] = {}
    level3_task_spawn_timer = 0.0
    level3_active_task: str | None = None
    level3_clear_progress = 0.0
    level3_active_notification = -1
    level3_focus_streak = 1
    level4_features: list[Level4Feature] = []
    level4_extra_index = 0
    level4_reenable_timer_ms = 0
    level4_new_feature_timer_ms = 0
    level4_popup_timer_ms = 0
    level4_popup_stack: list[Level4Popup] = []
    level4_popup_serial = 0
    level4_popup_seen: set[str] = set()
    level4_elapsed = 0.0
    level4_result: str | None = None
    level4_scroll = 0.0

    def start_level(level_def: LevelDef) -> None:
        nonlocal feed_score, falling_posts, spawn_counter, feed_ratio, booktok_topic_weights
        nonlocal level1_result, forum_comments, forum_points, forum_safety_score
        nonlocal forum_spawn_timer_ms, forum_ban_flash, forum_result
        nonlocal forum_points_delta, forum_points_delta_timer
        nonlocal level3_notifications, level3_notification_timer_ms, level3_stress
        nonlocal level3_break, level3_task_progress, level3_elapsed, level3_result
        nonlocal level3_pending_tasks, level3_task_cooldowns, level3_task_spawn_timer
        nonlocal level3_active_task, level3_clear_progress, level3_active_notification, level3_focus_streak
        nonlocal level4_features, level4_extra_index, level4_reenable_timer_ms
        nonlocal level4_new_feature_timer_ms, level4_popup_timer_ms, level4_popup_stack
        nonlocal level4_popup_serial, level4_popup_seen, level4_elapsed, level4_result, level4_scroll
        mode_in = level_def["mode"]
        if mode_in == "booktok":
            player.width = 90
            player.height = 16
            player.midbottom = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20)
            feed_score = 0
            falling_posts = []
            spawn_counter = 0
            feed_ratio = 0.25
            booktok_topic_weights = {label: 1.0 for label in BOOKTOK_LABELS}
            level1_result = None
        elif mode_in == "forum":
            forum_comments = []
            forum_points = 0
            forum_safety_score = 50
            forum_spawn_timer_ms = 0
            forum_ban_flash = 0.0
            forum_result = None
            forum_points_delta = 0
            forum_points_delta_timer = 0.0
        elif mode_in == "logoff":
            player.width = 28
            player.height = 28
            player.center = (200, WINDOW_HEIGHT // 2)
            level3_notifications = []
            level3_notification_timer_ms = 0
            level3_stress = 0.0
            level3_break = 0.0
            level3_task_progress = 0.0
            level3_elapsed = 0.0
            level3_result = None
            level3_pending_tasks = ["Do Work"]
            level3_task_cooldowns = {"Do Work": 0.0, "Water Plant": 2.5, "Make Meal": 5.0}
            level3_task_spawn_timer = 4.0
            level3_active_task = None
            level3_clear_progress = 0.0
            level3_active_notification = -1
            level3_focus_streak = 1
        elif mode_in == "settings":
            level4_features = [{"name": feature_name, "on": True, "active": True} for feature_name in LEVEL4_BASE_FEATURES]
            level4_extra_index = 0
            level4_reenable_timer_ms = 0
            level4_new_feature_timer_ms = 0
            level4_popup_timer_ms = 0
            level4_popup_stack = []
            level4_popup_serial = 0
            level4_popup_seen = set()
            level4_elapsed = 0.0
            level4_result = None
            level4_scroll = 0.0
        else:
            player.width = PLAYER_SIZE
            player.height = PLAYER_SIZE
            player.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    def level4_queue_popup(
        raw_text: str,
        *,
        title: str = "Sponsored",
        popup_kind: str = "ad",
        popup_tag: str = "SPONSORED",
        width: int = 440,
        height: int = 180,
    ) -> None:
        nonlocal level4_popup_stack, level4_popup_serial
        level4_popup_serial += 1
        text = raw_text
        # Popups appear in varied places while still staying readable.
        popup_offsets = [(-150, -85), (110, -70), (-108, 30), (95, 44), (-26, -18), (42, 8)]
        off_x, off_y = random.choice(popup_offsets)
        popup_x = max(28, min(WINDOW_WIDTH - 28 - width, WINDOW_WIDTH // 2 - (width // 2) + off_x))
        popup_y = max(24, min(WINDOW_HEIGHT - 24 - height, WINDOW_HEIGHT // 2 - (height // 2) + off_y))
        level4_popup_stack.append(
            {
                "title": title,
                "id": level4_popup_serial,
                "tag": popup_tag,
                "kind": popup_kind,
                "text": text,
                "x": popup_x,
                "y": popup_y,
                "w": width,
                "h": height,
            }
        )
        if len(level4_popup_stack) > 5:
            level4_popup_stack.pop(0)

    def level4_next_progressive_popup() -> PopupCampaign:
        nonlocal level4_popup_seen
        stage_count = len(LEVEL4_PROMPT_HOOKS)
        stage = min(stage_count - 1, int((level4_elapsed / LEVEL4_TIME_LIMIT) * stage_count))

        active_names = [str(f["name"]) for f in level4_features if bool(f["active"])]
        off_names = [str(f["name"]) for f in level4_features if bool(f["active"]) and not bool(f["on"])]
        focus_name = random.choice(off_names) if off_names else (random.choice(active_names) if active_names else "Smart Controls")

        for _ in range(48):
            channel = random.choices(["ad", "text", "news", "system"], weights=[0.46, 0.2, 0.2, 0.14], k=1)[0]
            popup_tag = "SPONSORED"
            popup_kind = "ad"
            if channel == "text":
                sender = random.choice(LEVEL4_CONTACTS)
                body = random.choice(LEVEL4_TEXT_NUDGES[stage]).format(name=focus_name)
                message = f"Message from {sender}: \"{body}\""
                popup_title = "Direct Message"
                popup_tag = "MESSAGE"
                popup_kind = "message"
            elif channel == "news":
                body = random.choice(LEVEL4_NEWS_ALERTS + LEVEL4_NEWS_NUDGES[stage]).format(name=focus_name)
                message = body
                popup_title = "News Alert"
                popup_tag = "ALERT"
                popup_kind = "news"
            elif channel == "ad":
                brand = random.choice(LEVEL4_AD_BRANDS)
                headline = random.choice(LEVEL4_AD_HEADLINES[stage]).format(name=focus_name)
                offer = random.choice(LEVEL4_AD_OFFERS[stage]).format(name=focus_name)
                cta = random.choice(LEVEL4_PROMPT_CTAS[stage]).format(name=focus_name)
                message = f"{brand}: {headline} {offer} {cta}"
                popup_title = brand
            else:
                hook = random.choice(LEVEL4_PROMPT_HOOKS[stage]).format(
                    name=focus_name,
                    proof=random.choice(LEVEL4_SOCIAL_PROOF),
                )
                benefit = random.choice(LEVEL4_PROMPT_BENEFITS[stage]).format(name=focus_name)
                cta = random.choice(LEVEL4_PROMPT_CTAS[stage]).format(name=focus_name)
                message = f"{hook} {benefit} {cta}"
                popup_title = "System Advisory"
                popup_tag = "SYSTEM"
                popup_kind = "update"
            if message not in level4_popup_seen:
                level4_popup_seen.add(message)
                return {"text": message, "title": popup_title, "kind": popup_kind, "tag": popup_tag}

        # Fallback is still unique once wrapped by Notice serial.
        return {
            "text": f"{focus_name} was automatically prioritized to improve platform performance.",
            "title": "System Advisory",
            "kind": "update",
            "tag": "SYSTEM",
        }

    def level4_layout() -> Level4Layout:
        layout_row_h = 46
        layout_gap = 10
        layout_app_frame = pygame.Rect(52, 34, WINDOW_WIDTH - 104, WINDOW_HEIGHT - 68)
        layout_header = pygame.Rect(
            layout_app_frame.x + 14,
            layout_app_frame.y + 14,
            layout_app_frame.width - 28,
            64,
        )
        layout_list_rect = pygame.Rect(
            layout_app_frame.x + 14,
            layout_header.bottom + 8,
            layout_app_frame.width - 28,
            layout_app_frame.height - 100,
        )
        layout_content_height = max(0, len(level4_features) * (layout_row_h + layout_gap) - layout_gap + 16)
        layout_max_scroll = max(0.0, float(layout_content_height - layout_list_rect.height))
        return {
            "app_frame": layout_app_frame,
            "header": layout_header,
            "list_rect": layout_list_rect,
            "row_x": 72,
            "row_w": WINDOW_WIDTH - 144,
            "row_h": layout_row_h,
            "start_y": layout_list_rect.y + 8,
            "gap": layout_gap,
            "content_height": layout_content_height,
            "max_scroll": layout_max_scroll,
        }

    def level3_notification_rect(notification_panel_rect: pygame.Rect, index: int) -> pygame.Rect:
        return pygame.Rect(
            notification_panel_rect.x + 10,
            notification_panel_rect.y + 10 + index * 34,
            notification_panel_rect.width - 20,
            28,
        )

    def level4_top_popup_close_rect(popup: Level4Popup) -> pygame.Rect:
        return pygame.Rect(
            int(popup["x"]) + int(popup["w"]) - 34,
            int(popup["y"]) + 10,
            24,
            24,
        )

    def level4_queue_campaign_popup(campaign: PopupCampaign) -> None:
        level4_queue_popup(
            campaign["text"],
            title=str(campaign["title"]),
            popup_kind=str(campaign["kind"]),
            popup_tag=str(campaign["tag"]),
        )

    running = True
    while running:
        dt_ms = clock.tick(FPS)
        dt = dt_ms / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == "menu":
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(levels)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(levels)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        active_level = levels[selected_index]
                        game_state = "briefing"
                    elif pygame.K_1 <= event.key <= pygame.K_4:
                        selected_index = min(event.key - pygame.K_1, len(levels) - 1)
                elif game_state == "playing" and event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                elif game_state == "briefing" and event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                elif (
                    game_state == "playing"
                    and active_level.get("mode") == "booktok"
                    and level1_result is not None
                    and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                ):
                    game_state = "menu"
                elif (
                    game_state == "playing"
                    and active_level.get("mode") == "forum"
                    and forum_result is not None
                    and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                ):
                    game_state = "menu"
                elif (
                    game_state == "playing"
                    and active_level.get("mode") == "logoff"
                    and level3_result is not None
                    and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                ):
                    game_state = "menu"
                elif (
                    game_state == "playing"
                    and active_level.get("mode") == "settings"
                    and level4_result is not None
                    and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                ):
                    game_state = "menu"
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and game_state == "briefing"
            ):
                understand_rect = pygame.Rect(WINDOW_WIDTH // 2 - 110, WINDOW_HEIGHT // 2 + 95, 220, 42)
                if understand_rect.collidepoint(event.pos):
                    start_level(active_level)
                    game_state = "playing"
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and game_state == "playing"
                and active_level.get("mode") == "forum"
                and forum_result is None
            ):
                for comment in forum_comments[:]:
                    approve_rect = comment["approve_rect"]
                    disapprove_rect = comment["disapprove_rect"]
                    if approve_rect.collidepoint(event.pos):
                        if comment["is_bad"]:
                            forum_points -= 1
                            forum_safety_score = max(0, forum_safety_score - 4)
                            forum_points_delta = -1
                        else:
                            forum_points += 1
                            forum_safety_score = min(100, forum_safety_score + 1)
                            forum_points_delta = 1
                        forum_points_delta_timer = forum_points_delta_duration
                        forum_comments.remove(comment)
                        break
                    if disapprove_rect.collidepoint(event.pos):
                        if comment["is_bad"]:
                            forum_ban_flash = 0.18
                        else:
                            pass
                        forum_points_delta = 0
                        forum_points_delta_timer = forum_points_delta_duration
                        forum_comments.remove(comment)
                        break
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and game_state == "playing"
                and active_level.get("mode") == "settings"
                and level4_result is None
            ):
                click_pos = event.pos
                if level4_popup_stack:
                    top_popup = level4_popup_stack[-1]
                    popup_close_rect = level4_top_popup_close_rect(top_popup)
                    if popup_close_rect.collidepoint(click_pos):
                        level4_popup_stack.pop()
                else:
                    layout = level4_layout()
                    list_rect = layout["list_rect"]
                    row_x = layout["row_x"]
                    row_w = layout["row_w"]
                    row_h = layout["row_h"]
                    start_y = layout["start_y"]
                    gap = layout["gap"]
                    level4_scroll = max(0.0, min(level4_scroll, layout["max_scroll"]))
                    for feature_index, feature in enumerate(level4_features):
                        if not bool(feature["active"]):
                            continue
                        row_y = start_y + feature_index * (row_h + gap) - int(level4_scroll)
                        row_rect = pygame.Rect(row_x, row_y, row_w, row_h)
                        if row_rect.bottom < list_rect.y + 6 or row_rect.top > list_rect.bottom - 6:
                            continue
                        if not list_rect.collidepoint(click_pos):
                            continue
                        if row_rect.collidepoint(click_pos):
                            feature["on"] = not bool(feature["on"])
                            if not bool(feature["on"]) and random.random() < 0.18 and len(level4_popup_stack) < 2:
                                campaign = level4_next_progressive_popup()
                                level4_queue_campaign_popup(campaign)
                            break
            elif (
                event.type == pygame.MOUSEWHEEL
                and game_state == "playing"
                and active_level.get("mode") == "settings"
                and level4_result is None
                and not level4_popup_stack
            ):
                layout = level4_layout()
                level4_scroll -= float(event.y) * 26.0
                level4_scroll = max(0.0, min(level4_scroll, layout["max_scroll"]))

        if game_state == "playing":
            keys = pygame.key.get_pressed()
            if active_level.get("mode") == "booktok":
                if level1_result is None:
                    player_speed = 7
                    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                        player.x -= player_speed
                    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                        player.x += player_speed
                    player.clamp_ip(screen.get_rect())
                    player.y = WINDOW_HEIGHT - player.height - 20

                    spawn_counter += 1
                    if spawn_counter >= LEVEL1_SPAWN_INTERVAL:
                        spawn_counter = 0
                        is_booktok = random.random() < feed_ratio
                        if is_booktok:
                            weights = [booktok_topic_weights[label] for label in BOOKTOK_LABELS]
                            label = random.choices(BOOKTOK_LABELS, weights=weights, k=1)[0]
                        else:
                            label = random.choice(OTHER_LABELS)
                        post_width = 150
                        post_height = 34
                        post_rect = pygame.Rect(
                            random.randint(10, WINDOW_WIDTH - post_width - 10),
                            -post_height,
                            post_width,
                            post_height,
                        )
                        falling_posts.append(
                            {
                                "rect": post_rect,
                                "label": label,
                                "is_booktok": is_booktok,
                                "speed": random.uniform(2.4, 4.2),
                            }
                        )

                    next_posts: list[FallingPost] = []
                    for post in falling_posts:
                        post_rect = post["rect"]
                        post_rect.y += int(post["speed"])

                        if post_rect.colliderect(player):
                            if post["is_booktok"]:
                                feed_score += 1
                                feed_ratio = min(1.0, feed_ratio + 0.08)
                                caught_label = str(post["label"])
                                booktok_topic_weights[caught_label] += 0.75
                            else:
                                feed_score = max(0, feed_score - 1)
                                feed_ratio = max(0.0, feed_ratio - 0.10)
                            continue

                        if post_rect.top <= WINDOW_HEIGHT:
                            next_posts.append(post)
                    falling_posts = next_posts

                    if feed_ratio >= 1.0:
                        level1_result = "win"
                    else:
                        active_booktok_posts = any(bool(post["is_booktok"]) for post in falling_posts)
                        if feed_ratio <= 0.0 and not active_booktok_posts:
                            level1_result = "lose"
            elif active_level.get("mode") == "forum":
                forum_ban_flash = max(0.0, forum_ban_flash - dt)
                forum_points_delta_timer = max(0.0, forum_points_delta_timer - dt)
                if forum_result is None:
                    forum_spawn_timer_ms += dt_ms
                    if forum_spawn_timer_ms >= FORUM_SPAWN_MS:
                        forum_spawn_timer_ms = 0
                        hate_probability = 0.75 - (forum_safety_score / 100) * 0.55
                        is_bad = random.random() < hate_probability
                        label = random.choice(FORUM_BAD_COMMENTS if is_bad else FORUM_GOOD_COMMENTS)
                        comment_width = WINDOW_WIDTH - 80
                        comment_height = 36
                        new_y = FORUM_THREAD_COMMENTS_TOP + len(forum_comments) * FORUM_COMMENT_ROW_HEIGHT
                        if new_y + comment_height <= WINDOW_HEIGHT - 18:
                            forum_comments.append(
                                {
                                    "rect": pygame.Rect(40, new_y, comment_width, comment_height),
                                    "text": label,
                                    "is_bad": is_bad,
                                    "age": 0.0,
                                    "life": FORUM_COMMENT_LIFE,
                                    "approve_rect": pygame.Rect(0, 0, 84, 28),
                                    "disapprove_rect": pygame.Rect(0, 0, 104, 28),
                                }
                            )

                    for comment in forum_comments:
                        comment["age"] += dt

                    for comment in forum_comments[:]:
                        if float(comment["age"]) >= float(comment["life"]):
                            if comment["is_bad"]:
                                forum_points -= 2
                                forum_safety_score = max(0, forum_safety_score - 4)
                                forum_points_delta = -2
                            else:
                                forum_points_delta = 0
                            forum_points_delta_timer = forum_points_delta_duration
                            forum_comments.remove(comment)

                    if forum_safety_score <= 0:
                        forum_result = "lose"
                    elif forum_safety_score >= 100:
                        forum_result = "win"

                for comment_index, comment in enumerate(forum_comments):
                    comment["rect"].y = FORUM_THREAD_COMMENTS_TOP + comment_index * FORUM_COMMENT_ROW_HEIGHT
                    comment["approve_rect"].x = comment["rect"].right - 204
                    comment["approve_rect"].y = comment["rect"].y + 4
                    comment["disapprove_rect"].x = comment["rect"].right - 112
                    comment["disapprove_rect"].y = comment["rect"].y + 4
            elif active_level.get("mode") == "logoff":
                work_rect = pygame.Rect(90, 140, 130, 90)
                meal_rect = pygame.Rect(290, 280, 110, 85)
                plant_rect = pygame.Rect(160, 430, 120, 95)
                task_rects = {"Do Work": work_rect, "Make Meal": meal_rect, "Water Plant": plant_rect}
                phone_screen_rect = pygame.Rect(WINDOW_WIDTH - 240, 120, 210, WINDOW_HEIGHT - 160)
                mouse_pos = pygame.mouse.get_pos()
                mouse_down = pygame.mouse.get_pressed()[0]

                if level3_result is None:
                    level3_elapsed += dt

                    level3_notification_timer_ms += dt_ms
                    if level3_notification_timer_ms >= LEVEL3_NOTIFICATION_SPAWN_MS:
                        level3_notification_timer_ms = 0
                        if len(level3_notifications) < LEVEL3_NOTIFICATION_MAX:
                            level3_notifications.append(random.choice(LEVEL3_NOTIFICATION_TEXTS))

                    hovered_notification_preview = -1
                    for preview_index, _ in enumerate(level3_notifications):
                        notif_rect = level3_notification_rect(phone_screen_rect, preview_index)
                        if notif_rect.collidepoint(mouse_pos):
                            hovered_notification_preview = preview_index
                            break
                    suppressing_notification = mouse_down and hovered_notification_preview >= 0
                    effective_notifications = len(level3_notifications) - (1 if suppressing_notification else 0)
                    effective_notifications = max(0, effective_notifications)

                    for task_name in level3_task_cooldowns:
                        level3_task_cooldowns[task_name] = max(0.0, level3_task_cooldowns[task_name] - dt)

                    level3_task_spawn_timer -= dt
                    if level3_task_spawn_timer <= 0.0:
                        available_tasks = [
                            task_name
                            for task_name in ("Do Work", "Make Meal", "Water Plant")
                            if task_name not in level3_pending_tasks and level3_task_cooldowns[task_name] <= 0.0
                        ]
                        if available_tasks:
                            level3_pending_tasks.append(available_tasks[0])
                        level3_task_spawn_timer = LEVEL3_TASK_SPAWN_SECONDS

                    stress_gain = dt * (effective_notifications * 1.6)
                    level3_stress = min(100.0, level3_stress + stress_gain)

                    hovered_task_name = None
                    for task_name in level3_pending_tasks:
                        pending_rect = task_rects[task_name].inflate(18, 18)
                        if pending_rect.collidepoint(mouse_pos):
                            hovered_task_name = task_name
                            break

                    if hovered_task_name and mouse_down:
                        if level3_active_task != hovered_task_name:
                            level3_task_progress = 0.0
                        level3_active_task = hovered_task_name
                        level3_task_progress = min(1.0, level3_task_progress + dt / LEVEL3_TASK_HOLD_SECONDS)
                    else:
                        level3_active_task = None
                        level3_task_progress = max(0.0, level3_task_progress - dt * 1.6)

                    if level3_task_progress >= 1.0 and level3_active_task is not None:
                        completed_task = level3_active_task
                        level3_task_progress = 0.0
                        level3_active_task = None
                        break_gain = 6.0 * float(level3_focus_streak)
                        level3_break = min(100.0, level3_break + break_gain)
                        level3_focus_streak += 1
                        if completed_task in level3_pending_tasks:
                            level3_pending_tasks.remove(completed_task)
                        level3_task_cooldowns[completed_task] = LEVEL3_TASK_COOLDOWN_SECONDS
                        if not level3_pending_tasks:
                            level3_task_spawn_timer = min(level3_task_spawn_timer, 2.5)

                    hovered_notification = -1
                    for clear_index, _ in enumerate(level3_notifications):
                        notif_rect = level3_notification_rect(phone_screen_rect, clear_index)
                        if notif_rect.collidepoint(mouse_pos):
                            hovered_notification = clear_index
                            break

                    if hovered_notification >= 0 and mouse_down:
                        if level3_active_notification != hovered_notification:
                            level3_clear_progress = 0.0
                        level3_active_notification = hovered_notification
                        level3_clear_progress = min(1.0, level3_clear_progress + dt / LEVEL3_CLEAR_HOLD_SECONDS)
                    else:
                        level3_active_notification = -1
                        level3_clear_progress = max(0.0, level3_clear_progress - dt * 2.0)

                    if level3_clear_progress >= 1.0:
                        level3_clear_progress = 0.0
                        if 0 <= level3_active_notification < len(level3_notifications):
                            level3_notifications.pop(level3_active_notification)
                        level3_active_notification = -1
                        level3_focus_streak = 1

                    if level3_break >= 100.0:
                        level3_result = "win"
                    elif level3_stress >= 100.0:
                        level3_result = "stress"
                    elif level3_elapsed >= LEVEL3_TIME_LIMIT:
                        level3_result = "time"
            elif active_level.get("mode") == "settings":
                if level4_result is None:
                    level4_elapsed += dt
                    level4_reenable_timer_ms += dt_ms
                    level4_new_feature_timer_ms += dt_ms
                    level4_popup_timer_ms += dt_ms

                    if level4_reenable_timer_ms >= LEVEL4_REENABLE_MS:
                        level4_reenable_timer_ms = 0
                        off_features = [f for f in level4_features if bool(f["active"]) and not bool(f["on"])]
                        if off_features:
                            picked = random.choice(off_features)
                            picked["on"] = True
                            level4_queue_popup(
                                random.choice(LEVEL4_UPDATE_MESSAGES).format(name=str(picked["name"])),
                                title="Update Installed",
                                popup_kind="update",
                                popup_tag="UPDATE",
                            )

                    if level4_new_feature_timer_ms >= LEVEL4_NEW_FEATURE_MS:
                        level4_new_feature_timer_ms = 0
                        if level4_extra_index < len(LEVEL4_EXTRA_FEATURES):
                            name = LEVEL4_EXTRA_FEATURES[level4_extra_index]
                            level4_features.append({"name": name, "on": True, "active": True})
                            level4_extra_index += 1
                            if random.random() < 0.6:
                                level4_queue_popup(
                                    f"New premium setting unlocked: '{name}'. It is now active by default.",
                                    title="Feature Drop",
                                    popup_kind="ad",
                                    popup_tag="NEW",
                                )

                    if level4_popup_timer_ms >= LEVEL4_POPUP_MS:
                        level4_popup_timer_ms = 0
                        if len(level4_popup_stack) < 2:
                            campaign = level4_next_progressive_popup()
                            level4_queue_campaign_popup(campaign)

                    active_features = [f for f in level4_features if bool(f["active"])]
                    if active_features and all(not bool(f["on"]) for f in active_features):
                        restored = random.choice(active_features)
                        restored["on"] = True
                        level4_queue_popup(
                            random.choice(LEVEL4_UPDATE_MESSAGES).format(name=str(restored["name"])),
                            title="Mandatory Update",
                            popup_kind="update",
                            popup_tag="UPDATE",
                        )
                    if level4_elapsed >= LEVEL4_TIME_LIMIT:
                        level4_result = "lose"
            elif active_level.get("mode") == "placeholder":
                pass
            else:
                pass

        if game_state == "menu":
            screen.fill((15, 15, 22))
            draw_3d_text(
                screen,
                title_font,
                "Undigital",
                (WINDOW_WIDTH // 2, 85),
            )
            draw_text(
                screen,
                title_font,
                "Select a Level",
                (235, 235, 245),
                (WINDOW_WIDTH // 2, 150),
            )
            for menu_index, level_info in enumerate(levels):
                color = (255, 220, 80) if menu_index == selected_index else (190, 190, 205)
                draw_text(
                    screen,
                    menu_font,
                    f"{menu_index + 1}. {level_info['name']}",
                    color,
                    (WINDOW_WIDTH // 2, 220 + menu_index * 55),
                )
            draw_text(
                screen,
                hud_font,
                "Use Up/Down or 1-4, Enter to start",
                (160, 160, 180),
                (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80),
            )
        elif game_state == "briefing":
            screen.fill((18, 22, 34))
            panel = pygame.Rect(90, 90, WINDOW_WIDTH - 180, WINDOW_HEIGHT - 180)
            pygame.draw.rect(screen, (32, 39, 58), panel, border_radius=14)
            pygame.draw.rect(screen, (74, 89, 126), panel, width=2, border_radius=14)
            draw_text(screen, title_font, str(active_level["name"]), (239, 243, 252), (WINDOW_WIDTH // 2, 145))

            mode = str(active_level.get("mode", "placeholder"))
            objective_lines = LEVEL_OBJECTIVES.get(mode, LEVEL_OBJECTIVES["placeholder"])
            y = 210
            for objective_index, line in enumerate(objective_lines):
                color = (234, 239, 250) if objective_index == 0 else (206, 215, 233)
                draw_text(screen, hud_font, line, color, (WINDOW_WIDTH // 2, y))
                y += 38

            understand_rect = pygame.Rect(WINDOW_WIDTH // 2 - 110, WINDOW_HEIGHT // 2 + 95, 220, 42)
            pygame.draw.rect(screen, (102, 128, 188), understand_rect, border_radius=10)
            pygame.draw.rect(screen, (147, 170, 224), understand_rect, width=2, border_radius=10)
            draw_text(screen, hud_font, "I Understand", (245, 248, 255), understand_rect.center)
            draw_text(screen, forum_text_font, "Click to begin", (176, 188, 212), (WINDOW_WIDTH // 2, understand_rect.bottom + 26))
        else:
            screen.fill(active_level["bg_color"])
            if active_level.get("mode") == "booktok":
                for post in falling_posts:
                    post_rect = post["rect"]
                    color = (242, 236, 225) if post["is_booktok"] else (224, 224, 230)
                    pygame.draw.rect(screen, color, post_rect, border_radius=4)
                    pygame.draw.rect(screen, (70, 70, 85), post_rect, width=2, border_radius=4)
                    label_surface = hud_font.render(str(post["label"]), True, (40, 40, 55))
                    label_rect = label_surface.get_rect(center=post_rect.center)
                    screen.blit(label_surface, label_rect)

                pygame.draw.rect(screen, (90, 190, 255), player, border_radius=4)
                score_text = f"Feed Score: {feed_score}"
                score_surface = hud_font.render(score_text, True, (240, 240, 250))
                screen.blit(score_surface, (20, 18))
                bar_width = 230
                bar_height = 12
                bar_x = (WINDOW_WIDTH - bar_width) // 2
                bar_y = 24
                pygame.draw.rect(screen, (70, 70, 90), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
                fill_width = int(feed_ratio * bar_width)
                pygame.draw.rect(screen, (120, 220, 160), (bar_x, bar_y, fill_width, bar_height), border_radius=4)
                progress_percent = int(feed_ratio * 100)
                progress_label = hud_font.render(f"BookTok Feed: {progress_percent}%", True, (200, 210, 225))
                progress_rect = progress_label.get_rect(midbottom=(WINDOW_WIDTH // 2, bar_y - 3))
                screen.blit(progress_label, progress_rect)
                help_surface = hud_font.render(
                    "Catch BookTok to reach 100%, avoid other posts",
                    True,
                    (190, 190, 210),
                )
                help_rect = help_surface.get_rect(midtop=(WINDOW_WIDTH // 2, 18))
                help_rect.y += 30
                screen.blit(help_surface, help_rect)
                esc_surface = hud_font.render("ESC: menu", True, (190, 190, 210))
                esc_rect = esc_surface.get_rect(topright=(WINDOW_WIDTH - 20, 18))
                screen.blit(esc_surface, esc_rect)

                if level1_result is not None:
                    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((8, 8, 12, 120))
                    screen.blit(overlay, (0, 0))
                    if level1_result == "win":
                        draw_text(
                            screen,
                            title_font,
                            "You Win!",
                            (245, 245, 255),
                            (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 10),
                        )
                        draw_text(
                            screen,
                            hud_font,
                            "You are now a member of BookTok!",
                            (235, 235, 245),
                            (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30),
                        )
                    else:
                        draw_text(
                            screen,
                            title_font,
                            "You Lost!",
                            (245, 245, 255),
                            (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 10),
                        )
                        draw_text(
                            screen,
                            hud_font,
                            "BookTok is no longer reachable from this feed.",
                            (235, 235, 245),
                            (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30),
                        )
                    draw_text(
                        screen,
                        hud_font,
                        "Press Enter for menu",
                        (215, 215, 230),
                        (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 68),
                    )
            elif active_level.get("mode") == "forum":
                header_rect = pygame.Rect(20, 14, WINDOW_WIDTH - 40, 66)
                post_rect = pygame.Rect(20, 92, WINDOW_WIDTH - 40, 114)
                thread_rect = pygame.Rect(20, 216, WINDOW_WIDTH - 40, WINDOW_HEIGHT - 236)

                pygame.draw.rect(screen, (34, 46, 70), header_rect, border_radius=8)
                draw_text_left(screen, forum_title_font, FORUM_TITLE_TEXT, (245, 247, 252), (34, 31))

                meter_bg = pygame.Rect(WINDOW_WIDTH - 220, 34, 170, 16)
                pygame.draw.rect(screen, (103, 114, 136), meter_bg, border_radius=5)
                meter_fill = pygame.Rect(meter_bg.x, meter_bg.y, int((forum_safety_score / 100) * meter_bg.width), meter_bg.height)
                pygame.draw.rect(screen, (103, 175, 230), meter_fill, border_radius=5)
                draw_text_left(screen, forum_text_font, f"Safety Score: {forum_safety_score}", (245, 247, 252), (WINDOW_WIDTH - 232, 52))

                pygame.draw.rect(screen, (255, 255, 255), post_rect, border_radius=8)
                pygame.draw.rect(screen, (191, 199, 217), post_rect, width=2, border_radius=8)
                draw_text_left(screen, forum_text_font, FORUM_POST_TITLE, (33, 35, 47), (34, 102))
                draw_text_left(screen, forum_text_font, FORUM_POST_BODY, (65, 67, 82), (34, 130))
                draw_text_left(screen, forum_text_font, "Approve or Disapprove each comment before it fades.", (65, 67, 82), (34, 156))
                draw_text_left(screen, forum_text_font, f"Points: {forum_points}", (33, 35, 47), (WINDOW_WIDTH - 162, 156))

                pygame.draw.rect(screen, (255, 255, 255), thread_rect, border_radius=8)
                pygame.draw.rect(screen, (191, 199, 217), thread_rect, width=2, border_radius=8)
                draw_text_left(screen, forum_text_font, "Comment Thread", (33, 35, 47), (34, 224))
                draw_text_left(screen, forum_text_font, "ESC: menu", (80, 86, 106), (WINDOW_WIDTH - 126, 224))
                if forum_points_delta_timer > 0:
                    progress = forum_points_delta_timer / forum_points_delta_duration
                    delta_alpha = int(255 * progress)
                    delta_y = int((1.0 - progress) * 8)
                    if forum_points_delta > 0:
                        delta_text = f"+{forum_points_delta}"
                        delta_color = (118, 205, 156)
                    elif forum_points_delta < 0:
                        delta_text = str(forum_points_delta)
                        delta_color = (232, 118, 118)
                    else:
                        delta_text = "0"
                        delta_color = (176, 181, 193)
                    delta_surface = forum_text_font.render(delta_text, True, delta_color)
                    delta_surface.set_alpha(delta_alpha)
                    screen.blit(delta_surface, (WINDOW_WIDTH - 80, 156 - delta_y))

                for comment in forum_comments:
                    comment_rect = comment["rect"]
                    life = float(comment["life"])
                    age = float(comment["age"])
                    alpha = max(40, int(255 * (1.0 - age / life)))
                    base_rgb = (225, 230, 241)
                    comment_surface = pygame.Surface((comment_rect.width, comment_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(comment_surface, (*base_rgb, alpha), comment_surface.get_rect(), border_radius=5)
                    pygame.draw.rect(comment_surface, (127, 136, 154, alpha), comment_surface.get_rect(), width=1, border_radius=5)
                    screen.blit(comment_surface, comment_rect.topleft)

                    label_surface = forum_comment_font.render(str(comment["text"]), True, (33, 35, 47))
                    text_y = comment_rect.y + (comment_rect.height - label_surface.get_height()) // 2
                    screen.blit(label_surface, (comment_rect.x + 10, text_y))

                    approve_rect = comment["approve_rect"]
                    disapprove_rect = comment["disapprove_rect"]
                    pygame.draw.rect(screen, (96, 170, 232), approve_rect, border_radius=4)
                    pygame.draw.rect(screen, (73, 136, 194), approve_rect, width=1, border_radius=4)
                    pygame.draw.rect(screen, (145, 153, 171), disapprove_rect, border_radius=4)
                    pygame.draw.rect(screen, (110, 118, 136), disapprove_rect, width=1, border_radius=4)
                    draw_text_left(screen, forum_comment_font, "Approve", (245, 248, 255), (approve_rect.x + 10, approve_rect.y + 5))
                    draw_text_left(screen, forum_comment_font, "Disapprove", (243, 245, 250), (disapprove_rect.x + 8, disapprove_rect.y + 5))

                if forum_ban_flash > 0:
                    flash_alpha = int(140 * (forum_ban_flash / 0.18))
                    flash = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    flash.fill((220, 20, 20, flash_alpha))
                    screen.blit(flash, (0, 0))

                if forum_result is not None:
                    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((8, 8, 12, 120))
                    screen.blit(overlay, (0, 0))
                    if forum_result == "win":
                        draw_text(
                            screen,
                            title_font,
                            "You Win!",
                            (245, 245, 255),
                            (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 10),
                        )
                        draw_text(
                            screen,
                            hud_font,
                            "Thread is safer and the tone improved.",
                            (235, 235, 245),
                            (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30),
                        )
                    else:
                        draw_text(
                            screen,
                            title_font,
                            "You Lost!",
                            (245, 245, 255),
                            (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 10),
                        )
                        draw_text(
                            screen,
                            hud_font,
                            "Safety collapsed under sustained harassment.",
                            (235, 235, 245),
                            (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30),
                        )
                    draw_text(
                        screen,
                        hud_font,
                        "Press Enter for menu",
                        (215, 215, 230),
                        (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 68),
                    )
            elif active_level.get("mode") == "logoff":
                phone_rect = pygame.Rect(WINDOW_WIDTH - 250, 70, 230, WINDOW_HEIGHT - 90)
                phone_screen_rect = pygame.Rect(WINDOW_WIDTH - 240, 120, 210, WINDOW_HEIGHT - 160)
                work_rect = pygame.Rect(90, 140, 130, 90)
                meal_rect = pygame.Rect(290, 280, 110, 85)
                plant_rect = pygame.Rect(160, 430, 120, 95)
                task_rects = {"Do Work": work_rect, "Make Meal": meal_rect, "Water Plant": plant_rect}
                mouse_pos = pygame.mouse.get_pos()

                pygame.draw.rect(screen, (38, 44, 60), pygame.Rect(20, 70, WINDOW_WIDTH - 280, WINDOW_HEIGHT - 90), border_radius=10)
                pygame.draw.rect(screen, (70, 78, 98), pygame.Rect(20, 70, WINDOW_WIDTH - 280, WINDOW_HEIGHT - 90), width=2, border_radius=10)

                ticks = pygame.time.get_ticks()
                for rect, label, color in (
                    (work_rect, "Do Work", (160, 148, 124)),
                    (meal_rect, "Make Meal", (176, 132, 106)),
                    (plant_rect, "Water Plant", (105, 149, 108)),
                ):
                    is_pending = label in level3_pending_tasks
                    is_hovered = rect.inflate(18, 18).collidepoint(mouse_pos)
                    border_color = (241, 212, 122) if is_pending else (54, 56, 68)
                    pygame.draw.rect(screen, color, rect, border_radius=8)
                    pygame.draw.rect(screen, border_color, rect, width=3 if is_pending else 2, border_radius=8)
                    if is_hovered and is_pending:
                        glow_rect = rect.inflate(10, 10)
                        pygame.draw.rect(screen, (241, 212, 122), glow_rect, width=2, border_radius=10)
                    draw_text(screen, hud_font, label, (245, 245, 250), rect.center)
                    if is_pending:
                        tag_rect = pygame.Rect(rect.x + 6, rect.y + 6, 62, 20)
                        pygame.draw.rect(screen, (94, 106, 139), tag_rect, border_radius=4)
                        draw_text_left(screen, forum_comment_font, "Pending", (236, 240, 250), (tag_rect.x + 6, tag_rect.y + 2))

                if level3_active_task == "Water Plant" and level3_task_progress > 0:
                    can_rect = pygame.Rect(plant_rect.right - 26, plant_rect.y - 28, 20, 16)
                    pygame.draw.rect(screen, (134, 152, 176), can_rect, border_radius=4)
                    spout_end = (can_rect.x + 2, can_rect.y + 9)
                    pygame.draw.line(screen, (134, 152, 176), (can_rect.x + 6, can_rect.y + 10), spout_end, 3)
                    for drop_index in range(6):
                        drop_phase = (ticks // 60 + drop_index * 2) % 20
                        drop_x = plant_rect.x + 16 + drop_index * 12
                        drop_y = plant_rect.y - 14 + drop_phase
                        pygame.draw.circle(screen, (116, 201, 245), (drop_x, drop_y), 3)
                    growth_h = int(16 * level3_task_progress)
                    growth_rect = pygame.Rect(plant_rect.centerx - 4, plant_rect.y + 20 - growth_h, 8, growth_h)
                    pygame.draw.rect(screen, (128, 198, 130), growth_rect, border_radius=3)
                elif level3_active_task == "Make Meal" and level3_task_progress > 0:
                    pan_rect = pygame.Rect(meal_rect.x + 14, meal_rect.y + 30, meal_rect.width - 30, 28)
                    pygame.draw.rect(screen, (92, 98, 112), pan_rect, border_radius=12)
                    pygame.draw.rect(screen, (72, 78, 92), pan_rect, width=2, border_radius=12)
                    for bubble_index in range(6):
                        bubble_x = pan_rect.x + 10 + bubble_index * 12
                        bubble_offset = ((ticks // 85 + bubble_index * 3) % 10)
                        bubble_y = pan_rect.y + 8 + bubble_offset
                        radius = 2 + ((ticks // 150 + bubble_index) % 2)
                        pygame.draw.circle(screen, (241, 218, 161), (bubble_x, bubble_y), radius)
                    for steam_index in range(3):
                        steam_x = meal_rect.centerx - 18 + steam_index * 18
                        steam_top = meal_rect.y + 6 - ((ticks // 95 + steam_index * 2) % 14)
                        pygame.draw.line(screen, (229, 231, 238), (steam_x, meal_rect.y + 18), (steam_x + 4, steam_top), 2)
                    stir_x = pan_rect.x + 8 + int((pan_rect.width - 16) * level3_task_progress)
                    pygame.draw.line(screen, (224, 174, 110), (stir_x, pan_rect.y + 4), (stir_x - 6, pan_rect.y + 20), 3)
                elif level3_active_task == "Do Work" and level3_task_progress > 0:
                    laptop_rect = pygame.Rect(work_rect.x + 16, work_rect.y + 20, work_rect.width - 32, 46)
                    pygame.draw.rect(screen, (70, 78, 98), laptop_rect, border_radius=5)
                    pygame.draw.rect(screen, (52, 58, 76), laptop_rect, width=2, border_radius=5)
                    for line_index in range(4):
                        line_w = 22 + ((ticks // 85 + line_index * 4) % 30)
                        line_rect = pygame.Rect(laptop_rect.x + 9, laptop_rect.y + 8 + line_index * 9, line_w, 3)
                        pygame.draw.rect(screen, (198, 209, 236), line_rect, border_radius=2)
                    cursor_x = laptop_rect.x + 10 + ((ticks // 70) % (laptop_rect.width - 20))
                    cursor_y = laptop_rect.bottom - 8
                    pygame.draw.line(screen, (246, 220, 132), (cursor_x, cursor_y), (cursor_x, cursor_y - 7), 2)
                    pulse_w = 2 + ((ticks // 140) % 2)
                    pygame.draw.rect(screen, (116, 144, 214), work_rect.inflate(8, 8), width=pulse_w, border_radius=9)

                if level3_active_task is not None:
                    active_rect = task_rects[level3_active_task]
                    task_bar_w = 160
                    task_bar_h = 10
                    task_bar_x = active_rect.centerx - task_bar_w // 2
                    task_bar_y = active_rect.y - 18
                    pygame.draw.rect(screen, (82, 89, 106), (task_bar_x, task_bar_y, task_bar_w, task_bar_h), border_radius=4)
                    pygame.draw.rect(
                        screen,
                        (119, 223, 173),
                        (task_bar_x, task_bar_y, int(task_bar_w * level3_task_progress), task_bar_h),
                        border_radius=4,
                    )

                pygame.draw.rect(screen, (22, 24, 35), phone_rect, border_radius=14)
                pygame.draw.rect(screen, (78, 88, 114), phone_rect, width=2, border_radius=14)
                pygame.draw.rect(screen, (41, 47, 66), phone_screen_rect, border_radius=8)
                draw_text(screen, hud_font, "Phone", (220, 226, 242), (phone_rect.centerx, 92))

                for notif_index, notif_text in enumerate(level3_notifications):
                    notif_rect = level3_notification_rect(phone_screen_rect, notif_index)
                    hovered = notif_rect.collidepoint(mouse_pos)
                    notif_color = (170, 136, 167) if hovered else (154, 123, 152)
                    pygame.draw.rect(screen, notif_color, notif_rect, border_radius=5)
                    pygame.draw.rect(screen, (96, 88, 108), notif_rect, width=1, border_radius=5)
                    draw_text_left(screen, forum_comment_font, notif_text, (242, 238, 246), (notif_rect.x + 8, notif_rect.y + 5))
                    if notif_index == level3_active_notification and level3_clear_progress > 0:
                        inner_bar = pygame.Rect(notif_rect.x + 8, notif_rect.bottom - 7, notif_rect.width - 16, 4)
                        pygame.draw.rect(screen, (80, 88, 112), inner_bar, border_radius=3)
                        pygame.draw.rect(screen, (122, 186, 235), (inner_bar.x, inner_bar.y, int(inner_bar.width * level3_clear_progress), inner_bar.height), border_radius=3)

                stress_bar = pygame.Rect(20, 20, 250, 14)
                break_bar = pygame.Rect(290, 20, 250, 14)
                pygame.draw.rect(screen, (77, 77, 90), stress_bar, border_radius=5)
                pygame.draw.rect(screen, (223, 116, 122), (stress_bar.x, stress_bar.y, int(stress_bar.width * (level3_stress / 100.0)), stress_bar.height), border_radius=5)
                pygame.draw.rect(screen, (77, 77, 90), break_bar, border_radius=5)
                pygame.draw.rect(screen, (114, 214, 166), (break_bar.x, break_bar.y, int(break_bar.width * (level3_break / 100.0)), break_bar.height), border_radius=5)
                draw_text_left(screen, forum_text_font, f"Stress Meter: {int(level3_stress)}", (235, 239, 248), (20, 38))
                draw_text_left(screen, forum_text_font, f"Progress Meter: {int(level3_break)}", (235, 239, 248), (290, 38))
                draw_text_left(screen, forum_text_font, f"Focus Multiplier: x{level3_focus_streak}", (200, 214, 238), (20, 58))

                remaining = max(0, int(LEVEL3_TIME_LIMIT - level3_elapsed))
                draw_text_left(screen, forum_text_font, f"Time Left: {remaining}s", (235, 239, 248), (560, 20))

                if level3_result is not None:
                    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((8, 8, 12, 120))
                    screen.blit(overlay, (0, 0))
                    if level3_result == "win":
                        draw_text(screen, title_font, "You Win!", (245, 245, 255), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 14))
                        draw_text(screen, hud_font, "You took a real break before burnout.", (235, 235, 245), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 24))
                    elif level3_result == "stress":
                        draw_text(screen, title_font, "You Lost!", (245, 245, 255), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 14))
                        draw_text(screen, hud_font, "Stress Meter filled completely.", (235, 235, 245), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 24))
                    else:
                        draw_text(screen, title_font, "Time Up!", (245, 245, 255), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 14))
                        draw_text(screen, hud_font, "Progress Meter did not fill in time.", (235, 235, 245), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 24))
                    draw_text(screen, hud_font, "Press Enter for menu", (215, 215, 230), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 62))
            elif active_level.get("mode") == "settings":
                layout = level4_layout()
                app_frame = layout["app_frame"]
                header = layout["header"]
                list_rect = layout["list_rect"]

                pygame.draw.rect(screen, (20, 24, 36), app_frame, border_radius=18)
                pygame.draw.rect(screen, (61, 74, 108), app_frame, width=2, border_radius=18)
                pygame.draw.rect(screen, (35, 46, 71), header, border_radius=10)
                draw_text_left(screen, menu_font, "App Settings", (238, 242, 251), (header.x + 14, header.y + 14))

                time_left = max(0, int(LEVEL4_TIME_LIMIT - level4_elapsed))
                draw_text_left(screen, forum_text_font, f"Time: {time_left}s", (200, 209, 226), (header.right - 120, header.y + 22))

                pygame.draw.rect(screen, (29, 36, 56), list_rect, border_radius=10)
                row_x = layout["row_x"]
                row_w = layout["row_w"]
                row_h = layout["row_h"]
                start_y = layout["start_y"]
                gap = layout["gap"]
                content_height = layout["content_height"]
                max_scroll = layout["max_scroll"]
                level4_scroll = max(0.0, min(level4_scroll, max_scroll))

                for render_feature_index, feature in enumerate(level4_features):
                    if not bool(feature["active"]):
                        continue
                    row_y = start_y + render_feature_index * (row_h + gap) - int(level4_scroll)
                    row_rect = pygame.Rect(row_x, row_y, row_w, row_h)
                    if row_rect.bottom < list_rect.y + 6 or row_rect.top > list_rect.bottom - 6:
                        continue
                    pygame.draw.rect(screen, (44, 53, 78), row_rect, border_radius=8)
                    pygame.draw.rect(screen, (67, 80, 113), row_rect, width=1, border_radius=8)
                    draw_text_left(screen, forum_text_font, str(feature["name"]), (228, 234, 247), (row_rect.x + 12, row_rect.y + 12))

                    toggle_rect = pygame.Rect(row_rect.right - 92, row_rect.y + 8, 76, 30)
                    if bool(feature["on"]):
                        pygame.draw.rect(screen, (196, 99, 112), toggle_rect, border_radius=15)
                        draw_text_left(screen, forum_comment_font, "ON", (255, 245, 247), (toggle_rect.x + 26, toggle_rect.y + 7))
                    else:
                        pygame.draw.rect(screen, (88, 150, 123), toggle_rect, border_radius=15)
                        draw_text_left(screen, forum_comment_font, "OFF", (236, 250, 244), (toggle_rect.x + 22, toggle_rect.y + 7))

                if max_scroll > 0:
                    track_rect = pygame.Rect(list_rect.right - 8, list_rect.y + 10, 4, list_rect.height - 20)
                    pygame.draw.rect(screen, (70, 83, 116), track_rect, border_radius=2)
                    thumb_h = max(30, int(track_rect.height * (list_rect.height / max(content_height, 1))))
                    thumb_y = track_rect.y + int((level4_scroll / max_scroll) * (track_rect.height - thumb_h))
                    thumb_rect = pygame.Rect(track_rect.x - 2, thumb_y, 8, thumb_h)
                    pygame.draw.rect(screen, (150, 167, 208), thumb_rect, border_radius=4)

                if level4_popup_stack:
                    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((8, 8, 12, 110))
                    screen.blit(overlay, (0, 0))
                    visible_popups = level4_popup_stack[-3:]
                    for idx, popup_item in enumerate(visible_popups):
                        layer = len(visible_popups) - idx - 1
                        popup_rect = pygame.Rect(
                            int(popup_item["x"]) + layer * 4,
                            int(popup_item["y"]) + layer * 4,
                            int(popup_item["w"]),
                            int(popup_item["h"]),
                        )
                        kind = str(popup_item.get("kind", "ad"))
                        if kind == "update":
                            fill = (54 + layer * 4, 60 + layer * 4, 82 + layer * 5)
                            border = (110 + layer * 4, 128 + layer * 4, 172 + layer * 5)
                            title_color = (238, 243, 252)
                            body_color = (212, 223, 242)
                            banner = (80, 94, 130)
                        elif kind == "news":
                            fill = (76 + layer * 3, 60 + layer * 3, 45 + layer * 4)
                            border = (178 + layer * 3, 134 + layer * 3, 97 + layer * 4)
                            title_color = (255, 243, 221)
                            body_color = (246, 229, 200)
                            banner = (142, 96, 56)
                        elif kind == "message":
                            fill = (48 + layer * 3, 64 + layer * 3, 56 + layer * 4)
                            border = (95 + layer * 3, 148 + layer * 3, 122 + layer * 4)
                            title_color = (233, 250, 238)
                            body_color = (214, 236, 220)
                            banner = (66, 118, 96)
                        else:
                            fill = (79 + layer * 3, 43 + layer * 4, 56 + layer * 5)
                            border = (206 + layer * 2, 122 + layer * 3, 143 + layer * 4)
                            title_color = (255, 236, 241)
                            body_color = (255, 219, 231)
                            banner = (170, 78, 111)
                        pygame.draw.rect(screen, fill, popup_rect, border_radius=12)
                        pygame.draw.rect(screen, border, popup_rect, width=2, border_radius=12)
                        banner_rect = pygame.Rect(popup_rect.x + 14, popup_rect.y + 12, popup_rect.width - 28, 24)
                        pygame.draw.rect(screen, banner, banner_rect, border_radius=6)
                        draw_text_left(
                            screen,
                            forum_comment_font,
                            str(popup_item.get("tag", "SPONSORED")),
                            (246, 248, 252),
                            (banner_rect.x + 8, banner_rect.y + 4),
                        )
                        title_surf = menu_font.render(str(popup_item.get("title", "Sponsored")), True, title_color)
                        title_rect = title_surf.get_rect(topleft=(popup_rect.x + 16, popup_rect.y + 46))
                        screen.blit(title_surf, title_rect)
                        if kind == "ad":
                            cta_rect = pygame.Rect(popup_rect.right - 160, popup_rect.bottom - 40, 142, 24)
                            pygame.draw.rect(screen, (239, 165, 196), cta_rect, border_radius=12)
                            draw_text(screen, forum_comment_font, "Learn More", (54, 23, 38), cta_rect.center)
                        draw_wrapped_text_center(
                            screen,
                            forum_text_font,
                            str(popup_item["text"]),
                            body_color,
                            popup_rect.centerx,
                            popup_rect.y + 74,
                            popup_rect.width - 44,
                            3,
                        )
                    top_popup = level4_popup_stack[-1]
                    close_rect = level4_top_popup_close_rect(top_popup)
                    pygame.draw.rect(screen, (235, 238, 246), close_rect, border_radius=12)
                    draw_text(screen, forum_comment_font, "X", (53, 58, 74), close_rect.center)

                if level4_result is not None:
                    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((8, 8, 12, 130))
                    screen.blit(overlay, (0, 0))
                    draw_text(screen, title_font, "You Lost!", (245, 245, 255), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 34))
                    draw_text(
                        screen,
                        hud_font,
                        "But you couldn't win, so don't feel too bad...",
                        (235, 235, 245),
                        (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 2),
                    )
                    draw_text(
                        screen,
                        hud_font,
                        "Digital disconnection is not just personal choice.",
                        (235, 235, 245),
                        (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30),
                    )
                    draw_text(
                        screen,
                        hud_font,
                        "Platforms are designed to resist being turned off.",
                        (235, 235, 245),
                        (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 62),
                    )
                    draw_text(screen, hud_font, "Press Enter for menu", (215, 215, 230), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 98))
            elif active_level.get("mode") == "placeholder":
                draw_text(
                    screen,
                    title_font,
                    active_level["name"],
                    (240, 244, 252),
                    (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 28),
                )
                draw_text(
                    screen,
                    hud_font,
                    "This level is not built yet.",
                    (194, 205, 223),
                    (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20),
                )
                draw_text(
                    screen,
                    hud_font,
                    "Press ESC to return to menu.",
                    (174, 186, 204),
                    (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 52),
                )
            else:
                pygame.draw.rect(screen, (70, 170, 255), player)
                draw_text(
                    screen,
                    hud_font,
                    f"{active_level['name']} | ESC: menu",
                    (240, 240, 250),
                    (WINDOW_WIDTH // 2, 24),
                )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
