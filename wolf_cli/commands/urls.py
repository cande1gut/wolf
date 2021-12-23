import typer
from pathlib import Path
from typing import Optional
import anyio
import httpx
from rich.console import Console
from rich.progress import Progress, TaskID
import json
import nest_asyncio
nest_asyncio.apply()

urls_app = typer.Typer()

#URLs retrieval code inspired from: https://lewoudar.medium.com/click-a-beautiful-python-library-to-write-cli-applications-9c8154847066

console = Console()
all_urls = []

def get_urls(path):
    urls = []
    p = Path(path)
    with p.open() as f:
        for line in f:
            line = line.strip(' \n')
            if not line:
                continue
            urls.append(line)
    return urls

async def unshorten_url(progress, task_id, url):
    global all_urls
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            #Could be that the url is double shortened
            if str(response.status_code/100).startswith("3") and response.headers['location']:
                url2 = response.headers['location']
                try:
                    response2 = await client.get(url2)
                    if str(response2.status_code/100).startswith("3") and response2.headers['location']:
                        uri = response2.headers['location']
                except:
                    uri = url2
            else:
                uri = url

            all_urls.append({url:uri})
        except:
            all_urls.append({url:"Error"})

        progress.update(task_id, advance=1)

async def worker(urls, progress, task_id):
    async with anyio.create_task_group() as tg:
        for url in urls:
            await tg.spawn(unshorten_url, progress, task_id, url)

@urls_app.command()
def unshorten_urls(input_file: Optional[Path] = typer.Option(..., help="Text file containing all URLs splited by line"), output_folder: Optional[Path] = typer.Option(..., help="Folder path where the images will be stored"), output_name: str = typer.Option(..., help="File name that will be used to store the unshortened URLs")):
    """
    Get all unshortened URLs from a text file (in Async mode)
    """
    if input_file is None:
        typer.echo("URLs text file not found!")
        raise typer.Abort()

    if not output_folder.is_dir():
        typer.echo("Folder not found!")
        raise typer.Abort()

    if input_file.is_file() and output_folder.is_dir() and output_name != "":
        urls = get_urls(input_file)
        with Progress(console=console) as progress:
            task_id = progress.add_task('Downloading', total=len(urls))
            anyio.run(worker, urls, progress, task_id)
        console.print('All urls unshortened!')
        with open(output_folder / (output_name+".json"), "w") as file:
            json.dump(all_urls, file, indent=2)