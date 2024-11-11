import asyncio
from aiopath import AsyncPath
from aioshutil import copyfile
import argparse
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def read_folder(source_folder, output_folder):
    try:
        tasks = []
        async for item in source_folder.iterdir():
            apath = AsyncPath(item)
            if await apath.is_file():
                tasks.append(copy_file(apath, output_folder))
            elif await apath.is_dir():
                tasks.append(read_folder(apath, output_folder))
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"read folder error: {e}")


async def copy_file(file, output_folder):
    try:
        file = AsyncPath(file)
        if not await file.is_file():
            return

        file_extension = file.suffix.lstrip(".").lower()
        target_folder = output_folder / file_extension
        copy_path = AsyncPath(target_folder)

        if not await copy_path.exists():
            await copy_path.mkdir(exist_ok=True, parents=True)

        target_file_path = copy_path / file.name
        await copyfile(file, target_file_path)

    except Exception as e:
        logging.error(f"copy file {file} error: {e}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_folder", type=str, help="source folder path")
    parser.add_argument("output_folder", type=str, help="output folder path")
    args = parser.parse_args()

    source_folder = AsyncPath(args.source_folder)
    output_folder = AsyncPath(args.output_folder)

    if not await source_folder.is_dir():
        logging.error(f"folder {source_folder} not exist")
        return

    await read_folder(source_folder, output_folder)
    logging.info("proccess done")


if __name__ == "__main__":
    asyncio.run(main())
