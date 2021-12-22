import click
#import urlexpander
from pathlib import Path
import anyio
import httpx
from rich.console import Console
from rich.progress import Progress, TaskID
import json
import nest_asyncio
nest_asyncio.apply()

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

@click.command(name="urls")
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
    help="Folder to where the result will be stored (If not created, it will be done automatically)",
    type=click.Path(exists=True, dir_okay=True),
)
@click.option(
    "--out-name",
    "out_name",
    required=True,
    help="Name of output file",
)
def getURLs(in_file, out_folder, out_name):
    urls = get_urls(in_file)
    with Progress(console=console) as progress:
        task_id = progress.add_task('Downloading', total=len(urls))
        anyio.run(worker, urls, progress, task_id)
    console.print('All urls unshortened!')
    with open(out_folder+"/"+out_name+".json", "w") as file:
        json.dump(all_urls, file, indent=4)