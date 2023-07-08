# check-scripts – An assortment of recurring of scripts

This repository contains scripts that run according to a schedule on my home
server.

## `perm.py`

PERM is the immigration process that comes before the filing of a green card. It
is long and tedious, and its processing time varies from month to month. Each
month a bulletin is posted at [https://flag.dol.gov/processingtimes](), showing
how long the wait for PERM is. This script checks that URL periodically and
sends a notification when a new bulletin is published.

## `uscis.py`

For most immigration documents, USCIS provides a receipt number. This number can
be used on the [https://egov.uscis.gov]() website to check the status. This
script checks that URL periodically and sends a notification when the case
status changes. It also keeps a history of previous statuses.
