# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## []
### Changed
- Updated Pipfile unifying packages and adding custom scripts

### Added
- Added tooltips to UI widgets
- Icon in status bar that shows internet connection status
- Show application version in About dialog
- Support for yfinance module to fetch stocks data

### Fixed
- Fixed bug where main window was hidden when closing app with unsaved changes

## [2.1.1] - 2020-01-13
### Changed
- Removed unused resource files
- Updated README

## [2.1.0] - 2020-01-12
### Changed
- Replaced TK user interface with GTK+ 3
- Tickers prices are fetched using `alpha-vantage` Python module
- **alpha_vantage_polling_period** configuration parameter is used to wait between each AV call
- AlphaVantage http requests are thread safe

### Added
- Status bar showing portfolio filepath
- Button to open a new window tailing the current application log file

## [2.0.0] - 2019-12-14
### Changed
- Issue37 - Improved installation process and dependencies setup
- Updated default .credentials configured path
- Re-design of system architecture and API
- Edited Portfolios are not saved automatically and a warning is displayed

### Added
- Added Pipfile to manage python dependencies
- Added `FEE` action
- Added `notes` field in trade
- Support load of multiple portfolios
- Save As and Save buttons per portfolio

## [1.0.0] 2019-05-03
### Added
- Initial release
