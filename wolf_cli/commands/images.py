import click
from pathlib import Path
import anyio
import httpx
from rich.console import Console
from rich.progress import Progress, TaskID
import nest_asyncio
nest_asyncio.apply()

console = Console()

#Code adapted from: https://lewoudar.medium.com/click-a-beautiful-python-library-to-write-cli-applications-9c8154847066

def get_image_urls(path):
    images = []
    p = Path(path)
    with p.open() as f:
        for line in f:
            line = line.strip(' \n')
            if not line:
                continue
            images.append(line)
    return images

async def download_image(progress, task_id, image_url, destination):
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url)
        if response.status_code >= 400:
            progress.console.print(f'image [blue]{image_url}[/] could not be downloaded')
            progress.update(task_id, advance=1)
            return

        path = Path(destination+"/"+image_url.split('/')[-1])
        path.write_bytes(response.content)
        progress.update(task_id, advance=1)


async def worker(image_urls, progress, task_id, destination):
    async with anyio.create_task_group() as tg:
        for image_url in image_urls:
            await tg.spawn(download_image, progress, task_id, image_url, destination)

@click.command(name="images")
@click.option(
    "--in",
    "in_file",
    required=True,
    help="Path of text file with a url per line",
    type=click.Path(exists=True, dir_okay=False, readable=True),
)
@click.option(
    "--out-folder",
    "out_folder",
    required=True,
    help="Folder to where the images will be stored",
    type=click.Path(exists=True, dir_okay=True),
)
def getImgs(in_file, out_folder):
    image_urls = get_image_urls(in_file)
    with Progress(console=console) as progress:
        task_id = progress.add_task('Downloading', total=len(image_urls))
        anyio.run(worker, image_urls, progress, task_id, out_folder)
    console.print('All images downloaded!')