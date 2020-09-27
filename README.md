# Taransay Data Service
Miniature data logger web service for Taransay energy monitors.

## Dates
Received datetimes are assumed to be timezone-naive UTC times. You can specify
a timezone in each device's configuration file and this can be used by clients
to scale the dates appropriately.

## Usage

### Development
Start development server with:

```bash
FLASK_APP=taransaydata.api python -m flask run
```
