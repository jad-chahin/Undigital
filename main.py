import sys
import random

import pygame


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
PLAYER_SIZE = 40

LEVELS = [
    {"name": "Level 1 - Build Your Feed", "bg_color": (18, 18, 28), "mode": "booktok"},
    {"name": "Level 2 - Protect the Space", "bg_color": (232, 236, 246), "mode": "forum"},
    {"name": "Level 3 - Log Off for a Bit", "bg_color": (27, 32, 48), "mode": "placeholder"},
    {"name": "Level 4 - Manage Yourself", "bg_color": (31, 43, 41), "mode": "placeholder"},
]

BOOKTOK_LABELS = ["#BookTok", "Romance", "Fantasy"]
OTHER_LABELS = ["Sports", "Cooking", "News", "Tech", "Travel", "Memes"]
LEVEL1_SPAWN_INTERVAL = 32
FORUM_TITLE_TEXT = "Undigital Forum"
FORUM_POST_TITLE = "Thread: Holding Space for Feminist Reading Recs"
FORUM_POST_BODY = "Share books centering women and marginalized voices. Keep this space constructive."
FORUM_GOOD_COMMENTS = [
    "Try Iron Widow. Great rage + resistance arc.",
    "The Once and Future Witches fits this thread well.",
    "If you want lyrical prose, read Circe.",
    "Parable of the Sower is heavy but essential.",
    "Can we pin recs by theme? This list is amazing.",
    "Adding The Fifth Season. Big themes, incredible worldbuilding.",
    "Mexican Gothic has great atmosphere and gender politics.",
    "If anyone wants nonfiction, Hood Feminism is a strong pick.",
    "Beloved is difficult but worth discussing with care.",
    "Can we make a shelf just for queer feminist fantasy?",
    "I appreciate how supportive this thread is staying.",
    "Please drop more translated works by women authors.",
    "Convenience Store Woman sparked great discussion in our group.",
    "This is the first forum thread where I feel heard.",
    "If you want speculative fiction, try The Power.",
]
FORUM_BAD_COMMENTS = [
    "Women like you ruin every community.",
    "Shut up and go back to the kitchen.",
    "Nobody wants to hear from feminists.",
    "You're all too emotional to think clearly.",
    "This thread needs fewer women talking.",
    "You sound dumb, stay out of this.",
    "Women authors are automatically overrated.",
    "Get lost, nobody respects your opinions.",
    "You people are a joke.",
    "Cry harder, no one cares about your safety.",
    "Women shouldn't lead discussions like this.",
    "You're pathetic and embarrassing.",
    "This space is better without you in it.",
    "Your voice does not matter here.",
    "You're all delusional.",
]
FORUM_SPAWN_MS = 1450
FORUM_COMMENT_LIFE = 7.8
FORUM_THREAD_COMMENTS_TOP = 260
FORUM_COMMENT_ROW_HEIGHT = 42


def draw_text(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color: tuple[int, int, int],
    center: tuple[int, int],
) -> None:
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=center)
    screen.blit(surface, rect)


def draw_text_left(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color: tuple[int, int, int],
    position: tuple[int, int],
) -> None:
    surface = font.render(text, True, color)
    rect = surface.get_rect(topleft=position)
    screen.blit(surface, rect)


def draw_3d_text(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    center: tuple[int, int],
) -> None:
    depth_color = (35, 35, 50)
    main_color = (245, 245, 255)
    highlight_color = (120, 210, 255)

    for offset in range(6, 0, -1):
        draw_text(
            screen,
            font,
            text,
            depth_color,
            (center[0] + offset, center[1] + offset),
        )

    draw_text(screen, font, text, main_color, center)
    draw_text(screen, font, text, highlight_color, (center[0] - 2, center[1] - 2))


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
    active_level = LEVELS[selected_index]
    feed_score = 0
    falling_posts: list[dict[str, object]] = []
    spawn_counter = 0
    feed_ratio = 0.25
    booktok_topic_weights: dict[str, float] = {}
    level1_result: str | None = None
    forum_comments: list[dict[str, object]] = []
    forum_points = 0
    forum_safety_score = 50
    forum_spawn_timer_ms = 0
    forum_ban_flash = 0.0
    forum_result: str | None = None
    forum_points_delta = 0
    forum_points_delta_timer = 0.0
    forum_points_delta_duration = 0.55

    def start_level(level: dict[str, object]) -> None:
        nonlocal feed_score, falling_posts, spawn_counter, feed_ratio, booktok_topic_weights
        nonlocal level1_result, forum_comments, forum_points, forum_safety_score
        nonlocal forum_spawn_timer_ms, forum_ban_flash, forum_result
        nonlocal forum_points_delta, forum_points_delta_timer
        if level.get("mode") == "booktok":
            player.width = 90
            player.height = 16
            player.midbottom = (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20)
            feed_score = 0
            falling_posts = []
            spawn_counter = 0
            feed_ratio = 0.25
            booktok_topic_weights = {label: 1.0 for label in BOOKTOK_LABELS}
            level1_result = None
        elif level.get("mode") == "forum":
            forum_comments = []
            forum_points = 0
            forum_safety_score = 50
            forum_spawn_timer_ms = 0
            forum_ban_flash = 0.0
            forum_result = None
            forum_points_delta = 0
            forum_points_delta_timer = 0.0
        else:
            player.width = PLAYER_SIZE
            player.height = PLAYER_SIZE
            player.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

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
                        selected_index = (selected_index - 1) % len(LEVELS)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(LEVELS)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        active_level = LEVELS[selected_index]
                        start_level(active_level)
                        game_state = "playing"
                    elif pygame.K_1 <= event.key <= pygame.K_4:
                        selected_index = min(event.key - pygame.K_1, len(LEVELS) - 1)
                elif game_state == "playing" and event.key == pygame.K_ESCAPE:
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

                    next_posts: list[dict[str, object]] = []
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

                for i, comment in enumerate(forum_comments):
                    comment["rect"].y = FORUM_THREAD_COMMENTS_TOP + i * FORUM_COMMENT_ROW_HEIGHT
                    comment["approve_rect"].x = comment["rect"].right - 204
                    comment["approve_rect"].y = comment["rect"].y + 4
                    comment["disapprove_rect"].x = comment["rect"].right - 112
                    comment["disapprove_rect"].y = comment["rect"].y + 4
            elif active_level.get("mode") == "placeholder":
                pass
            else:
                speed = active_level["speed"]
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    player.x -= speed
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    player.x += speed
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    player.y -= speed
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    player.y += speed
                player.clamp_ip(screen.get_rect())

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
            for i, level in enumerate(LEVELS):
                color = (255, 220, 80) if i == selected_index else (190, 190, 205)
                draw_text(
                    screen,
                    menu_font,
                    f"{i + 1}. {level['name']}",
                    color,
                    (WINDOW_WIDTH // 2, 220 + i * 55),
                )
            draw_text(
                screen,
                hud_font,
                "Use Up/Down or 1-4, Enter to start",
                (160, 160, 180),
                (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80),
            )
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
