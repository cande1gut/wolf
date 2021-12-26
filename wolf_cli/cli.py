import typer
from .commands import urls
from .commands import images
from .commands import trading

app = typer.Typer(help="CLI tool to assist and make easy repetitive tasks such as downloading images and URLs unshortening")
urls = urls.urls_app
images = images.images_app
trading = trading.trading_app

app.add_typer(urls, name="urls", help="Operations to perform over URLs")
app.add_typer(images, name="images", help="Operations to perform over images")
app.add_typer(trading, name="trading", help="Operations for trading")

if __name__ == "__main__":
    app()