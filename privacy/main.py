import json
import enum
import click
import typing
from typing import NamedTuple, TypeAlias

import asyncio
import websockets

############### CONFIG ####################


class BinanceWS(enum.Enum):
    spot = "wss://stream.binance.com/"
    future = "wss://fstream.binance.com/"


class Coins(enum.Enum):
    adausdt = "adausdt"
    avaxusdt = "avaxusdt"
    dogeusdt = "dogeusdt"


class Derivative(enum.Enum):
    spot = "spot"
    future = "future"


############### utils.py
class Storage(enum.Enum):
    inmemory = "inmemory"


class Repository:
    schema = {
        "id": "primary key",
        "time_ob": "numberic",
        "orderbook": "json",
        "trade_volume": "json",
        "trade_time": "numeric",
        "correlation": "float",
        "volume24h": "int",
    }

    def __init__(
        self, table_name: str, database: Storage = Storage.inmemory, *args, **kwargs
    ):
        self.table_name = table_name
        self.table = []
        self.database = database

    def set(self, key, value, *args, **kwags):
        pass

    def get(self, key, *arsg, **kwargs):
        pass

    def push(self, value):
        self.table.append(value)

    def save(self):
        with open(f"{self.table_name}.json", "w") as f:
            json.dump(self.table, f)

def isSpot(uri):
    return uri == BinanceWS.spot.value


CoinLinkPair = NamedTuple("CoinLinkPairs", [("coin", str), ("link", str)])


############### order_book.py
class OrderBookCoroutinesFactory:
    coin: Coins
    uri: BinanceWS
    derivative: Derivative

    def __init__(self) -> None:
        pass

    def prepare(self, pair: CoinLinkPair):
        self.coin = Coins(pair.coin)
        self.uri = BinanceWS(pair.link)
        self.is_spot = isSpot(self.uri.value)
        self.derivative = Derivative.spot if self.is_spot else Derivative.future
        self.table_name = f"{self.coin}_{self.derivative}"
        self.ws_uri = f"{self.uri.value}ws/{self.coin.value}@depth"
        self.uri_api = "https://fapi.binance.com/fapi" if self.uri == BinanceWS.future else "https://api.binance.com/api" # TODO: debug self.uri == BinanceWS.future

    def to_coroutine(self):
        pass


############### trade_feed.py
class TradeFeedCoroutinesFactory:
    coin: Coins
    uri: BinanceWS
    derivative: Derivative

    def __init__(self) -> None:
        pass

    def prepare(self, pair: CoinLinkPair):
        self.coin = Coins(pair.coin)
        self.uri = BinanceWS(pair.link)
        self.is_spot = isSpot(self.uri.value)
        self.derivative = Derivative.spot if self.is_spot else Derivative.future
        self.table_name = f"{self.coin}_{self.derivative}"
        self.ws_uri = f"{self.uri.value}ws/{self.coin.value}@aggTrade"
        self.repository = Repository(self.table_name)

    def to_coroutine(self):
        async def coroutine():
            ws = await websockets.connect(self.ws_uri, ping_interval=9, ping_timeout=9)
            print("new scoket: ", ws)
            running = True
            while running:
                response = await ws.recv()
                data = json.loads(response)
                data = parse_response_json(data)
                self.repository.push(data)
                # running = False

            await ws.close()
            self.repository.save()
            return

        return coroutine()

    def create_corouting(self, pair: CoinLinkPair):
        self.prepare(pair)
        return self.to_coroutine()


PriceQty = NamedTuple("PriceQty", [("price", float), ("quantity", float)])
Trades = NamedTuple("Trades", [("time", int), ("price_qty", PriceQty)])

def parse_response_json(json):
    price_trade = json.get("p")
    quantity = json.get("q")
    time_event = json.get("T")
    price_qty = PriceQty(price_trade, quantity)
    trades = Trades(time_event, price_qty)

    if price_trade is None:
        print("WARN: Price is None: ", trades, json)

    return trades

############### runnner.py
@click.command("trade_feed")
@click.argument(
    "coins",
    # help="list of coins, example: 'adausdt,avaxusdt,dogeusdt'",
)
def start_trade_feed(coins: str):
    _coins = coins.split(",")
    pairs = []

    for coin in _coins:
        pairs.append(CoinLinkPair(coin=coin, link=BinanceWS.spot.value))
        pairs.append(CoinLinkPair(coin=coin, link=BinanceWS.future.value))

    factory = TradeFeedCoroutinesFactory()

    tasks = [factory.create_corouting(pair) for pair in pairs]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    except KeyboardInterrupt:
        print("END")
    return 0


@click.command("order_book")
@click.option(
    "-c",
    "--coins",
    multiple=True,
    default=[],
    help="list of coins, example: 'adausdt,avaxusdt,dogeusdt'",
)
def start_order_book(coins: list[str]):
    click.echo(coins)
    return 0


@click.group(commands=[start_trade_feed, start_order_book])
@click.pass_context
def main(ctx, *args, **kwargs):
    pass


if __name__ == "__main__":
    main()
