import os
from dotenv import load_dotenv

from sdk import GameEventClient, GameEventClientConfig, InstallEvent, PurchaseEvent

load_dotenv()

def main():
    client = GameEventClient(
        GameEventClientConfig(
            base_url="http://127.0.0.1:8000",
            api_key=os.getenv("EVENT_API_KEY"),
        )
    )

    install = InstallEvent.create(
        player_id="player_1",
        app_id="com.game.test",
        platform="ios",
    )

    resp = client.send_install(install)
    print("Install response:", resp.status_code, resp.text)

    purchase = PurchaseEvent.create(
        player_id="player_1",
        app_id="com.game.test",
        platform="ios",
        product_id="gems_pack_01",
        amount_micros=4_990_000,
        currency="EUR",
    )

    resp = client.send_purchase(purchase)
    print("Purchase response:", resp.status_code, resp.text)

if __name__ == "__main__":
    main()
