import pygame


def wrap_text_lines(font: pygame.font.Font, text: str, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


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


def draw_wrapped_text_center(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color: tuple[int, int, int],
    center_x: int,
    top_y: int,
    max_width: int,
    line_gap: int = 4,
) -> None:
    lines = wrap_text_lines(font, text, max_width)
    if not lines:
        return

    y = top_y
    for line in lines:
        surf = font.render(line, True, color)
        rect = surf.get_rect(midtop=(center_x, y))
        screen.blit(surf, rect)
        y += surf.get_height() + line_gap


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
