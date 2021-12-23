import typer
from .commands import urls
from .commands import images

app = typer.Typer(help="CLI tool to assist and make easy repetitive tasks such as downloading images and unshortening URLs")
urls = urls.urls_app
images = images.images_app

app.add_typer(urls, name="urls", help="Operations to perform over URLs")
app.add_typer(images, name="images", help="Operations to perform over images")

if __name__ == "__main__":
    app()