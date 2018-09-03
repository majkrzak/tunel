from asyncio import StreamReader, StreamWriter

CHUNK_SIZE = 2048


async def pipe(reader: StreamReader, writer: StreamWriter) -> None:
	try:
		while not reader.at_eof():
			writer.write(await reader.read(CHUNK_SIZE))
	finally:
		writer.close()
