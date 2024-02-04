from PIL import ImageFont, Image, ImageDraw
from brother_ql import BrotherQLRaster, create_label
from brother_ql.backends import guess_backend
from brother_ql.backends.helpers import send
from datetime import datetime
from requests import HTTPError

import config
from UnifiConnector import UnifiConnector


def create_voucher(room, checkout):
    c = UnifiConnector()
    checkout = checkout.replace(hour=12, minute=0, second=0)
    note = f"Room #{room} @ {datetime.now().strftime('%b %d')}"
    response = c.create_voucher(note, checkout)
    if hasattr(response, "get") and response.get("error"):
        raise HTTPError(response=response.get("error"))
    expires_at = checkout.strftime("Expires %b %d @ Checkout")
    create_time = response[0].get("create_time")
    response = c.list_vouchers(timestamp=create_time)[0]
    code = response["code"][:5] + "-" + response["code"][5:]
    return note, code, expires_at


font = ImageFont.truetype("DejaVuSansMono-Bold.ttf", 38)


def generate_label(note, code, expires_at):
    width = 596
    height = 220

    # Create a new image
    image = Image.new("RGB", (width, height), "white")

    # Create an ImageDraw object
    draw = ImageDraw.Draw(image)

    draw.text(
        (10, 0.0),
        "Budget Motel, Longview",
        font=ImageFont.truetype("DejaVuSerif-Bold.ttf", 42),
        fill="red",
    )
    draw.text(
        (80, 60),
        note,
        font=ImageFont.truetype("DejaVuSansMono-Bold.ttf", 42),
        fill="black",
    )
    draw.text(
        (10, 125),
        "Wi-Fi Code:",
        font=ImageFont.truetype("DejaVuSansMono-Bold.ttf", 42),
        fill="black",
    )
    draw.text(
        (300, 123),
        code,
        font=ImageFont.truetype("DejaVuSansMono-Bold.ttf", 44),
        fill="red",
    )
    draw.text(
        (10.5, 180),
        expires_at,
        font=ImageFont.truetype("DejaVuSansMono-Bold.ttf", 38),
        fill="black",
    )
    # # Calculate the text positions
    # for i, string in enumerate(lines):
    #     _, _, w, h = draw.textbbox((0, 0), string, font=font)
    #     position = ((width - w) / 2, (height - h) / len(lines) * i)
    #     pprint(position)
    #     draw.text(
    #         position,
    #         string,
    #         font=font,
    #         fill=font_color,
    #     )

    # Save the image
    filename = "label.png"
    image.save(filename)
    return filename


def print_label(filename):
    qlr = BrotherQLRaster(config.BROTHER_QL_MODEL)

    create_label(
        qlr,
        filename,
        "62red",
        red=True,
        dpi_600=True,
        hq=True,
    )

    send(
        qlr.data,
        printer_identifier=config.BROTHER_QL_PRINTER,
        backend_identifier=guess_backend(config.BROTHER_QL_PRINTER),
        blocking=True,
    )
