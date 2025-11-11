import asyncio
import aiohttp

LINKS = [
    "https://api.github.com/users/google",
    "https://jsonplaceholder.typicode.com/todos/1",
    "https://api.exchangerate-api.com/v4/latest/USD",
    "https://www.nytimes.com/",
    "https://www.nasa.gov/",
    "https://www.google.com/",
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/404"
]

async def web_checker(session,link):
    while True:
        try:
            async with session.get(link) as response:
                if response.status == 200:
                    contenido = await response.text()
                    print(f"Éxito en intento")
                    await asyncio.sleep(5)
                    print("Contenido analizado, web_checker despertado")


                elif response.status >= 500:
                        # Error del servidor, vale la pena reintentar
                        print(f"Error {response.status}, reintentando...")
                        await asyncio.sleep(5)
                else:
                        # Error del cliente (4xx), no vale la pena reintentar
                        print(f"Error {response.status}, no reintentable")
                        await asyncio.sleep(5)
        except asyncio.TimeoutError:
            print(f" Timeout en intento ")
        
        except aiohttp.ClientError as e:
            print(f"Error de red: {e}")



async def main():
    corrutinas=[]
    try:
        async with aiohttp.ClientSession() as session:
            for url in LINKS:
                response = web_checker(session,link=url)
                print(response)
                corrutinas.append(response)

            # corrutinas = [await web_checker(session,link=url) for url in LINKS]
            while True:
                resultados = await asyncio.gather(*corrutinas)
            print(resultados)
    except KeyboardInterrupt:
         print(resultados)
         exit()

if __name__ == '__main__':
    asyncio.run(main())