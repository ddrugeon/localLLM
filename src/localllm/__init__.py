import asyncio

from localllm.application.application import Application


async def application_main() -> None:
    app = Application()
    await app.index_albums()


def main() -> None:
    asyncio.run(application_main())


if __name__ == "__main__":
    asyncio.run(application_main())
