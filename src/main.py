import asyncio
import click
import functools

from src.libs.amazon.scraper import scrape_amazon


@click.group()
def cli():
    """CLI principal"""
    pass

def async_command(sync_func):
    """Permite definir comandos Click asíncronos."""
    @functools.wraps(sync_func)
    def wrapper(*args, **kwargs):
        return asyncio.run(sync_func(*args, **kwargs))
    return wrapper

@cli.command()
@click.argument('sku', nargs=-1, required=False)
@async_command
async def search(sku):
    """Comando para buscar un SKU"""
    sku = ' '.join(sku)
    if sku:
        click.echo(f"Buscando el articulo: {sku}")
        response = await scrape_amazon(sku)
        if response["success"]:
            click.echo("Articulo encontrado")
        else:
            click.echo(f"Error al buscar el articulo: {response['message']}")
    else:
        click.echo("Debes proporcionar un articulo válido.")


@cli.command()
@async_command
async def exit():
    """Comando para salir del CLI"""
    click.echo("Saliendo...")
    raise SystemExit


async def show_menu():
    """Muestra los comandos disponibles al usuario"""
    click.echo("\nComandos disponibles:")
    click.echo("  search    - Busca un artículo [search sku]")
    click.echo("  exit      - Salir del programa\n")


async def main():
    """Bucle principal asíncrono"""
    while True:
        try:
            click.clear()
            # Mostrar un banner
            click.echo("Bienvenido al CLI")
            # Mostrar el menú
            await show_menu()
            # Pedir el comando al usuario
            command = await asyncio.to_thread(click.prompt, "Introduce un comando", type=str)
            # Pasar el comando como si fuera desde la terminal
            await asyncio.to_thread(cli.main, args=command.split(), standalone_mode=False)
        except SystemExit:
            click.echo("¡Goodbye!")
            break
        except Exception as e:
            click.echo(f"Ocurrió un error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
