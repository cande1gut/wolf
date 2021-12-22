import click
from .commands import urls
from .commands import images

@click.group(help="CLI tool to manage full development cycle of projects")
def cli():
    pass

cli.add_command(urls.getURLs)
cli.add_command(images.getImgs)

if __name__ == '__main__':
    cli()