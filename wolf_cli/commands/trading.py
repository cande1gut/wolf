import typer
from pathlib import Path
from typing import Optional
import json
from yahoo_fin import stock_info
from datetime import datetime

today = datetime.now()

trading_app = typer.Typer()

def get_latest(symbol):
    symbolTable = stock_info.get_quote_table(symbol)
    data = json.dumps(symbolTable, sort_keys=False, indent=2)
    return data

@trading_app.command()
def latest_ticker(symbol: str = typer.Option(..., prompt=True)):
    """
    Get latest ticker price for a symbol
    """
    print("Date & Time:", today)
    print(get_latest(symbol))