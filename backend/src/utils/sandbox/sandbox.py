import asyncio

from utils.log_utils import initialize_logs

initialize_logs("sandbox")


async def main() -> None:

    from dependencies.job import get_system_information_strategy
    from dependencies.utils import get_db, get_http_client

    strategy = get_system_information_strategy()
    try:
        await strategy.execute()
    finally:
        await get_http_client().aclose()
        get_db().close()


if __name__ == "__main__":
    asyncio.run(main())
