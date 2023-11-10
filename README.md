# check-scripts – An assortment of recurring scripts

This repository contains scripts that run according to a schedule on my home
server.

## `perm.py`

PERM is the immigration process that comes before filing a green card. It is
long and tedious, and its processing time varies from month to month. Each month
a bulletin is posted at https://flag.dol.gov/processingtimes, showing how
long the wait for PERM is. This script checks that URL periodically and sends a
notification when a new bulletin is published.

## `uscis-status.py`

For most immigration documents, USCIS provides a receipt number. This number can
be used on the https://egov.uscis.gov website to check the case status. This
script checks that URL periodically and sends a notification when the case
status changes. It also keeps a history of previous status.

## `visa-bulletin.py`

The [visa bulletin](https://web.archive.org/web/20231108164359/https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html)
is released once a month by the State Department, and it details how visas will
be allotted in that month. This script checks the visa bulletin periodically and
sends a notification when a new one comes out.
