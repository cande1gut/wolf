import click
from .commands import urls
from .commands import images

@click.group(help="CLI tool to assist and make easy repetitive tasks such as downloading images and unshortening URLs")
def cli():
    pass

cli.add_command(urls.getURLs)
cli.add_command(images.getImgs)

if __name__ == '__main__':
    cli()