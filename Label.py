from PIL import ImageFont, Image, ImageDraw
from brother_ql import BrotherQLRaster, create_label
from brother_ql.backends import guess_backend
from brother_ql.backends.helpers import send
from datetime import datetime

from config import BROTHER_QL_MODEL, BROTHER_QL_PRINTER
from UnifiAPI import UnifiAPI


def create_voucher(room, checkout):
    c = UnifiAPI()

    note = f"Room #{room} @ {datetime.now().strftime('%b %d')}"
    checkout = checkout.replace(hour=12, minute=0, second=0)
    expires_at = checkout.strftime("Expires %b %d @ Checkout")

    response = c.create_voucher(note, checkout)
    code = response.get("code")[:5] + "-" + response.get("code")[5:]
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
        (6, 0.0),
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
        (6, 118),
        "Wi-Fi Code:",
        font=ImageFont.truetype("DejaVuSansMono-Bold.ttf", 42),
        fill="black",
    )
    draw.text(
        (296, 115),
        code,
        font=ImageFont.truetype("DejaVuSansMono-Bold.ttf", 44),
        fill="red",
    )
    draw.text(
        (6, 175),
        expires_at,
        font=ImageFont.truetype("DejaVuSansMono-Bold.ttf", 38),
        fill="black",
    )

    # Save the image
    filename = "label.png"
    image.save(filename)
    return filename


def print_label(filename):
    qlr = BrotherQLRaster(BROTHER_QL_MODEL)

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
        printer_identifier=BROTHER_QL_PRINTER,
        backend_identifier=guess_backend(BROTHER_QL_PRINTER),
        blocking=True,
    )
