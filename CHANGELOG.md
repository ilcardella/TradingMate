# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## []
### Changed
- Replaced TK user interface with GTK+ 3
- Tickers prices are fetched using `alpha-vantage` Python module

### Added
- Status bar showing portfolio filepath

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
