"""メインアプリケーション"""

import os

import typer
from rich.console import Console
from rich.panel import Panel

from tjpw_schedule_watcher.domain.interfaces import ScheduleExternalApi

from . import __version__
from .domain.value_objects import ScrapeRange
from .infrastructure.external_apis import (
    NullScheduleExternalApi,
    ScheduleGoogleCalendarApi,
)
from .infrastructure.scrapers import SeleniumScraper
from .infrastructure.selenium_factory import (
    NotReadyError,
    SeleniumFactory,
)
from .usecase.scrape_tjpw import ScrapeTjpw

app = typer.Typer(
    name="tjpw-schedule-watcher",
    help="TJPW Schedule Watcher - 東京女子プロレスのスケジュールを自動取得",
    add_completion=False,
)
console = Console()


@app.command()
def update(
    development: bool = typer.Option(
        False, "--dev", help="開発モード（7日間のみ取得）"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="外部APIに保存しない（テスト用）"
    ),
) -> None:
    """TJPWスケジュールを更新します。

    TJPWの公式サイトからスケジュールを取得し、外部API（Google Calendar）に保存します。
    """
    console.print("🚀 [bold]TJPW Schedule Watcher を起動しています...[/bold]")

    # Validate Selenium connection
    try:
        console.print("Seleniumの接続を確認中...")
        SeleniumFactory.validate()
        console.print("✅ [green]Seleniumの準備ができました[/green]")
    except NotReadyError as e:
        console.print(f"❌ [red]Seleniumが準備できていません: {e}[/red]")
        console.print(
            "[yellow]Seleniumコンテナを起動してください。詳細はREADMEを参照してください。[/yellow]"
        )
        raise typer.Exit(code=1)

    # Create scraper
    scraper = SeleniumScraper()

    # Create external APIs
    external_apis: list[ScheduleExternalApi] = []
    if not dry_run:
        # Try to create Google Calendar API
        if os.environ.get("LAMBDA_GOOGLE_CALENDAR_API_DOMAIN"):
            try:
                external_apis.append(ScheduleGoogleCalendarApi())
                console.print("✅ [green]Google Calendar API が設定されています[/green]")
            except ValueError as e:
                console.print(f"⚠️  [yellow]Google Calendar API が設定されていません: {e}[/yellow]")

        if not external_apis:
            console.print("⚠️  [yellow]外部APIが設定されていません。dry-runモードで実行します。[/yellow]")
            external_apis.append(NullScheduleExternalApi())
    else:
        console.print("🔍 [yellow]Dry-runモード: 外部APIに保存しません[/yellow]")
        external_apis.append(NullScheduleExternalApi())

    # Create use case
    use_case = ScrapeTjpw(scraper=scraper, external_apis=external_apis)

    # Create scrape range
    scrape_range = ScrapeRange.default(development=development)
    console.print(
        f"📅 取得期間: [cyan]{scrape_range.start_date.date()}[/cyan] から [cyan]{scrape_range.end_date.date()}[/cyan]"
    )

    # Execute
    try:
        use_case.execute(scrape_range)
        console.print("✅ [bold green]正常に完了しました！[/bold green]")
    except Exception as e:
        console.print(f"❌ [red]エラーが発生しました: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def hello(name: str = typer.Option("World", help="挨拶する相手の名前")) -> None:
    """挨拶を表示します"""
    console.print(
        Panel(
            f"[bold green]こんにちは、{name}![/bold green]",
            title="Python Project 2026",
            border_style="blue",
        )
    )


@app.command()
def version() -> None:
    """バージョン情報を表示します"""
    console.print(f"Python Project 2026 version: [bold]{__version__}[/bold]")


if __name__ == "__main__":
    app()
