from PIL import Image, ImageDraw
import argparse
from pathlib import Path


def interpolate_color(value):
    if value < 0.33:
        ratio = value / 0.33
        r = int(0 + (255 * ratio))
        g = 255
        b = 0
    elif value < 0.66:
        ratio = (value - 0.33) / 0.33
        r = 255
        g = int(255 - (90 * ratio))
        b = 0
    else:
        ratio = (value - 0.66) / 0.34
        r = 255
        g = int(165 - (165 * ratio))
        b = 0
    return (r, g, b, 255)


def draw_gauge(draw, x, y, state, config):
    if config.vertical:
        gauge_rect = [x, y, x + config.bar_height, y + config.total_gauge_width]
        draw.rectangle(
            gauge_rect, outline=config.outline_color, width=config.outline_width
        )

        for i in range(state):
            value = i / (config.bar_count - 1)
            fill_color = interpolate_color(value)
            bar_y = (
                y
                + config.total_gauge_width
                - (i + 1) * (config.bar_width + config.bar_spacing)
            )
            bar_rect = [x, bar_y, x + config.bar_height, bar_y + config.bar_width]
            draw.rectangle(bar_rect, fill=fill_color)
    else:
        gauge_rect = [x, y, x + config.total_gauge_width, y + config.bar_height]
        draw.rectangle(
            gauge_rect, outline=config.outline_color, width=config.outline_width
        )

        for i in range(state):
            value = i / (config.bar_count - 1)
            fill_color = interpolate_color(value)
            bar_x = x + i * (config.bar_width + config.bar_spacing)
            bar_rect = [bar_x, y, bar_x + config.bar_width, y + config.bar_height]
            draw.rectangle(bar_rect, fill=fill_color)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_screen_width", type=int, default=800)
    parser.add_argument("--base_screen_height", type=int, default=480)
    parser.add_argument("--target_screen_width", type=int, default=800)
    parser.add_argument("--target_screen_height", type=int, default=480)
    parser.add_argument("--base_total_gauge_width", type=int, default=138)
    parser.add_argument("--base_bar_height", type=int, default=15)
    parser.add_argument("--base_bar_spacing", type=float, default=1.5)
    parser.add_argument("--bar_count", type=int, default=15)
    parser.add_argument("--outline_width", type=int, default=0)
    parser.add_argument("--vertical", action="store_true", default=False)
    parser.add_argument(
        "--base_line_color",
        type=lambda s: tuple(map(int, s.split(","))),
        default=(255, 0, 255, 255),
    )
    parser.add_argument("--base_line_thickness", type=int, default=2)
    parser.add_argument(
        "--background",
        type=lambda s: tuple(map(int, s.split(","))),
        default=(0, 0, 0, 0),
    )
    parser.add_argument(
        "--outline_color",
        type=lambda s: tuple(map(int, s.split(","))),
        default=(0, 255, 0, 255),
    )
    parser.add_argument("--file_prefix", type=str, default="bar_guage")
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=Path("./output"),
    )
    parser.add_argument("--file_ext", type=str, default=".png")
    args = parser.parse_args()

    x_scale = args.target_screen_width / args.base_screen_width
    y_scale = args.target_screen_height / args.base_screen_height

    args.total_gauge_width = int(
        args.base_total_gauge_width * (y_scale if args.vertical else x_scale)
    )
    args.bar_spacing = max(
        int(args.base_bar_spacing * (y_scale if args.vertical else x_scale)), 1
    )
    args.bar_height = max(
        int(args.base_bar_height * (x_scale if args.vertical else y_scale)), 1
    )

    available_width = args.total_gauge_width - (args.bar_count - 1) * args.bar_spacing
    args.bar_width = available_width / args.bar_count

    if args.vertical:
        image_width = args.bar_height + args.outline_width * 2 + 2
        image_height = args.total_gauge_width + args.outline_width * 2
        prefix = "vertical"
    else:
        image_width = args.total_gauge_width + args.outline_width * 2
        image_height = args.bar_height + args.outline_width * 2 + 2
        prefix = "horizontal"

    args.file_prefix = f"{prefix}_{args.file_prefix}"

    output_dir_name = (
        f"{args.file_prefix}_{args.base_bar_height}x{args.base_total_gauge_width}"
    )
    output_dir = args.output_dir / output_dir_name

    output_dir.mkdir(parents=True, exist_ok=True)

    for state in range(args.bar_count + 1):
        img = Image.new("RGBA", (int(image_width), int(image_height)), args.background)
        draw = ImageDraw.Draw(img)

        draw_gauge(draw, args.outline_width, args.outline_width, state, args)

        if state == 0:
            if args.vertical:
                y_base = image_height - args.base_line_thickness - args.outline_width
                draw.rectangle(
                    [
                        args.outline_width,
                        y_base,
                        image_width - args.outline_width,
                        y_base + args.base_line_thickness,
                    ],
                    fill=args.base_line_color,
                )
            else:
                draw.rectangle(
                    [
                        args.outline_width,
                        args.outline_width,
                        args.outline_width + args.base_line_thickness,
                        image_height - args.outline_width,
                    ],
                    fill=args.base_line_color,
                )

        if state == args.bar_count:
            if args.vertical:
                img = img.crop((0, 0, img.width, img.height - 1))
            else:
                img = img.crop((0, 0, img.width - 1, img.height))

        filename = f"{state:02}_{args.file_prefix}{args.file_ext}"
        img.save(output_dir / filename)

    print(f"✅ Done! {args.bar_count + 1} bar images saved to: '{output_dir}'")


if __name__ == "__main__":
    main()
