from pathlib import Path
from typing import Any, Dict, List

from .. import TradingMate
from ..model import Portfolio, Trade


class TradingMateClient:
    """Client interface to the TradingMate business logic"""

    def __init__(self, server: TradingMate) -> None:
        self._server = server

    def stop(self) -> None:
        """Handle stop event"""
        self._server.close_view_event()

    def get_portfolios(self) -> List[Portfolio]:
        """Get the loaded portfolios"""
        return self._server.get_portfolios()

    def new_trade_event(self, new_trade: Trade, portfolio_id: str) -> None:
        """Push new trade notification to the server"""
        self._server.new_trade_event(new_trade, portfolio_id)

    def manual_refresh_event(self, portfolio_id: str) -> None:
        """Request server to refresh portfolio data"""
        self._server.manual_refresh_event(portfolio_id)

    def set_auto_refresh_event(self, value: bool, portfolio_id: str) -> None:
        """Set server to automatically update data for the portfolio"""
        self._server.set_auto_refresh(value, portfolio_id)

    def open_portfolio_event(self, filepath: Path) -> None:
        """Request server to open a portfolio"""
        self._server.open_portfolio_event(filepath)

    def save_portfolio_event(self, portfolio_id: str, filepath: Path) -> None:
        """Request server to save a portfolio"""
        self._server.save_portfolio_event(portfolio_id, filepath)

    def get_settings_event(self) -> None:
        """Request server to fetch TradingMate settings"""
        return self._server.get_settings_event()

    def save_settings_event(self, settings: Dict[str, Any]) -> None:
        """Request server to save the settings"""
        self._server.save_settings_event(settings)

    def unsaved_changes(self) -> bool:
        """Request if open portfolios have unsaved changes and return True"""
        for pf in self._server.get_portfolios():
            if pf.has_unsaved_changes():
                return True
        return False

    def is_portfolio_auto_refreshing(self, portfolio_id: str) -> bool:
        """Return True if portfolio has data auto refresh enabled, False otherwise"""
        pf = list(
            filter(lambda p: p.get_id() == portfolio_id, self._server.get_portfolios())
        )
        if pf is not None and len(pf) == 1:
            return pf[0].get_auto_refresh_enabled()
        else:
            raise ValueError(f"Portfolio {portfolio_id} does not exists")

    def get_app_log_filepath(self) -> Path:
        return self._server.get_app_log_filepath()

    def get_app_version(self) -> str:
        return self._server.get_app_version()

    def delete_trade(self, portfolio_id: str, trade_id: str) -> None:
        self._server.delete_trade_event(portfolio_id, trade_id)

    def get_market_details(self, market_ticker: str) -> Any:
        return self._server.get_market_details(market_ticker)
